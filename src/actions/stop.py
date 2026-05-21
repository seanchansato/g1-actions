from actions.base import PoseAction
from poses import HOME, STOP_1, STOP_2


class Stop(PoseAction):

    def __init__(self):
        super().__init__([
            (0.0, HOME),
            (1.5, STOP_1),
            (3.0, STOP_2),
            (4.5, STOP_1),
            (6.0, HOME),
        ])
