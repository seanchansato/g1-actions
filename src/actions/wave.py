import math
from actions.base import Action, lerp, cosine_ease
from poses import HOME, WAVE_RAISED

_RAISE_T  = 1.5   # s to raise arm
_WAVE_T   = 4.0   # s of waving
_LOWER_T  = 1.5   # s to lower arm
_FREQ     = 1.5   # Hz of wrist oscillation
_YAW_AMP  = 0.6   # rad amplitude of right_wrist_yaw swing


class Wave(Action):
    """
    1. Raise right arm to WAVE_RAISED over _RAISE_T seconds.
    2. Oscillate right_wrist_yaw at _FREQ Hz for _WAVE_T seconds.
    3. Lower arm back to HOME over _LOWER_T seconds.
    """

    duration = _RAISE_T + _WAVE_T + _LOWER_T

    def update(self, t):

        end_raise = _RAISE_T
        end_wave  = _RAISE_T + _WAVE_T
        end_lower = end_wave + _LOWER_T

        if t < end_raise:
            alpha = cosine_ease(t / _RAISE_T)
            return {
                k: lerp(HOME.get(k, 0.0), WAVE_RAISED.get(k, 0.0), alpha)
                for k in set(HOME) | set(WAVE_RAISED)
            }

        elif t < end_wave:
            wt = t - end_raise
            yaw = _YAW_AMP * math.sin(2 * math.pi * _FREQ * wt)
            pose = dict(WAVE_RAISED)
            pose["right_wrist_yaw"] = yaw
            return pose

        elif t < end_lower:
            alpha = cosine_ease((t - end_wave) / _LOWER_T)
            return {
                k: lerp(WAVE_RAISED.get(k, 0.0), HOME.get(k, 0.0), alpha)
                for k in set(HOME) | set(WAVE_RAISED)
            }

        return dict(HOME)
