from actions.base import PoseAction
from poses import HOME, ARMS_UP


class ArmsUp(PoseAction):

    def __init__(self):
        super().__init__([
            (0.0, HOME),
            (1.5, ARMS_UP),
            (3.5, ARMS_UP),
            (5.0, HOME),
        ])
