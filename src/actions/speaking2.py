from actions.base import PoseAction
from poses import HOME, SPEAKING2_1, SPEAKING2_2, SPEAKING2_3, SPEAKING2_4


class Speaking2(PoseAction):

    def __init__(self):
        super().__init__([
            (0.0, HOME),
            (1.5, SPEAKING2_1),
            (3.0, SPEAKING2_2),
            (4.5, SPEAKING2_3),
            (6.0, SPEAKING2_4),
            (7.5, HOME),
        ])
