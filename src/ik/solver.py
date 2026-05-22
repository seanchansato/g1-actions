"""G1 29-DOF arm forward kinematics and numerical IK.

All positions in the pelvis frame (X forward, Y left, Z up).
Geometry extracted directly from models/g1_29dof.xml.

Joint order for the 7-element angle arrays:
  [shoulder_pitch, shoulder_roll, shoulder_yaw, elbow,
   wrist_roll, wrist_pitch, wrist_yaw]
"""

import numpy as np
from math import cos, sin


# ── Rotation helpers ─────────────────────────────────────────────────────────

def _qmat(w, x, y, z):
    """Quaternion (w,x,y,z) → 3×3 rotation matrix."""
    return np.array([
        [1 - 2*(y*y + z*z),  2*(x*y - w*z),       2*(x*z + w*y)      ],
        [2*(x*y + w*z),       1 - 2*(x*x + z*z),   2*(y*z - w*x)      ],
        [2*(x*z - w*y),       2*(y*z + w*x),        1 - 2*(x*x + y*y) ],
    ], dtype=float)


def _rx(a):
    c, s = cos(a), sin(a)
    return np.array([[1,0,0],[0,c,-s],[0,s,c]], dtype=float)


def _ry(a):
    c, s = cos(a), sin(a)
    return np.array([[c,0,s],[0,1,0],[-s,0,c]], dtype=float)


def _rz(a):
    c, s = cos(a), sin(a)
    return np.array([[c,-s,0],[s,c,0],[0,0,1]], dtype=float)


# ── Geometry constants from g1_29dof.xml ─────────────────────────────────────
# Waist chain at zero angles: pelvis → waist_yaw(0,0,0) → waist_roll(-0.004,0,0.035)
#                                      → torso(0,0,0.019)
_PELVIS_TO_TORSO = np.array([-0.0039635, 0.0, 0.054], dtype=float)

# Left arm ─ body offsets (in parent frame) and initial body quaternions
_L = {
    "sp_pos":  np.array([0.0039563,  0.10022,    0.23778], dtype=float),
    "sp_quat": (0.990264,  0.139201,  0.0, 0.0),
    "sr_pos":  np.array([0.0,        0.038,     -0.013831], dtype=float),
    "sr_quat": (0.990268, -0.139172,  0.0, 0.0),
    "sy_pos":  np.array([0.0,        0.00624,   -0.1032], dtype=float),
    "el_pos":  np.array([0.015783,   0.0,       -0.080518], dtype=float),
    "wr_pos":  np.array([0.1,        0.00188791,-0.01], dtype=float),
    "wp_pos":  np.array([0.038,      0.0,        0.0], dtype=float),
    "wy_pos":  np.array([0.046,      0.0,        0.0], dtype=float),
    "ee_pos":  np.array([0.0415,     0.003,      0.0], dtype=float),
}

# Right arm ─ mirrored Y signs and quaternion X signs
_R = {
    "sp_pos":  np.array([0.0039563, -0.10021,    0.23778], dtype=float),
    "sp_quat": (0.990264, -0.139201,  0.0, 0.0),
    "sr_pos":  np.array([0.0,       -0.038,     -0.013831], dtype=float),
    "sr_quat": (0.990268,  0.139172,  0.0, 0.0),
    "sy_pos":  np.array([0.0,       -0.00624,   -0.1032], dtype=float),
    "el_pos":  np.array([0.015783,   0.0,       -0.080518], dtype=float),
    "wr_pos":  np.array([0.1,       -0.00188791,-0.01], dtype=float),
    "wp_pos":  np.array([0.038,      0.0,        0.0], dtype=float),
    "wy_pos":  np.array([0.046,      0.0,        0.0], dtype=float),
    "ee_pos":  np.array([0.0415,    -0.003,      0.0], dtype=float),
}

# Joint limits [min, max] rad – from g1_29dof.xml actuatorfrcrange/range
LEFT_LIMITS = np.array([
    [-3.0892,  2.6704],   # shoulder_pitch
    [-1.5882,  2.2515],   # shoulder_roll
    [-2.618,   2.618 ],   # shoulder_yaw
    [-1.0472,  2.0944],   # elbow
    [-1.97222, 1.97222],  # wrist_roll
    [-1.61443, 1.61443],  # wrist_pitch
    [-1.61443, 1.61443],  # wrist_yaw
], dtype=float)

RIGHT_LIMITS = np.array([
    [-3.0892,  2.6704],   # shoulder_pitch
    [-2.2515,  1.5882],   # shoulder_roll  (mirrored)
    [-2.618,   2.618 ],   # shoulder_yaw
    [-1.0472,  2.0944],   # elbow
    [-1.97222, 1.97222],  # wrist_roll
    [-1.61443, 1.61443],  # wrist_pitch
    [-1.61443, 1.61443],  # wrist_yaw
], dtype=float)

LEFT_JOINTS  = ["left_shoulder_pitch",  "left_shoulder_roll",  "left_shoulder_yaw",
                "left_elbow",  "left_wrist_roll",  "left_wrist_pitch",  "left_wrist_yaw"]
RIGHT_JOINTS = ["right_shoulder_pitch", "right_shoulder_roll", "right_shoulder_yaw",
                "right_elbow", "right_wrist_roll", "right_wrist_pitch", "right_wrist_yaw"]

# Preferred null-space angles: arm raised, elbow bent, wrists neutral
_NULL_LEFT  = np.array([-0.8,  0.3, 0.0, 0.5, 0.0, 0.0, 0.0], dtype=float)
_NULL_RIGHT = np.array([-0.8, -0.3, 0.0, 0.5, 0.0, 0.0, 0.0], dtype=float)


# ── Forward kinematics ────────────────────────────────────────────────────────

def fk(q, side="right"):
    """
    Return end-effector (palm centre) position in pelvis frame.

    q: array-like of 7 angles [sp, sr, sy, elbow, wr, wp, wy].
    """
    sp, sr, sy, el, wr, wp, wy = q
    g = _L if side == "left" else _R

    # Start at torso origin (zero waist joints assumed for IK)
    p = _PELVIS_TO_TORSO.copy()
    R = np.eye(3, dtype=float)

    def _step(body_pos, body_quat, joint_R):
        nonlocal p, R
        p = p + R @ body_pos
        R = R @ _qmat(*body_quat) @ joint_R

    # 1. Shoulder pitch  (axis Y)
    _step(g["sp_pos"], g["sp_quat"], _ry(sp))
    # 2. Shoulder roll   (axis X)
    _step(g["sr_pos"], g["sr_quat"], _rx(sr))
    # 3. Shoulder yaw    (axis Z) – no body quaternion on this link
    p = p + R @ g["sy_pos"];  R = R @ _rz(sy)
    # 4. Elbow pitch     (axis Y)
    p = p + R @ g["el_pos"];  R = R @ _ry(el)
    # 5. Wrist roll      (axis X)
    p = p + R @ g["wr_pos"];  R = R @ _rx(wr)
    # 6. Wrist pitch     (axis Y)
    p = p + R @ g["wp_pos"];  R = R @ _ry(wp)
    # 7. Wrist yaw       (axis Z)
    p = p + R @ g["wy_pos"];  R = R @ _rz(wy)
    # End-effector offset
    ee = p + R @ g["ee_pos"]
    return ee


def fk_full(q, side="right"):
    """
    Return (ee_pos, ee_R) where ee_R is the 3×3 end-effector orientation.

    Column conventions of ee_R (verified against HOME pose):
      col 0 ([:,0]) — finger direction (along hand)
      col 1 ([:,1]) — thumb-side direction
      col 2 ([:,2]) — palm normal (which way the palm faces)
    """
    sp, sr, sy, el, wr, wp, wy = q
    g = _L if side == "left" else _R

    p = _PELVIS_TO_TORSO.copy()
    R = np.eye(3, dtype=float)

    def _step(body_pos, body_quat, joint_R):
        nonlocal p, R
        p = p + R @ body_pos
        R = R @ _qmat(*body_quat) @ joint_R

    _step(g["sp_pos"], g["sp_quat"], _ry(sp))
    _step(g["sr_pos"], g["sr_quat"], _rx(sr))
    p = p + R @ g["sy_pos"];  R = R @ _rz(sy)
    p = p + R @ g["el_pos"];  R = R @ _ry(el)
    p = p + R @ g["wr_pos"];  R = R @ _rx(wr)
    p = p + R @ g["wp_pos"];  R = R @ _ry(wp)
    p = p + R @ g["wy_pos"];  R = R @ _rz(wy)
    ee = p + R @ g["ee_pos"]
    return ee, R.copy()


# ── Palm-forward wrist solver ─────────────────────────────────────────────────

# Desired end-effector frame for a high-five.
# Verified against STOP_2 pose where the palm clearly faces forward (+X):
#   col_x ([:,0]) finger direction = [0, 0, 1]  (fingers pointing up)
#   col_y ([:,1]) palm normal      = [1, 0, 0]  (palm facing the person, +X forward)
#   col_z ([:,2]) back-of-hand     = col_x × col_y = [0, 1, 0]
# Same target orientation for both arms.
_R_PALM_FORWARD = np.array([
    [0.,  1.,  0.],
    [0.,  0.,  1.],
    [1.,  0.,  0.],
], dtype=float)


def _xyz_euler(M):
    """
    Decompose rotation matrix M = Rx(α) @ Ry(β) @ Rz(γ).
    Returns (α, β, γ).
    """
    beta  = float(np.arcsin(np.clip(M[0, 2], -1.0, 1.0)))
    cb    = np.cos(beta)
    if abs(cb) > 1e-6:
        alpha = float(np.arctan2(-M[1, 2], M[2, 2]))
        gamma = float(np.arctan2(-M[0, 1], M[0, 0]))
    else:
        # Gimbal lock — set yaw=0, solve for roll only
        alpha = float(np.arctan2(M[2, 1], M[1, 1]))
        gamma = 0.0
    return alpha, beta, gamma


def wrist_for_palm_forward(q_arm, side="right"):
    """
    Given joint angles (or just the first 4 shoulder/elbow angles), compute
    wrist_roll, wrist_pitch, wrist_yaw so the palm faces forward (+X robot).

    q_arm : 7-element array — only indices 0-3 (shoulder+elbow) matter;
            the function replaces indices 4-6.

    Returns a new 7-element array with corrected wrist angles (clamped to limits).
    """
    limits = LEFT_LIMITS if side == "left" else RIGHT_LIMITS

    # Rotation of arm frame after elbow with wrist joints zeroed out
    q0 = np.array(q_arm, dtype=float)
    q0[4:] = 0.0
    _, R_arm = fk_full(q0, side)

    # Required wrist rotation: Rx(wr) @ Ry(wp) @ Rz(wy) = R_arm.T @ R_desired
    M  = R_arm.T @ _R_PALM_FORWARD
    wr, wp, wy = _xyz_euler(M)

    # Clamp to wrist joint limits
    wr = float(np.clip(wr, limits[4, 0], limits[4, 1]))
    wp = float(np.clip(wp, limits[5, 0], limits[5, 1]))
    wy = float(np.clip(wy, limits[6, 0], limits[6, 1]))

    q_out      = np.array(q_arm, dtype=float)
    q_out[4]   = wr
    q_out[5]   = wp
    q_out[6]   = wy
    return q_out


def _jacobian(q, side):
    """Numerical 3×7 position Jacobian via central differences."""
    eps = 1e-5
    J = np.empty((3, 7), dtype=float)
    for i in range(7):
        dq = np.zeros(7)
        dq[i] = eps
        J[:, i] = (fk(q + dq, side) - fk(q - dq, side)) / (2 * eps)
    return J


# ── Inverse kinematics ────────────────────────────────────────────────────────

def solve_ik(target, side="right", q0=None, max_iter=300, pos_tol=0.02):
    """
    Damped-least-squares IK with null-space postural objective.

    target   : (3,) array, pelvis-frame metres.
    side     : 'left' or 'right'
    q0       : initial 7-element angle array (auto-chosen if None).
    pos_tol  : acceptable end-effector error in metres.

    Returns (q, converged) where q is a 7-element numpy array.
    """
    limits   = LEFT_LIMITS  if side == "left"  else RIGHT_LIMITS
    q_null   = _NULL_LEFT   if side == "left"  else _NULL_RIGHT
    target   = np.asarray(target, dtype=float)

    if q0 is None:
        q0 = q_null.copy()
    q = np.clip(np.asarray(q0, dtype=float), limits[:, 0], limits[:, 1])

    lam        = 0.05   # damping factor
    step       = 0.4    # gradient step scale
    null_gain  = 0.15   # pull toward postural preference

    for _ in range(max_iter):
        ee  = fk(q, side)
        err = target - ee
        dist = float(np.linalg.norm(err))

        if dist < pos_tol:
            break

        J    = _jacobian(q, side)
        JJT  = J @ J.T + (lam ** 2) * np.eye(3)
        Jpinv = J.T @ np.linalg.solve(JJT, np.eye(3))

        # Primary: move toward target
        dq_primary = Jpinv @ err

        # Null-space: pull toward preferred arm posture (only acts in null-space)
        null_proj = np.eye(7) - Jpinv @ J
        dq_null   = null_proj @ (q_null - q)

        q = q + step * dq_primary + null_gain * dq_null
        q = np.clip(q, limits[:, 0], limits[:, 1])

    final_err = float(np.linalg.norm(target - fk(q, side)))
    return q, final_err <= pos_tol


def joint_dict(q, side):
    """Convert 7-element angle array → {joint_name: angle} dict."""
    names = LEFT_JOINTS if side == "left" else RIGHT_JOINTS
    return dict(zip(names, (float(v) for v in q)))
