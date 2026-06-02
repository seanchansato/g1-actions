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
    try:
        import mediapipe.solutions.hands as _mp_hands
    except ModuleNotFoundError:
        import mediapipe.python.solutions.hands as _mp_hands
    _HAS_MP = True
except ImportError:
    _HAS_MP = False


# Landmark indices
_WRIST = 0
_FINGER_TIPS = [4, 8, 12, 16, 20]   # thumb, index, middle, ring, pinky tips
_FINGER_MCPS = [2, 5,  9, 13, 17]   # corresponding base knuckles
_FINGER_PIPS = [3, 6, 10, 14, 18]   # first interphalangeal joints


def _is_high_five_pose(landmarks):
    """
    Return True only when the hand shows clear, deliberate high-five intent:
      1. All 4 fingers (excl. thumb) extended past both MCP and PIP joints.
      2. Thumb extended past its MCP.
      3. Palm squarely facing the camera (strict depth threshold).
      4. Fingers spread — adjacent fingertip pairs are not bunched together.

    Uses only MediaPipe's normalised 3-D landmarks.
    """
    lm = landmarks.landmark
    wrist = np.array([lm[_WRIST].x, lm[_WRIST].y, lm[_WRIST].z])

    # ── 1. Non-thumb fingers: tip must clear both MCP and PIP ────────────────
    # Checking against PIP (not just MCP) rejects a loosely-open hand.
    for tip_idx, mcp_idx, pip_idx in zip(_FINGER_TIPS[1:], _FINGER_MCPS[1:], _FINGER_PIPS[1:]):
        tip = np.array([lm[tip_idx].x, lm[tip_idx].y, lm[tip_idx].z])
        mcp = np.array([lm[mcp_idx].x, lm[mcp_idx].y, lm[mcp_idx].z])
        pip = np.array([lm[pip_idx].x, lm[pip_idx].y, lm[pip_idx].z])
        d_wrist = np.linalg.norm(tip - wrist)
        if d_wrist <= np.linalg.norm(mcp - wrist):
            return False
        if d_wrist <= np.linalg.norm(pip - wrist):
            return False

    # ── 2. Thumb: tip must clear its MCP ─────────────────────────────────────
    thumb_tip = np.array([lm[4].x, lm[4].y, lm[4].z])
    thumb_mcp = np.array([lm[2].x, lm[2].y, lm[2].z])
    if np.linalg.norm(thumb_tip - wrist) <= np.linalg.norm(thumb_mcp - wrist):
        return False

    # ── 3. Palm facing camera — strict threshold ──────────────────────────────
    # All four non-thumb fingertips must individually be in front (negative Z).
    tip_zs = [lm[i].z for i in _FINGER_TIPS[1:]]  # index, middle, ring, pinky
    if any(z >= -0.05 for z in tip_zs):
        return False

    # ── 4. Fingers spread (not bunched) ──────────────────────────────────────
    # Adjacent non-thumb fingertip pairs must be at least 3 % of image width apart.
    tips_xy = [np.array([lm[i].x, lm[i].y]) for i in _FINGER_TIPS[1:]]
    for a, b in zip(tips_xy, tips_xy[1:]):
        if np.linalg.norm(a - b) < 0.03:
            return False

    return True


class HandDetector:
    """
    Detect hands and return their 3-D camera-frame positions.

    Parameters
    ----------
    max_hands : int
        Maximum number of hands to track simultaneously.
    min_detection_confidence : float
    min_tracking_confidence : float
    """

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
        depth_m : np.ndarray, shape (H, W), dtype float32  (optional)
            Depth image aligned to rgb_frame, values in metres.
        camera_matrix : np.ndarray, shape (3, 3)  (optional)
            Intrinsics [[fx,0,cx],[0,fy,cy],[0,0,1]].

        Returns
        -------
        list of dicts, each with:
          'position'     : np.ndarray (3,) – [x_cam, y_cam, z_cam] metres
          'side'         : 'left' | 'right'  (from the *person's* perspective)
          'high_five'    : bool – open palm facing camera
          'landmarks'    : raw MediaPipe NormalizedLandmarkList
        """
        h, w = rgb_frame.shape[:2]
        results = self._hands.process(rgb_frame)

        if not results.multi_hand_landmarks:
            return []

        detected = []
        for lm, handedness in zip(results.multi_hand_landmarks,
                                   results.multi_handedness):
            wrist = lm.landmark[_WRIST]
            side  = handedness.classification[0].label.lower()

            if depth_m is not None and camera_matrix is not None:
                px = int(np.clip(wrist.x * w, 0, w - 1))
                py = int(np.clip(wrist.y * h, 0, h - 1))

                p     = self._DEPTH_PATCH
                patch = depth_m[max(0, py-p):py+p+1, max(0, px-p):px+p+1]
                valid = patch[patch > 0.05]
                if valid.size == 0:
                    continue
                z  = float(np.median(valid))
                fx = camera_matrix[0, 0];  fy = camera_matrix[1, 1]
                cx = camera_matrix[0, 2];  cy = camera_matrix[1, 2]
                pos = np.array([(px - cx) * z / fx,
                                (py - cy) * z / fy,
                                z], dtype=float)
            else:
                z   = max(0.3, 0.8 - wrist.z)
                pos = np.array([(wrist.x - 0.5) * z * 1.5,
                                (wrist.y - 0.5) * z * 1.2,
                                z], dtype=float)

            detected.append({
                "position":  pos,
                "side":      side,
                "high_five": _is_high_five_pose(lm),
                "landmarks": lm,
            })

        return detected

    def close(self):
        self._hands.close()
