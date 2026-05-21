from actions.base import PoseAction
from poses import HOME, PUSH_1, PUSH_2


class Push(PoseAction):

    def __init__(self):
        super().__init__([
            (0.0, HOME),
            (1.5, PUSH_1),
            (3.0, PUSH_2),
            (4.5, HOME),
        ])
