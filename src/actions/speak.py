from actions.base import PoseAction
from poses import HOME, SPEAK1, SPEAK2


class Speak(PoseAction):

    def __init__(self):
        super().__init__([
            (0.0, HOME),
            (1.5, SPEAK1),
            (3.0, SPEAK2),
            (4.5, SPEAK1),
            (6.0, HOME),
        ])
