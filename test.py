import numpy as np
from core.math.common import line_plane_intersection


def main():
    plane_norm = np.array([0.0, 1.0, 0.0])
    plane_pt = np.array([0.0, 0.0, 0.0])

    line_pt1 = np.array([0.0, 10.0, 0.0])
    line_pt2 = np.array([0.0, 1.0, 0.0])

    interset_pt = line_plane_intersection(plane_norm, plane_pt, line_pt1, line_pt2)
    print(interset_pt)


if __name__ == "__main__":
    main()