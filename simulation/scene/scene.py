import numpy as np
from glob import glob
from typing import List
from simulation.routing.route import Route
from simulation.objects.vehicle import Vehicle
from simulation.objects.planegrid import PlaneGrid
from simulation.drawing.drawable import Drawable, Camera, Axes


class Scene(Drawable):
    def __init__(self):
        super().__init__() # Drawable
        self._plane_grid = None
        self._vehicles = []
        self._routes = []
        self.vehicle_route_map = {}
        self.vehicles_to_randomize = []
        self.loop_routes = False
        self.models_dir = ""
        self._last_timestamp = 0.0

    @property
    def plane_grid(self) -> PlaneGrid:
        return self._plane_grid

    @plane_grid.setter
    def plane_grid(self, val: PlaneGrid):
        self._plane_grid = val

    @property
    def routes(self) -> List[Route]:
        return self._routes

    @routes.setter
    def routes(self, val: List[Route]):
        self._routes = val

    def add_route(self, route: Route) -> int:
        self._routes.append(route)

        return len(self._routes) - 1

    @property
    def vehicles(self) -> List[Vehicle]:
        return self._vehicles

    @vehicles.setter
    def vehicles(self, val: List[Vehicle]):
        self._vehicles = val

    def add_vehicle(self, vehicle: Vehicle) -> int:
        self._vehicles.append(vehicle)

        return len(self._vehicles) - 1

    def get_random_model_file(self):
        model_files = sorted(glob(self.models_dir + "/*.json"))
        idx = np.random.randint(0, len(model_files))

        return model_files[idx]

    def update_world(self, timestamp: float):
        # update vehicles positions
        for v, r in self.vehicle_route_map.items():
            if v is None or r is None:
                continue
            if v < 0 or v >= len(self._vehicles):
                continue
            if r < 0 or r >= len(self._routes):
                continue
            route = self._routes[r]
            vehicle = self._vehicles[v]

            timestamp_ = timestamp
            if self.loop_routes and route.duration() > 0.0:
                timestamp_ = timestamp % route.duration()
                if v in self.vehicles_to_randomize:
                    if timestamp_ < (timestamp - self._last_timestamp):
                        vehicle.load_from_file(self.get_random_model_file())

            vehicle.pose = route.interpolate_pose(timestamp_)
            vehicle.eulers = route.interpolate_eulers(timestamp_)

        self._last_timestamp = timestamp

    def draw(self, canvas: Axes, camera: Camera):
        # draw plane grid
        if self._plane_grid is not None:
            self._plane_grid.draw(canvas, camera)

        # draw routes
        for route in self._routes:
            route.draw(canvas, camera)

        # draw vehicles
        for vehicle in self._vehicles:
            vehicle.draw(canvas, camera)
