import matplotlib.pyplot as plt
from glob import glob
from typing import List
from matplotlib.axes import Axes
# from core.objects.carskeleton import CarSkeleton
from core.camera.camera import Camera
# from core.objects.grid import Grid


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

    if event.key == 'ctrl+right':
        vehicle.translate(x=1.0)
    if event.key == 'ctrl+left':
        vehicle.translate(x=-1.0)
    if event.key == 'ctrl+up':
        vehicle.translate(z=1.0)
    if event.key == 'ctrl+down':
        vehicle.translate(z=-1.0)

    if event.key == '=':
        camera.zoom(1.0)
    if event.key == '-':
        camera.zoom(-1.0)

    if event.key == 'm':
        models = sorted(glob("data/models/*"))
        model_id = model_id + 1
        if model_id >= len(models):
            model_id = 0
        vehicle.load(models[model_id])
        vehicle.tag = models[model_id]

    draw_scene(ax, camera, [vehicle])


def draw_scene(ax: Axes, camera: Camera, vehicles: List[CarSkeleton]):
    ax.cla()
    ax.set_xlim(0, camera.img_size[0])
    ax.set_ylim(0, camera.img_size[1])
    ax.invert_yaxis()
    ax.set_aspect('equal')

    for vehicle in vehicles:
        ax.set_title(vehicle.tag)
        vehicle.draw(ax, camera, draw_axes=True)

    grid = Grid()
    grid.draw(ax, camera)

    fig.canvas.draw_idle()


def main():
    global camera, models, model_id, vehicle, ax, fig

    # camera
    camera = Camera(aov_h=60, img_size=(800, 600), pose_xyz=(0, -3, -8), eulers_xyz=(-10, 0, 0))

    # models
    models = sorted(glob("data/models/*"))
    model_id = 0

    # vehicle
    vehicle = CarSkeleton(tag=models[model_id])
    vehicle.load(models[model_id])

    # figure
    fig = plt.figure(figsize=(8, 8))
    ax = fig.add_subplot(1, 1, 1)
    fig.canvas.mpl_connect('key_press_event', on_keyboard_press)
    draw_scene(ax, camera, [vehicle])
    plt.show()


if __name__ == "__main__":
    main()
