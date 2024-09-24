import numpy as np
from typing import List, Tuple, Dict
from scipy.optimize import differential_evolution
from core.objects.carskeleton3d import CarSkeleton3d
from core.camera.camera import Camera
from copy import deepcopy


# from fcmaes.decpp import minimize, Bounds
from fcmaes.de import minimize, Bounds
# from fcmaes.bitecpp import minimize, Bounds


"""
Calculates reprojection error for given parameters.
x : h, xr, zr, fovh, fovv, cx, cy, k1, yr1, model1, yr2, model2...

Possible CAMERA parameters to optimize:
- pose: (0, ty, 0) - only y-coordinate of camera is intrested
- eulers: (rx, 0, rz) - we don't need to calibrate y-rotation due to vehicles y-rotations
- focal length (fx, fy) - only for full (precise) calibration, otherwise we set f = fx = fy
- optical center (cx, cy) - only for full (precise) calibration, otherwise we set it to half of image size
- skew (0) - we assume that skew parameter is zero for most cameras
- k1, k2(0) - polynomial model distortion parameters

So, current CAMERA FULL parameters to optimize are:
- ty, rx, rz, fx, fy, cx, cy, k1

And current CAMERA IDEAL parameters to optimize are:
- ty, rx, rz, fx, [k1]

Possible VEHICLE parameters to optimize:
- pose: we calculate it automaticaly throw 2d keypoints assuming vehicle is on the ground plane
- eulers: (0, ry, 0) - we calibrate only y-rotation of each vehicle assuming there is no restrictions
on its y-rotation orientation
- model: we try to find best 3d vehicle model to fit 2d keypoints

So, current VEHICLE parameters to optimize are:
- ry1, model1, ry2, model2, ...

So, full list of parameters is:
- cam_ty, cam_rx, cam_rz, cam_fx, veh_ry1, veh_model1, veh_ry2, veh_model2, ...
"""


class ReprojSolver():
    base_params_size = 4
    variadic_params_size = 2

    def __init__(self,
                 img_w: int,
                 img_h: int,
                 bounds: List[Tuple[float, float]],
                 car_models: List[CarSkeleton3d]):
        self._img_w = img_w
        self._img_h = img_h

        bounds_size = self.base_params_size + self.variadic_params_size
        if len(bounds) != bounds_size:
            raise ValueError(f"The size of bounds must be equal to {bounds_size}")
        self._bounds = bounds

        if not len(car_models):
            raise ValueError("The number of car models must be > 0")
        self._car_models = car_models

        # TODO: check bounds for car models (compare with the length of avaible car models)

        self._cars_2d = None

    def solve(self, cars_2d: List[Dict[str, np.ndarray]]) -> List[float]:
        # check inputs
        if not len(cars_2d):
            raise ValueError("The length of cars_2d must be > 0")

        # prepare bounds
        bounds = self._bounds[:self.base_params_size]
        bounds += len(cars_2d) * self._bounds[self.base_params_size:
                                              self.base_params_size+self.variadic_params_size]

        # optimize
        # result = differential_evolution(func=self.reproj_error,
        #                                 bounds=bounds,
        #                                 args=[cars_2d],
        #                                 maxiter=8,
        #                                 popsize=8,
        #                                 workers=-1,
        #                                 disp=True
        # )

        # return result.x

        self._cars_2d = cars_2d
        # print(bounds)
        # de = DiffEvol(self.reproj_error, bounds, 128)
        # x, cost = de.optimize(ngen=1024)
        # print("cost: ", cost)
        # return x

        # ret = retry.minimize(self.reproj_error,
        #                      bounds,
        #                      args=[cars_2d],
        #                     #  logger=logger(),
        #                      optimizer=De_cpp(100))

        lb_bounds = [b[0] for b in bounds]
        ub_bounds = [b[1] for b in bounds]
        bounds = Bounds(lb=lb_bounds, ub=ub_bounds)
        # print(bounds)

        ints = len(bounds.lb) * [0]
        ints[5] = 1
        ints[7] = 1
        ints = np.array(ints, dtype=np.bool8)
        # print(ints)

        result = minimize(fun=self.reproj_error,
                          bounds=bounds,
                          popsize=32,
                          max_evaluations=256,
                          ints=ints
                        )

        print(result)

        return result.x


    def reproj_error(self, x: List[float]) -> float: # , *args
        """
        x = cam_ty, cam_rx, cam_rz, cam_fx, veh_ry1, veh_model1, veh_ry2, veh_model2, ...
        """

        # cars_2d = args[0]
        cars_2d = deepcopy(self._cars_2d)

        # create camera
        camera = Camera(aov_h=x[3],
                        img_size=(self._img_w, self._img_h),
                        pose=(0, x[0], 0),
                        eulers=(x[1], 0, x[2]))

        # calculate cars reprojection errors
        cars_reproj_errors = []
        for idx, car2d in enumerate(cars_2d):
            x_offset = 2 * idx

            # create 3d car model
            model_id = int(x[self.base_params_size + x_offset + 1])
            car3d = deepcopy(self._car_models[model_id])
            car3d.pose = (0, 0, 0)
            car3d.eulers = (0, 0, 0)
            car3d.rotate(y=x[self.base_params_size + x_offset])
            # car3d.eulers = (0.0, x[self.base_params_size + x_offset], 0.0)

            # calc x, z vehicle position
            x_mean, z_mean = [], []
            for label, ref_point2d in car2d.items():
                ref_point3d = car3d.world_node(label) # TODO: check if label doesn't exist?
                plane_norm = np.array([0, -1.0, 0])
                plane_orig = np.array([0, ref_point3d[1], 0])
                point3d = camera.unproject_point(ref_point2d, plane_norm, plane_orig)
                if point3d is None:
                    continue

                xyz = point3d - ref_point3d
                x_mean.append(xyz[0])
                z_mean.append(xyz[2])

            if not len(x_mean):
                cars_reproj_errors.append(1000.0) # TODO: fictive error
                continue

            car3d.translate(x=np.mean(x_mean), z=np.mean(z_mean))
            # car3d.pose = (np.mean(x_mean), 0.0, np.mean(z_mean))
            # print(car3d.pose)

            # print(car3d.pose, car3d.eulers)

            # project car3d and calc error
            car_errors = []
            for label, real_point2d in car2d.items():
                point3d = car3d.world_node(label)
                proj_point2d = camera.project_points([point3d])
                if proj_point2d is None:
                    # assert False # TODO: what to do in this case ?
                    car_errors.append(1000.0) # TODO:
                    continue
                proj_point2d = proj_point2d[0]
                err = np.linalg.norm(proj_point2d - real_point2d)
                car_errors.append(err)

            # if not len(car_errors):
            #     cars_reproj_errors.extend([1000.0]) # TODO:
            # else:
            cars_reproj_errors.extend(car_errors)
            # cars_reproj_errors.append(np.mean(car_errors))

        # print(len(cars_reproj_errors))
        # TODO:
        # if not len(cars_reproj_errors):
            # return 1000.0
        # else:
        return np.mean(cars_reproj_errors)
