from actions.base import PoseAction
from poses import HOME, SPEAKING2_1, TALKING4S_2, SPEAK1, SPEAKING2_4


class Talking10s(PoseAction):

    def __init__(self):
        super().__init__([
            (0.0,  HOME),
            (2.0,  SPEAKING2_1),
            (4.0,  TALKING4S_2),
            (6.0,  SPEAK1),
            (8.0,  SPEAKING2_4),
            (10.0, HOME),
        ])
