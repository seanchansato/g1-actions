import os
import mujoco
import mujoco.viewer
from poses import STANDING_BASE

_HERE = os.path.dirname(os.path.abspath(__file__))
MODEL_PATH = os.path.join(_HERE, "..", "models", "g1_29dof.xml")

# Physics steps per render frame.  At timestep=0.001 this gives 10ms
# per render frame (~100 Hz physics, ~60 Hz visual).
N_SUBSTEPS = 10


class Simulator:

    def __init__(self):

        self.model = mujoco.MjModel.from_xml_path(MODEL_PATH)
        self.data = mujoco.MjData(self.model)
        self._seed_qpos()

    def _seed_qpos(self):
        """Set initial joint positions from STANDING_BASE so physics starts
        in the correct pose rather than settling from the zero state."""
        for i in range(self.model.nu):
            act_name = mujoco.mj_id2name(
                self.model, mujoco.mjtObj.mjOBJ_ACTUATOR, i
            )
            if act_name not in STANDING_BASE:
                continue
            joint_id = int(self.model.actuator_trnid[i, 0])
            if joint_id < 0:
                continue
            self.data.qpos[int(self.model.jnt_qposadr[joint_id])] = (
                STANDING_BASE[act_name]
            )
        mujoco.mj_forward(self.model, self.data)

    def run(self, controller):

        duration = controller.action.duration
        quit_requested = [False]

        def on_key(keycode):
            if keycode in (ord('q'), ord('Q')):
                quit_requested[0] = True

        with mujoco.viewer.launch_passive(
            self.model,
            self.data,
            key_callback=on_key,
        ) as viewer:

            while viewer.is_running() and not quit_requested[0]:

                if duration is None or controller.elapsed() <= duration:
                    controller.update(self.data)
                else:
                    controller.hold_home(self.data)

                for _ in range(N_SUBSTEPS):
                    mujoco.mj_step(self.model, self.data)

                viewer.sync()
