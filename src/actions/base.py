import bisect
import json
import math


def lerp(a, b, t):
    return a + (b - a) * t


def cosine_ease(t):
    """Smooth ease-in-out, t in [0, 1]."""
    return (1 - math.cos(t * math.pi)) / 2


class Action:

    duration = None  # override to auto-close the viewer when done

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

    @property
    def duration(self):
        return self.keyframes[-1][0] if self.keyframes else None

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


class TrajectoryAction(Action):
    """
    Plays back a recorded joint trajectory from a JSON file.

    Expected format:
    {
      "joint_names": ["left_shoulder_pitch", ...],
      "frames": [{"t": 0.0, "q": [...]}, ...]
    }

    Linear interpolation between frames.  Optionally prepends a smooth
    ramp from start_pose (e.g. NEUTRAL) to the first frame so the robot
    doesn't snap.

    json_path   : path to the recording JSON
    pre_roll    : seconds to ease from start_pose to first frame (0 = off)
    start_pose  : {joint: angle} to ease from; defaults to first frame values
    loop        : repeat the recording indefinitely
    """

    def __init__(self, json_path, pre_roll=1.5, start_pose=None, loop=False):

        with open(json_path) as f:
            data = json.load(f)

        self._names = data["joint_names"]
        raw = [(fr["t"], fr["q"]) for fr in data["frames"]]

        self._loop = loop
        self._rec_duration = raw[-1][0] if raw else 0.0
        self._pre_roll = pre_roll

        first_pose = dict(zip(self._names, raw[0][1]))

        home_pos = (
            dict(zip(self._names, data["home_position"]))
            if "home_position" in data else None
        )
        if home_pos is not None:
            base = start_pose if start_pose is not None else {}
            self._start_pose = {**base, **home_pos}
        elif start_pose is not None:
            self._start_pose = start_pose
        else:
            self._start_pose = first_pose
        self._first_pose = first_pose

        # Shift recording times so they start after the pre-roll
        offset = pre_roll
        self._times = [offset + t for t, _ in raw]
        self._qs    = [q for _, q in raw]

    @property
    def duration(self):
        return None if self._loop else self._times[-1] if self._times else None

    def update(self, t):

        if not self._times:
            return {}

        # Pre-roll: cosine ease from start_pose to first recorded frame
        if self._pre_roll > 0 and t < self._pre_roll:
            alpha = cosine_ease(t / self._pre_roll)
            return {
                k: lerp(
                    self._start_pose.get(k, 0.0),
                    self._first_pose.get(k, 0.0),
                    alpha,
                )
                for k in self._names
            }

        # Looping: wrap within the recording window
        if self._loop:
            rec_t = (t - self._pre_roll) % self._rec_duration
            t = rec_t + self._pre_roll

        if t <= self._times[0]:
            return dict(zip(self._names, self._qs[0]))

        if t >= self._times[-1]:
            return dict(zip(self._names, self._qs[-1]))

        # Binary search for surrounding frames
        idx = bisect.bisect_right(self._times, t) - 1
        idx = max(0, min(idx, len(self._times) - 2))

        t0, q0 = self._times[idx],     self._qs[idx]
        t1, q1 = self._times[idx + 1], self._qs[idx + 1]
        alpha = (t - t0) / (t1 - t0)

        return {
            self._names[j]: lerp(q0[j], q1[j], alpha)
            for j in range(len(self._names))
        }
