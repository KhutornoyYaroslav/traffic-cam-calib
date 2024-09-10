from copy import deepcopy
from typing import List, Dict
from core.objects.carskeleton3d import CarSkeleton3d
from core.camera.camera import Camera
from simulation.scene.scene import Scene
from simulation.errors.normalerror3d import NormalError3d
from simulation.routing.route import Route


class Simulator():
    def __init__(self):
        self._scene = Scene()
        self._cameras = {}
        self.cars_pose_error = NormalError3d()
        self.cars_eulers_error = NormalError3d()
        self.camera_pose_error = {}
        self.camera_eulers_error = {}

    def get_routes(self) -> List[Route]:
        return self._scene.routes

    def get_cars(self) -> List[CarSkeleton3d]:
        result = self._scene.cars
        for car in result:
            car.pose += self.cars_pose_error.rand()
            car.eulers += self.cars_eulers_error.rand()

        return result

    def add_camera(self, name: str, cam: Camera) -> bool:
        if name in self._cameras:
            return False
        self._cameras[name] = cam

        return True

    def get_cameras(self) -> Dict[str, Camera]:
        result = {}
        for name, cam in self._cameras.items():
            res_cam = deepcopy(cam)
            if name in self.camera_pose_error:
                res_cam.pose += self.camera_pose_error[name].rand()
            if name in self.camera_eulers_error:
                res_cam.eulers += self.camera_eulers_error[name].rand()
            result[name] = res_cam

        return result

    def update(self, timestamp: float):
        self._scene.update_world(timestamp)
