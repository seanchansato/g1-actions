import time

from actions.salute import Salute

class Controller:

    def __init__(self):

        self.action = Salute()

        self.start_time = time.time()

    def update(self, data):

        t = (
            time.time()
            - self.start_time
        )

        joints = self.action.update(t)

        data.ctrl[0] = joints[
            "right_shoulder"
        ]
