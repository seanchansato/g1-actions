import math


def lerp(a, b, t):
    return a + (b - a) * t


def cosine_ease(t):
    """Smooth ease-in-out, t in [0, 1]."""
    return (1 - math.cos(t * math.pi)) / 2


class Action:

    def update(self, t):
        """Return {actuator_name: target_angle_rad} for time t."""
        return {}


class PoseAction(Action):
    """
    Interpolates through a sequence of (time, pose) keyframes using
    cosine easing between each pair.  Pose dicts map actuator names to
    target angles in radians.

    keyframes: [(t0, pose0), (t1, pose1), ...]  in ascending time order.
    """

    def __init__(self, keyframes):
        self.keyframes = keyframes

    def update(self, t):

        if not self.keyframes:
            return {}

        if t <= self.keyframes[0][0]:
            return dict(self.keyframes[0][1])

        if t >= self.keyframes[-1][0]:
            return dict(self.keyframes[-1][1])

        for i in range(len(self.keyframes) - 1):
            t0, pose0 = self.keyframes[i]
            t1, pose1 = self.keyframes[i + 1]
            if t0 <= t <= t1:
                alpha = cosine_ease((t - t0) / (t1 - t0))
                keys = set(pose0) | set(pose1)
                return {
                    k: lerp(
                        pose0.get(k, 0.0),
                        pose1.get(k, 0.0),
                        alpha
                    )
                    for k in keys
                }

        return {}
