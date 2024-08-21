import numpy as np
from typing import Tuple
from simulation.drawing.drawable import Drawable, Axes, Camera


class PlaneGrid(Drawable):
    def __init__(self, x_range: Tuple[float, float],
                       z_range: Tuple[float, float],
                       step: float = 1.0):
        assert x_range[1] >= x_range[0]
        assert z_range[1] >= z_range[0]
        self._zlines = [[[x, 0, z_range[0]], [x, 0, z_range[1]]] for x in np.arange(x_range[0], x_range[1]+step, step)]
        self._xlines = [[[x_range[0], 0, z], [x_range[1], 0, z]] for z in np.arange(z_range[0], z_range[1]+step, step)]
        self._color = (0.82, 0.82, 0.82)

    def draw(self, canvas: Axes, camera: Camera):
        # draw x-axes lines
        for x_line in self._xlines:
            res = camera.project_line(x_line[0], x_line[1])
            if res is not None:
                res = np.stack(res, 0)
                canvas.plot(res[:, 0], res[:, 1], color=self._color, lw=1, alpha=0.5)
        # draw z-axes lines
        for z_line in self._zlines:
            res = camera.project_line(z_line[0], z_line[1])
            if res is not None:
                res = np.stack(res, 0)
                canvas.plot(res[:, 0], res[:, 1], color=self._color, lw=1, alpha=0.5)
