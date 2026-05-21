from actions.base import PoseAction
from poses import HOME, HANDS_UP


class HandsUp(PoseAction):

    def __init__(self):
        super().__init__([
            (0.0, HOME),
            (1.5, HANDS_UP),   # 1.5 s to raise both arms
            (4.0, HANDS_UP),   # hold 2.5 s
            (5.5, HOME),       # 1.5 s to lower
        ])
