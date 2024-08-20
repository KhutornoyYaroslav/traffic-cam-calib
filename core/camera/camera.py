import numpy as np
from typing import Tuple
from core.camera.functional import eulers2rotmat


def line_plane_intersection(plane_norm: np.ndarray,
                            plane_pt: np.ndarray,
                            line_pt1: np.ndarray,
                            line_pt2: np.ndarray) -> np.ndarray:
    line_dir = line_pt1 - line_pt2
    line_dir /= np.linalg.norm(line_dir)
    dot_prod = np.dot(line_dir, plane_norm)

    if dot_prod == 0:
        print("The line is parallel to the plane. No intersection point.")
        return None
    else:
        # Compute the parameter t that gives the intersection point
        t = sum([(a-b)*c for a,b,c in zip(plane_pt, line_pt1, plane_norm)]) / dot_prod

        # Compute the intersection point by plugging t into the line equation
        inter_pt = [a + b*t for a,b in zip(line_pt1, line_dir)]

        # Print the intersection point
        # print("The intersection point is", inter_pt)

        return np.array(inter_pt)


class Camera:
    """
    Camera class allows you to project 3d world points onto the image plane.
    It uses the right-handed coordinate system. Positive rotations are clockwise.
    See for more info: https://www.evl.uic.edu/ralph/508S98/coordinates.html.
    """
    def __init__(self,
                 aov_h: float,
                 img_size: Tuple[int, int],
                 pose_xyz: Tuple[float, float, float] = (0, 0, 0),
                 eulers_xyz: Tuple[float, float, float] = (0, 0, 0)):
        self.aov_h = aov_h
        self.img_size = img_size
        self.pose_xyz =  np.array(pose_xyz)
        self.eulers_xyz = np.array(eulers_xyz)
        self.near_clip_z = 0.001

    def set_aovh(self, aov_h: float):
        self.aov_h = aov_h

    def zoom(self, angles: float):
        self.aov_h += angles

    def get_intrinsic_matrix(self):
        mat = np.zeros((3, 3), dtype=np.float32)
        mat[0, 0] = self.img_size[0] / (2 * np.tan(np.radians(self.aov_h) / 2))
        mat[1, 1] = mat[0, 0]
        mat[0, 2] = (self.img_size[0] - 1) / 2
        mat[1, 2] = (self.img_size[1] - 1) / 2
        mat[2, 2] = 1

        return mat

    def get_extrinsic_matrix(self):
        mat = np.zeros((3, 4), dtype=np.float32)
        r = eulers2rotmat(self.eulers_xyz, degrees=True)
        rt = np.transpose(r)
        mat[:3, :3] = rt
        mat[:3, 3] = np.matmul(-rt, self.pose_xyz)

        return mat

    def get_proj_matrix(self):
        return np.matmul(self.get_intrinsic_matrix(), self.get_extrinsic_matrix())

    def project_line(self, point3d_1: np.ndarray, point3d_2: np.ndarray):
        extr = self.get_extrinsic_matrix()
        intr = self.get_intrinsic_matrix()

        point3d_1_cam = np.matmul(extr, np.append(point3d_1, 1.0))
        point3d_2_cam = np.matmul(extr, np.append(point3d_2, 1.0))

        if point3d_1_cam[-1] < self.near_clip_z and point3d_2_cam[-1] < self.near_clip_z:
            return None

        if point3d_1_cam[-1] < self.near_clip_z or point3d_2_cam[-1] < self.near_clip_z:
            intersect_pt = line_plane_intersection(np.array([0.0, 0.0, 1.0]), np.array([0.0, 0.0, self.near_clip_z]), point3d_1_cam, point3d_2_cam)
            if intersect_pt is None:
                return None

            if point3d_1_cam[-1] < point3d_2_cam[-1]:
                point3d_1_cam = intersect_pt
            else:
                point3d_2_cam = intersect_pt

        point2d_1 = np.matmul(intr, point3d_1_cam)
        point2d_1 /= point2d_1[2]
        point2d_1 = point2d_1[:2]
        point2d_2 = np.matmul(intr, point3d_2_cam)
        point2d_2 /= point2d_2[2]
        point2d_2 = point2d_2[:2]

        return point2d_1, point2d_2

    def project_points(self, points3d: np.ndarray, drop_out: bool = False):
        # proj = self.get_proj_matrix()
        extr = self.get_extrinsic_matrix()
        intr = self.get_intrinsic_matrix()

        points2d = []
        for point3d in points3d:

            pt3d_ = np.matmul(extr, np.append(point3d, 1.0))

            if pt3d_[2] < 0.1:
                # TODO: clip by plane
                continue
            # pt3d_[2] = np.clip(pt3d_[2], 0.1, None)

            point2d = np.matmul(intr, pt3d_)

            # point2d = np.matmul(proj, np.append(point3d, 1.0))
            point2d /= point2d[2]
            point2d = point2d[:2]

            if drop_out:
                if not (0 < point2d[0] <= self.img_size[0]) or not (0 < point2d[1] <= self.img_size[1]):
                    continue

            points2d.append(point2d)

        if not len(points2d):
            return None # TODO:

        return np.stack(points2d, 0)
