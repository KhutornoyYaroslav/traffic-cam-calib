import numpy as np
from typing import Union
from copy import deepcopy
from core.math.eulers import heading_to_eulers


def check_waypoints(val: Union[list, np.ndarray]):
    if isinstance(val, list):
        val = np.array(val, np.float32)
    if val.ndim != 2 or val.shape[1] != 3:
        raise ValueError("Value must have shape (N, 3)")

    return val


def check_dts(val: Union[list, np.ndarray]):
    if isinstance(val, list):
        val = np.array(val, np.float32)
    if val.ndim != 1:
        raise ValueError("Value must have single dimension")

    return val


class Route():
    def __init__(self,
                 waypoints: Union[list, np.ndarray],
                 dts: Union[list, np.ndarray],
                 loop_enable: bool = False):
        self._waypoints = check_waypoints(waypoints)
        self._dts = check_dts(dts)
        assert self._waypoints.shape[0] - self._dts.shape[0] == 1
        self.loop_enable = loop_enable
        self._prev_cycle = None
        self._cycle_changed = False
        self._cycle_counter = 0

    @property
    def waypoints(self) -> np.ndarray:
        return deepcopy(self._waypoints)

    @waypoints.setter
    def waypoints(self, val: Union[list, np.ndarray]):
        self._waypoints = check_waypoints(val)

    @property
    def dts(self) -> np.ndarray:
        return deepcopy(self._dts)

    @dts.setter
    def dts(self, val: Union[list, np.ndarray]):
        self._dts = check_dts(val)

    def length(self) -> float:
        result = 0.0
        for wp_idx in range(0, len(self._waypoints) - 1):
            vec = self._waypoints[wp_idx + 1] - self._waypoints[wp_idx]
            vec_length = np.linalg.norm(vec)
            result += vec_length

        return result

    def duration(self) -> float:
        return np.sum(self._dts)

    def cycle_changed(self) -> bool:
        return self._cycle_changed
    
    def cycle_count(self) -> int:
        return self._cycle_counter

    def process_timestamp(self, timestamp: float) -> float:
        if self.loop_enable and self.duration() > 0.0:
            cur_cycle = int(timestamp // self.duration())
            self._cycle_changed = self._prev_cycle != None and cur_cycle != self._prev_cycle
            if self._cycle_changed:
                self._cycle_counter += 1
            self._prev_cycle = cur_cycle
            return timestamp % self.duration()

        return timestamp

    def interpolate_pose(self, timestamp: float) -> np.ndarray:
        assert timestamp >= 0, "timestamp must be positive"
        dt_sum = 0.0
        for i, dt in enumerate(self._dts):
            if timestamp < dt_sum + dt:
                vec = self._waypoints[i + 1] - self._waypoints[i]
                vec_length = np.linalg.norm(vec)
                vec_norm = vec / vec_length
                vec_part = (timestamp - dt_sum) / dt
                return self._waypoints[i] + vec_norm * vec_length * vec_part
            dt_sum += dt

        return self._waypoints[-1]

    def interpolate_eulers(self, timestamp: float) -> np.ndarray:
        assert timestamp >= 0, "timestamp must be positive"
        last_eulers = np.zeros(3, np.float32)
        dt_sum = 0.0
        for i, dt in enumerate(self._dts):
            vec = self._waypoints[i + 1] - self._waypoints[i]
            vec_length = np.linalg.norm(vec)
            vec_norm = vec / vec_length
            last_eulers = heading_to_eulers(vec_norm, True)
            if timestamp < dt_sum + dt:
                return last_eulers
            dt_sum += dt

        return last_eulers

    def is_end(self, timestamp: float, eps: float = 0.001):
        if np.linalg.norm(self.interpolate_pose(timestamp) - self._waypoints[-1]) < eps:
            return True

        return False
