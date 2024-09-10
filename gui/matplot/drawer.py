import numpy as np
import matplotlib.pyplot as plt
from matplotlib.backend_bases import KeyEvent
from typing import List, Callable, Optional, Dict
from gui.matplot.common.drawable import Drawable, Axes, Camera


class Drawer():
    def __init__(self,
                 on_keyboard_press: Optional[Callable[[KeyEvent], None]] = None,
                 plt_cols: int = 1):
        assert plt_cols > 0
        self.plt_cols = plt_cols
        self._figure = None
        self._canvases = []
        self._on_keyboard_press = on_keyboard_press

    def _draw_canvas(self,
                     canvas: Axes,
                     camera: Camera,
                     drawables: List[Drawable],
                     title: str = ""):
        canvas.cla()
        canvas.set_xlim(0, camera.img_w)
        canvas.set_ylim(0, camera.img_h)
        canvas.invert_yaxis()
        canvas.set_aspect('equal')
        canvas.axis('off')
        canvas.set_title(title, {'fontsize': 8.0})
        for drawable in drawables:
            drawable.draw(canvas, camera)

    def draw(self,
             cameras: Dict[str, Camera],
             drawables: List[Drawable],
             autoplay: bool = True):
        if not len(cameras):
            return

        # create figure
        if self._figure is None or len(self._canvases) != len(cameras):
            plt_cols = self.plt_cols
            plt_rows = int(np.ceil(len(cameras) / plt_cols))
            if plt_rows == 1:
                plt_cols = min(self.plt_cols, len(cameras))

            self._figure = plt.figure(figsize=(8 * plt_cols, 8 * plt_rows))
            if self._on_keyboard_press is not None:
                self._figure.canvas.mpl_connect('key_press_event', self._on_keyboard_press)

            for subplt_idx in range(len(cameras)):
                subplt = self._figure.add_subplot(plt_rows, plt_cols, subplt_idx + 1)
                self._canvases.append(subplt)

        # draw
        for canvas, (camera_name, camera) in zip(self._canvases, cameras.items()):
            self._draw_canvas(canvas, camera, drawables, camera_name)

        self._figure.canvas.draw_idle()
        plt.waitforbuttonpress(0.01 if autoplay else 0)
