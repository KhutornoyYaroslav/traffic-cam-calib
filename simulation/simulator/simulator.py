import numpy as np
from copy import deepcopy
from typing import List, Dict
from core.camera import Camera
from core.objects import CarSkeleton3d
from simulation.scene import Scene
from simulation.routing import Route
from simulation.errors import NormalError2d, NormalError3d


class Simulator():
    def __init__(self):
        self._scene = Scene()
        self._camera = Camera()
        self.cars_pose_error = NormalError3d()
        self.cars_eulers_error = NormalError3d()
        self.cars_projection_error = NormalError2d()
        self.cars_detecton_score = 1.0
        self.camera_pose_error = NormalError3d()
        self.camera_eulers_error = NormalError3d()

    def get_routes(self) -> List[Route]:
        return self._scene.routes

    def get_cars(self) -> List[CarSkeleton3d]:
        result = self._scene.cars
        for car in result:
            car.pose += self.cars_pose_error.rand()
            car.eulers += self.cars_eulers_error.rand()

        return result
    
    def get_projected_cars(self, camera: Camera, only_visible_nodes: bool = True):
        result = []

        for car3d in self.get_cars():
            brect, mask = CarSkeleton3d.get_brect_and_mask(car3d.get_projection(camera, only_visible_nodes=False))
            if brect is None:
                continue

            points2d = {}
            brect_diag = np.linalg.norm(brect[2:])
            for label, pt in car3d.get_projection(camera, only_visible_nodes).items():
                if np.random.choice([0, 1], size=1, p=[1 - self.cars_detecton_score, self.cars_detecton_score]):
                    err = brect_diag * self.cars_projection_error.rand()
                    points2d[label] = np.clip(pt + err.astype(np.int32), [0, 0], [camera.img_w - 1, camera.img_h - 1])

            if not len(points2d):
                continue

            result.append((car3d, points2d, brect, mask))

        return result # CarSkeleton3d, keypoint3d, brect, mask

    def get_camera(self) -> Camera:
        camera = deepcopy(self._camera)
        camera.pose += self.camera_pose_error.rand()
        camera.eulers += self.camera_eulers_error.rand()

        return camera

    def update(self, timestamp: float):
        self._scene.update_world(timestamp)
