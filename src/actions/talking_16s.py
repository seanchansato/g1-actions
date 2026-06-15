from actions.base import PoseAction
from poses import HOME, SPEAK2, SPEAKING2_2, TALKING4S_0, SPEAK1, TALKING4S_3, SPEAKING2_3, TALKING4S_1


class Talking16s(PoseAction):

    def __init__(self):
        super().__init__([
            (0.0,  HOME),
            (2.0,  SPEAK2),
            (4.0,  SPEAKING2_2),
            (6.0,  TALKING4S_0),
            (8.0,  SPEAK1),
            (10.0, TALKING4S_3),
            (12.0, SPEAKING2_3),
            (14.0, TALKING4S_1),
            (16.0, HOME),
        ])
