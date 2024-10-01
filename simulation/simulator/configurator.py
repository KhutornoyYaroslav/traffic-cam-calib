import json
import numpy as np
from core.camera import Camera
from simulation.simulator import Simulator
from simulation.scene import Configurator as SceneConfigurator
from simulation.errors import NormalError2d, NormalError3d


class Configurator():
    def __init__(self, simulator: Simulator):
        self.simulator = simulator

    def parse_scene(self, data: dict):
        path = data.get("scene_config_path", "")
        configurator = SceneConfigurator(self.simulator._scene)
        configurator.configurate(path)

    def parse_cameras(self, data: dict):
        camera_data = data.get("camera", {})
        # params
        camera = self.simulator._camera
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
        # errors
        errors_params = camera_data.get("errors", {})
        self.simulator.camera_pose_error = NormalError3d.from_json(errors_params.get("pose", {}))
        self.simulator.camera_eulers_error = NormalError3d.from_json(errors_params.get("eulers", {}))

    def parse_cars_errors(self, data: dict):
        params = data.get("cars_errors", {})
        self.simulator.cars_pose_error = NormalError3d.from_json(params.get("pose", {}))
        self.simulator.cars_eulers_error = NormalError3d.from_json(params.get("eulers", {}))
        self.simulator.cars_projection_error = NormalError2d.from_json(params.get("projection", {}))
        self.simulator.cars_detecton_score = np.clip(params.get("detection_score", 1.0), 0.0, 1.0)

    def configurate(self, filepath: str):
        with open(filepath, 'r') as f:
            data = json.load(f)
            self.parse_scene(data)
            self.parse_cameras(data)
            self.parse_cars_errors(data)
