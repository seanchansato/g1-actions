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
#
# NOTE: Pose values are approximate starting estimates.
# Tune visually in simulation — sign conventions depend on the G1's
# actual joint zeroing and the arm attachment quaternions in the XML.

NEUTRAL = {
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
SALUTE = {
    "right_shoulder_pitch": 0.35,
    "right_shoulder_roll":  -0.35,
    "right_shoulder_yaw":   0.0,
    "right_elbow":          1.9,
    "right_wrist_pitch":    -0.3,
    "right_wrist_roll":     0.0,
    "right_wrist_yaw":      0.2,

    "left_shoulder_pitch":  0.0,
    "left_shoulder_roll":   0.0,
    "left_shoulder_yaw":    0.0,
    "left_elbow":           0.0,
    "left_wrist_roll":      0.0,
    "left_wrist_pitch":     0.0,
    "left_wrist_yaw":       0.0,
}

# Both arms raised straight up.
HANDS_UP = {
    "right_shoulder_pitch": -1.57,
    "right_shoulder_roll":  0.0,
    "right_shoulder_yaw":   0.0,
    "right_elbow":          0.0,
    "right_wrist_roll":     0.0,
    "right_wrist_pitch":    0.0,
    "right_wrist_yaw":      0.0,

    "left_shoulder_pitch":  -1.57,
    "left_shoulder_roll":   0.0,
    "left_shoulder_yaw":    0.0,
    "left_elbow":           0.0,
    "left_wrist_roll":      0.0,
    "left_wrist_pitch":     0.0,
    "left_wrist_yaw":       0.0,
}

# Right arm raised, wrist ready to wave.
WAVE_RAISED = {
    "right_shoulder_pitch": -0.8,
    "right_shoulder_roll":  -0.3,
    "right_shoulder_yaw":   0.0,
    "right_elbow":          1.5,
    "right_wrist_roll":     0.0,
    "right_wrist_pitch":    0.0,
    "right_wrist_yaw":      0.0,

    "left_shoulder_pitch":  0.0,
    "left_shoulder_roll":   0.0,
    "left_shoulder_yaw":    0.0,
    "left_elbow":           0.0,
    "left_wrist_roll":      0.0,
    "left_wrist_pitch":     0.0,
    "left_wrist_yaw":       0.0,
}
