import matplotlib.pyplot as plt
from glob import glob
from typing import List
from matplotlib.axes import Axes
from engine.camera.camera import Camera
from simulation.objects.vehicle import Vehicle
from simulation.objects.planegrid import PlaneGrid
from simulation.drawing.drawable import Drawable


def on_keyboard_press(event):
    global interrupted, vehicle, models, model_id
    if event.key == 'q':
        interrupted = True
    if event.key == 'right':
        vehicle.rotate(y=3.0)
    if event.key == 'left':
        vehicle.rotate(y=-3.0)
    if event.key == 'up':
        vehicle.rotate(x=3.0)
    if event.key == 'down':
        vehicle.rotate(x=-3.0)
    if event.key == 'm':
        model_id += 1
        if model_id >= len(models):
            model_id = 0
        vehicle.load_from_file(models[model_id])


def draw_scene(fig,
               ax: Axes,
               camera: Camera,
               drawables: List[Drawable],
               model_name: str = ""):
    ax.cla()
    ax.set_xlim(0, camera.img_size[0])
    ax.set_ylim(0, camera.img_size[1])
    ax.invert_yaxis()
    ax.set_aspect('equal')
    # ax.axis('off')

    if len(model_name):
        ax.set_title(model_name)

    for drawable in drawables:
        drawable.draw(ax, camera)

    fig.canvas.draw_idle()


def main():
    global interrupted, vehicle, models, model_id
    interrupted = False

    # camera
    camera = Camera(aov_h=60, img_size=(1920, 1080), pose=(0, -3, -8), eulers=(-20, 0, 0))

    # vehicle
    model_id = 0
    models = sorted(glob("data/models/*.json"))

    vehicle = Vehicle()
    vehicle.rotate(y=135)
    vehicle.load_from_file(models[model_id])

    # plane grid
    plane_grid = PlaneGrid(x_range=(-3, 3), z_range=(-3, 3), step=0.5)

    # drawables
    drawables = [vehicle, plane_grid]

    # figure
    fig = plt.figure(figsize=(8, 8))
    ax = fig.add_subplot(1, 1, 1)
    fig.canvas.mpl_connect('key_press_event', on_keyboard_press)
    mng = plt.get_current_fig_manager()
    mng.window.showMaximized()

    while not interrupted:
        draw_scene(fig, ax, camera, drawables, models[model_id])
        plt.waitforbuttonpress(0)


# python3 -m scripts.visualize_vehicle
if __name__ == "__main__":
    main()
