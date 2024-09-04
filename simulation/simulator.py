import matplotlib.pyplot as plt
from typing import List
from matplotlib.axes import Axes
from engine.camera.camera import Camera
from simulation.scene.scene import Scene


class Simulator():
    def __init__(self):
        self._scene = Scene()
        self._cameras = []
        self._t_start = 0.
        self._t_stop = 0.
        self._t_step = 0.1
        self._t_curr = self._t_start
        self._interrupted = False
        self._draw_scene = False

    @property
    def scene(self) -> Scene:
        return self._scene

    @scene.setter
    def scene(self, val: Scene):
        self._scene = val

    @property
    def draw_scene(self) -> bool:
        return self._draw_scene

    @draw_scene.setter
    def draw_scene(self, val: bool):
        self._draw_scene = val

    @property
    def cameras(self) -> List[Camera]:
        return self._cameras

    @cameras.setter
    def cameras(self, val: List[Camera]):
        self._cameras = val

    @property
    def t_start(self) -> float:
        return self._t_start

    @t_start.setter
    def t_start(self, val: float):
        self._t_start = val

    @property
    def t_stop(self) -> float:
        return self._t_stop

    @t_stop.setter
    def t_stop(self, val: float):
        self._t_stop = val

    @property
    def t_step(self) -> float:
        return self._t_step

    @t_step.setter
    def t_step(self, val: float):
        self._t_step = val

    @property
    def t_curr(self) -> float:
        return self._t_curr

    @t_curr.setter
    def t_curr(self, val: float):
        self._t_curr = val

    def on_keyboard_press(self, event):
        if event.key == 'q':
            self._interrupted = True

    def draw(self, figure, canvas: Axes, camera: Camera):
        canvas.cla()
        canvas.set_xlim(0, camera.img_w)
        canvas.set_ylim(0, camera.img_h)
        canvas.invert_yaxis()
        canvas.set_aspect('equal')
        canvas.axis('off')
        self._scene.draw(canvas, camera)
        figure.canvas.draw_idle()

    def interrupt(self):
        self._interrupted = True

    def tick(self, reverse_time: bool = False) -> bool:
        if self._t_curr < self._t_stop:
            self._scene.update_world(self._t_curr)
            print(f"Simulation updated at {self._t_curr:.2f}s")
            self._t_curr += (-1 if reverse_time else 1) * self._t_step
            return True

        return False

    def run(self, autoplay: bool = True):
        # drawing
        canvases = []
        if self._draw_scene:
            plt_rows = len(self._cameras)
            figure = plt.figure(figsize=(8, 8 * plt_rows))  # TODO: optimize. recreating figure
            figure.canvas.mpl_connect('key_press_event', self.on_keyboard_press)
            for subplt_idx in range(plt_rows):
                canvases.append(figure.add_subplot(plt_rows, 1, subplt_idx + 1))

        # main loop
        while not self._interrupted:
            self.tick()
            if self._draw_scene:
                for idx, canvas in enumerate(canvases):
                    self.draw(figure, canvas, self._cameras[idx])
                if autoplay:
                    plt.pause(0.001)
                else:
                    plt.waitforbuttonpress(0)
