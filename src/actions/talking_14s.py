from actions.base import PoseAction
from poses import HOME, SPEAKING2_3, TALKING4S_1, SPEAK1, SPEAKING2_1, TALKING4S_2, SPEAKING2_4


class Talking14s(PoseAction):

    def __init__(self):
        super().__init__([
            (0.0,  HOME),
            (2.0,  SPEAKING2_3),
            (4.0,  TALKING4S_1),
            (6.0,  SPEAK1),
            (8.0,  SPEAKING2_1),
            (10.0, TALKING4S_2),
            (12.0, SPEAKING2_4),
            (14.0, HOME),
        ])
