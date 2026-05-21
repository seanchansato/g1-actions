from actions.base import PoseAction
from poses import HOME, T_POSE


class TPosition(PoseAction):

    def __init__(self):
        super().__init__([
            (0.0, HOME),
            (1.5, T_POSE),
            (3.5, T_POSE),
            (5.0, HOME),
        ])
