import numpy as np
from typing import Union
from engine.math.eulers import eulers2rotmat
from engine.common.transformable import Transformable
from simulation.drawing.drawable import Drawable, Axes, Camera


class Axes3d(Transformable, Drawable):
    def __init__(self,
                 pose: Union[list, tuple, np.ndarray] = [0., 0., 0.],
                 eulers: Union[list, tuple, np.ndarray] = [0., 0., 0.],
                 scale: float = 1.):
        super().__init__(pose, eulers, scale)

    def draw(self, canvas: Axes, camera: Camera):
        axes3d = np.array([[1, 0, 0], [0, 1, 0], [0, 0, 1]])
        axes3d = self._scale * axes3d
        r = eulers2rotmat(self._eulers, degrees=True)
        r = np.transpose(r)
        axes3d = np.matmul(r, axes3d)
        axes3d = axes3d + self._pose
        for ax3d, col, text in zip(axes3d, ['r', 'g', 'b'], ['x', 'y', 'z']):
            res = camera.project_line(ax3d, self._pose)
            if res is not None:
                canvas.arrow(*res[1], *(res[0] - res[1]), width=1, color=col, alpha=0.5)
                canvas.annotate(text, xy=res[0], xytext=res[0], alpha=0.5)
