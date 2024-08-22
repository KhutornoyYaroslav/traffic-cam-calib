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


class Vertices3d(Transformable):
    def __init__(self, vertices: Union[list, np.ndarray], *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._vertices = check_value(vertices)

    @property
    def vertices(self) -> np.ndarray:
        return self._vertices

    @vertices.setter
    def vertices(self, val: Union[list, np.ndarray]):
        self._vertices = check_value(val)

    def centroid(self) -> np.ndarray:
       return np.mean(self._vertices, axis=0)

    def world_vertices(self) -> np.ndarray:
        result = []

        # rotate
        c = self.centroid()
        rot_mat = eulers2rotmat(self._eulers, degrees=True)
        for v in self._vertices:
            result.append(np.matmul(rot_mat, v - c) + c)
        result = np.stack(result, 0)

        # scale, translate
        return self._scale * result + self._pose
