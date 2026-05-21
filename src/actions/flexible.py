from actions.base import PoseAction
from poses import HOME, FLEX1, FLEX2, FLEX3, FLEX4


class Flexible(PoseAction):

    def __init__(self):
        super().__init__([
            (0.0,  HOME),
            (1.5,  FLEX1),
            (3.0,  FLEX2),
            (4.5,  FLEX3),
            (6.0,  FLEX4),
            (7.5,  HOME),
        ])
