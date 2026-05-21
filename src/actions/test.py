from actions.base import PoseAction
from poses import HOME, TEST


class Test(PoseAction):

    def __init__(self):
        super().__init__([
            (0.0, HOME),
            (1.5, TEST),
            (3.5, TEST),
            (5.0, HOME),
        ])
