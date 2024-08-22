from simulation.routing.route import Route
from simulation.objects.vehicle import Vehicle
from simulation.objects.planegrid import PlaneGrid
from simulation.drawing.drawable import Drawable, Camera, Axes


ROUTE_1_WAYPOINTS = [
    [-2, 0, -10],
    [-2, 0, 50]
]

ROUTE_2_WAYPOINTS = [
    [2, 0, -20],
    [2, 0, 40]
]

ROUTE_3_WAYPOINTS = [
    [2, 0, -30],
    [2, 0, 70]
]


DEFAULT_SPEED = 30.0 # mps


class Scene(Drawable):
    def __init__(self):
        super().__init__() # Drawable
        self._plane_grid = PlaneGrid((-4.0, 4.0), (-100.0, 100.0), 1.0)
        self._vehicles = [
            Vehicle("data/models/Ford_Mondeo.json"),
            Vehicle("data/models/Smart.json"),
            Vehicle("data/models/Range_Rover.json")]
        self._routes = [
            Route(ROUTE_1_WAYPOINTS),
            Route(ROUTE_2_WAYPOINTS),
            Route(ROUTE_3_WAYPOINTS)]
        self._vehicle_route_map = {0: 0, 1: 1, 2: 2}

    def update_world(self, timestamp: float):
        # update vehicles positions
        for v, r in self._vehicle_route_map.items():
            route = self._routes[r]
            vehicle = self._vehicles[v]
            current_station = timestamp * DEFAULT_SPEED
            current_station %= route.length()
            vehicle.pose = route.interpolate_pose(current_station)

    def draw(self, canvas: Axes, camera: Camera):
        # draw plane grid
        self._plane_grid.draw(canvas, camera)

        # draw vehicles
        for vehicle in self._vehicles:
            vehicle.draw(canvas, camera)
