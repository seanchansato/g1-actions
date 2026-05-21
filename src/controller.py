import time
import mujoco
from poses import STANDING_BASE

# PD gains per actuator group (kp Nm/rad, kd Nm·s/rad).
# Matched to each joint's ctrlrange in the XML.
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
_DEFAULT_GAINS = (20.0, 2.0)


def _gains_for(name):
    for key, gains in _GAINS.items():
        if key in name:
            return gains
    return _DEFAULT_GAINS


class Controller:

    def __init__(self, model, action):

        self.action = action
        self.start_time = None

        # Build: actuator_name -> (qpos_adr, dof_adr, ctrl_idx, kp, kd)
        self._acts = {}
        for i in range(model.nu):
            act_name = mujoco.mj_id2name(
                model, mujoco.mjtObj.mjOBJ_ACTUATOR, i
            )
            if act_name is None:
                continue
            joint_id = int(model.actuator_trnid[i, 0])
            if joint_id < 0:
                continue
            kp, kd = _gains_for(act_name)
            self._acts[act_name] = (
                int(model.jnt_qposadr[joint_id]),
                int(model.jnt_dofadr[joint_id]),
                i,
                kp,
                kd,
            )

    def elapsed(self):
        return time.time() - self.start_time if self.start_time is not None else 0.0

    def update(self, data):

        if self.start_time is None:
            self.start_time = time.time()

        t = time.time() - self.start_time
        targets = self.action.update(t)

        # Every actuator is PD-controlled: use the action target if present,
        # otherwise hold the joint at its STANDING_BASE value.
        for act_name, (qpos_adr, dof_adr, ctrl_idx, kp, kd) in self._acts.items():
            q_des = targets.get(act_name, STANDING_BASE.get(act_name, 0.0))
            q  = data.qpos[qpos_adr]
            dq = data.qvel[dof_adr]
            data.ctrl[ctrl_idx] = kp * (q_des - q) - kd * dq
