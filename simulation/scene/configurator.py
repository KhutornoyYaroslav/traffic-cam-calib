import json
from simulation.scene.scene import Scene
from simulation.routing.route import Route
from core.objects.carskeleton3d import CarSkeleton3d
from core.objects.carskeleton3d import LABELS as car_keypoints_labels


class Configurator():
    def __init__(self, scene: Scene):
        self.scene = scene

    def parse_common(self, data: dict):
        self.scene.car_models_path = data.get("car_models_path", "")

    def parse_routes(self, data: dict):
        routes = data.get("routes", [])
        for route in routes:
            waypoints = route.get("waypoints", [])
            dts = route.get("dts", [])
            loop = route.get("loop", False)
            self.scene.add_route(Route(waypoints, dts, loop))

    def parse_cars(self, data: dict):
        cars_params = data.get("cars", [])
        for car_params in cars_params:
            model_path = car_params.get("model_path", self.scene.get_random_car_model_filepath())
            new_car = CarSkeleton3d()
            new_car.load_from_file(model_path, car_keypoints_labels)
            car_idx = self.scene.add_car(new_car)
            self.scene.car_route_map[car_idx] = car_params.get("route_id", None)
            if car_params.get("randomize_model", False):
                self.scene.car_idxs_to_randomize.append(car_idx)

    def configurate(self, filepath: str):
        with open(filepath, 'r') as f:
            data = json.load(f)
            self.parse_common(data)
            self.parse_routes(data)
            self.parse_cars(data)
