import json
from simulation.scene.scene import Scene
from simulation.routing.route import Route
from simulation.objects.planegrid import PlaneGrid
from simulation.objects.vehicle import Vehicle, LABELS


class SceneReader():
    def __init__(self, scene: Scene):
        self._scene = scene

    def parse_common(self, data: dict):
        self._scene.loop_routes = data.get("loop_routes", False)
        self._scene.models_dir = data.get("models_dir", "")

    def parse_routes(self, data: dict):
        routes = data.get("routes", [])
        for route in routes:
            waypoints = route.get("waypoints", [])
            dts = route.get("dts", [])
            self._scene.add_route(Route(waypoints, dts))

    def parse_vehicles(self, data: dict):
        vehicles = data.get("vehicles", [])
        for vehicle in vehicles:
            model_path = vehicle.get("model_path", [])
            new_vehicle = Vehicle()
            new_vehicle.load_from_file(model_path, LABELS)
            vehicle_id = self._scene.add_vehicle(new_vehicle)
            self._scene.vehicle_route_map[vehicle_id] = vehicle.get("route_id", None)
            if vehicle.get("randomize_model", False):
                self._scene.vehicles_to_randomize.append(vehicle_id)

    def prase_plane_grid(self, data: dict):
        pg_data = data.get("plane_grid", {})
        plane_grid = PlaneGrid(x_range=(pg_data["x_min"], pg_data["x_max"]),
                               z_range=(pg_data["z_min"], pg_data["z_max"]),
                               step=pg_data["step"])
        self._scene.plane_grid = plane_grid

    def read(self, filepath: str):
        with open(filepath, 'r') as f:
            data = json.load(f)
            self.parse_common(data)
            self.parse_routes(data)
            self.parse_vehicles(data)
            self.prase_plane_grid(data)
