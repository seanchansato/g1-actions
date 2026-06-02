"""Live camera view with hand detection overlay.

Run from src/:
    python -m perception.visualize
    python -m perception.visualize --realsense   # force RealSense
"""

import sys
import time
import numpy as np
import cv2

try:
    try:
        import mediapipe.solutions.hands as _mp_hands
        import mediapipe.solutions.drawing_utils as _mp_draw
    except ModuleNotFoundError:
        import mediapipe.python.solutions.hands as _mp_hands
        import mediapipe.python.solutions.drawing_utils as _mp_draw
except ImportError as e:
    print(f"mediapipe not available: {e}")
    sys.exit(1)

from perception.camera import cam_to_robot, _WebcamBackend, _RealSenseBackend, _Insta360Backend
from perception.hand_detector import _is_high_five_pose


def run(prefer_realsense=False, rtsp_url=None):
    if rtsp_url:
        try:
            backend = _Insta360Backend(rtsp_url)
            print(f"[viz] Insta360 RTSP backend: {rtsp_url}")
        except Exception as e:
            print(f"[viz] Insta360 failed ({e}), using webcam")
            backend = _WebcamBackend()
    elif prefer_realsense:
        try:
            backend = _RealSenseBackend()
            print("[viz] RealSense backend")
        except Exception as e:
            print(f"[viz] RealSense failed ({e}), using webcam")
            backend = _WebcamBackend()
    else:
        backend = _WebcamBackend()
        print("[viz] Webcam backend")

    detector = _mp_hands.Hands(
        static_image_mode=False,
        max_num_hands=2,
        min_detection_confidence=0.7,
        min_tracking_confidence=0.5,
    )

    # How long the HIGH FIVE flash stays on screen after last detection (s)
    _FLASH_HOLD = 0.6
    last_hf_time = 0.0

    print("[viz] Press Q to quit — open palm facing camera triggers HIGH FIVE")

    while True:
        try:
            rgb, depth = backend.read()
        except RuntimeError as e:
            print(f"[viz] Read error: {e}")
            break

        h, w = rgb.shape[:2]
        results = detector.process(rgb)
        display = cv2.cvtColor(rgb, cv2.COLOR_RGB2BGR)

        # Depth heatmap thumbnail (RealSense only)
        if depth is not None:
            d_vis   = np.clip(depth / 4.0, 0, 1)
            d_color = cv2.applyColorMap((d_vis * 255).astype(np.uint8), cv2.COLORMAP_TURBO)
            d_small = cv2.resize(d_color, (w // 4, h // 4))
            display[0:h//4, 0:w//4] = d_small
            cv2.putText(display, "depth", (4, h//4 - 4),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.4, (255, 255, 255), 1)

        any_high_five = False
        cam_matrix    = getattr(backend, "camera_matrix", None)

        if results.multi_hand_landmarks:
            for lm, handedness in zip(results.multi_hand_landmarks,
                                       results.multi_handedness):
                side      = handedness.classification[0].label.lower()
                hf_ready  = _is_high_five_pose(lm)
                any_high_five = any_high_five or hf_ready

                # Skeleton colour: bright green if high-five, else side colour
                if hf_ready:
                    skel_color = (0, 255, 80)
                elif side == "left":
                    skel_color = (0, 200, 255)
                else:
                    skel_color = (255, 100, 0)

                _mp_draw.draw_landmarks(
                    display, lm,
                    _mp_hands.HAND_CONNECTIONS,
                    _mp_draw.DrawingSpec(color=skel_color, thickness=2, circle_radius=3),
                    _mp_draw.DrawingSpec(color=(200, 200, 200), thickness=1),
                )

                # Wrist pixel
                wrist = lm.landmark[0]
                px = int(np.clip(wrist.x * w, 0, w - 1))
                py = int(np.clip(wrist.y * h, 0, h - 1))

                # Robot-frame position
                if depth is not None and cam_matrix is not None:
                    p     = 4
                    patch = depth[max(0,py-p):py+p+1, max(0,px-p):px+p+1]
                    valid = patch[patch > 0.05]
                    if valid.size > 0:
                        z  = float(np.median(valid))
                        fx, fy = cam_matrix[0,0], cam_matrix[1,1]
                        cx, cy = cam_matrix[0,2], cam_matrix[1,2]
                        pos_robot = cam_to_robot(
                            np.array([(px-cx)*z/fx, (py-cy)*z/fy, z]))
                        depth_tag = ""
                    else:
                        pos_robot = None
                        depth_tag = " (no depth)"
                else:
                    z = max(0.3, 0.8 - wrist.z)
                    pos_robot = cam_to_robot(
                        np.array([(wrist.x-0.5)*z*1.5, (wrist.y-0.5)*z*1.2, z]))
                    depth_tag = " (est)"

                if pos_robot is not None:
                    arm   = "LEFT arm" if pos_robot[1] > 0 else "RIGHT arm"
                    coord = (f"{side[0].upper()} "
                             f"fwd={pos_robot[0]:.2f} "
                             f"lat={pos_robot[1]:+.2f} "
                             f"up={pos_robot[2]:.2f}m{depth_tag}")
                    cv2.putText(display, coord,  (px - 60, py - 18),
                                cv2.FONT_HERSHEY_SIMPLEX, 0.5, skel_color, 2)
                    cv2.putText(display, arm,    (px - 40, py + 18),
                                cv2.FONT_HERSHEY_SIMPLEX, 0.45, (180, 255, 180), 1)

                # "READY" badge on the wrist when high-five pose is held
                if hf_ready:
                    cv2.putText(display, "READY", (px - 28, py - 38),
                                cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 80), 2)
        else:
            cv2.putText(display, "no hands detected", (10, h - 30),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.6, (60, 60, 255), 2)

        # Full-frame HIGH FIVE flash
        if any_high_five:
            last_hf_time = time.monotonic()
        if time.monotonic() - last_hf_time < _FLASH_HOLD:
            cv2.rectangle(display, (0, 0), (w - 1, h - 1), (0, 255, 80), 6)
            cv2.putText(display, "HIGH FIVE!", (w//2 - 110, 55),
                        cv2.FONT_HERSHEY_DUPLEX, 1.4, (0, 255, 80), 3)

        cv2.putText(display, f"{w}x{h}  Q=quit", (w - 160, h - 8),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.4, (160, 160, 160), 1)

        cv2.imshow("G1 Hand Perception", display)
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    detector.close()
    backend.stop()
    cv2.destroyAllWindows()


if __name__ == "__main__":
    rtsp = None
    if "--rtsp" in sys.argv:
        i = sys.argv.index("--rtsp")
        rtsp = sys.argv[i + 1] if i + 1 < len(sys.argv) else "rtsp://localhost:8554/top_camera_raw"
    elif "--insta360" in sys.argv:
        rtsp = "rtsp://localhost:8554/top_camera_raw"
    run(prefer_realsense="--realsense" in sys.argv, rtsp_url=rtsp)
