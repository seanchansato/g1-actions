# g1-actions

MuJoCo simulation for developing and recording scripted arm actions on the Unitree G1 (29-DOF).  Uses classical PD control — no RL.

## Setup

```bash
cd g1-actions
python -m venv venv
source venv/bin/activate
pip install mujoco
```

## Running a scripted action

```bash
python src/main.py <action>
python src/main.py <action> --loop   # repeat indefinitely
```

Press **Q** to quit the viewer at any time.

| Action | Description |
|---|---|
| `salute` | Military salute (scripted keyframes) |
| `wave` | Wrist wave — arm raises then oscillates (scripted) |
| `hands_up` | Both arms raised straight up (scripted) |
| `face_wave` | Wave recorded from real robot |
| `hands_up_rec` | Hands-up recorded from real robot |
| `shake_hand` | Handshake recorded from real robot |
| `show_hand` | Show hand recorded from real robot |
| `do_payment` | Payment gesture recorded from real robot |
| `down_payment` | Down payment gesture recorded from real robot |

The viewer closes automatically when the action finishes.  Scripted actions (`PoseAction`) close when the last keyframe is reached; recorded actions (`TrajectoryAction`) close at the end of the recording unless `--loop` is passed.

## Recording a new action

Launch the recorder:

```bash
python src/record.py
```

The robot opens in the MuJoCo viewer at the home position.  Use keyboard controls to pose the arms, then press **K** to latch the current pose as a keyframe.  The arm joints use gravity compensation — they hold wherever placed rather than snapping back.  Close the window when done and enter a name when prompted.

### Recorder keyboard controls

| Key | Action |
|---|---|
| **Tab** | Select next arm joint |
| **`** (backtick) | Select previous arm joint |
| **↑ / ↓** | Nudge selected joint ±0.02 rad (fine) |
| **] / [** | Nudge selected joint ±0.1 rad (coarse) |
| **K** | Record current pose as a keyframe |
| Close window | Finish and save |

The terminal prints the selected joint name and its current angle after every change so you always know where you are.

Keyframes are saved to `keyframes/<name>.json`.

### Home position

The recorder reads `keyframes/home.json` on startup.  If that file exists, the right arm is initialized from the stored home position rather than `poses.HOME`, so the recorder always starts from the robot's actual resting pose.

## Playing back recorded keyframes

```bash
python src/playback.py <action_name>
```

Loads `keyframes/<action_name>.json`, smoothly interpolates between each keyframe using smoothstep easing (200 physics steps × 10 substeps per transition), then holds the final pose until the window is closed.

## Turning a keyframe recording into a runnable action

After previewing with `playback.py`, add the action to the codebase in two steps.

**1. Add a class to `src/actions/wave_recorded.py`:**

```python
class MyAction(TrajectoryAction):
    def __init__(self, loop=False):
        super().__init__(_rec("my_action.json"), pre_roll=1.5, start_pose=HOME, loop=loop)
```

- `pre_roll=1.5` eases the robot from home into the first keyframe over 1.5 s so there is no snap
- `loop=True` repeats the action indefinitely (the viewer will not auto-close)

**2. Register it in `src/main.py`:**

```python
from actions.wave_recorded import ..., MyAction

ACTIONS = {
    ...
    "my_action": MyAction,
}
```

Then run it like any other action:

```bash
python src/main.py my_action
```

## How the simulation works

The robot starts every run in the **home position** — arms hanging naturally at the sides with a slight elbow bend, legs slightly bent for stable standing.  This is defined by two poses in `src/poses.py`:

- **`STANDING_BASE`** — all 29 joints.  Legs are slightly bent for stable standing; arm joints are zero.  Used as the PD fallback for any joint not commanded by the current action.
- **`HOME`** — arm joints only, at the real robot's recorded resting position.  Applied on top of `STANDING_BASE` when seeding the initial physics state, so the arms visually start in the correct position without affecting the leg balance.

The **PD controller** runs every physics step.  For each joint it uses the action's target if provided, otherwise falls back to `STANDING_BASE`.  This means unconstrained joints (e.g. the left arm during a right-arm-only action) are held steady automatically.

Actions set a `duration` property.  When elapsed time exceeds it the viewer closes automatically.  Actions without a duration (or with `loop=True`) run until the window is closed.

## Project structure

```
g1-actions/
├── models/
│   └── g1_29dof.xml        # G1 model (free-floating base, torque actuators)
├── recordings/             # Real-robot arm trajectories (JSON)
├── keyframes/              # Poses recorded with record.py (JSON)
│   ├── home.json           # Saved home / resting position for the recorder
│   └── Salute.json         # Salute recorded as keyframes
└── src/
    ├── main.py             # Entry point — lists all available actions
    ├── record.py           # Interactive keyframe recorder (keyboard-driven)
    ├── playback.py         # Keyframe playback with smoothstep interpolation
    ├── simulator.py        # MuJoCo viewer loop + qpos seeding
    ├── controller.py       # PD controller (all 29 joints)
    ├── poses.py            # Named poses: STANDING_BASE, HOME, NEUTRAL, SALUTE, …
    └── actions/
        ├── base.py         # PoseAction (keyframe) and TrajectoryAction (recorded)
        ├── salute.py
        ├── wave.py
        ├── hands_up.py
        └── wave_recorded.py
```

## Adding a new scripted action

1. Add any new target poses to `src/poses.py`.  Start and end at `HOME` so the robot begins and ends in the natural resting position.
2. Create `src/actions/<name>.py` subclassing `PoseAction` with a list of `(time, pose)` keyframes.
3. Register it in the `ACTIONS` dict in `src/main.py`.
