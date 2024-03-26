import numpy as np
from typing import Tuple
from core.camera.functional import eulers2rotmat


class Camera:
    """
    Camera class allows you to project 3d world points onto the image plane.
    It uses the OpenGL camera coordinate system, where the X axis is pointing to the right,
    Y axis is pointing upwards and the Z axis is pointing backwards.
    """
    def __init__(self,
                 aov_h: float,
                 img_size: Tuple[int, int],
                 pose_xyz: Tuple[float, float, float] = (0, 0, 0),
                 eulers_xyz: Tuple[float, float, float] = (0, 0, 0)):
        self.aov_h = aov_h
        self.pose_xyz = pose_xyz
        self.eulers_xyz = (eulers_xyz[0] + 180.0, eulers_xyz[1], eulers_xyz[2])
        self.img_size = img_size

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
        r = eulers2rotmat(np.radians(self.eulers_xyz), order='YXZ')
        rt = np.transpose(r)
        t = np.array(self.pose_xyz)
        mat[:3, :3] = rt
        mat[:3, 3] = np.matmul(-rt, t)

        return mat

    def get_proj_matrix(self):
        return np.matmul(self.get_intrinsic_matrix(), self.get_extrinsic_matrix())

    def project_points(self, points3d: np.ndarray, drop_out: bool = False):
        proj = self.get_proj_matrix()

        points2d = []
        for point3d in points3d:
            point2d = np.matmul(proj, np.append(point3d, 1.0))
            point2d /= point2d[2]
            point2d = point2d[:2]

            if drop_out:
                if not (0 < point2d[0] <= self.resolution[0]) or not (0 < point2d[1] <= self.resolution[1]):
                    continue

            points2d.append(point2d)

        return np.stack(points2d, 0)
