import numpy as np
from simulation.routing.route import Route
from gui.matplot.common.drawable import Drawable, Axes, Camera


class RouteDrawer(Drawable):
    def __init__(self, route: Route):
        self._route = route
        self._color = (0.8, 0.5, 0.8)

    def draw(self, canvas: Axes, camera: Camera):
        # draw edges
        for wp_idx in range(0, len(self._route._waypoints) - 1):
            wp_1 = self._route._waypoints[wp_idx]
            wp_2 = self._route._waypoints[wp_idx + 1]

            res = camera.project_line(wp_1, wp_2)
            if res is not None:
                res = np.stack(res, 0)
                canvas.plot(res[:, 0], res[:, 1], color=self._color, lw=1, alpha=0.5)

        # draw nodes
        points2d = camera.project_points(self._route._waypoints)
        if points2d is not None:
            for point2d in points2d:
                canvas.plot(point2d[0], point2d[1], 'o', color=self._color, markersize=1)
