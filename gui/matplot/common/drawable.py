from typing import Tuple
from matplotlib.axes import Axes
from core.camera.camera import Camera


class Drawable():
    def __init__(self):
        self._color = (0., 0., 0.)

    @property
    def color(self) -> Tuple[float, float, float]:
        return self._color

    @color.setter
    def color(self, val: Tuple[float, float, float]):
        self._color = val

    def draw(self, canvas: Axes, camera: Camera):
        raise NotImplementedError()
