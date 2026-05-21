from actions.base import PoseAction
from poses import NEUTRAL, SALUTE


class Salute(PoseAction):

    def __init__(self):
        super().__init__([
            (0.0, NEUTRAL),
            (2.0, SALUTE),   # 2 s to raise
            (4.0, SALUTE),   # hold 2 s
            (6.0, NEUTRAL),  # 2 s to lower
        ])
