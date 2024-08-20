import numpy as np


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
        print("The intersection point is", inter_pt)

        return np.array(inter_pt)