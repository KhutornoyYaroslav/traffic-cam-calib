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
            ts = route.process_timestamp(timestamp)
            car.pose = route.interpolate_pose(ts)
            car.eulers = route.interpolate_eulers(ts)
            if route.cycle_changed():
                # print(f"Route {r_idx} cycle counts: {route.cycle_count()}")
                if c_idx in self.car_idxs_to_randomize:
                    car.load_from_file(self.get_random_car_model_filepath())
