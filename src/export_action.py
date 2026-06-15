"""
Convert a PoseAction keyframe sequence to the recording JSON format
used by the OM1-ros2-sdk g1_action_replay / g1_arm_action nodes.

Usage:
    python src/export_action.py --action salute --out recordings/salute.json
"""
import argparse
import json
import math
import sys


# ── Joint definitions ──────────────────────────────────────────────────────
JOINT_NAMES = [
    "left_shoulder_pitch",
    "left_shoulder_roll",
    "left_shoulder_yaw",
    "left_elbow",
    "left_wrist_roll",
    "left_wrist_pitch",
    "left_wrist_yaw",
    "right_shoulder_pitch",
    "right_shoulder_roll",
    "right_shoulder_yaw",
    "right_elbow",
    "right_wrist_roll",
    "right_wrist_pitch",
    "right_wrist_yaw",
]

MOTOR_INDICES = [15, 16, 17, 18, 19, 20, 21, 22, 23, 24, 25, 26, 27, 28]


# ── Interpolation helpers ──────────────────────────────────────────────────
def cosine_ease(t):
    return (1 - math.cos(t * math.pi)) / 2


def lerp(a, b, t):
    return a + (b - a) * t


def sample_pose_action(keyframes, t):
    """Sample a PoseAction at time t using cosine easing."""
    if t <= keyframes[0][0]:
        return dict(keyframes[0][1])
    if t >= keyframes[-1][0]:
        return dict(keyframes[-1][1])

    for i in range(len(keyframes) - 1):
        t0, pose0 = keyframes[i]
        t1, pose1 = keyframes[i + 1]
        if t0 <= t <= t1:
            alpha = cosine_ease((t - t0) / (t1 - t0))
            keys = set(pose0) | set(pose1)
            return {k: lerp(pose0.get(k, 0.0), pose1.get(k, 0.0), alpha) for k in keys}

    return {}


# ── Main conversion ────────────────────────────────────────────────────────
def convert(keyframes, rate_hz=20.0, hold_on_complete=False, next_action=None):
    duration = keyframes[-1][0]
    home_pose = keyframes[0][1]

    home_position = [home_pose.get(j, 0.0) for j in JOINT_NAMES]

    n_frames = int(duration * rate_hz) + 1
    frames = []
    for i in range(n_frames):
        t = i / rate_hz
        if t > duration:
            t = duration
        pose = sample_pose_action(keyframes, t)
        q = [pose.get(j, home_pose.get(j, 0.0)) for j in JOINT_NAMES]
        frames.append({"t": round(t, 6), "q": [round(v, 6) for v in q]})

    return {
        "robot": "unitree_g1",
        "joint_names": JOINT_NAMES,
        "motor_indices": MOTOR_INDICES,
        "home_position": [round(v, 6) for v in home_position],
        "record_rate_hz": rate_hz,
        "num_frames": len(frames),
        "duration_s": round(duration, 4),
        "hold_on_complete": hold_on_complete,
        "next_action": next_action,
        "frames": frames,
    }


# ── Action definitions ─────────────────────────────────────────────────────
# Import poses inline so this script is self-contained when run from src/.
sys.path.insert(0, "src")
try:
    from poses import HOME, SALUTE, SALUTE_NEW, HANDS_UP, WAVE_RAISED, SHRUG, FLEX1, FLEX2, FLEX3, FLEX4, TEST, SPEAK1, SPEAK2, ARMS_UP, T_POSE, COME_CLOSER_1, COME_CLOSER_2, COME_CLOSER2_1, COME_CLOSER2_2, HEART, SPEAKING2_1, SPEAKING2_2, SPEAKING2_3, SPEAKING2_4, PUSH_1, PUSH_2, STOP_1, STOP_2, HANDSPIN_1, HANDSPIN_2, TALKING4S_0, TALKING4S_1, TALKING4S_2, TALKING4S_3
except ImportError:
    from poses import HOME, SALUTE, SALUTE_NEW, HANDS_UP, WAVE_RAISED, SHRUG, FLEX1, FLEX2, FLEX3, FLEX4, TEST, SPEAK1, SPEAK2, ARMS_UP, T_POSE, COME_CLOSER_1, COME_CLOSER_2, COME_CLOSER2_1, COME_CLOSER2_2, HEART, SPEAKING2_1, SPEAKING2_2, SPEAKING2_3, SPEAKING2_4, PUSH_1, PUSH_2, STOP_1, STOP_2, HANDSPIN_1, HANDSPIN_2, TALKING4S_0, TALKING4S_1, TALKING4S_2, TALKING4S_3  # noqa: F811

ACTIONS = {
    "salute": {
        "keyframes": [
            (0.0, HOME),
            (2.0, SALUTE),
            (4.0, SALUTE),
            (6.0, HOME),
        ],
        "hold_on_complete": False,
        "next_action": None,
    },
    "salute_new": {
        "keyframes": [
            (0.0, HOME),
            (2.0, SALUTE_NEW),
            (4.0, SALUTE_NEW),
            (6.0, HOME),
        ],
        "hold_on_complete": False,
        "next_action": None,
    },
    "hands_up_scripted": {
        "keyframes": [
            (0.0, HOME),
            (2.0, HANDS_UP),
        ],
        "hold_on_complete": False,
        "next_action": None,
    },
    "shrug": {
        "keyframes": [
            (0.0, HOME),
            (1.5, SHRUG),
            (3.5, SHRUG),
            (5.0, HOME),
        ],
        "hold_on_complete": False,
        "next_action": None,
    },
    "handspin": {
        "keyframes": [
            (0.0, HOME),
            (1.5, HANDSPIN_1),
            (3.0, HANDSPIN_2),
            (4.5, HANDSPIN_1),
            (6.0, HOME),
        ],
        "hold_on_complete": False,
        "next_action": None,
    },
    "stop": {
        "keyframes": [
            (0.0, HOME),
            (1.5, STOP_1),
            (3.0, STOP_2),
            (4.5, HOME),
        ],
        "hold_on_complete": False,
        "next_action": None,
    },
    "push": {
        "keyframes": [
            (0.0, HOME),
            (1.5, PUSH_1),
            (3.0, PUSH_2),
            (4.5, HOME),
        ],
        "hold_on_complete": False,
        "next_action": None,
    },
    "speaking2": {
        "keyframes": [
            (0.0, HOME),
            (1.5, SPEAKING2_1),
            (3.0, SPEAKING2_2),
            (4.5, SPEAKING2_1),
            (6.0, HOME),
        ],
        "hold_on_complete": False,
        "next_action": None,
    },
    "heart": {
        "keyframes": [
            (0.0, HOME),
            (1.5, HEART),
            (3.5, HEART),
            (5.0, HOME),
        ],
        "hold_on_complete": False,
        "next_action": None,
    },
    "come_closer2": {
        "keyframes": [
            (0.0, HOME),
            (1.5, COME_CLOSER2_1),
            (2.5, COME_CLOSER2_2),
            (3.5, COME_CLOSER2_1),
            (4.5, COME_CLOSER2_2),
            (6.0, HOME),
        ],
        "hold_on_complete": False,
        "next_action": None,
    },
    "come_closer": {
        "keyframes": [
            (0.0, HOME),
            (1.5, COME_CLOSER_1),
            (2.5, COME_CLOSER_2),
            (3.5, COME_CLOSER_1),
            (4.5, COME_CLOSER_2),
            (5.5, COME_CLOSER_1),
            (7.0, HOME),
        ],
        "hold_on_complete": False,
        "next_action": None,
    },
    "t_position": {
        "keyframes": [
            (0.0, HOME),
            (1.5, T_POSE),
            (3.5, T_POSE),
            (5.0, HOME),
        ],
        "hold_on_complete": False,
        "next_action": None,
    },
    "arms_up": {
        "keyframes": [
            (0.0, HOME),
            (1.5, ARMS_UP),
            (3.5, ARMS_UP),
            (5.0, HOME),
        ],
        "hold_on_complete": False,
        "next_action": None,
    },
    "test": {
        "keyframes": [
            (0.0, HOME),
            (1.5, TEST),
            (3.5, TEST),
            (5.0, HOME),
        ],
        "hold_on_complete": False,
        "next_action": None,
    },
    "flexible": {
        "keyframes": [
            (0.0,  HOME),
            (1.5,  FLEX1),
            (3.0,  FLEX2),
            (4.5,  FLEX3),
            (6.0,  FLEX4),
            (7.5,  HOME),
        ],
        "hold_on_complete": False,
        "next_action": None,
    },
    "talking_2s": {
        "keyframes": [
            (0.0, HOME),
            (1.0, TALKING4S_1),
            (2.0, HOME),
        ],
        "hold_on_complete": False,
        "next_action": None,
    },
    "talking_4s": {
        "keyframes": [
            (0.0, HOME),
            (1.0, SPEAK1),
            (2.5, SPEAK2),
            (4.0, HOME),
        ],
        "hold_on_complete": False,
        "next_action": None,
    },
    "talking_6s": {
        "keyframes": [
            (0.0, HOME),
            (1.5, SPEAK1),
            (3.0, SPEAKING2_2),
            (4.5, TALKING4S_3),
            (6.0, HOME),
        ],
        "hold_on_complete": False,
        "next_action": None,
    },
    "talking_8s": {
        "keyframes": [
            (0.0, HOME),
            (2.0, TALKING4S_1),
            (4.0, SPEAKING2_3),
            (6.0, SPEAK2),
            (8.0, HOME),
        ],
        "hold_on_complete": False,
        "next_action": None,
    },
    "talking_10s": {
        "keyframes": [
            (0.0,  HOME),
            (2.0,  SPEAKING2_1),
            (4.0,  TALKING4S_2),
            (6.0,  SPEAK1),
            (8.0,  SPEAKING2_4),
            (10.0, HOME),
        ],
        "hold_on_complete": False,
        "next_action": None,
    },
    "talking_12s": {
        "keyframes": [
            (0.0,  HOME),
            (2.0,  TALKING4S_0),
            (4.0,  SPEAK2),
            (6.0,  SPEAKING2_2),
            (8.0,  TALKING4S_3),
            (10.0, SPEAK1),
            (12.0, HOME),
        ],
        "hold_on_complete": False,
        "next_action": None,
    },
    "talking_14s": {
        "keyframes": [
            (0.0,  HOME),
            (2.0,  SPEAKING2_3),
            (4.0,  TALKING4S_1),
            (6.0,  SPEAK1),
            (8.0,  SPEAKING2_1),
            (10.0, TALKING4S_2),
            (12.0, SPEAKING2_4),
            (14.0, HOME),
        ],
        "hold_on_complete": False,
        "next_action": None,
    },
    "talking_16s": {
        "keyframes": [
            (0.0,  HOME),
            (2.0,  SPEAK2),
            (4.0,  SPEAKING2_2),
            (6.0,  TALKING4S_0),
            (8.0,  SPEAK1),
            (10.0, TALKING4S_3),
            (12.0, SPEAKING2_3),
            (14.0, TALKING4S_1),
            (16.0, HOME),
        ],
        "hold_on_complete": False,
        "next_action": None,
    },
    "talking_18s": {
        "keyframes": [
            (0.0,  HOME),
            (2.0,  SPEAKING2_2),
            (4.0,  TALKING4S_0),
            (6.0,  SPEAK1),
            (8.0,  SPEAKING2_3),
            (10.0, TALKING4S_3),
            (12.0, SPEAK2),
            (14.0, SPEAKING2_1),
            (16.0, TALKING4S_2),
            (18.0, HOME),
        ],
        "hold_on_complete": False,
        "next_action": None,
    },
    "talking_20s": {
        "keyframes": [
            (0.0,  HOME),
            (2.5,  TALKING4S_2),
            (5.0,  SPEAK1),
            (7.5,  SPEAKING2_4),
            (10.0, TALKING4S_0),
            (12.5, SPEAKING2_1),
            (15.0, SPEAK2),
            (17.5, TALKING4S_3),
            (20.0, HOME),
        ],
        "hold_on_complete": False,
        "next_action": None,
    },
}


def main():
    parser = argparse.ArgumentParser(description="Export a PoseAction to recording JSON")
    parser.add_argument("--action", required=True, choices=list(ACTIONS.keys()))
    parser.add_argument("--out", "-o", required=True, help="Output JSON path")
    parser.add_argument("--rate", type=float, default=20.0, help="Sample rate in Hz")
    args = parser.parse_args()

    cfg = ACTIONS[args.action]
    recording = convert(
        cfg["keyframes"],
        rate_hz=args.rate,
        hold_on_complete=cfg["hold_on_complete"],
        next_action=cfg["next_action"],
    )

    with open(args.out, "w") as f:
        json.dump(recording, f, indent=2)

    print(f"Wrote {recording['num_frames']} frames ({recording['duration_s']}s) → {args.out}")


if __name__ == "__main__":
    main()
