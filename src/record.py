#!/usr/bin/env python3
"""
Interactive keyframe recorder for the Unitree G1.

  python src/record.py

The robot starts at the home position.  Perturb arm joints using
Ctrl+click+drag in the viewer, then press K to latch the current pose
as a keyframe.  The PD controller holds the new pose so you can inspect
it before continuing.  Close the window when done and enter an action
name to save keyframes/<name>.json.
"""
import os
import json
import mujoco
import mujoco.viewer
from poses import HOME, STANDING_BASE

_HERE = os.path.dirname(os.path.abspath(__file__))
MODEL_PATH    = os.path.join(_HERE, "..", "models", "g1_29dof.xml")
KEYFRAMES_DIR = os.path.join(_HERE, "..", "keyframes")
HOME_JSON     = os.path.join(KEYFRAMES_DIR, "home.json")

_RIGHT_ARM = [
    "right_shoulder_pitch", "right_shoulder_roll", "right_shoulder_yaw",
    "right_elbow", "right_wrist_roll", "right_wrist_pitch", "right_wrist_yaw",
]

_GAINS = {
    "hip":            (100.0, 10.0),
    "knee":           (100.0, 10.0),
    "ankle":          ( 50.0,  5.0),
    "waist":          ( 80.0,  8.0),
    "shoulder_pitch": ( 40.0,  4.0),
    "shoulder_roll":  ( 40.0,  4.0),
    "shoulder_yaw":   ( 30.0,  3.0),
    "elbow":          ( 30.0,  3.0),
    "wrist_roll":     ( 10.0,  1.0),
    "wrist_pitch":    ( 10.0,  1.0),
    "wrist_yaw":      ( 10.0,  1.0),
}


def _gains_for(name):
    for key, gains in _GAINS.items():
        if key in name:
            return gains
    return (20.0, 2.0)


def _build_acts(model):
    acts = {}
    for i in range(model.nu):
        act_name = mujoco.mj_id2name(model, mujoco.mjtObj.mjOBJ_ACTUATOR, i)
        if act_name is None:
            continue
        joint_id = int(model.actuator_trnid[i, 0])
        if joint_id < 0:
            continue
        kp, kd = _gains_for(act_name)
        acts[act_name] = (
            int(model.jnt_qposadr[joint_id]),
            int(model.jnt_dofadr[joint_id]),
            i, kp, kd,
        )
    return acts


def _load_home():
    """Start from poses.HOME, override right arm from home.json if present."""
    pose = dict(STANDING_BASE)
    pose.update(HOME)
    if os.path.exists(HOME_JSON):
        with open(HOME_JSON) as f:
            data = json.load(f)
        for name, val in zip(_RIGHT_ARM, data.get("home_position", [])):
            pose[name] = val
    return pose


def main():
    model = mujoco.MjModel.from_xml_path(MODEL_PATH)
    data  = mujoco.MjData(model)
    acts  = _build_acts(model)

    # Ordered joint names matching actuator indices (for the saved JSON)
    joint_names = [
        mujoco.mj_id2name(model, mujoco.mjtObj.mjOBJ_ACTUATOR, i)
        for i in range(model.nu)
    ]

    # Mutable target: PD controller tracks this dict
    target = _load_home()

    # Seed qpos so physics starts at home (no settling jerk)
    for act_name, (qpos_adr, _, _, _, _) in acts.items():
        data.qpos[qpos_adr] = target.get(act_name, 0.0)
    mujoco.mj_forward(model, data)

    keyframes = []

    def key_callback(keycode):
        if keycode != ord('K'):
            return
        # Latch current pose into target so PD holds the new position
        for act_name, (qpos_adr, _, _, _, _) in acts.items():
            target[act_name] = float(data.qpos[qpos_adr])
        # Record ctrl array in actuator index order
        ctrl_snap = [target.get(n, 0.0) for n in joint_names]
        keyframes.append(ctrl_snap)
        print(f"  keyframe {len(keyframes):2d} recorded  "
              f"(right_shoulder_pitch={target.get('right_shoulder_pitch', 0):.3f})")

    print("Controls:")
    print("  Ctrl+click+drag  — perturb joints")
    print("  K                — record current pose as a keyframe")
    print("  close window     — finish and save\n")

    with mujoco.viewer.launch_passive(
        model, data, key_callback=key_callback
    ) as viewer:
        while viewer.is_running():
            for act_name, (qpos_adr, dof_adr, ctrl_idx, kp, kd) in acts.items():
                q_des = target.get(act_name, 0.0)
                q     = data.qpos[qpos_adr]
                dq    = data.qvel[dof_adr]
                data.ctrl[ctrl_idx] = kp * (q_des - q) - kd * dq
            mujoco.mj_step(model, data)
            viewer.sync()

    if not keyframes:
        print("No keyframes recorded — nothing saved.")
        return

    name = input(f"\nAction name ({len(keyframes)} keyframes): ").strip()
    if not name:
        print("Cancelled.")
        return

    os.makedirs(KEYFRAMES_DIR, exist_ok=True)
    out = {
        "joint_names": joint_names,
        "frames": [
            {"label": f"frame_{i}", "ctrl": kf}
            for i, kf in enumerate(keyframes)
        ],
    }
    out_path = os.path.join(KEYFRAMES_DIR, f"{name}.json")
    with open(out_path, "w") as f:
        json.dump(out, f, indent=2)
    print(f"Saved {len(keyframes)} keyframes → {out_path}")


if __name__ == "__main__":
    main()
