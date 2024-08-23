import matplotlib.pyplot as plt
from matplotlib.axes import Axes
from engine.camera.camera import Camera
from simulation.scene.scene import Scene
from simulation.scene.reader import SceneReader


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
    # camera
    camera = Camera(aov_h=40, img_size=(1920, 1080), pose=(-5, -5, -10), eulers=(-15, 20, 0))

    # scene
    scene = Scene()
    scene_reader = SceneReader(scene)
    scene_reader.read("config/scene/scene_1.json")

    # figure
    fig = plt.figure(figsize=(8, 8))
    ax = fig.add_subplot(1, 1, 1)
    
    dt = 0.1 # sec

    t = 0.0
    while True:
        t += dt
        scene.update_world(t)
        draw_scene(fig, ax, camera, scene)
        plt.pause(0.001)

    # plt.show()


if __name__ == "__main__":
    main()
