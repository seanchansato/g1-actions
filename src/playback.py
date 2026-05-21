#!/usr/bin/env python3
"""
Play back a recorded keyframe sequence.

  python src/playback.py <action_name>

Loads keyframes/<action_name>.json and smoothly interpolates between each
pose using smoothstep easing over STEPS_PER_TRANSITION physics steps,
then holds the final pose until the window is closed.
"""
import os
import sys
import json
import mujoco
import mujoco.viewer
from poses import HOME, STANDING_BASE

_HERE = os.path.dirname(os.path.abspath(__file__))
MODEL_PATH    = os.path.join(_HERE, "..", "models", "g1_29dof.xml")
KEYFRAMES_DIR = os.path.join(_HERE, "..", "keyframes")
HOME_JSON     = os.path.join(KEYFRAMES_DIR, "home.json")

STEPS_PER_TRANSITION = 200
N_SUBSTEPS           = 10

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
    pose = dict(STANDING_BASE)
    pose.update(HOME)
    if os.path.exists(HOME_JSON):
        with open(HOME_JSON) as f:
            data = json.load(f)
        for name, val in zip(_RIGHT_ARM, data.get("home_position", [])):
            pose[name] = val
    return pose


def _smoothstep(t):
    return t * t * (3.0 - 2.0 * t)


def _pd(data, acts, pose):
    for act_name, (qpos_adr, dof_adr, ctrl_idx, kp, kd) in acts.items():
        q_des = pose.get(act_name, 0.0)
        q     = data.qpos[qpos_adr]
        dq    = data.qvel[dof_adr]
        data.ctrl[ctrl_idx] = kp * (q_des - q) - kd * dq


def main():
    if len(sys.argv) < 2:
        print("Usage: python src/playback.py <action_name>")
        sys.exit(1)

    action_name = sys.argv[1]
    kf_path = os.path.join(KEYFRAMES_DIR, f"{action_name}.json")
    if not os.path.exists(kf_path):
        print(f"Not found: {kf_path}")
        sys.exit(1)

    with open(kf_path) as f:
        raw = json.load(f)

    joint_names = raw["joint_names"]
    kf_frames   = raw["frames"]

    model = mujoco.MjModel.from_xml_path(MODEL_PATH)
    data  = mujoco.MjData(model)
    acts  = _build_acts(model)

    home_pose = _load_home()

    # Seed qpos and apply home ctrl before the first step
    for act_name, (qpos_adr, _, _, _, _) in acts.items():
        data.qpos[qpos_adr] = home_pose.get(act_name, 0.0)
    mujoco.mj_forward(model, data)
    _pd(data, acts, home_pose)
    mujoco.mj_step(model, data)

    # Convert each raw ctrl list → pose dict using the stored joint_names
    def to_pose(ctrl_list):
        return dict(zip(joint_names, ctrl_list))

    poses = [home_pose] + [to_pose(fr["ctrl"]) for fr in kf_frames]

    print(f"Playing '{action_name}' — {len(kf_frames)} keyframes, "
          f"{STEPS_PER_TRANSITION} steps each")

    with mujoco.viewer.launch_passive(model, data) as viewer:

        for idx in range(len(poses) - 1):
            src = poses[idx]
            dst = poses[idx + 1]
            for step in range(STEPS_PER_TRANSITION):
                t = _smoothstep(step / STEPS_PER_TRANSITION)
                interp = {
                    k: src.get(k, 0.0) + t * (dst.get(k, 0.0) - src.get(k, 0.0))
                    for k in set(src) | set(dst)
                }
                _pd(data, acts, interp)
                for _ in range(N_SUBSTEPS):
                    mujoco.mj_step(model, data)
                viewer.sync()
                if not viewer.is_running():
                    return

        # Hold final pose
        final = poses[-1]
        while viewer.is_running():
            _pd(data, acts, final)
            for _ in range(N_SUBSTEPS):
                mujoco.mj_step(model, data)
            viewer.sync()


if __name__ == "__main__":
    main()
