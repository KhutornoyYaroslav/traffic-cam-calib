import numpy as np
from typing import Union
from engine.math.eulers import heading_to_eulers
from simulation.drawing.drawable import Drawable, Camera, Axes


def check_value(val: Union[list, np.ndarray]):
    if isinstance(val, list):
        val = np.array(val, np.float32)
    if val.ndim != 2 or val.shape[1] != 3:
        raise ValueError("Value must have shape (N, 3)")

    return val


class Route():
    def __init__(self, waypoints: Union[list, np.ndarray]):
        self._waypoints = check_value(waypoints)

    @property
    def waypoints(self) -> np.ndarray:
        return self._waypoints

    @waypoints.setter
    def waypoints(self, val: Union[list, np.ndarray]):
        self._waypoints = check_value(val)

    def length(self) -> float:
        result = 0.0
        for wp_idx in range(0, len(self._waypoints) - 1):
            vec = self._waypoints[wp_idx + 1] - self._waypoints[wp_idx]
            vec_length = np.linalg.norm(vec)
            result += vec_length

        return result

    def interpolate_pose(self, s: float) -> np.ndarray:
        assert s >= 0, "Station distance must be positive"

        vec_length_sum = 0.0
        for wp_idx in range(0, len(self._waypoints) - 1):
            vec = self._waypoints[wp_idx + 1] - self._waypoints[wp_idx]
            vec_length = np.linalg.norm(vec)
            if s < vec_length_sum + vec_length:
                ds = s - vec_length_sum
                vec_norm = vec / vec_length
                return self._waypoints[wp_idx] + vec_norm * ds
            vec_length_sum += vec_length

        return self._waypoints[-1]

    def interpolate_eulers(self, s: float) -> np.ndarray:
        assert s >= 0, "Station distance must be positive"

        last_eulers = np.zeros(3, np.float32)
        vec_length_sum = 0.0
        for wp_idx in range(0, len(self._waypoints) - 1):
            vec = self._waypoints[wp_idx + 1] - self._waypoints[wp_idx]
            vec_length = np.linalg.norm(vec)
            vec_norm = vec / vec_length
            last_eulers = heading_to_eulers(vec_norm, True)
            if s < vec_length_sum + vec_length:
                return last_eulers
            vec_length_sum += vec_length

        return last_eulers

    def is_end(self, s: float, eps: float = 0.001):
        if np.linalg.norm(self.interpolate_pose(s) - self._waypoints[-1]) < eps:
            return True

        return False

    def draw(self, canvas: Axes, camera: Camera):
        # color
        color = (0.8, 0.5, 0.8)

        # draw edges
        for wp_idx in range(0, len(self._waypoints) - 1):
            wp_1 = self._waypoints[wp_idx]
            wp_2 = self._waypoints[wp_idx + 1]

            res = camera.project_line(wp_1, wp_2)
            if res is not None:
                res = np.stack(res, 0)
                canvas.plot(res[:, 0], res[:, 1], color=color, lw=1, alpha=0.5)

        # draw nodes
        points2d = camera.project_points(self._waypoints)
        if points2d is not None:
            for point2d in points2d:
                canvas.plot(point2d[0], point2d[1], 'o', color=color, markersize=1)
