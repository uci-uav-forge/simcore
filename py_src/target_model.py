import random
from pathlib import Path
from typing import Optional, Tuple, List


class TargetModel:
    """
    Represents a target for the sim. Has the following attributes:
        - name: the name of the target (must be name in models folder)
        - orient_rand: a list of tuples (min, max) for (roll, pitch, yaw) randomization (radians).
        - HSV_rand: a list of tuples (min, max) for (hue, saturation, value) randomization.
        - scale_rand: a tuple (min, max) for scale randomization.
    """

    def __init__(
        self,
        name: str,
        orient_rand: Optional[List[Tuple[float, float]]] = None,
        HSV_rand: Optional[List[Tuple[float, float]]] = None,
        scale_rand: Optional[Tuple[float, float]] = None,
    ):
        self.name = name
        self.orient_rand = orient_rand
        self.HSV_rand = HSV_rand
        self.scale_rand = scale_rand

        base_path = Path(__file__).parent.parent.resolve()
        self.model_path = str(base_path / f"ardu_ws/src/ardupilot_gazebo/models/{name}")

    def get_path(self) -> str:
        return self.model_path

    def get_orient(self) -> Tuple[float, float, float]:
        if self.orient_rand is None:
            return (0.0, 0.0, 0.0)
        return tuple(
            random.uniform(bounds[0], bounds[1]) for bounds in self.orient_rand
        )

    def get_HSV(self) -> Optional[Tuple[float, float, float]]:
        if self.HSV_rand is None:
            return None
        return tuple(random.uniform(bounds[0], bounds[1]) for bounds in self.HSV_rand)

    def get_scale(self) -> float:
        if self.scale_rand is None:
            return 1.0
        return random.uniform(self.scale_rand[0], self.scale_rand[1])
