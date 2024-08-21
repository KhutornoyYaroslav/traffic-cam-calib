import numpy as np
from typing import Union


def check_value(val: Union[list, tuple, np.ndarray]):
    if isinstance(val, (list, tuple)):
        val = np.array(val, np.float32)
    if val.size != 3:
        raise ValueError("Value must be three dimensional")

    return val


class Transformable():
    def __init__(self,
                 pose: Union[list, tuple, np.ndarray] = [0., 0., 0.],
                 eulers: Union[list, tuple, np.ndarray] = [0., 0., 0.],
                 scale: float = 1.):
        self._pose = check_value(pose)
        self._eulers = check_value(eulers)
        self._scale = scale

    @property
    def pose(self) -> np.ndarray:
        return self._pose

    @pose.setter
    def pose(self, val: Union[list, tuple, np.ndarray]):
        self._pose = check_value(val)

    @property
    def eulers(self) -> np.ndarray:
        return self._eulers

    @eulers.setter
    def eulers(self, val: Union[list, tuple, np.ndarray]):
        self._eulers = check_value(val)

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
