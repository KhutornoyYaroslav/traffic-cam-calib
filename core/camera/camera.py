import numpy as np
from typing import Tuple, Union
from core.math.eulers import eulers2rotmat
from core.math.geometry import line_plane_intersection
from core.common.transformable import Transformable


class Camera(Transformable):
    """
    Camera class allows you to project 3d world points onto the image plane.
    It uses the right-handed coordinate system. Positive rotations are clockwise.
    See for more info: https://www.evl.uic.edu/ralph/508S98/coordinates.html.
    """
    def __init__(self,
                 aov_h: float = 45.0,
                 img_size: Tuple[int, int] = (1920, 1080),
                 pose: Union[list, tuple, np.ndarray] = [0., 0., 0.],
                 eulers: Union[list, tuple, np.ndarray] = [0., 0., 0.]):
        super().__init__(pose, eulers)
        self.aov_h = aov_h
        self.img_w = img_size[0]
        self.img_h = img_size[1]
        self.z_clipping_far = 1000.0
        self.z_clipping_near = 0.001

    def get_intrinsic_matrix(self):
        mat = np.zeros((3, 3), dtype=np.float32)
        mat[0, 0] = self.img_w / (2 * np.tan(np.radians(self.aov_h) / 2))
        mat[1, 1] = mat[0, 0]
        mat[0, 2] = (self.img_w - 1) / 2
        mat[1, 2] = (self.img_h - 1) / 2
        mat[2, 2] = 1

        return mat

    def get_extrinsic_matrix(self):
        mat = np.zeros((3, 4), dtype=np.float32)
        r = eulers2rotmat(self.eulers, degrees=True)
        rt = np.transpose(r)
        mat[:3, :3] = rt
        mat[:3, 3] = np.matmul(-rt, self.pose)

        return mat

    def get_proj_matrix(self):
        return np.matmul(self.get_intrinsic_matrix(), self.get_extrinsic_matrix())

    def project_points(self, points3d: np.ndarray):
        intr_mat = self.get_intrinsic_matrix()
        extr_mat = self.get_extrinsic_matrix()

        points2d = []
        for point3d in points3d:
            # to camera coordinate system
            point3d = np.matmul(extr_mat, np.append(point3d, 1.0))

            # check z-clipping
            if point3d[2] < self.z_clipping_near or point3d[2] > self.z_clipping_far:
                continue

            # to image plane
            point2d = np.matmul(intr_mat, point3d)
            point2d /= point2d[2]
            point2d = point2d[:2]
            if not (0 < point2d[0] <= self.img_w) or not (0 < point2d[1] <= self.img_h):
                continue
            points2d.append(point2d)

        if not len(points2d):
            return None

        return np.stack(points2d, 0)

    def project_line(self, line_pt1: np.ndarray, line_pt2: np.ndarray):
        # to camera coordinate system
        extr_mat = self.get_extrinsic_matrix()
        line_pt1 = np.matmul(extr_mat, np.append(line_pt1, 1.0))
        line_pt2 = np.matmul(extr_mat, np.append(line_pt2, 1.0))

        # check near z-clipping
        if line_pt1[2] < self.z_clipping_near and line_pt2[2] < self.z_clipping_near:
            return None

        cam_norm = np.array([0.0, 0.0, 1.0])
        cam_pt = np.array([0.0, 0.0, self.z_clipping_near])

        if line_pt1[2] < self.z_clipping_near or line_pt2[2] < self.z_clipping_near:
            intersect_pt = line_plane_intersection(cam_norm, cam_pt, line_pt1, line_pt2)
            if intersect_pt is None:
                return None
            if line_pt1[2] < line_pt2[2]:
                line_pt1 = intersect_pt
            else:
                line_pt2 = intersect_pt

        # check far z-clipping
        if line_pt1[2] > self.z_clipping_far and line_pt2[2] > self.z_clipping_far:
            return None

        cam_pt = np.array([0.0, 0.0, self.z_clipping_far])

        if line_pt1[2] > self.z_clipping_far or line_pt2[2] > self.z_clipping_far:
            intersect_pt = line_plane_intersection(cam_norm, cam_pt, line_pt1, line_pt2)
            if intersect_pt is None:
                return None
            if line_pt1[2] > line_pt2[2]:
                line_pt1 = intersect_pt
            else:
                line_pt2 = intersect_pt

        # to image plane
        intr_mat = self.get_intrinsic_matrix()
        line_pt1 = np.matmul(intr_mat, line_pt1)
        line_pt1 /= line_pt1[2]
        line_pt1 = line_pt1[:2]
        line_pt2 = np.matmul(intr_mat, line_pt2)
        line_pt2 /= line_pt2[2]
        line_pt2 = line_pt2[:2]

        return line_pt1, line_pt2
