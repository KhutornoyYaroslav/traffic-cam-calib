import matplotlib.pyplot as plt
from matplotlib.axes import Axes
from engine.camera.camera import Camera
from simulation.scene.scene import Scene
from simulation.scene.reader import SceneReader


def on_keyboard_press(event):
    global interrupted, dt_sign
    if event.key == 'q':
        interrupted = True
    if event.key == 'right':
        dt_sign = 1
    if event.key == 'left':
        dt_sign = -1


def draw_scene(fig, ax: Axes, camera: Camera, scene: Scene):
    ax.cla()
    ax.set_xlim(0, camera.img_size[0])
    ax.set_ylim(0, camera.img_size[1])
    ax.invert_yaxis()
    ax.set_aspect('equal')
    ax.axis('off')
    scene.draw(ax, camera)
    fig.canvas.draw_idle()


def main():
    global interrupted, dt_sign
    interrupted = False
    dt_sign = 1

    # camera
    camera = Camera(aov_h=50, img_size=(1920, 1080), pose=(-5, -5, -10), eulers=(-15, 20, 0))
    # camera = Camera(aov_h=60, img_size=(1920, 1080), pose=(0, -5, -10), eulers=(-20, 0, 0))
    # camera = Camera(aov_h=60, img_size=(1920, 1080), pose=(-12, -5, 30), eulers=(-10, 60, 0))

    # scene
    scene = Scene()
    scene_reader = SceneReader(scene)
    scene_reader.read("config/scene/scene_2.json")

    # figure
    fig = plt.figure(figsize=(8, 8))
    ax = fig.add_subplot(1, 1, 1)
    fig.canvas.mpl_connect('key_press_event', on_keyboard_press)

    t = 0.0
    dt = 0.033 # sec

    while not interrupted:
        t += dt_sign*dt
        scene.update_world(t)
        draw_scene(fig, ax, camera, scene)
        plt.pause(0.001)
        # plt.waitforbuttonpress(0)


if __name__ == "__main__":
    main()
