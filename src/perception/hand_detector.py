"""MediaPipe-based hand detection.

Returns hand wrist positions in the camera's optical frame:
  X right, Y down, Z forward (standard pinhole convention).

With a depth frame the positions are metric (metres).
Without depth, the Z axis is MediaPipe's relative estimate and
XY are scaled to a rough metric approximation.
"""

import numpy as np

try:
    import mediapipe as mp
    import mediapipe.solutions.hands as _mp_hands
    _HAS_MP = True
except ImportError:
    _HAS_MP = False


class HandDetector:
    """
    Detect raised hands and return their 3-D camera-frame positions.

    Parameters
    ----------
    max_hands : int
        Maximum number of hands to track simultaneously.
    min_detection_confidence : float
    min_tracking_confidence : float
    """

    # MediaPipe wrist landmark index
    _WRIST = 0
    # Patch half-size for depth averaging (pixels)
    _DEPTH_PATCH = 4

    def __init__(self, max_hands=2, min_detection_confidence=0.7,
                 min_tracking_confidence=0.5):
        if not _HAS_MP:
            raise ImportError(
                "mediapipe is required.  Install with:  pip install mediapipe"
            )
        self._hands = _mp_hands.Hands(
            static_image_mode=False,
            max_num_hands=max_hands,
            min_detection_confidence=min_detection_confidence,
            min_tracking_confidence=min_tracking_confidence,
        )

    def detect(self, rgb_frame, depth_m=None, camera_matrix=None):
        """
        Detect hands in an RGB frame and return metric 3-D positions.

        Parameters
        ----------
        rgb_frame : np.ndarray, shape (H, W, 3), dtype uint8
            RGB image from the camera.
        depth_m : np.ndarray, shape (H, W), dtype float32  (optional)
            Depth image aligned to rgb_frame, values in metres.
            If None, MediaPipe's relative Z estimate is used with crude scaling.
        camera_matrix : np.ndarray, shape (3, 3)  (optional)
            Intrinsics [[fx,0,cx],[0,fy,cy],[0,0,1]].
            Required when depth_m is provided.

        Returns
        -------
        list of dicts, each with:
          'position' : np.ndarray (3,) – [x_cam, y_cam, z_cam] metres
          'side'     : 'left' | 'right'  (from the *person's* perspective)
        """
        h, w = rgb_frame.shape[:2]
        results = self._hands.process(rgb_frame)

        if not results.multi_hand_landmarks:
            return []

        detected = []
        for lm, handedness in zip(results.multi_hand_landmarks,
                                   results.multi_handedness):
            wrist = lm.landmark[self._WRIST]
            side  = handedness.classification[0].label.lower()  # 'left'/'right'

            if depth_m is not None and camera_matrix is not None:
                px = int(np.clip(wrist.x * w, 0, w - 1))
                py = int(np.clip(wrist.y * h, 0, h - 1))

                # Median depth over a small patch (robust to single-pixel noise)
                p  = self._DEPTH_PATCH
                patch = depth_m[max(0, py-p):py+p+1, max(0, px-p):px+p+1]
                valid = patch[patch > 0.05]
                if valid.size == 0:
                    continue
                z = float(np.median(valid))

                fx = camera_matrix[0, 0]
                fy = camera_matrix[1, 1]
                cx = camera_matrix[0, 2]
                cy = camera_matrix[1, 2]
                pos = np.array([(px - cx) * z / fx,
                                (py - cy) * z / fy,
                                z], dtype=float)
            else:
                # Rough metric estimate from normalised + relative coordinates.
                # Assumes the hand is ~0.6–1.0 m from the camera.
                z   = max(0.3, 0.8 - wrist.z)        # MediaPipe z is relative; invert
                pos = np.array([(wrist.x - 0.5) * z * 1.5,
                                (wrist.y - 0.5) * z * 1.2,
                                z], dtype=float)

            detected.append({"position": pos, "side": side})

        return detected

    def close(self):
        self._hands.close()
