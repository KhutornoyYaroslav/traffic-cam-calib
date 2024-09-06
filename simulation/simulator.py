import matplotlib.pyplot as plt
from matplotlib.axes import Axes
from engine.camera.camera import Camera
from simulation.scene.scene import Scene


class Simulator():
    def __init__(self):
        self.scene = Scene()
        self.t_start = 0.
        self.t_stop = 0.
        self.t_step = 0.1
        self._t_curr = self.t_start
        self._interrupted = False
        self.draw_routes = True
        self.draw_plane_grid = True
        self.cameras = {}

    def on_keyboard_press(self, event):
        if event.key == 'q':
            self._interrupted = True

    def _draw(self,
             figure,
             canvas: Axes,
             camera: Camera,
             title: str = ""):
        canvas.cla()
        canvas.set_xlim(0, camera.img_w)
        canvas.set_ylim(0, camera.img_h)
        canvas.invert_yaxis()
        canvas.set_aspect('equal')
        canvas.axis('off')
        canvas.set_title(title)

        if self.draw_plane_grid:
            if self.scene.plane_grid is not None:
                self.scene.plane_grid.draw(canvas, camera)

        if self.draw_routes:
            for route in self.scene.routes:
                route.draw(canvas, camera)

        for vehicle in self.scene.vehicles:
            vehicle.draw(canvas, camera)

        figure.canvas.draw_idle()

    def interrupt(self):
        self._interrupted = True

    def is_finished(self) -> bool:
        return self._t_curr >= self.t_stop

    def tick(self, reverse_time: bool = False):
        if self._t_curr < self.t_stop:
            self.scene.update_world(self._t_curr)
            print(f"Simulation updated at {self._t_curr:.2f}s")
            self._t_curr += (-1 if reverse_time else 1) * self.t_step

    def run(self, autoplay: bool = True):
        # init drawing
        canvases = []
        plt_rows = len(self.cameras)
        figure = plt.figure(figsize=(8, 8 * plt_rows))
        figure.canvas.mpl_connect('key_press_event', self.on_keyboard_press)
        for subplt_idx in range(plt_rows):
            canvases.append(figure.add_subplot(plt_rows, 1, subplt_idx + 1))

        # main loop
        while not self._interrupted and not self.is_finished():
            self.tick()
            for idx, (name, camera) in enumerate(self.cameras.items()):
                self._draw(figure, canvases[idx], camera, name)
            if autoplay:
                plt.pause(0.001)
            else:
                plt.waitforbuttonpress(0)
