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
```

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

The viewer opens in a window.  Close it to exit.

## Recording a new action

Launch the recorder:

```bash
python src/record.py
```

1. The robot opens in the MuJoCo viewer at the home position.
2. **Ctrl+click+drag** on any body to perturb a joint into the pose you want.
3. Press **K** to lock that pose as a keyframe — the robot holds the new position.
4. Repeat to add more keyframes.
5. Close the window, then enter a name when prompted.

Keyframes are saved to `keyframes/<name>.json`.

## Playing back recorded keyframes

```bash
python src/playback.py <action_name>
```

Loads `keyframes/<action_name>.json`, smoothly interpolates between each keyframe using smoothstep easing (200 physics steps per transition), then holds the final pose.

## Project structure

```
g1-actions/
├── models/
│   └── g1_29dof.xml        # G1 model (fixed pelvis, torque actuators)
├── recordings/             # Real-robot arm trajectories (JSON)
├── keyframes/              # Poses recorded with record.py (JSON)
│   └── home.json           # Right arm home/rest position
└── src/
    ├── main.py             # Entry point for scripted actions
    ├── record.py           # Interactive keyframe recorder
    ├── playback.py         # Keyframe playback
    ├── simulator.py        # MuJoCo viewer loop
    ├── controller.py       # PD controller (all 29 joints)
    ├── poses.py            # Named poses (NEUTRAL, HOME, SALUTE, etc.)
    └── actions/
        ├── base.py         # PoseAction and TrajectoryAction base classes
        ├── salute.py
        ├── wave.py
        ├── hands_up.py
        └── wave_recorded.py
```

## Adding a new scripted action

1. Add any new target poses to `src/poses.py`.
2. Create `src/actions/<name>.py` inheriting from `PoseAction` or `TrajectoryAction`.
3. Register it in the `ACTIONS` dict in `src/main.py`.
