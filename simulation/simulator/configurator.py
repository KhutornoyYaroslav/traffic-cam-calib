import json
from core.camera.camera import Camera
from simulation.simulator.simulator import Simulator
from simulation.scene.configurator import Configurator as SceneConfigurator
from simulation.errors.normalerror3d import NormalError3d


class Configurator():
    def __init__(self, simulator: Simulator):
        self.simulator = simulator

    def parse_scene(self, data: dict):
        path = data.get("scene_config_path", "")
        configurator = SceneConfigurator(self.simulator._scene)
        configurator.configurate(path)

    def parse_cameras(self, data: dict):
        for camera_data in data.get("cameras", []):
            # name
            name = camera_data.get("name", "")
            if not len(name):
                print("Failed to add camera. Name must not be empty.")
                continue
            # params
            camera = Camera()
            params = camera_data.get("params", {})
            camera.aov_h = params.get("aov_h", 50.0)
            camera.img_w = params.get("img_w", 1920)
            camera.img_h = params.get("img_h", 1080)
            params_pose = params.get("pose", {})
            camera.pose = (
                params_pose.get("x", 0.0),
                params_pose.get("y", 0.0),
                params_pose.get("z", 0.0)
            )
            params_eulers = params.get("eulers", {})
            camera.eulers = (
                params_eulers.get("x", 0.0),
                params_eulers.get("y", 0.0),
                params_eulers.get("z", 0.0)
            )
            if not self.simulator.add_camera(name, camera):
                print("Failed to add camera. Found duplicated camera names.")
                continue
            # errors
            errors_params = camera_data.get("errors", {})
            self.simulator.camera_pose_error[name] = NormalError3d.from_json(errors_params.get("pose", {}))
            self.simulator.camera_eulers_error[name] = NormalError3d.from_json(errors_params.get("eulers", {}))

    def parse_cars_errors(self, data: dict):
        params = data.get("cars_errors", {})
        self.simulator.cars_pose_error = NormalError3d.from_json(params.get("pose", {}))
        self.simulator.cars_eulers_error = NormalError3d.from_json(params.get("eulers", {}))

    def configurate(self, filepath: str):
        with open(filepath, 'r') as f:
            data = json.load(f)
            self.parse_scene(data)
            self.parse_cameras(data)
            self.parse_cars_errors(data)
