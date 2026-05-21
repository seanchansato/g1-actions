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
# Arm values measured from the real robot's home_position recording.

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

# Home pose: real robot resting position.
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

# Alias kept for compatibility.
NEUTRAL = HOME

# Right hand raised to forehead — military salute.
# Recorded from simulation using the keyframe recorder.
SALUTE = {
    "waist_yaw":   0.0,
    "waist_roll":  0.0331,
    "waist_pitch": 0.0117,

    "right_shoulder_pitch":  0.6758,
    "right_shoulder_roll":  -1.8338,
    "right_shoulder_yaw":   -1.8065,
    "right_elbow":          -0.6472,
    "right_wrist_roll":      1.0551,
    "right_wrist_pitch":    -0.1111,
    "right_wrist_yaw":       0.2513,

    "left_shoulder_pitch":   0.1863,
    "left_shoulder_roll":    0.1131,
    "left_shoulder_yaw":     0.1615,
    "left_elbow":            1.3149,
    "left_wrist_roll":       0.0360,
    "left_wrist_pitch":     -0.0370,
    "left_wrist_yaw":       -0.0304,
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

# Both arms raised and rotated — shrug gesture.
SHRUG = {
    "waist_yaw":   0.0,
    "waist_roll":  0.0019,
    "waist_pitch": -0.0134,

    "left_shoulder_pitch":  0.1446,
    "left_shoulder_roll":   0.1952,
    "left_shoulder_yaw":    1.4178,
    "left_elbow":          -1.0471,
    "left_wrist_roll":     -1.5038,
    "left_wrist_pitch":    -0.0093,
    "left_wrist_yaw":       1.0874,

    "right_shoulder_pitch":  0.2572,
    "right_shoulder_roll":  -0.2931,
    "right_shoulder_yaw":   -1.7065,
    "right_elbow":          -1.0472,
    "right_wrist_roll":      1.5948,
    "right_wrist_pitch":    -0.0088,
    "right_wrist_yaw":      -1.3923,
}

# Flexible sequence — 5 keyframes recorded from simulation.
FLEX1 = {
    "waist_yaw":   0.0,
    "waist_roll":  0.0013,
    "waist_pitch": 0.0429,

    "left_shoulder_pitch":  0.2474,
    "left_shoulder_roll":   0.2935,
    "left_shoulder_yaw":   -0.0825,
    "left_elbow":          -0.0784,
    "left_wrist_roll":     -1.8736,
    "left_wrist_pitch":     0.0063,
    "left_wrist_yaw":      -0.0026,

    "right_shoulder_pitch":  0.2563,
    "right_shoulder_roll":  -0.2923,
    "right_shoulder_yaw":    0.0935,
    "right_elbow":          -0.0129,
    "right_wrist_roll":      1.9722,
    "right_wrist_pitch":    -0.0976,
    "right_wrist_yaw":      -0.0001,
}

FLEX2 = {
    "waist_yaw":   0.0,
    "waist_roll":  0.0024,
    "waist_pitch": 0.0365,

    "left_shoulder_pitch":  0.2479,
    "left_shoulder_roll":   0.2935,
    "left_shoulder_yaw":   -0.0796,
    "left_elbow":          -0.0788,
    "left_wrist_roll":     -1.7724,
    "left_wrist_pitch":    -0.0361,
    "left_wrist_yaw":      -1.5576,

    "right_shoulder_pitch":  0.2565,
    "right_shoulder_roll":  -0.2923,
    "right_shoulder_yaw":    0.0935,
    "right_elbow":          -0.0130,
    "right_wrist_roll":      1.9722,
    "right_wrist_pitch":    -0.0976,
    "right_wrist_yaw":       1.6144,
}

FLEX3 = {
    "waist_yaw":   0.0,
    "waist_roll":  -0.0034,
    "waist_pitch": 0.0355,

    "left_shoulder_pitch":  0.2475,
    "left_shoulder_roll":   0.2946,
    "left_shoulder_yaw":   -0.0766,
    "left_elbow":          -0.0813,
    "left_wrist_roll":      1.9722,
    "left_wrist_pitch":     1.5577,
    "left_wrist_yaw":      -1.5434,

    "right_shoulder_pitch":  0.2565,
    "right_shoulder_roll":  -0.2923,
    "right_shoulder_yaw":    0.0935,
    "right_elbow":          -0.0130,
    "right_wrist_roll":      1.9722,
    "right_wrist_pitch":    -0.0976,
    "right_wrist_yaw":       1.6144,
}

FLEX4 = {
    "waist_yaw":   0.0,
    "waist_roll":  -0.0005,
    "waist_pitch": 0.0325,

    "left_shoulder_pitch":  0.2454,
    "left_shoulder_roll":   0.2857,
    "left_shoulder_yaw":   -0.0737,
    "left_elbow":          -0.2860,
    "left_wrist_roll":      1.9719,
    "left_wrist_pitch":     1.5245,
    "left_wrist_yaw":      -1.6071,

    "right_shoulder_pitch":  0.2585,
    "right_shoulder_roll":  -0.2931,
    "right_shoulder_yaw":    0.0874,
    "right_elbow":          -0.0151,
    "right_wrist_roll":     -1.9722,
    "right_wrist_pitch":     1.5516,
    "right_wrist_yaw":       1.5713,
}

FLEX5 = {
    "waist_yaw":   0.0,
    "waist_roll":  0.0159,
    "waist_pitch": -0.0708,

    "left_shoulder_pitch":  0.4778,
    "left_shoulder_roll":   0.7882,
    "left_shoulder_yaw":    1.6241,
    "left_elbow":           2.0944,
    "left_wrist_roll":      1.9694,
    "left_wrist_pitch":     1.5565,
    "left_wrist_yaw":      -1.5463,

    "right_shoulder_pitch":  0.2638,
    "right_shoulder_roll":  -1.0019,
    "right_shoulder_yaw":   -0.9195,
    "right_elbow":           2.0931,
    "right_wrist_roll":     -1.9720,
    "right_wrist_pitch":    -1.5383,
    "right_wrist_yaw":       1.6144,
}

# Speak gesture — keyframe 1. Left arm extended forward/down, right wrist rolled out.
SPEAK1 = {
    "waist_yaw":   0.0,
    "waist_roll":  -0.006,
    "waist_pitch":  0.0427,

    "left_shoulder_pitch":  0.2474,
    "left_shoulder_roll":   0.3935,
    "left_shoulder_yaw":   -0.0825,
    "left_elbow":          -0.0784,
    "left_wrist_roll":     -0.8038,
    "left_wrist_pitch":     0.0063,
    "left_wrist_yaw":      -0.0026,

    "right_shoulder_pitch":  0.2563,
    "right_shoulder_roll":  -0.2923,
    "right_shoulder_yaw":    0.0935,
    "right_elbow":          -0.1129,
    "right_wrist_roll":      0.9948,
    "right_wrist_pitch":     0.0024,
    "right_wrist_yaw":      -0.0001,
}

# Speak gesture — keyframe 2. Left arm rotated further, right shoulder pitched down.
SPEAK2 = {
    "waist_yaw":   0.0,
    "waist_roll":  -0.0005,
    "waist_pitch":  0.0472,

    "left_shoulder_pitch":  0.2474,
    "left_shoulder_roll":   0.3935,
    "left_shoulder_yaw":    0.3175,
    "left_elbow":          -0.1784,
    "left_wrist_roll":     -1.5038,
    "left_wrist_pitch":     0.0063,
    "left_wrist_yaw":      -0.0026,

    "right_shoulder_pitch":  0.1563,
    "right_shoulder_roll":  -0.2923,
    "right_shoulder_yaw":   -0.5065,
    "right_elbow":          -0.1129,
    "right_wrist_roll":      1.2948,
    "right_wrist_pitch":     0.0024,
    "right_wrist_yaw":       0.0999,
}

# Right arm raised for waving — wrist oscillates in Wave action.
# Left arm stays at home.
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

    "left_shoulder_pitch":  0.2474,
    "left_shoulder_roll":   0.2935,
    "left_shoulder_yaw":   -0.0825,
    "left_elbow":           0.8216,
    "left_wrist_roll":     -0.0038,
    "left_wrist_pitch":     0.0063,
    "left_wrist_yaw":      -0.0026,
}
