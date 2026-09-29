import numpy as np


# AmazingHand joint order:
#
# 0 finger1_motor1
# 1 finger1_motor2
# 2 finger2_motor1
# 3 finger2_motor2
# 4 finger3_motor1
# 5 finger3_motor2
# 6 finger4_motor1
# 7 finger4_motor2


ROCK_DEG = np.array([
    88, -88,
    88, -88,
    88, -88,
    88, -88,
], dtype=float)


PAPER_DEG = np.array([
    -32, 35,
    -40, 27,
    -37, 40,
    -15, 75,
], dtype=float)



SCISSORS_DEG = np.array([
    -62, 15,
    -20, 57,
    82, -82,
    82, -82,
], dtype=float)



MIDDLE_DEG = np.array([
    3, 0,
    -5, -8,
    -2, 5,
    -12, 0,
], dtype=float)


PROUD_BASE_DEG = np.array([
    -40, 40,
    85, -85,
    85, -85,
    82, -82,
], dtype=float)


PROUD_LEFT_DEG = np.array([
    -55, 25,      # Index：左摆
    85, -85,      # Middle：收起
    85, -85,      # Ring：收起
    82, -82,     # Thumb：竖起
], dtype=float)


PROUD_RIGHT_DEG = np.array([
    -25, 55,      # Index：右摆
    85, -85,      # Middle：收起
    85, -85,      # Ring：收起
    82, -82,     # Thumb：收起
], dtype=float)


SHAME_DEG = np.array([
    88, -88,      # Index：收起
    88, -88,      # Middle：收起
    88, -88,      # Ring：收起
    18, 88,     # Thumb：竖起
], dtype=float)


CHALLENGE_OPEN_DEG = np.array([
    -35, 35,      # Index：伸直
    -40, 27,      # Middle：伸直
    -37, 40,      # Ring：伸直
    60, -60,      # Thumb：向左
], dtype=float)


CHALLENGE_CLOSE_DEG = np.array([
    80, -80,      # Index：弯曲
    80, -80,      # Middle：弯曲
    80, -80,      # Ring：弯曲
    60, -60,      # Thumb：保持向左
], dtype=float)


POSES = {
    "rock": ROCK_DEG,
    "paper": PAPER_DEG,
    "scissors": SCISSORS_DEG,
    "middle": MIDDLE_DEG,

    "proud_base": PROUD_BASE_DEG,
    "proud_left": PROUD_LEFT_DEG,
    "proud_right": PROUD_RIGHT_DEG,

    "shame": SHAME_DEG,

    "challenge_open": CHALLENGE_OPEN_DEG,
    "challenge_close": CHALLENGE_CLOSE_DEG,
}