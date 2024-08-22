import numpy as np
from typing import Union


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

    # TODO: add method to interpolate_eulers
    # https://stackoverflow.com/questions/21622956/how-to-convert-direction-vector-to-euler-angles

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

    def is_end(self, s: float, eps: float = 0.001):
        if np.linalg.norm(self.interpolate_pose(s) - self._waypoints[-1]) < eps:
            return True

        return False
