import numpy as np
from numpy.typing import ArrayLike


def _check_value(val: ArrayLike):
    val = np.asarray(val, dtype=np.float32)
    if val.size != 3:
        raise ValueError("The value must have the size = 3")

    return val


class Transformable():
    def __init__(self,
                 pose: ArrayLike = [0., 0., 0.],
                 eulers: ArrayLike = [0., 0., 0.],
                 scale: float = 1.):
        self._pose = _check_value(pose)
        self._eulers = _check_value(eulers)
        self._scale = scale

    @property
    def pose(self) -> np.ndarray:
        return self._pose.copy()

    @pose.setter
    def pose(self, val: ArrayLike):
        self._pose = _check_value(val)

    @property
    def eulers(self) -> np.ndarray:
        return self._eulers.copy()

    @eulers.setter
    def eulers(self, val: ArrayLike):
        self._eulers = _check_value(val)
        self._eulers %= 360.0

    @property
    def scale(self) -> float:
        return self._scale

    @scale.setter
    def scale(self, val: float):
        self._scale = val

    def translate(self, x: float = 0., y: float = 0., z: float = 0.):
        self._pose += np.array([x, y, z], np.float32)

    def rotate(self, x: float = 0., y: float = 0., z: float = 0.):
        self._eulers += np.array([x, y, z], dtype=np.float32) 
        self._eulers %= 360.0
