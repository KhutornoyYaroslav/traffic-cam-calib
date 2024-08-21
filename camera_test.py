import matplotlib.pyplot as plt
from matplotlib.axes import Axes
from engine.camera.camera import Camera
from typing import List
from simulation.drawing.drawable import Drawable
from simulation.objects.axes3d import Axes3d
from simulation.objects.vehicle import Vehicle
from simulation.objects.planegrid import PlaneGrid


def on_keyboard_press(event):
    global camera, ax, fig, drawables

    if event.key == 'right':
        camera.rotate(y=5.0)
    if event.key == 'left':
        camera.rotate(y=-5.0)
    if event.key == 'up':
        camera.rotate(x=5.0)
    if event.key == 'down':
        camera.rotate(x=-5.0)

    if event.key == 'ctrl+right':
        camera.translate(x=0.1)
    if event.key == 'ctrl+left':
        camera.translate(x=-0.1)
    if event.key == 'ctrl+up':
        camera.translate(z=0.1)
    if event.key == 'ctrl+down':
        camera.translate(z=-0.1)

    if event.key == '=':
        camera.zoom(1.0)
    if event.key == '-':
        camera.zoom(-1.0)

    draw_scene(ax, camera, drawables)


def draw_scene(ax: Axes, camera: Camera, drawables: List[Drawable]):
    ax.cla()
    ax.set_xlim(0, camera.img_size[0])
    ax.set_ylim(0, camera.img_size[1])
    ax.invert_yaxis()
    ax.set_aspect('equal')
    ax.axis('off')

    # draw
    for drawable in drawables:
        drawable.draw(ax, camera)
    fig.canvas.draw_idle()


def main():
    global camera, ax, fig, drawables

    # camera
    camera = Camera(aov_h=60, img_size=(800, 600), pose=(-5, -3, -10), eulers=(-10, 20, 0))

    drawables = []

    # plane grid
    plane = PlaneGrid(x_range=(-5., 5.), z_range=(-5., 5.))
    drawables.append(plane)

    # world axes
    axes3d = Axes3d()
    axes3d.translate(x=-4.0, z=-3.0)
    drawables.append(axes3d)

    # vehicle
    vehicle = Vehicle("data/models/019-SUV.json")
    drawables.append(vehicle)

    # figure
    fig = plt.figure(figsize=(8, 8))
    ax = fig.add_subplot(1, 1, 1)
    fig.canvas.mpl_connect('key_press_event', on_keyboard_press)
    draw_scene(ax, camera, drawables)
    plt.show()


if __name__ == "__main__":
    main()
