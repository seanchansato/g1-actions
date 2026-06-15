from actions.base import PoseAction
from poses import HOME, TALKING4S_0, SPEAK2, SPEAKING2_2, TALKING4S_3, SPEAK1


class Talking12s(PoseAction):

    def __init__(self):
        super().__init__([
            (0.0,  HOME),
            (2.0,  TALKING4S_0),
            (4.0,  SPEAK2),
            (6.0,  SPEAKING2_2),
            (8.0,  TALKING4S_3),
            (10.0, SPEAK1),
            (12.0, HOME),
        ])
