import numpy as np
from typing import Union
from engine.math.eulers import eulers2rotmat
from engine.common.transformable import Transformable


def check_value(val: Union[list, np.ndarray]):
    if isinstance(val, list):
        val = np.array(val, np.float32)
    if val.ndim != 2 or val.shape[1] != 3:
        raise ValueError("Value must have shape (N, 3)")

    return val


class Object3d(Transformable):
    def __init__(self,
                 points: Union[list, np.ndarray],
                 pose: Union[list, tuple, np.ndarray] = [0., 0., 0.],
                 eulers: Union[list, tuple, np.ndarray] = [0., 0., 0.],
                 scale: float = 1.):
        super().__init__(pose, eulers, scale)
        self._points = points
    
    @property
    def points(self) -> np.ndarray:
        return self._points

    @points.setter
    def points(self, val: Union[list, np.ndarray]):
        self._points = check_value(val)

    def centroid(self) -> np.ndarray:
       return np.mean(self._points, axis=0)

    def world_points(self):
        result = []

        # rotate
        c = self.centroid()
        rot_mat = eulers2rotmat(self._eulers, degrees=True)
        for pt in self._points:
            result.append(np.matmul(rot_mat, pt - c) + c)
        result = np.stack(result, 0)

        # scale
        result = result * self._scale

        # translate
        return result + self._pose
