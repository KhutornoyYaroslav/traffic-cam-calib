import json
import numpy as np
from typing import List, Union
from engine.objects.skeleton3d import Skeleton3d
from simulation.drawing.drawable import Drawable, Axes, Camera
from engine.math.geometry import plane_normal, vectors_angle


# LABELS_NEW = [
#     "wheel_front_left", # 0
#     "wheel_back_left", # 1
#     "wheel_front_right", # 2
#     "wheel_back_right", # 3
#     "windshield_top_right", # 4
#     "windshield top_left", # 5
#     "windshield bottom_left", # 6
#     "windshield bottom_right", # 7
#     "rear_window_top_left", # 8
#     "rear_window_top_right", # 9
#     "rear_window_bottom_right", # 10
#     "rear_window_bottom_left", # 11
#     "rearview_mirror_right", # 12
#     "rearview_mirror_left", # 13
#     "license_front_right", # 14
#     "license_front_left", # 15
#     "license_back_left", # 16
#     "license_back_right", # 17
#     "lights_inner_front_right", # 18
#     "lights_outer_front_right", # 19
#     "lights_inner_front_left", # 20
#     "lights_outer_front_left", # 21
#     "lights_inner_back_left", # 22
#     "lights_outer_back_left", # 23
#     "lights_inner_back_right", # 24
#     "lights_outer_back_right", # 25
#     "bumper_front_right", # 26
#     "bumper_front_left", # 27
#     "bumper_back_left", # 28
#     "bumper_back_right", # 29
#     "side_window_back_right", # 30
#     "side_window_back_left", # 31
# ]


LABELS = [
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


EDGES = [
    # Face
    [14, 26], [14, 18],
    [15, 27], [15, 20],
    [14, 15],
    [26, 18], [26, 19], [18, 19],
    [27, 20], [27, 21], [20, 21],
    # Windshield
    [4, 5], [5, 6], [6, 7], [7, 4],
    # Face <-> Windshield
    [19, 7], [21, 6],
    # Back
    [16, 28], [16, 22],
    [17, 29], [17, 24],
    [16, 17],
    [28, 22], [28, 23], [22, 23],
    [29, 24], [29, 25], [24, 25],
    # Rear window
    [8, 9], [9, 10], [10, 11], [11, 8],
    # Back <-> Rear window
    [23, 11], [25, 10],
    # Face <-> Back (roof part)
    [4, 9], [5, 8],
    # Wheels
    [0, 1], [2, 3],
    # Front wheels <-> Face
    [0, 27], [0, 21],
    [2, 26], [2, 19],
    # Back wheels <-> Back
    [1, 28], [1, 23],
    [3, 29], [3, 25],
    # Left side windows
    [6, 31], [31, 11],
    # Right side windows
    [7, 30], [30, 10],
    # Left rearview mirror
    [6, 13], [5, 13],
    # Right rearview mirror
    [7, 12], [4, 12],
]


"""
Visibility faces are used to determine visibility of
certain node of skeleton with respect to camera position.
The order of points in faces is important due to plane
normal vector calculation, so the normal vector must be
outside from vehicle. It is also important to remember
about those faces that can change the order of points
depending on vehicle model. Don't use such faces.
"""
VISIBILITY_FACES = [
    [7, 6, 5, 4], # 0 [windshield corners]
    [11, 10, 9, 8], # 1 [rear window corners]
    [0, 1, 31], # 2 [left side plane 1]
    [0, 1, 6], # 3 [left side plane 2]
    [0, 1, 13], # 4 [left side plane 3]
    [13, 1, 31], # 5 [left side plane 4]
    [3, 2, 30], # 6 [right side plane 1]
    [3, 2, 7], # 7 [right side plane 2]
    [3, 2, 12], # 8 [right side plane 3]
    [30, 3, 12], # 9 [right side plane 4]
    [5, 6, 13], # 10 [left rear view from front]
    [12, 7, 4], # 11 [right rear view from front]
    [20, 15, 27], # 12 [front left lp-inlight-bumper]
    [27, 21, 20], # 13 [front left outlight-inlight-bumper]
    [26, 14, 18], # 14 [front right lp-inlight-bumper]
    [18, 19, 26], # 15 [front right outlight-inlight-bumper]
    [28, 22, 23], # 16 [back left outlight-inlight-bumper]
    [25, 24, 29], # 17 [back right outlight-inlight-bumper]
    [28, 29, 24, 22], # 18 [back left-right bumper-inligts]
    [26, 27, 20, 18], # 19 [front left-right bumper-inligts]
]


"""
The mapping between certain skeleton node
and face(s) to analyze its visibility.
"""
VISIBILITY_POINT_FACE_MAP = {
    0: [2, 3], # fl wheel
    1: [2, 3], # bl wheel
    2: [6, 7], # fr wheel
    3: [6, 7], # br wheel
    4: [0], # windshield tr
    5: [0], # windshield tl
    6: [0], # windshield bl
    7: [0], # windshield br
    8: [1], # rear window tl
    9: [1], # rear window tr
    10: [1], # rear window br
    11: [1], # rear window bl
    12: [8, 9, 11], # rearview mirror r
    13: [4, 5, 10], # rearview mirror l
    14: [19], # bottom of license fr
    15: [19], # bottom of license fl
    16: [18], # bottom of license bl
    17: [18], # bottom of license br
    18: [14], # headlight fr inner bottom
    19: [14, 15], # headlight fr outer top
    20: [12], # headlight fl inner bottom
    21: [12, 13], # headlight fl outer top
    22: [18], # headlight bl inner bottom
    23: [16], # headlight bl outer top
    24: [18], # headlight br inner bottom
    25: [17], # headlight br outer top
    26: [15], # bottom bumper fr
    27: [13], # bottom bumper fl
    28: [16], # bottom bumper bl
    29: [17], # bottom bumper br
    30: [6], # side window back r
    31: [2], # side window back l
}


class Vehicle(Skeleton3d, Drawable):
    def __init__(self, *args, **kwargs):
        super().__init__({}, EDGES, *args, **kwargs)
        # super(Drawable, self).__init__()

    def load_from_file(self, path: str, labels_filter: Union[List[str], None] = None):
        nodes = {}
        with open(path, 'r') as f:
            data = json.load(f)
            file_labels = data.get('pts', {})
            file_vertices = data.get('vertices', [])
            for file_label, file_vertex_idx in file_labels.items():
                if (labels_filter is not None) and (file_label not in labels_filter):
                    continue
                if file_vertex_idx >= 0 and file_vertex_idx < len(file_vertices):
                    nodes[file_label] = file_vertices[file_vertex_idx]
        self.nodes = nodes

    def get_visible_node_labels(self, camera: Camera, max_angle: float = 82.5) -> List[str]:
        result = []

        # find visible by faces normals
        for label, world_pt in self.world_nodes().items():
            label_idx = LABELS.index(label)
            if label_idx not in VISIBILITY_POINT_FACE_MAP:
                continue
            
            best_angle = 3.14
            for face_idx in VISIBILITY_POINT_FACE_MAP[label_idx]:
                face = VISIBILITY_FACES[face_idx]

                # calc face normal
                face_pts = []
                for pt_idx in face:
                    face_pts.append(self.world_node(LABELS[pt_idx]))
                face_pts = np.stack(face_pts, 0)
                face_normal = plane_normal(face_pts)

                # calc angle
                pt1 = world_pt
                pt2 = world_pt + face_normal
                normal_vec = pt2 - pt1
                camera_vec = camera.pose - pt1
                angle_to_cam = vectors_angle(camera_vec, normal_vec)

                if angle_to_cam < best_angle:
                    best_angle = angle_to_cam

            if best_angle < np.deg2rad(max_angle):
                result.append(label)

        return result

    def draw(self, canvas: Axes, camera: Camera):
        # color
        color = (1.0, 0.5, 0.5)

        # draw edges
        for idx1, idx2 in self._edges:
            res = camera.project_line(self.world_node(LABELS[idx1]), self.world_node(LABELS[idx2]))
            if res is not None:
                res = np.stack(res, 0)
                canvas.plot(res[:, 0], res[:, 1], color=color, lw=1, alpha=0.5)

        # # draw centroid
        # pts = np.expand_dims(self.world_centroid(), 0)
        # points2d = camera.project_points(pts)
        # if points2d is not None:
        #     for point2d in points2d:
        #         canvas.plot(point2d[0], point2d[1], '+', color=color, markersize=5)

        # # draw nodes
        # for idx, (label, point3d) in enumerate(self.world_nodes().items()):
        #     point2d = camera.project_points([point3d])
        #     if point2d is not None:
        #         point2d = point2d[0]
        #         canvas.plot(point2d[0], point2d[1], 'o', color=color, markersize=1)
        #         canvas.annotate(f"{idx:d}", xy=point2d, xytext=point2d, alpha=0.5)

        # draw visible nodes
        visible_labels = self.get_visible_node_labels(camera, max_angle=80.0)
        if len(visible_labels):
            visible_points = []
            for label in visible_labels:
                visible_points.append(self.world_node(label))
            visible_points = np.stack(visible_points, 0)

            points2d = camera.project_points(visible_points)
            if points2d is not None:
                for point2d in points2d:
                    canvas.plot(point2d[0], point2d[1], 'o', color=(0.7, 0, 0), markersize=2)
