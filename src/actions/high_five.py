"""High-five action.

Uses the G1's depth camera (or falls back to a webcam) to locate a person's
raised hand, selects the nearest robot arm, solves inverse kinematics, and
smoothly executes the high-five gesture.

Arm selection rule:
  target Y > 0  (person's hand is on the robot's LEFT side)  → left arm
  target Y ≤ 0  (person's hand is on the robot's RIGHT side) → right arm

Coordinate frame for target_pos: pelvis origin, X forward, Y left, Z up.

Typical reachable target zone (in pelvis frame, metres):
  X  0.35 – 0.65   (in front of the robot)
  Y  ±0.1 – ±0.45  (to the side)
  Z  0.30 – 0.70   (pelvis+0.30 → ~1.1m AGL to pelvis+0.70 → ~1.49m AGL)
"""

import sys
import os
import numpy as np

# Allow imports from src/ regardless of how main.py is invoked
_SRC = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if _SRC not in sys.path:
    sys.path.insert(0, _SRC)

from actions.base import Action, PoseAction
from ik.solver import solve_ik, joint_dict, fk, fk_full, wrist_for_palm_forward, LEFT_JOINTS, RIGHT_JOINTS
from poses import HOME

# ── Arm geometry constants (pelvis frame, metres) ─────────────────────────────
# Shoulder joint positions (approximate, at zero waist angles)
_SHOULDER_POS = {
    "right": np.array([ 0.0,  -0.100,  0.292], dtype=float),
    "left":  np.array([ 0.0,   0.100,  0.292], dtype=float),
}
# 90% of max arm reach (0.452m) – leave margin so IK reliably converges
_MAX_REACH = 0.41

# ── Default test targets (pelvis frame, metres) ───────────────────────────────
# Pre-verified to be within arm reach from the shoulder.
_TEST_TARGETS = {
    "right": np.array([0.38, -0.25, 0.45], dtype=float),
    "left":  np.array([0.38,  0.25, 0.45], dtype=float),
}


def _clamp_target(target, side):
    """
    If the target is further than _MAX_REACH from the shoulder, project it
    onto the sphere of radius _MAX_REACH centred on the shoulder.  This lets
    the robot always reach *toward* the person even when they're too far away.
    """
    shoulder = _SHOULDER_POS[side]
    vec  = target - shoulder
    dist = float(np.linalg.norm(vec))
    if dist > _MAX_REACH:
        return shoulder + vec / dist * _MAX_REACH
    return target

# ── Raise fraction: how far along the shoulder→target ray the "palm up"
#    intermediate pose sits.  0.55 means arm raised and visible but elbow
#    still comfortably bent before the forward push.
_RAISE_FRACTION = 0.55


class HighFiveAction(Action):
    """
    Perform a high five toward a detected or explicitly provided hand position.

    Motion sequence (mirroring stop.py's two-phase structure):
      HOME → raise palm up (arm raised, elbow bent, palm already forward)
           → push forward to target (arm extends to contact point)
           → brief hold
           → HOME

    Parameters
    ----------
    target_pos : array-like (3,) or None
        Hand position in the robot/pelvis frame (metres).
        When None and camera is not None, the camera scans for a raised hand.
        When both are None the action uses a built-in test position.
    camera : DepthCamera or None
        Instance of perception.camera.DepthCamera.  Supply for live use;
        omit for simulation / testing with a fixed target.
    side : 'auto' | 'left' | 'right'
        Force a specific arm, or 'auto' to choose by Y-position of the target.
    """

    def __init__(self, target_pos=None, camera=None, side="auto"):

        # ── Step 1: obtain target position ───────────────────────────────────
        if target_pos is None and camera is not None:
            target_pos = camera.scan_for_raised_hand(timeout_s=4.0)

        if target_pos is None:
            arm = "right" if side == "auto" else side
            target_pos = _TEST_TARGETS[arm]
            print(f"[high_five] No target given – using test position "
                  f"(side={arm}): {target_pos}")

        target_pos = np.asarray(target_pos, dtype=float)

        # ── Step 2: select arm ────────────────────────────────────────────────
        if side == "auto":
            arm = "left" if target_pos[1] > 0 else "right"
        else:
            arm = side
        print(f"[high_five] Target {target_pos}, arm: {arm}")

        # ── Step 3: clamp to reachable workspace ─────────────────────────────
        clamped = _clamp_target(target_pos, arm)
        if not np.allclose(clamped, target_pos):
            print(f"[high_five] Target clamped to reach boundary: {clamped}")
        target_pos = clamped

        # ── Step 4: solve IK for the "push forward" (final contact) pose ─────
        q_push, converged = solve_ik(target_pos, side=arm)
        error_m = float(np.linalg.norm(target_pos - fk(q_push, arm)))
        if converged:
            print(f"[high_five] IK converged  (error {error_m*100:.1f} cm)")
        else:
            print(f"[high_five] IK best-effort (error {error_m*100:.1f} cm)")

        q_push = wrist_for_palm_forward(q_push, arm)
        _, R_ee = fk_full(q_push, arm)
        print(f"[high_five] Palm normal: {R_ee[:,1].round(2)}  (want ≈ [1,0,0])")
        push_pose = {**HOME, **joint_dict(q_push, arm)}

        # ── Step 5: solve IK for the "palm up" (raised, elbow bent) pose ─────
        # Intermediate target sits 55% of the way from shoulder to final target,
        # so the arm is raised in the right direction but not yet extended.
        shoulder   = _SHOULDER_POS[arm]
        raise_tgt  = shoulder + (target_pos - shoulder) * _RAISE_FRACTION
        q_raise, _ = solve_ik(raise_tgt, side=arm, q0=q_push)
        q_raise    = wrist_for_palm_forward(q_raise, arm)
        raise_pose = {**HOME, **joint_dict(q_raise, arm)}

        print(f"[high_five] Raise target: {raise_tgt.round(3)}, "
              f"push target: {target_pos.round(3)}")

        # ── Step 6: build keyframe sequence ──────────────────────────────────
        #   0.0 s  HOME
        #   1.5 s  raise palm up   (arm up, elbow bent, palm already facing fwd)
        #   3.0 s  push forward    (arm extends to contact point)
        #   3.5 s  hold            (the slap moment)
        #   4.2 s  push back       (recoil — arm pulls back to raised position)
        #   5.2 s  HOME
        self._action = PoseAction([
            (0.0, HOME),
            (1.5, raise_pose),
            (3.0, push_pose),
            (3.5, push_pose),
            (4.2, raise_pose),
            (5.2, HOME),
        ])

    # ── Action interface ──────────────────────────────────────────────────────

    @property
    def duration(self):
        return self._action.duration

    def update(self, t):
        return self._action.update(t)
