from actions.base import PoseAction
from poses import HOME, TALKING4S_2, SPEAK1, SPEAKING2_4, TALKING4S_0, SPEAKING2_1, SPEAK2, TALKING4S_3


class Talking20s(PoseAction):

    def __init__(self):
        super().__init__([
            (0.0,  HOME),
            (2.5,  TALKING4S_2),
            (5.0,  SPEAK1),
            (7.5,  SPEAKING2_4),
            (10.0, TALKING4S_0),
            (12.5, SPEAKING2_1),
            (15.0, SPEAK2),
            (17.5, TALKING4S_3),
            (20.0, HOME),
        ])
