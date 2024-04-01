import json
import numpy as np
from typing import Tuple
from matplotlib.axes import Axes
from core.camera.camera import Camera
from core.camera.functional import eulers2rotmat
from core.vehicle.vehicle_keypoints import nodes, edges


class Vehicle():
    def __init__(self, tag: str = ""):
        self.tag = tag
        self.obj_pts = {}
        self.rot_xyz = np.zeros(3, dtype=np.float32)
        self.pose_xyz = np.zeros(3, dtype=np.float32)

    def points_count(self):
        return len(self.obj_pts)

    def load(self, path: str):
        with open(path, 'r') as f:
            data = json.load(f)
            vertices = data.get('vertices', [])
            for label, idx in data.get('pts', {}).items():
                assert label in nodes, f"found bad label '{label}' in model '{path}'"
                assert idx < len(vertices), f"found bad model '{path}'. Failed to parse point with index '{idx}' and label '{label}'"
                assert len(vertices[idx]) == 3, f"found bad model '{path}'. Point with index '{idx}' and label '{label}' must be 3-dimensional (xyz)"
                self.obj_pts[label] = vertices[idx]

    def _get_centroid(self) -> np.ndarray:
        result = np.zeros(3, dtype=np.float32)
        for pt in self.obj_pts.values():
            result += pt

        return result / len(self.obj_pts)

    def set_pose(self, x: float = 0.0, y: float = 0.0, z: float = 0.0):
        self.pose_xyz = np.array([x, y, z], dtype=np.float32)

    def translate(self, x: float = 0.0, y: float = 0.0, z: float = 0.0):
        self.pose_xyz += np.array([x, y, z], dtype=np.float32)

    def set_rotation(self, x: float = 0.0, y: float = 0.0, z: float = 0.0):
        self.rot_xyz = np.array([x, y, z], dtype=np.float32) 
        self.rot_xyz %= 360.0

    def rotate(self, x: float = 0.0, y: float = 0.0, z: float = 0.0):
        self.rot_xyz += np.array([x, y, z], dtype=np.float32) 
        self.rot_xyz %= 360.0

    def get_world_pts(self):
        world_pts = {}

        # rotate
        c = self._get_centroid()
        r = eulers2rotmat(self.rot_xyz, degrees=True)
        for key in self.obj_pts.keys():
            world_pts[key] = np.matmul(r, self.obj_pts[key] - c) + c

        # translate
        for key in world_pts.keys():
            world_pts[key] += self.pose_xyz

        return world_pts


    def get_obj_pts(self, centered: bool = False):
        result = self.obj_pts.copy()

        if centered:
            c = self._get_centroid()
            for label in result.keys():
                result[label] -= c

        return result
            

    def draw(self,
             canvas: Axes,
             camera: Camera,
             draw_axes: bool = True,
             color: Tuple[float, float, float] = (1.0, 0.5, 0.5)):
        
        world_pts = self.get_world_pts()

        # draw axes
        if draw_axes:
            center3d = self._get_centroid()
            axes3d = np.array([[1, 0, 0], [0, 1, 0], [0, 0, 1]])
            r = eulers2rotmat(self.rot_xyz, degrees=True)
            r = np.transpose(r)
            axes3d = np.matmul(r, axes3d) + center3d
            axes2d = camera.project_points(axes3d + self.pose_xyz)
            center3d_world = center3d + self.pose_xyz
            center2d = camera.project_points(center3d_world.reshape(1, -1))[0]
            for vec, col, text in zip(axes2d, ['r', 'g', 'b'], ['x', 'y', 'z']):
                canvas.arrow(*center2d, *(vec - center2d), width=1, color=col, alpha=0.5)
                canvas.annotate(text, xy=vec, xytext=vec, alpha=0.5)

        # draw lines
        for idx1, idx2 in edges:
            label1, label2 = nodes[idx1], nodes[idx2]
            points3d = np.array([world_pts[label1], world_pts[label2]])
            points2d = camera.project_points(points3d)
            canvas.plot(points2d[:, 0], points2d[:, 1], color=color, lw=1, alpha=0.5)

        # draw points
        points3d = np.array(list(world_pts.values()))
        points2d = camera.project_points(points3d)
        for point2d in points2d:
            canvas.plot(point2d[0], point2d[1], 'o', color=color, markersize=2)
