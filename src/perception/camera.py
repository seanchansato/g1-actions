"""Camera input abstraction + camera-to-robot coordinate transform.

Supported backends (tried in priority order):
  1. Insta360 via RTSP stream (robot's chest-mounted camera)
  2. Intel RealSense (pyrealsense2) – metric depth, real intrinsics
  3. OpenCV webcam – fallback for local development

Coordinate frames
-----------------
Camera optical frame  : X right, Y down, Z forward  (standard pinhole)
Robot / pelvis frame  : X forward, Y left, Z up

Insta360 is mounted on the robot's RIGHT chest panel, facing forward.
Extrinsics below use placeholder values — update _T_CAM_IN_ROBOT once
the physical mount position has been measured.
"""

import time
import numpy as np
import cv2

from .hand_detector import HandDetector

# ── Camera → robot rotation ───────────────────────────────────────────────────
# Camera faces forward on the chest, same optical orientation as the head cam:
#   robot_x (forward) = cam_z (forward)
#   robot_y (left)    = -cam_x (-right)
#   robot_z (up)      = -cam_y (-down)
_R_CAM_TO_ROBOT = np.array([
    [ 0,  0,  1],
    [-1,  0,  0],
    [ 0, -1,  0],
], dtype=float)

# Camera origin in pelvis frame [x_fwd, y_left, z_up] (metres).
# Measured: 4 in forward (0.102 m), 4 in right (-0.102 m), 15.75 in up (0.400 m).
_T_CAM_IN_ROBOT = np.array([0.102, -0.102, 0.400], dtype=float)


def cam_to_robot(pos_cam):
    """Transform a 3-D point from camera frame to robot/pelvis frame."""
    return _R_CAM_TO_ROBOT @ pos_cam + _T_CAM_IN_ROBOT


def update_extrinsics(x_fwd, y_left, z_up):
    """
    Call this at startup once the mount position has been measured.

    Parameters (all in metres, pelvis frame):
      x_fwd  : forward distance from pelvis centre to camera lens
      y_left : lateral offset (negative = robot's right side)
      z_up   : height above pelvis joint
    """
    global _T_CAM_IN_ROBOT
    _T_CAM_IN_ROBOT = np.array([x_fwd, y_left, z_up], dtype=float)
    print(f"[camera] Extrinsics updated: {_T_CAM_IN_ROBOT}")


# ── Camera backends ───────────────────────────────────────────────────────────

class _Insta360Backend:
    """
    Reads from the Insta360 RTSP stream published by the OM1 SDK node.

    The insta360_stream ROS2 node re-publishes the camera feed as:
      rtsp://localhost:8554/top_camera_raw   (on the robot)

    When running on a laptop connected to the robot's network, pass the
    robot's IP:  rtsp://<robot-ip>:8554/top_camera_raw
    """

    def __init__(self, rtsp_url="rtsp://localhost:8554/top_camera_raw"):
        # Quick TCP probe before handing to OpenCV — avoids a multi-second hang
        import socket, urllib.parse
        parsed = urllib.parse.urlparse(rtsp_url)
        host = parsed.hostname or "localhost"
        port = parsed.port or 554
        try:
            s = socket.create_connection((host, port), timeout=1.0)
            s.close()
        except OSError:
            raise RuntimeError(f"Insta360 RTSP port unreachable: {host}:{port}")

        self._cap = cv2.VideoCapture(rtsp_url, cv2.CAP_FFMPEG)
        self._cap.set(cv2.CAP_PROP_BUFFERSIZE, 1)
        if not self._cap.isOpened():
            raise RuntimeError(f"Cannot open Insta360 RTSP stream: {rtsp_url}")
        print(f"[camera] Insta360 RTSP stream opened: {rtsp_url}")
        self.camera_matrix = None   # no depth / no calibrated intrinsics

    def read(self):
        ok, frame = self._cap.read()
        if not ok:
            raise RuntimeError("Insta360 stream read failed")
        return cv2.cvtColor(frame, cv2.COLOR_BGR2RGB), None

    def stop(self):
        self._cap.release()


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
        self._scale   = depth_sensor.get_depth_scale()
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
        frames    = self._pipeline.wait_for_frames(timeout_ms=2000)
        aligned   = self._align.process(frames)
        depth_raw = np.asarray(aligned.get_depth_frame().get_data())
        color_bgr = np.asarray(aligned.get_color_frame().get_data())
        return (cv2.cvtColor(color_bgr, cv2.COLOR_BGR2RGB),
                depth_raw.astype(float) * self._scale)

    def stop(self):
        self._pipeline.stop()


class _WebcamBackend:
    def __init__(self, index=None):
        candidates = [index] if index is not None else list(range(4))
        for i in candidates:
            cap = cv2.VideoCapture(i)
            if cap.isOpened():
                self._cap = cap
                print(f"[camera] Opened webcam at index {i}")
                break
            cap.release()
        else:
            raise RuntimeError(f"Cannot open any webcam (tried {candidates})")
        self.camera_matrix = None

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
    Unified camera wrapper.

    Priority order:
      1. Insta360 RTSP stream (robot hardware)
      2. RealSense depth camera
      3. OpenCV webcam (local dev fallback)

    Usage
    -----
    cam = DepthCamera()                          # auto-detect
    cam = DepthCamera(backend="insta360")        # force Insta360
    cam = DepthCamera(backend="insta360",
                      rtsp_url="rtsp://192.168.1.100:8554/top_camera_raw")
    cam = DepthCamera(backend="webcam")          # local dev
    hands = cam.get_hands_in_robot_frame()
    cam.stop()
    """

    def __init__(self, backend="auto", rtsp_url="rtsp://localhost:8554/top_camera_raw",
                 prefer_realsense=False, show=False):
        self._backend = None
        self._detector = HandDetector()
        self._show = show

        if backend == "insta360" or backend == "auto":
            try:
                self._backend = _Insta360Backend(rtsp_url)
                return
            except RuntimeError as e:
                if backend == "insta360":
                    raise
                print(f"[camera] Insta360 unavailable ({e}), trying next backend")

        if prefer_realsense or backend == "realsense":
            try:
                self._backend = _RealSenseBackend()
                print("[camera] RealSense depth camera initialised")
                return
            except Exception as e:
                if backend == "realsense":
                    raise
                print(f"[camera] RealSense unavailable ({e}), trying webcam")

        self._backend = _WebcamBackend()
        print("[camera] Webcam backend initialised (no metric depth)")

    def get_hands_in_robot_frame(self):
        """
        Capture one frame, detect hands, return list of dicts:
          {'robot_pos': np.ndarray (3,), 'side': 'left'|'right',
           'high_five': bool}
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
            {
                "robot_pos": cam_to_robot(h["position"]),
                "side":      h["side"],
                "high_five": h["high_five"],
            }
            for h in raw
        ]

    def scan_for_high_five(self, timeout_s=6.0, hold_s=0.5):
        """
        Poll until the person holds a strict high-five pose for *hold_s*
        continuous seconds, or *timeout_s* elapses.

        Returns robot-frame position (np.ndarray) or None on timeout.
        When self._show is True, opens a live CV window with hold progress.
        """
        HOLD_S   = hold_s
        deadline = time.monotonic() + timeout_s
        print(f"[camera] Waiting for high-five gesture "
              f"({timeout_s:.0f}s window, hold {HOLD_S:.1f}s)...")

        # ── Shared hold-timer state ───────────────────────────────────────────
        hold_since = None   # time() when current hold streak started
        last_pos   = None

        def _update_hold(ready_hands):
            """Update hold timer; return confirmed pos or None."""
            nonlocal hold_since, last_pos
            now = time.monotonic()
            if ready_hands:
                best     = max(ready_hands, key=lambda h: h["robot_pos"][2])
                last_pos = best["robot_pos"]
                if hold_since is None:
                    hold_since = now
                    print("[camera] Hold started — keep palm open...")
                if now - hold_since >= HOLD_S:
                    print(f"[camera] High-five confirmed at robot pos "
                          f"({last_pos[0]:.2f}, {last_pos[1]:.2f}, {last_pos[2]:.2f}) m")
                    return last_pos
            else:
                if hold_since is not None:
                    print("[camera] Hold broken — waiting again...")
                hold_since = None
            return None

        # ── Headless path ─────────────────────────────────────────────────────
        if not self._show:
            while time.monotonic() < deadline:
                hands = self.get_hands_in_robot_frame()
                pos   = _update_hold([h for h in hands if h["high_five"]])
                if pos is not None:
                    return pos
            print("[camera] No high-five gesture detected within timeout")
            return None

        # ── Visual path ───────────────────────────────────────────────────────
        try:
            try:
                import mediapipe.solutions.drawing_utils as _mp_draw
                import mediapipe.solutions.hands as _mp_hands
            except ModuleNotFoundError:
                import mediapipe.python.solutions.drawing_utils as _mp_draw
                import mediapipe.python.solutions.hands as _mp_hands
        except ImportError as e:
            print(f"[camera] mediapipe drawing unavailable ({e}), blind scan")
            self._show = False
            return self.scan_for_high_five(timeout_s=timeout_s, hold_s=hold_s)

        result_pos = None
        while time.monotonic() < deadline:
            try:
                rgb, depth = self._backend.read()
            except RuntimeError as e:
                print(f"[camera] Frame read error: {e}")
                break

            cam_matrix = getattr(self._backend, "camera_matrix", None)
            raw        = self._detector.detect(rgb, depth_m=depth, camera_matrix=cam_matrix)
            h, w       = rgb.shape[:2]
            display    = cv2.cvtColor(rgb, cv2.COLOR_RGB2BGR)
            now        = time.monotonic()

            ready_hands = []
            for det in raw:
                lm        = det["landmarks"]
                side      = det["side"]
                hf        = det["high_five"]
                robot_pos = cam_to_robot(det["position"])
                if hf:
                    ready_hands.append({**det, "robot_pos": robot_pos})

                color = ((0, 255, 80) if hf
                         else ((0, 200, 255) if side == "left" else (255, 100, 0)))
                _mp_draw.draw_landmarks(
                    display, lm, _mp_hands.HAND_CONNECTIONS,
                    _mp_draw.DrawingSpec(color=color, thickness=2, circle_radius=3),
                    _mp_draw.DrawingSpec(color=(200, 200, 200), thickness=1),
                )
                wrist = lm.landmark[0]
                px    = int(np.clip(wrist.x * w, 0, w - 1))
                py    = int(np.clip(wrist.y * h, 0, h - 1))
                arm   = "LEFT arm" if robot_pos[1] > 0 else "RIGHT arm"
                cv2.putText(display,
                            f"{side[0].upper()} fwd={robot_pos[0]:.2f} "
                            f"lat={robot_pos[1]:+.2f} up={robot_pos[2]:.2f}m",
                            (px - 60, py - 18), cv2.FONT_HERSHEY_SIMPLEX, 0.5, color, 2)
                cv2.putText(display, arm, (px - 40, py + 18),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.45, (180, 255, 180), 1)

            if not raw:
                cv2.putText(display, "no hands detected", (10, h - 30),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.6, (60, 60, 255), 2)

            # Hold progress bar
            if hold_since is not None and ready_hands:
                held    = min(now - hold_since, HOLD_S)
                pct     = held / HOLD_S
                bar_w   = int(w * 0.6)
                bar_x   = (w - bar_w) // 2
                cv2.rectangle(display, (bar_x, h - 22), (bar_x + bar_w, h - 8),
                              (60, 60, 60), -1)
                cv2.rectangle(display, (bar_x, h - 22),
                              (bar_x + int(bar_w * pct), h - 8), (0, 255, 80), -1)
                cv2.putText(display, f"Hold... {held:.1f}/{HOLD_S:.1f}s",
                            (bar_x, h - 26), cv2.FONT_HERSHEY_SIMPLEX, 0.55,
                            (0, 255, 80), 2)
            elif ready_hands:
                cv2.putText(display, "OPEN PALM DETECTED", (w // 2 - 120, h - 15),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.65, (0, 255, 80), 2)

            remaining = max(0.0, deadline - now)
            cv2.putText(display, f"{remaining:.1f}s  Q=cancel",
                        (w - 130, 25), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 0), 2)
            cv2.imshow("G1 High Five - Hand Detection", display)
            if cv2.waitKey(1) & 0xFF == ord('q'):
                break

            result_pos = _update_hold(ready_hands)
            if result_pos is not None:
                break

        cv2.destroyAllWindows()
        if result_pos is None:
            print("[camera] No high-five gesture detected within timeout")
        return result_pos

    def scan_for_raised_hand(self, timeout_s=6.0):
        """Alias for scan_for_high_five — kept for backward compatibility."""
        return self.scan_for_high_five(timeout_s=timeout_s)

    def stop(self):
        if self._backend is not None:
            self._backend.stop()
        self._detector.close()
