from actions.base import PoseAction
from poses import HOME, COME_CLOSER2_1, COME_CLOSER2_2


class ComeCloser2(PoseAction):

    def __init__(self):
        super().__init__([
            (0.0, HOME),
            (1.5, COME_CLOSER2_1),
            (2.5, COME_CLOSER2_2),
            (3.5, COME_CLOSER2_1),
            (4.5, COME_CLOSER2_2),
            (6.0, HOME),
        ])
