from actions.base import PoseAction
from poses import HOME, COME_CLOSER_1, COME_CLOSER_2


class ComeCloser(PoseAction):

    def __init__(self):
        super().__init__([
            (0.0, HOME),
            (1.5, COME_CLOSER_1),
            (2.5, COME_CLOSER_2),
            (3.5, COME_CLOSER_1),
            (4.5, COME_CLOSER_2),
            (5.5, COME_CLOSER_1),
            (7.0, HOME),
        ])
