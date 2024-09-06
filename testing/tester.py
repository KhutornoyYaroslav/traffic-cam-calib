# from typing import List
import matplotlib.pyplot as plt
from copy import deepcopy
from matplotlib.axes import Axes
from simulation.simulator import Simulator


# # model camera errors
# self._noisy_cameras.clear()
# for idx, camera in enumerate(self.cameras):
#     noisy_camera = deepcopy(camera)
#     if idx in self.cameras_pose_errors:
#         noisy_camera.pose += self.cameras_pose_errors[idx].rand_error()
#     if idx in self.cameras_eulers_errors:
#         noisy_camera.eulers += self.cameras_eulers_errors[idx].rand_error()
#     self._noisy_cameras.append(noisy_camera)

# # model vehicle errors
# self._noisy_vehicles.clear()
# for vehicle in self.scene.vehicles:
#     noisy_vehicle = deepcopy(vehicle)
#     for label in noisy_vehicle.nodes.keys():
#         noisy_vehicle.nodes[label] += self.vehicles_points_detection_error.rand_error()
#     self._noisy_vehicles.append(noisy_vehicle)


class Tester():
    def __init__(self):
        self.simulator = Simulator()
        self._interrupted = False
        self.cameras_pose_errors = {}
        self.cameras_eulers_errors = {}
        self.noisy_cameras = {}

    def on_keyboard_press(self, event):
        if event.key == 'q':
            self._interrupted = True

    def interrupt(self):
        self._interrupted = True

    def tick(self):
        self.simulator.tick()

        # add camera errors
        self.noisy_cameras.clear()
        for name, camera in self.simulator.cameras.items():
            noisy_camera = deepcopy(camera)
            if name in self.cameras_pose_errors:
                noisy_camera.pose += self.cameras_pose_errors[name].rand()
            if name in self.cameras_eulers_errors:
                noisy_camera.eulers += self.cameras_eulers_errors[name].rand()
            self.noisy_cameras[name] = noisy_camera

        # add vehicle errors
        # TODO:

        # prepare 



    def run(self):
        # init drawing
        canvases = []
        plt_rows = len(self.simulator.cameras)
        figure = plt.figure(figsize=(8, 8 * plt_rows))
        figure.canvas.mpl_connect('key_press_event', self.on_keyboard_press)
        for subplt_idx in range(plt_rows):
            canvases.append(figure.add_subplot(plt_rows, 1, subplt_idx + 1))

        # main loop
        while not self._interrupted and not self.simulator.is_finished():
            self.tick()
            for idx, (name, camera) in enumerate(self.noisy_cameras.items()):
                self.simulator._draw(figure, canvases[idx], camera, name)
            plt.pause(0.001)
