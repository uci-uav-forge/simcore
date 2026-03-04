import math
from .target_model import TargetModel

# TARGETS
CANOPY1 = TargetModel(
    "canopy1",
    orient_rand=[(0, 0), (0, 0), (0, math.pi * 2)],
    HSV_rand=[(0.0, 1.0), (0.5, 1.0), (0.5, 1.0)],
    scale_rand=(0.8, 1.5),
)
CANOPY2 = TargetModel(
    "canopy2",
    orient_rand=[(0, 0), (0, 0), (0, math.pi * 2)],
    HSV_rand=[(0.0, 1.0), (0.5, 1.0), (0.5, 1.0)],
    scale_rand=(0.8, 1.5),
)

HUMAN1 = TargetModel(
    "human1",
    orient_rand=[(0, 0), (0, math.pi / 2.0), (0, math.pi * 2)],
    HSV_rand=[(0.0, 1.0), (0.5, 1.0), (0.5, 1.0)],
)

HUMAN2 = TargetModel(
    "human2",
    orient_rand=[(0, 0), (0, math.pi / 2.0), (0, math.pi * 2)],
    HSV_rand=[(0.0, 1.0), (0.5, 1.0), (0.5, 1.0)],
)

# NOISE
STOP_SIGN = TargetModel(
    "stop_sign", orient_rand=[(0, 0), (0, 0), (0, math.pi * 2)]
)  # doesnt exist yet, placeholder for testing
# TODO: add more noise targets
