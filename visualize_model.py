import numpy as np
import matplotlib.pyplot as plt
from matplotlib.axes import Axes
from core.camera.camera import Camera
from core.vehicle.vehicle import Vehicle
from typing import List
from glob import glob


def on_keyboard_press(event):
    if event.key == 'right':
        vehicle.rotate(y=5.0)
    if event.key == 'left':
        vehicle.rotate(y=-5.0)
    if event.key == 'up':
        vehicle.rotate(x=5.0)
    if event.key == 'down':
        vehicle.rotate(x=-5.0)
    # if event.key == 'm':
    #     models = sorted(glob("data/models/*"))
    #     global model_id
    #     model_id = model_id + 1
    #     if model_id >= len(models):
    #         model_id = 0
    #     vehicle.load(models[model_id])
    #     vehicle.set_pose(0, 0, 0)
    #     vehicle.rotate(0, 45, 0)

    draw_scene(ax, camera, [vehicle])
    fig.canvas.draw_idle()


def draw_scene(ax: Axes,
               camera: Camera,
               vehicles: List[Vehicle]):
    ax.cla()
    ax.set_xlim(0, camera.img_size[0])
    ax.set_ylim(0, camera.img_size[1])
    ax.invert_yaxis()
    ax.set_aspect('equal')

    for vehicle in vehicles:
        vehicle.draw(ax, camera, draw_axes=True)


def main():
    # init vehicle
    models = sorted(glob("data/models/*"))
    vehicle.load(models[model_id])
    vehicle.set_pose(0, 0, 0)

    # create plot
    fig.canvas.mpl_connect('key_press_event', on_keyboard_press)
    draw_scene(ax, camera, [vehicle])
    plt.show()


if __name__ == "__main__":
    # global vars
    camera = Camera(aov_h=40, img_size=(800, 600), pose_xyz=(0, -4, -10), eulers_xyz=(-22, 0, 0))
    vehicle = Vehicle()
    model_id = 0
    fig = plt.figure(figsize=(8, 8))
    ax = fig.add_subplot(1, 1, 1)

    main()

# https://docs.opencv.org/4.x/d9/d0c/group__calib3d.html
# https://www.evl.uic.edu/ralph/508S98/coordinates.html
