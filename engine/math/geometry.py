import numpy as np
from typing import Optional


def line_plane_intersection(plane_norm: np.ndarray,
                            plane_pt: np.ndarray,
                            line_pt1: np.ndarray,
                            line_pt2: np.ndarray) -> Optional[np.ndarray]:
    """
    Calculates XYZ coordinates of intersection point between line and plane.

    Parameters:
        plane_norm : array
            XYZ norm vector of plane.
        plane_pt : array
            XYZ point on plane.
        line_pt1 : array
            First XYZ line point.
        line_pt2 : array
            Second XYZ line point.      
        
    Returns:
        point : array | None
            XYZ intersection point or None if line is parallel to the plane.
    """
    line_vec = line_pt1 - line_pt2
    line_vec /= np.linalg.norm(line_vec)
    dot_prod = np.dot(line_vec, plane_norm)

    if dot_prod == 0:
        return None

    t = np.sum((plane_pt - line_pt1) * plane_norm) / dot_prod
    result = line_pt1 + t * line_vec

    return result
