"""Camera input abstraction + camera-to-robot coordinate transform.

Supported backends (tried in priority order):
  1. Intel RealSense (pyrealsense2) – metric depth, real intrinsics.
  2. OpenCV webcam – no real depth; falls back to MediaPipe relative Z.

Coordinate frames
-----------------
Camera optical frame  : X right, Y down, Z forward  (standard pinhole)
Robot / pelvis frame  : X forward, Y left, Z up

The G1's depth camera (D435i) lives in the head unit.  Approximate
extrinsics (measured from CAD / robot spec):
  translation : [0.07, 0.0, 0.357]  (metres, camera origin in pelvis frame)
  rotation    : see _R_CAM_TO_ROBOT below
"""

import time
import numpy as np
import cv2

from .hand_detector import HandDetector

# ── Camera → robot rotation ───────────────────────────────────────────────────
# robot_x (forward) = cam_z (forward)
# robot_y (left)    = -cam_x (-right)
# robot_z (up)      = -cam_y (-down)
_R_CAM_TO_ROBOT = np.array([
    [ 0,  0,  1],
    [-1,  0,  0],
    [ 0, -1,  0],
], dtype=float)

# Camera origin in pelvis frame [x_fwd, y_left, z_up] (metres)
_T_CAM_IN_ROBOT = np.array([0.07, 0.0, 0.357], dtype=float)


def cam_to_robot(pos_cam):
    """Transform a 3-D point from camera frame to robot/pelvis frame."""
    return _R_CAM_TO_ROBOT @ pos_cam + _T_CAM_IN_ROBOT


# ── Camera backends ───────────────────────────────────────────────────────────

class _RealSenseBackend:
    def __init__(self):
        import pyrealsense2 as rs
        self._rs = rs
        pipeline = rs.pipeline()
        cfg = rs.config()
        cfg.enable_stream(rs.stream.depth, 640, 480, rs.format.z16,  30)
        cfg.enable_stream(rs.stream.color, 640, 480, rs.format.bgr8, 30)
        profile = pipeline.start(cfg)

        depth_sensor  = profile.get_device().first_depth_sensor()
        self._scale   = depth_sensor.get_depth_scale()  # typically 0.001
        self._align   = rs.align(rs.stream.color)
        self._pipeline = pipeline

        intr = (profile.get_stream(rs.stream.color)
                .as_video_stream_profile().get_intrinsics())
        self.camera_matrix = np.array([
            [intr.fx, 0,        intr.ppx],
            [0,        intr.fy, intr.ppy],
            [0,        0,       1       ],
        ], dtype=float)

    def read(self):
        """Return (rgb_uint8, depth_m_float32) or raise on timeout."""
        frames   = self._pipeline.wait_for_frames(timeout_ms=2000)
        aligned  = self._align.process(frames)
        depth_raw = np.asarray(aligned.get_depth_frame().get_data())
        color_bgr = np.asarray(aligned.get_color_frame().get_data())
        return (cv2.cvtColor(color_bgr, cv2.COLOR_BGR2RGB),
                depth_raw.astype(float) * self._scale)

    def stop(self):
        self._pipeline.stop()


class _WebcamBackend:
    def __init__(self, index=0):
        self._cap = cv2.VideoCapture(index)
        if not self._cap.isOpened():
            raise RuntimeError(f"Cannot open webcam at index {index}")
        self.camera_matrix = None   # no depth / no intrinsics

    def read(self):
        ok, frame = self._cap.read()
        if not ok:
            raise RuntimeError("Webcam read failed")
        return cv2.cvtColor(frame, cv2.COLOR_BGR2RGB), None

    def stop(self):
        self._cap.release()


# ── Public interface ──────────────────────────────────────────────────────────

class DepthCamera:
    """
    Unified camera wrapper.  Tries RealSense first; falls back to webcam.

    Usage
    -----
    cam = DepthCamera()
    hands = cam.get_hands_in_robot_frame()
    cam.stop()
    """

    def __init__(self, prefer_realsense=True):
        self._backend = None
        self._detector = HandDetector()

        if prefer_realsense:
            try:
                self._backend = _RealSenseBackend()
                print("[camera] RealSense depth camera initialised")
                return
            except Exception as e:
                print(f"[camera] RealSense unavailable ({e}), trying webcam")

        self._backend = _WebcamBackend()
        print("[camera] Webcam backend initialised (no metric depth)")

    # ------------------------------------------------------------------

    def get_hands_in_robot_frame(self):
        """
        Capture one frame, detect hands, return list of dicts:
          {'robot_pos': np.ndarray (3,), 'side': 'left'|'right'}
        Returns [] if no hands found or on read error.
        """
        try:
            rgb, depth = self._backend.read()
        except RuntimeError as e:
            print(f"[camera] Frame read error: {e}")
            return []

        cam_matrix = getattr(self._backend, "camera_matrix", None)
        raw = self._detector.detect(rgb, depth_m=depth,
                                    camera_matrix=cam_matrix)
        return [
            {"robot_pos": cam_to_robot(h["position"]), "side": h["side"]}
            for h in raw
        ]

    def scan_for_raised_hand(self, timeout_s=4.0):
        """
        Poll the camera until a hand is detected or *timeout_s* elapses.

        Returns the robot-frame position (np.ndarray) of the highest
        (most upward) detected hand, or None if nothing was found.
        """
        deadline = time.monotonic() + timeout_s
        print(f"[camera] Scanning for raised hand ({timeout_s:.0f}s timeout)...")
        while time.monotonic() < deadline:
            hands = self.get_hands_in_robot_frame()
            if hands:
                best = max(hands, key=lambda h: h["robot_pos"][2])
                pos  = best["robot_pos"]
                print(f"[camera] Hand detected at robot pos "
                      f"({pos[0]:.2f}, {pos[1]:.2f}, {pos[2]:.2f}) m")
                return pos
        print("[camera] No hand detected within timeout")
        return None

    def stop(self):
        if self._backend is not None:
            self._backend.stop()
        self._detector.close()
