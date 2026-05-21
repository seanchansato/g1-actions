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

# Full 29-joint home pose.  Leg joints are slightly bent (typical upright
# stance for G1); arms and waist at zero.  Used as:
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

    "left_shoulder_pitch":  0.0,
    "left_shoulder_roll":   0.0,
    "left_shoulder_yaw":    0.0,
    "left_elbow":           0.0,
    "left_wrist_roll":      0.0,
    "left_wrist_pitch":     0.0,
    "left_wrist_yaw":       0.0,

    "right_shoulder_pitch": 0.0,
    "right_shoulder_roll":  0.0,
    "right_shoulder_yaw":   0.0,
    "right_elbow":          0.0,
    "right_wrist_roll":     0.0,
    "right_wrist_pitch":    0.0,
    "right_wrist_yaw":      0.0,
}

# Arm pose recorded from a real G1 at rest — natural hanging position with
# a slight elbow bend.  Used as the start/end for scripted actions so the
# robot begins and ends in the same state as recorded motions.
HOME = {
    "waist_yaw":   0.0,
    "waist_roll":  0.0,
    "waist_pitch": 0.0,

    "left_shoulder_pitch":  0.2474,
    "left_shoulder_roll":   0.2935,
    "left_shoulder_yaw":   -0.0825,
    "left_elbow":           0.8216,
    "left_wrist_roll":     -0.0038,
    "left_wrist_pitch":     0.0063,
    "left_wrist_yaw":      -0.0026,

    "right_shoulder_pitch":  0.2563,
    "right_shoulder_roll":  -0.2923,
    "right_shoulder_yaw":    0.0935,
    "right_elbow":           0.7871,
    "right_wrist_roll":     -0.0052,
    "right_wrist_pitch":     0.0024,
    "right_wrist_yaw":      -0.0001,
}

# Standing straight: all arm/waist joints at zero.
# Arms hang at sides, torso upright, facing forward.
NEUTRAL = {
    "waist_yaw":   0.0,
    "waist_roll":  0.0,
    "waist_pitch": 0.0,

    "left_shoulder_pitch":  0.0,
    "left_shoulder_roll":   0.0,
    "left_shoulder_yaw":    0.0,
    "left_elbow":           0.0,
    "left_wrist_roll":      0.0,
    "left_wrist_pitch":     0.0,
    "left_wrist_yaw":       0.0,

    "right_shoulder_pitch": 0.0,
    "right_shoulder_roll":  0.0,
    "right_shoulder_yaw":   0.0,
    "right_elbow":          0.0,
    "right_wrist_roll":     0.0,
    "right_wrist_pitch":    0.0,
    "right_wrist_yaw":      0.0,
}

# Right hand raised to forehead — military salute.
# Left arm stays at side (neutral).
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

    "left_shoulder_pitch":  0.2474,
    "left_shoulder_roll":   0.2935,
    "left_shoulder_yaw":   -0.0825,
    "left_elbow":           0.8216,
    "left_wrist_roll":     -0.0038,
    "left_wrist_pitch":     0.0063,
    "left_wrist_yaw":      -0.0026,
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
# Left arm stays at side (neutral).
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

    "left_shoulder_pitch":   0.0,
    "left_shoulder_roll":    0.0,
    "left_shoulder_yaw":     0.0,
    "left_elbow":            0.0,
    "left_wrist_roll":       0.0,
    "left_wrist_pitch":      0.0,
    "left_wrist_yaw":        0.0,
}
