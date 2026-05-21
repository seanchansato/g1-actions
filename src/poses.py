# Named poses for the Unitree G1 29-DOF.
# Keys are actuator names (joint name minus the "_joint" suffix).
# Values are target angles in radians.
#
# Arm actuator indices (from g1_29dof.xml):
#   15 left_shoulder_pitch   22 right_shoulder_pitch   axis 0 1 0
#   16 left_shoulder_roll    23 right_shoulder_roll    axis 1 0 0
#   17 left_shoulder_yaw     24 right_shoulder_yaw     axis 0 0 1
#   18 left_elbow            25 right_elbow            axis 0 1 0
#   19 left_wrist_roll       26 right_wrist_roll       axis 1 0 0
#   20 left_wrist_pitch      27 right_wrist_pitch      axis 0 1 0
#   21 left_wrist_yaw        28 right_wrist_yaw        axis 0 0 1
# Waist:  12 waist_yaw  13 waist_roll  14 waist_pitch
# Legs:    0-5 left hip/knee/ankle   6-11 right hip/knee/ankle
#
# NOTE: shoulder_pitch=0 is NOT arms-at-sides for the G1.  At zero the arm
# is nearly horizontal (T-pose).  ~+0.79 rad (≈45° positive pitch) rotates
# the arm to hang straight down.  HANDS_UP uses -1.57 (arm straight up),
# confirming that negative pitch raises and positive pitch lowers the arm.

# Arms-hanging-down shoulder pitch value (calculated from model geometry).
_ARM_DOWN = 0.79

# Full 29-joint standing pose.  Leg joints slightly bent; arms hanging at
# sides.  Used as:
#   1. Initial qpos seed in the Simulator.
#   2. PD fallback in the Controller for joints not commanded by the action.
STANDING_BASE = {
    "left_hip_pitch":    -0.1,
    "left_hip_roll":      0.0,
    "left_hip_yaw":       0.0,
    "left_knee":          0.3,
    "left_ankle_pitch":  -0.2,
    "left_ankle_roll":    0.0,

    "right_hip_pitch":   -0.1,
    "right_hip_roll":     0.0,
    "right_hip_yaw":      0.0,
    "right_knee":         0.3,
    "right_ankle_pitch": -0.2,
    "right_ankle_roll":   0.0,

    "waist_yaw":          0.0,
    "waist_roll":         0.0,
    "waist_pitch":        0.0,

    "left_shoulder_pitch":  _ARM_DOWN,
    "left_shoulder_roll":   0.0,
    "left_shoulder_yaw":    0.0,
    "left_elbow":           0.0,
    "left_wrist_roll":      0.0,
    "left_wrist_pitch":     0.0,
    "left_wrist_yaw":       0.0,

    "right_shoulder_pitch": _ARM_DOWN,
    "right_shoulder_roll":  0.0,
    "right_shoulder_yaw":   0.0,
    "right_elbow":          0.0,
    "right_wrist_roll":     0.0,
    "right_wrist_pitch":    0.0,
    "right_wrist_yaw":      0.0,
}

# Home pose: arms hanging straight down at sides, torso upright.
HOME = {
    "waist_yaw":   0.0,
    "waist_roll":  0.0,
    "waist_pitch": 0.0,

    "left_shoulder_pitch":  _ARM_DOWN,
    "left_shoulder_roll":   0.0,
    "left_shoulder_yaw":    0.0,
    "left_elbow":           0.0,
    "left_wrist_roll":      0.0,
    "left_wrist_pitch":     0.0,
    "left_wrist_yaw":       0.0,

    "right_shoulder_pitch": _ARM_DOWN,
    "right_shoulder_roll":  0.0,
    "right_shoulder_yaw":   0.0,
    "right_elbow":          0.0,
    "right_wrist_roll":     0.0,
    "right_wrist_pitch":    0.0,
    "right_wrist_yaw":      0.0,
}

# Alias kept for compatibility.
NEUTRAL = HOME

# Right hand raised to forehead — military salute.
# Left arm stays at side.
SALUTE = {
    "waist_yaw":   0.0,
    "waist_roll":  0.0,
    "waist_pitch": 0.0,

    "right_shoulder_pitch": -1.0,
    "right_shoulder_roll":  -0.3,
    "right_shoulder_yaw":    0.5,
    "right_elbow":           1.5,
    "right_wrist_roll":      0.0,
    "right_wrist_pitch":    -0.2,
    "right_wrist_yaw":       0.0,

    "left_shoulder_pitch":  _ARM_DOWN,
    "left_shoulder_roll":   0.0,
    "left_shoulder_yaw":    0.0,
    "left_elbow":           0.0,
    "left_wrist_roll":      0.0,
    "left_wrist_pitch":     0.0,
    "left_wrist_yaw":       0.0,
}

# Both arms raised straight up.
HANDS_UP = {
    "waist_yaw":   0.0,
    "waist_roll":  0.0,
    "waist_pitch": 0.0,

    "right_shoulder_pitch": -1.57,
    "right_shoulder_roll":   0.0,
    "right_shoulder_yaw":    0.0,
    "right_elbow":           0.0,
    "right_wrist_roll":      0.0,
    "right_wrist_pitch":     0.0,
    "right_wrist_yaw":       0.0,

    "left_shoulder_pitch":  -1.57,
    "left_shoulder_roll":    0.0,
    "left_shoulder_yaw":     0.0,
    "left_elbow":            0.0,
    "left_wrist_roll":       0.0,
    "left_wrist_pitch":      0.0,
    "left_wrist_yaw":        0.0,
}

# Right arm raised for waving — wrist oscillates in Wave action.
# Left arm stays at side.
WAVE_RAISED = {
    "waist_yaw":   0.0,
    "waist_roll":  0.0,
    "waist_pitch": 0.0,

    "right_shoulder_pitch": -0.8,
    "right_shoulder_roll":  -0.3,
    "right_shoulder_yaw":    0.0,
    "right_elbow":           1.5,
    "right_wrist_roll":      0.0,
    "right_wrist_pitch":     0.0,
    "right_wrist_yaw":       0.0,

    "left_shoulder_pitch":  _ARM_DOWN,
    "left_shoulder_roll":   0.0,
    "left_shoulder_yaw":    0.0,
    "left_elbow":           0.0,
    "left_wrist_roll":      0.0,
    "left_wrist_pitch":     0.0,
    "left_wrist_yaw":       0.0,
}
