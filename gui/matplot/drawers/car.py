import cv2 as cv
import numpy as np
from core.objects import CarSkeleton3d
from core.objects.carskeleton3d import LABELS
from gui.matplot.common.drawable import Drawable, Axes, Camera


class CarSkeletonDrawer(Drawable):
    def __init__(self, car_skeleton: CarSkeleton3d):
        self._car_skeleton = car_skeleton
        self._color = (1.0, 0.5, 0.5)

    def draw(self, canvas: Axes, camera: Camera):
        # draw edges
        for idx1, idx2 in self._car_skeleton.edges:
            res = camera.project_line(self._car_skeleton.world_node(LABELS[idx1]), self._car_skeleton.world_node(LABELS[idx2]))
            if res is not None:
                res = np.stack(res, 0)
                canvas.plot(res[:, 0], res[:, 1], color=self._color, lw=1, alpha=0.5)

        # # draw visible nodes
        # nodes_2d = self._car_skeleton.get_projection(camera, only_visible_nodes=True)
        # for point2d in nodes_2d.values():
        #     canvas.plot(point2d[0], point2d[1], 'o', color=(0.7, 0, 0), markersize=2)

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
