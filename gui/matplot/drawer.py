import matplotlib.pyplot as plt
from typing import List, Callable, Optional
from gui.matplot.common.drawable import Drawable
from core.camera.camera import Camera
from matplotlib.backend_bases import KeyEvent


    #     # # init drawing
    #     # canvases = []
    #     # plt_rows = len(self.cameras)
    #     # figure = plt.figure(figsize=(8, 8 * plt_rows))
    #     # figure.canvas.mpl_connect('key_press_event', self.on_keyboard_press)
    #     # for subplt_idx in range(plt_rows):
    #     #     canvases.append(figure.add_subplot(plt_rows, 1, subplt_idx + 1))

    #     # main loop
    #     while not self._interrupted and not self.is_finished():
    #         self.tick()
    #         # for idx, (name, camera) in enumerate(self.cameras.items()):
    #         #     self._draw(figure, canvases[idx], camera, name)
    #         # if autoplay:
    #         #     plt.pause(0.001)
    #         # else:
    #         #     plt.waitforbuttonpress(0)


class Drawer():
    def __init__(self,
                #  plt_rows: int,
                #  plt_cols: int,
                 on_keyboard_press: Optional[Callable[[KeyEvent], None]] = None):
        self._drawables = []
        # assert plt_rows > 0 and plt_cols > 0
        # figure = plt.figure(figsize=(8 * plt_cols, 8 * plt_rows))
        self._figure = plt.figure(figsize=(8, 8))
        if on_keyboard_press is not None:
            self._figure.canvas.mpl_connect('key_press_event', on_keyboard_press)
        self._canvas = self._figure.add_subplot(1, 1, 1)

    # def show(self):
    #     pass

    # def close(self):
    #     pass

    def redraw(self, camera: Camera):
        self._canvas.cla()
        self._canvas.set_xlim(0, camera.img_w)
        self._canvas.set_ylim(0, camera.img_h)
        self._canvas.invert_yaxis()
        self._canvas.set_aspect('equal')
        self._canvas.axis('off')
        # self._canvas.set_title(title)

        for drawable in self._drawables:
            drawable.draw(self._canvas, camera)

        self._figure.canvas.draw_idle()
        # plt.pause(0.001)
        plt.waitforbuttonpress(0.01) # TODO: ?

    def set_drawables(self, drawables: List[Drawable]):
        self._drawables = drawables

    # def set_cameras(self, cameras: List[Camera]): # TODO: dict with names
    #     pass
