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
        self.points3d = {}
        self.rot_xyz = np.zeros(3, dtype=np.float32)

    def points_count(self):
        return len(self.points3d)

    def load(self, path: str):
        with open(path, 'r') as f:
            data = json.load(f)
            vertices = data.get('vertices', [])
            for label, idx in data.get('pts', {}).items():
                assert label in nodes, f"found bad label '{label}' in model '{path}'"
                assert idx < len(vertices), f"found bad model '{path}'. Failed to parse point with index '{idx}' and label '{label}'"
                assert len(vertices[idx]) == 3, f"found bad model '{path}'. Point with index '{idx}' and label '{label}' must be 3-dimensional (xyz)"
                self.points3d[label] = vertices[idx]

                print(label, self.points3d[label])

    def get_centroid(self) -> np.ndarray:
        result = np.zeros(3, dtype=np.float32)
        for pt in self.points3d.values():
            result += pt

        return result / len(self.points3d)

    def set_pose(self, x: float = 0.0, y: float = 0.0, z: float = 0.0):
        delta = [x, y, z] - self.get_centroid()
        self.translate(*delta)

    def translate(self, x: float = 0.0, y: float = 0.0, z: float = 0.0):
        for key in self.points3d.keys():
            self.points3d[key] += np.array([x, y, z])

    def rotate(self, x: float = 0.0, y: float = 0.0, z: float = 0.0):
        c = self.get_centroid()

        # back to original position (from world to object coordinate system)
        r_inv = eulers2rotmat(self.rot_xyz, degrees=True)
        r_inv = np.transpose(r_inv)

        # rotate with new angles (rotate in object coordinate system)
        self.rot_xyz += (x, y, z)
        self.rot_xyz %= 360.0
        r_new = eulers2rotmat(self.rot_xyz, degrees=True)

        for key in self.points3d.keys():
            pt = self.points3d[key]
            self.points3d[key] = np.matmul(r_new, np.matmul(r_inv, pt - c)) + c

    def draw(self,
             canvas: Axes,
             camera: Camera,
             draw_axes: bool = True,
             color: Tuple[float, float, float] = (1.0, 0.5, 0.5)):
        # draw axes
        if draw_axes:
            center3d = self.get_centroid()
            center2d = camera.project_points(center3d.reshape(1, -1))[0]
            axes3d = np.array([[1, 0, 0], [0, 1, 0], [0, 0, 1]])
            r = eulers2rotmat(self.rot_xyz, degrees=True)
            r = np.transpose(r)
            axes2d = camera.project_points(np.matmul(r, axes3d) + center3d)
            for vec, col, text in zip(axes2d, ['r', 'g', 'b'], ['x', 'y', 'z']):
                canvas.arrow(*center2d, *(vec - center2d), width=1, color=col, alpha=0.5)
                canvas.annotate(text, xy=vec, xytext=vec, alpha=0.5)

        # draw lines
        for idx1, idx2 in edges:
            label1, label2 = nodes[idx1], nodes[idx2]
            points3d = np.array([self.points3d[label1], self.points3d[label2]])
            points2d = camera.project_points(points3d)
            canvas.plot(points2d[:, 0], points2d[:, 1], color=color, lw=1, alpha=0.5)

        # draw points
        points3d = np.array(list(self.points3d.values()))
        points2d = camera.project_points(points3d)
        for point2d in points2d:
            canvas.plot(point2d[0], point2d[1], 'o', color=color, markersize=2)
