from actions.base import PoseAction
from poses import HOME, TALKING4S_1, SPEAKING2_3, SPEAK2


class Talking8s(PoseAction):

    def __init__(self):
        super().__init__([
            (0.0,  HOME),
            (2.0,  TALKING4S_1),
            (4.0,  SPEAKING2_3),
            (6.0,  SPEAK2),
            (8.0,  HOME),
        ])
