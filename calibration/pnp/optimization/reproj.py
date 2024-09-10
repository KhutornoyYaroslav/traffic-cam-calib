from typing import List


class ReprojSolver():
    def __init__(self):
        pass

    def reproj_error(self, x: List[float]) -> float:
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

        # TODO: steps (see Optimizer.cpp, 81)
        # 0) Check inputs - equality of sizes of parameters, bounds, etc.
        # 1) Create camera object with given parameters
        # 2) Calculate tx, tz vehicle position with created camera
        # 3) Project 3d model subset of vehicle's keypoints on image plane
        # 4) Calculate reprojection errors for each point for each vehicle
        # 5) Return error (or average error, but it is unnecessary to average error)

        raise NotImplementedError