from actions.base import PoseAction
from poses import HOME, HANDSPIN_1, HANDSPIN_2


class HandSpin(PoseAction):

    def __init__(self):
        super().__init__([
            (0.0, HOME),
            (1.5, HANDSPIN_1),
            (3.0, HANDSPIN_2),
            (4.5, HANDSPIN_1),
            (6.0, HOME),
        ])
