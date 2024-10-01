import json
import cv2 as cv
import numpy as np
from numpy.typing import ArrayLike
from typing import List, Dict, Optional
from core.camera import Camera
from core.objects.skeleton3d import Skeleton3d
from core.math.geometry import plane_normal, vectors_angle


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


class CarSkeleton3d(Skeleton3d):
    def __init__(self, *args, **kwargs):
        super().__init__({}, EDGES, *args, **kwargs)
        self._model_name = None

    def load_from_file(self, path: str, labels_filter: Optional[List[str]] = None):
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
            self._model_name = data.get('name', None)
        self.nodes = nodes

    def get_model_name(self) -> Optional[str]:
        return self._model_name

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

    def get_projection(self,
                       camera: Camera,
                       only_visible_nodes: bool = False) -> Dict[str, np.ndarray]:
        result = {}

        if only_visible_nodes:
            labels = self.get_visible_node_labels(camera)
        else:
            labels = self._nodes.keys()

        for label in labels:
            pt_3d = self.world_node(label)
            pt_2d = camera.project_points([pt_3d])
            if pt_2d is not None:
                result[label] = pt_2d[0].astype(np.int)

        return result

    @staticmethod
    def get_brect_and_mask(keypoints: Dict[str, ArrayLike]):
        if not len(keypoints):
            return None, None

        # get brect
        pts = list(keypoints.values())
        pts = np.stack(pts, 0).astype(np.int32)
        brect = cv.boundingRect(pts)

        # get mask as convex hull
        conv_hull = cv.convexHull(pts)
        conv_hull -= brect[0:2]
        mask = np.zeros(shape=(brect[3], brect[2]), dtype=np.uint8)
        cv.drawContours(mask, [conv_hull], 0, color=(255), thickness=-1)

        return brect, mask  # [x, y, w, h], np.array(uint8)
