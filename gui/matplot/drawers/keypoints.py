import numpy as np
from typing import Dict
from numpy.typing import ArrayLike
from core.objects.carskeleton3d import LABELS, EDGES
from gui.matplot.common.drawable import Drawable, Axes, Camera


class KeypointsDrawer(Drawable):
    def __init__(self, keypoints: Dict[str, ArrayLike]):
        self._keypoints = keypoints
        self._color = (1.0, 0.5, 0.5)

    def draw(self, canvas: Axes, camera: Camera):
        # draw edges
        for idx1, idx2 in EDGES:
            if (LABELS[idx1] in self._keypoints) and (LABELS[idx2] in self._keypoints):
                line = np.stack([self._keypoints[LABELS[idx1]], self._keypoints[LABELS[idx2]]], 0)
                canvas.plot(line[:, 0], line[:, 1], color=self._color, lw=1, alpha=0.5)

        # draw nodes
        points2d = list(self._keypoints.values())
        if len(points2d):
            points2d = np.stack(points2d, 0)
            canvas.plot(points2d[:, 0], points2d[:, 1], 'o', color=self._color, markersize=1)
