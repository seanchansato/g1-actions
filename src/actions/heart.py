from actions.base import PoseAction
from poses import HOME, HEART


class Heart(PoseAction):

    def __init__(self):
        super().__init__([
            (0.0, HOME),
            (1.5, HEART),
            (3.5, HEART),
            (5.0, HOME),
        ])
