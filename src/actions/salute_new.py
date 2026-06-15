from actions.base import PoseAction
from poses import HOME, SALUTE_NEW


class SaluteNew(PoseAction):

    def __init__(self):
        super().__init__([
            (0.0, HOME),
            (2.0, SALUTE_NEW),
            (4.0, SALUTE_NEW),
            (6.0, HOME),
        ])
