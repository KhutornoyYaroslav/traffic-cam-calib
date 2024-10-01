import numpy as np
from copy import deepcopy
from typing import Union, Dict
from numpy.typing import ArrayLike
from core.math.eulers import eulers2rotmat
from core.common.transformable import Transformable


def _check_value(val: ArrayLike):
    val = np.asarray(val, dtype=np.float32)
    if val.size != 3:
        raise ValueError("The value must have the size = 3")

    return val


class Skeleton3d(Transformable):
    def __init__(self, nodes: Dict[str,  ArrayLike], edges: list, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._nodes = dict([(k, _check_value(v)) for k, v in nodes.items()])
        self._edges = edges

    @property
    def nodes(self) -> Dict[str,  np.ndarray]:
        return deepcopy(self._nodes)

    @nodes.setter
    def nodes(self, val: Dict[str, ArrayLike]):
        self._nodes = dict([(k, _check_value(v)) for k, v in val.items()])

    @property
    def edges(self) -> list:
        return deepcopy(self._edges)

    @edges.setter
    def edges(self, val: list):
        self._edges = val

    def size(self) -> int:
        return len(self._nodes)

    def node(self, label: str) -> np.ndarray:
        return deepcopy(self._nodes[label])

    def world_node(self, label: str) -> np.ndarray:
        return self.world_nodes()[label]

    def centroid(self) -> np.ndarray:
       return np.mean(list(self._nodes.values()), axis=0)

    def world_centroid(self) -> np.ndarray:
       return np.mean(list(self.world_nodes().values()), axis=0)

    def world_nodes(self) -> Dict[str, np.ndarray]:
        result = {}

        c = self.centroid()
        rot_mat = eulers2rotmat(self._eulers, degrees=True)
        for k, v in self._nodes.items():
            rotated = np.matmul(rot_mat, v - c) + c
            scaled = self._scale * rotated
            tranlstaed = scaled + self._pose
            result[k] = tranlstaed

        return result
