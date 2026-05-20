import mujoco
import mujoco.viewer

MODEL_PATH = "models/humanoid.xml"

class Simulator:

    def __init__(self):

        self.model = mujoco.MjModel.from_xml_path(
            MODEL_PATH
        )

        self.data = mujoco.MjData(
            self.model
        )

    def run(self, controller):

        with mujoco.viewer.launch_passive(
            self.model,
            self.data
        ) as viewer:

            while viewer.is_running():

                controller.update(
                    self.data
                )

                mujoco.mj_step(
                    self.model,
                    self.data
                )

                viewer.sync()

