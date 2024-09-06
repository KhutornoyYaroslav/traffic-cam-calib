import json
from testing.tester import Tester
from simulation.configurator import Configurator as SimConfigurator
from testing.errors.normalerror3d import NormalError3d


class Configurator():
    def __init__(self, tester: Tester):
        self.tester = tester

    def parse_simulator(self, data: dict):
        path = data.get("simulator_config_path", "")
        configurator = SimConfigurator(self.tester.simulator)
        configurator.configurate(path)

    def parse_cameras_errors(self, data: dict):
        for camera_errors_params in data.get("cameras_errors", []):
            name = camera_errors_params.get("camera_name", "")
            if len(name):
                self.tester.cameras_pose_errors[name] = NormalError3d().from_json(
                    camera_errors_params.get("pose_errors", {}))
                self.tester.cameras_eulers_errors[name] = NormalError3d().from_json(
                    camera_errors_params.get("eulers_errors", {}))

    # def parse_drawings(self, data: dict):
    #     self.simulator.draw_scene = data.get("draw_scene", False)
    #     self.simulator.draw_routes = data.get("draw_routes", True)
    #     self.simulator.draw_plane_grid = data.get("draw_plane_grid", True)

    # def parse_vehicles_errors(self, data: dict):
    #     params = data.get("vehicles_errors", {})
    #     # points detection error
    #     pts_det_err = NormalError3d()
    #     params_pts_det_err = params.get("points_detection_error", {})
    #     pts_det_err.x_mean = params_pts_det_err.get("x_mean", 0.0)
    #     pts_det_err.x_std = params_pts_det_err.get("x_std", 0.0)
    #     pts_det_err.y_mean = params_pts_det_err.get("y_mean", 0.0)
    #     pts_det_err.y_std = params_pts_det_err.get("y_std", 0.0)
    #     pts_det_err.z_mean = params_pts_det_err.get("z_mean", 0.0)
    #     pts_det_err.z_std = params_pts_det_err.get("z_std", 0.0)
    #     self.simulator.vehicles_points_detection_error = pts_det_err

    def configurate(self, filepath: str):
        with open(filepath, 'r') as f:
            data = json.load(f)
            self.parse_simulator(data)
            self.parse_cameras_errors(data)
