from actions.base import PoseAction
from poses import HOME, SHRUG


class Shrug(PoseAction):

    def __init__(self):
        super().__init__([
            (0.0, HOME),
            (1.5, SHRUG),
            (3.5, SHRUG),
            (5.0, HOME),
        ])
