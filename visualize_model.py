import matplotlib.pyplot as plt
from glob import glob
from typing import List
from matplotlib.axes import Axes
from core.camera.camera import Camera
from core.vehicle.vehicle import Vehicle


def on_keyboard_press(event):
    global camera, models, model_id, vehicle, ax, fig

    if event.key == 'right':
        vehicle.rotate(y=5.0)
    if event.key == 'left':
        vehicle.rotate(y=-5.0)
    if event.key == 'up':
        vehicle.rotate(x=5.0)
    if event.key == 'down':
        vehicle.rotate(x=-5.0)

    if event.key == 'm':
        models = sorted(glob("data/models/*"))
        model_id = model_id + 1
        if model_id >= len(models):
            model_id = 0
        vehicle.load(models[model_id])

    if event.key == 'ctrl+right':
        vehicle.translate(x=1.0)
    if event.key == 'ctrl+left':
        vehicle.translate(x=-1.0)
    if event.key == 'ctrl+up':
        vehicle.translate(z=1.0)
    if event.key == 'ctrl+down':
        vehicle.translate(z=-1.0)

    draw_scene(ax, camera, [vehicle])


def draw_scene(ax: Axes, camera: Camera, vehicles: List[Vehicle]):
    ax.cla()
    ax.set_xlim(0, camera.img_size[0])
    ax.set_ylim(0, camera.img_size[1])
    # ax.set_axis_off()
    ax.invert_yaxis()
    ax.set_aspect('equal')

    for vehicle in vehicles:
        vehicle.draw(ax, camera, draw_axes=True)

    fig.canvas.draw_idle()


def main():
    global camera, models, model_id, vehicle, ax, fig

    # camera
    # camera = Camera(aov_h=40, img_size=(800, 600), pose_xyz=(0, -4, -10), eulers_xyz=(-22, 0, 0))
    camera = Camera(aov_h=40, img_size=(800, 600), pose_xyz=(0, 0, -10), eulers_xyz=(0, 0, 0))

    # models
    models = sorted(glob("data/models/*"))
    model_id = 0

    # vehicle
    vehicle = Vehicle()
    vehicle.load(models[model_id])
    vehicle.set_pose(0, 0, 0)
    # vehicle.set_rotation(0, 135.0, 0)

    # figure
    fig = plt.figure(figsize=(8, 8))
    ax = fig.add_subplot(1, 1, 1)
    fig.canvas.mpl_connect('key_press_event', on_keyboard_press)
    draw_scene(ax, camera, [vehicle])
    plt.show()


if __name__ == "__main__":
    main()
