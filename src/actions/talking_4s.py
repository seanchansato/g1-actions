from actions.base import PoseAction
from poses import HOME, SPEAK1, SPEAK2


class Talking4s(PoseAction):

    def __init__(self):
        super().__init__([
            (0.0, HOME),
            (1.0, SPEAK1),
            (2.5, SPEAK2),
            (4.0, HOME),
        ])
