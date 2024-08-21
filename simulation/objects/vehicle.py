import json
import numpy as np
from typing import Union, Tuple
from engine.objects.skeleton3d import Skeleton3d
from simulation.drawing.drawable import Drawable, Axes, Camera


class Vehicle(Skeleton3d, Drawable):
    def __init__(self,
                 model_path: str,
                 pose: Union[list, tuple, np.ndarray] = [0., 0., 0.],
                 eulers: Union[list, tuple, np.ndarray] = [0., 0., 0.],
                 scale: float = 1.,
                 color: Tuple[float, float, float] = (1.0, 0.5, 0.5),
                 tag: str = ""):
        self._labels = self.get_labels()
        self._color = color
        self._tag = tag
        super().__init__(self.load_points_from_file(model_path),
                         self.get_edges(),
                         pose,
                         eulers,
                         scale)

    def load_points_from_file(self, path: str):
        result = []

        with open(path, 'r') as f:
            data = json.load(f)
            vertices = data.get('vertices', [])
            for label, idx in data.get('pts', {}).items():
                assert label in self._labels, f"found bad label '{label}' in model '{path}'"
                assert idx < len(vertices), f"found bad model '{path}'. Failed to parse point with index '{idx}' and label '{label}'"
                assert len(vertices[idx]) == 3, f"found bad model '{path}'. Point with index '{idx}' and label '{label}' must be 3-dimensional (xyz)"
                result.append(vertices[idx])

        return result

    def draw(self, canvas: Axes, camera: Camera):
        world_points = self.world_points()

        # draw edges
        for idx1, idx2 in self._edges:
            res = camera.project_line(world_points[idx1], world_points[idx2])
            if res is not None:
                res = np.stack(res, 0)
                canvas.plot(res[:, 0], res[:, 1], color=self._color, lw=1, alpha=0.5)

        # draw nodes
        points2d = camera.project_points(world_points)
        if points2d is not None:
            for point2d in points2d:
                canvas.plot(point2d[0], point2d[1], 'o', color=self._color, markersize=2)

    @staticmethod
    def get_edges():
        edges = [
            # face
            [14, 26], [14, 18],
            [15, 27], [15, 20],
            [14, 15],
            [26, 18], [26, 19], [18, 19],
            [27, 20], [27, 21], [20, 21],
            [18, 20],
            [19, 21],
            # windshield and rearview mirrors
            [4, 5], [5, 6], [6, 7], [7, 4],
            [12, 4], [12, 7],
            [13, 5], [13, 6],
            # face <-> windshield
            [19, 7], [21, 6],
            # back
            [16, 28], [16, 22],
            [17, 29], [17, 24],
            [16, 17],
            [28, 22], [28, 23], [22, 23],
            [29, 24], [29, 25], [24, 25],
            [22, 24],
            [23, 25],
            # eear window
            [8, 9], [9, 10], [10, 11], [11, 8],
            # back <-> rear window
            [23, 11], [25, 10],
            # face <-> back (roof part)
            [4, 9], [5, 8],
            # wheels
            [0, 1], [2, 3],
            # front wheels <-> face and rearview mirrors
            [0, 27], [0, 21], [0, 13],
            [2, 26], [2, 19], [2, 12],
            # back wheels <-> back and rearview mirrors
            [1, 13], [1, 31], [1, 28],
            [3, 12], [3, 30], [3, 29],
            # side window <-> rear window
            [30, 10], [31, 11],
            # side window <-> rearview mirrors
            [30, 12], [31, 13]
        ]

        return edges

    @staticmethod
    def get_labels():
        labels = [
            "fl wheel", # 0
            "bl wheel", # 1
            "fr wheel", # 2
            "br wheel", # 3
            "windshield tr", # 4
            "windshield tl", # 5
            "windshield bl", # 6
            "windshield br", # 7
            "rear window tl", # 8
            "rear window tr", # 9
            "rear window br", # 10
            "rear window bl", # 11
            "rearview mirror r", # 12
            "rearview mirror l", # 13
            "bottom of license fr", # 14
            "bottom of license fl", # 15
            "bottom of license bl", # 16
            "bottom of license br", # 17
            "headlight fr inner bottom", # 18
            "headlight fr outer top", # 19
            "headlight fl inner bottom", # 20
            "headlight fl outer top", # 21
            "headlight bl inner bottom", # 22
            "headlight bl outer top", # 23
            "headlight br inner bottom", # 24
            "headlight br outer top", # 25
            "bottom bumper fr", # 26
            "bottom bumper fl", # 27
            "bottom bumper bl", # 28
            "bottom bumper br", # 29
            "side window back r", # 30
            "side window back l", # 31
        ]

        return labels
