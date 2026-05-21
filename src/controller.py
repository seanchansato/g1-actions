import time
import mujoco

# PD gains per actuator group (kp Nm/rad, kd Nm·s/rad).
# Motor force limits: arm ±25 Nm, wrist ±5 Nm.
_GAINS = {
    "shoulder_pitch": (40.0, 4.0),
    "shoulder_roll":  (40.0, 4.0),
    "shoulder_yaw":   (30.0, 3.0),
    "elbow":          (30.0, 3.0),
    "wrist_roll":     (10.0, 1.0),
    "wrist_pitch":    (10.0, 1.0),
    "wrist_yaw":      (10.0, 1.0),
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

    def update(self, data):

        if self.start_time is None:
            self.start_time = time.time()

        t = time.time() - self.start_time
        targets = self.action.update(t)

        for act_name, q_des in targets.items():
            if act_name not in self._acts:
                continue
            qpos_adr, dof_adr, ctrl_idx, kp, kd = self._acts[act_name]
            q  = data.qpos[qpos_adr]
            dq = data.qvel[dof_adr]
            data.ctrl[ctrl_idx] = kp * (q_des - q) - kd * dq
