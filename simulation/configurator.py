import json
from engine.camera.camera import Camera
from simulation.simulator import Simulator
from simulation.scene.configurator import SceneConfigurator


class Configurator():
    def __init__(self, simulator: Simulator):
        self._simulator = simulator

    def parse_scene(self, data: dict):
        path = data.get("scene_config_path", "")
        configurator = SceneConfigurator(self._simulator.scene)
        configurator.configurate(path)

    def parse_cameras(self, data: dict):
        cameras = []
        for params in data.get("cameras", []):
            camera = Camera()
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
            cameras.append(camera)
        self._simulator.cameras = cameras

    def parse_timing(self, data: dict):
        self._simulator.t_start = data.get("t_start", 0.0)
        self._simulator.t_stop = data.get("t_stop", 0.0)
        self._simulator.t_step = data.get("t_step", 0.1)

    def parse_drawings(self, data: dict):
        self._simulator.draw_scene = data.get("draw_scene", False)
        self._simulator.draw_routes = data.get("draw_routes", True)
        self._simulator.draw_plane_grid = data.get("draw_plane_grid", True)

    def configurate(self, filepath: str):
        with open(filepath, 'r') as f:
            data = json.load(f)
            self.parse_scene(data)
            self.parse_cameras(data)
            self.parse_timing(data)
            self.parse_drawings(data)
