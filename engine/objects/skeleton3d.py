import numpy as np
from typing import Union, Tuple
from matplotlib.axes import Axes
from engine.camera.camera import Camera
from engine.math.eulers import eulers2rotmat
from engine.common.transformable import Transformable
from engine.objects.object3d import Object3d


class Skeleton3d(Object3d):
    """s
    Skeleton3d represents an object in 3d space as a set of nodes and edges.

    Parameters:
        points : array
            XYZ coordinates of skeleton nodes with shape (N, 3).
    """
    def __init__(self,
                 points: np.ndarray,
                 edges: np.ndarray,
                 pose: Union[list, tuple, np.ndarray] = [0., 0., 0.],
                 eulers: Union[list, tuple, np.ndarray] = [0., 0., 0.],
                 scale: float = 1.):
        super().__init__(points, pose, eulers, scale)
        self._edges = edges
