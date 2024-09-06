import numpy as np
from glob import glob
from typing import List
from copy import deepcopy
from simulation.routing.route import Route
from core.objects.carskeleton3d import CarSkeleton3d


"""
It is primarily used to link objects (currently only cars)
to specific routes along which they will move over time.
Also updates the positions of objects according to a given timestamp.
"""
class Scene():
    def __init__(self):
        self._cars = []
        self._routes = []
        self.car_route_map = {}
        self.car_idxs_to_randomize = []
        self.car_models_path = ""
        self.routes_idxs_to_loop = []
        self._prev_timestamp = 0.0

    @property
    def routes(self) -> List[Route]:
        return deepcopy(self._routes)

    @routes.setter
    def routes(self, val: List[Route]):
        self._routes = val

    def add_route(self, route: Route) -> int:
        self._routes.append(route)
        return len(self._routes) - 1

    @property
    def cars(self) -> List[CarSkeleton3d]:
        return deepcopy(self._cars)

    @cars.setter
    def cars(self, val: List[CarSkeleton3d]):
        self._cars = val

    def add_car(self, car: CarSkeleton3d) -> int:
        self._cars.append(car)
        return len(self._cars) - 1

    def get_random_car_model_filepath(self) -> str:
        model_files = sorted(glob(self.car_models_path + "/*.json"))
        idx = np.random.randint(0, len(model_files))
        return model_files[idx]

    def update_world(self, timestamp: float):
        for c_idx, r_idx in self.car_route_map.items():
            if c_idx is None or r_idx is None:
                continue
            if c_idx < 0 or c_idx >= len(self._cars):
                continue
            if r_idx < 0 or r_idx >= len(self._routes):
                continue
            car = self._cars[c_idx]
            route = self._routes[r_idx]

            # timestamp_ = timestamp
            # if self.loop_routes and route.duration() > 0.0:
            #     timestamp_ = timestamp % route.duration()
            #     if c_idx in self.car_idxs_to_randomize:
            #         if timestamp_ < (timestamp - self._last_timestamp):
            #             car.load_from_file(self.get_random_car_model_filepath())

            # TODO: move logic to Route class ?
            # loop ?
            # cycles_seen_counter ?
            timestamp_ = timestamp
            if r_idx in self.routes_idxs_to_loop and route.duration() > 0.0:
                timestamp_ = timestamp % route.duration()
                curr_cycle = int(timestamp // route.duration())
                prev_cycle = int(self._prev_timestamp // route.duration())
                if curr_cycle > prev_cycle:
                    if c_idx in self.car_idxs_to_randomize:
                        car.load_from_file(self.get_random_car_model_filepath())
                    # TODO: increment route cycles ? or assign curr cycle ?

            car.pose = route.interpolate_pose(timestamp_)
            car.eulers = route.interpolate_eulers(timestamp_)

        self._prev_timestamp = timestamp
