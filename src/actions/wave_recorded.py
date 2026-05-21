import os
from actions.base import TrajectoryAction
from poses import HOME

_DIR = os.path.join(
    os.path.dirname(os.path.abspath(__file__)),
    "..", "..", "recordings",
)


def _rec(filename):
    return os.path.join(_DIR, filename)


class WaveRecorded(TrajectoryAction):
    def __init__(self, loop=False):
        super().__init__(_rec("face_wave.json"), pre_roll=1.5, start_pose=HOME, loop=loop)


class HandsUpRecorded(TrajectoryAction):
    def __init__(self, loop=False):
        super().__init__(_rec("hands_up.json"), pre_roll=1.5, start_pose=HOME, loop=loop)


class ShakeHand(TrajectoryAction):
    def __init__(self, loop=False):
        super().__init__(_rec("shake_hand.json"), pre_roll=1.5, start_pose=HOME, loop=loop)


class ShowHand(TrajectoryAction):
    def __init__(self, loop=False):
        super().__init__(_rec("show_hand.json"), pre_roll=1.5, start_pose=HOME, loop=loop)


class DoPayment(TrajectoryAction):
    def __init__(self, loop=False):
        super().__init__(_rec("do_payment.json"), pre_roll=1.5, start_pose=HOME, loop=loop)


class DownPayment(TrajectoryAction):
    def __init__(self, loop=False):
        super().__init__(_rec("down_payment.json"), pre_roll=1.5, start_pose=HOME, loop=loop)
