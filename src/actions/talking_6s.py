from actions.base import PoseAction
from poses import HOME, SPEAK1, SPEAKING2_2, TALKING4S_3


class Talking6s(PoseAction):

    def __init__(self):
        super().__init__([
            (0.0, HOME),
            (1.5, SPEAK1),
            (3.0, SPEAKING2_2),
            (4.5, TALKING4S_3),
            (6.0, HOME),
        ])
