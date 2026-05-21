import os
import mujoco
import mujoco.viewer

_HERE = os.path.dirname(os.path.abspath(__file__))
MODEL_PATH = os.path.join(_HERE, "..", "models", "g1_29dof.xml")

# Physics steps per render frame.  At timestep=0.001 this gives 10ms
# per render frame (~100 Hz physics, ~60 Hz visual).
N_SUBSTEPS = 10


class Simulator:

    def __init__(self):

        self.model = mujoco.MjModel.from_xml_path(MODEL_PATH)
        self.data = mujoco.MjData(self.model)

    def run(self, controller):

        with mujoco.viewer.launch_passive(
            self.model,
            self.data
        ) as viewer:

            while viewer.is_running():

                controller.update(self.data)

                for _ in range(N_SUBSTEPS):
                    mujoco.mj_step(self.model, self.data)

                viewer.sync()
