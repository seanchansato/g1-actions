from actions.base import PoseAction
from poses import HOME, SPEAKING2_1, SPEAKING2_2


class Speaking2(PoseAction):

    def __init__(self):
        super().__init__([
            (0.0, HOME),
            (1.5, SPEAKING2_1),
            (3.0, SPEAKING2_2),
            (4.5, SPEAKING2_1),
            (6.0, HOME),
        ])
