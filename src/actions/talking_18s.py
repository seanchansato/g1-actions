from actions.base import PoseAction
from poses import HOME, SPEAKING2_2, TALKING4S_0, SPEAK1, SPEAKING2_3, TALKING4S_3, SPEAK2, SPEAKING2_1, TALKING4S_2


class Talking18s(PoseAction):

    def __init__(self):
        super().__init__([
            (0.0,  HOME),
            (2.0,  SPEAKING2_2),
            (4.0,  TALKING4S_0),
            (6.0,  SPEAK1),
            (8.0,  SPEAKING2_3),
            (10.0, TALKING4S_3),
            (12.0, SPEAK2),
            (14.0, SPEAKING2_1),
            (16.0, TALKING4S_2),
            (18.0, HOME),
        ])
