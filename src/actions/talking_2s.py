from actions.base import PoseAction
from poses import HOME, TALKING4S_1


class Talking2s(PoseAction):

    def __init__(self):
        super().__init__([
            (0.0, HOME),
            (1.0, TALKING4S_1),
            (2.0, HOME),
        ])
