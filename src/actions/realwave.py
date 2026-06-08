from actions.base import PoseAction
from poses import HOME, REALWAVE_1, REALWAVE_2, REALWAVE_3


class RealWave(PoseAction):

    def __init__(self):
        super().__init__([
            (0.0, HOME),
            (1.5, REALWAVE_1),
            (2.25, REALWAVE_2),
            (3.0, REALWAVE_3),
            (3.75, REALWAVE_2),
            (4.5, REALWAVE_3),
            (5.25, REALWAVE_2),
            (6.0, REALWAVE_1),
            (7.5, HOME),
        ])
