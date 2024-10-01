import numpy as np
import matplotlib.pyplot as plt
from matplotlib.axes import Axes
from simulation.routing import Route


def draw_scene(ax: Axes, route: Route, s: float):
    ax.cla()
    ax.set_xlim(-100, 100)
    ax.set_ylim(-100, 100)
    ax.set_aspect('equal')

    # draw route way
    for i in range(len(route.waypoints) - 1):
        start = route.waypoints[i]
        end = route.waypoints[i + 1]
        ax.plot([start[0], end[0]], [start[2], end[2]], color=(1.0, 0.0, 0.0), lw=1, alpha=0.5)
        # ax.arrow(*start[::2], *(end[::2] - start[::2]), width=1, color=(1.0, 0.0, 0.0), alpha=0.5)

    # draw current position
    cur_wp = route.interpolate_pose(s)
    ax.plot(cur_wp[0], cur_wp[2], '+', color=(0.0, 0.0, 1.0), markersize=5)

    fig.canvas.draw_idle()


def main():
    global ax, fig

    # route
    waypoints = [
        [0, 0, 0],
        [10, 0, 10],
        [20, 0, 20],
        [20, 0, 30],
        [20, 0, 50],
        [10, 0, 60],
        [0, 0, 80],
        [-20, 0, 85]
    ]
    route = Route(waypoints)

    # figure
    fig = plt.figure(figsize=(8, 8))
    ax = fig.add_subplot(1, 1, 1)
    
    dt = 0.1 # sec
    speed = 30.0 # mps

    t = 0
    while True:
        s = (t * speed) 
        s %= route.length()
        if route.is_end(s):
            break
        t += dt
        draw_scene(ax, route, s)
        plt.pause(0.05)

    # plt.show()

if __name__ == "__main__":
    main()
