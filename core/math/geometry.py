import numpy as np
from typing import Optional
from numpy.typing import ArrayLike


def _check_value(val: ArrayLike, size: int = 3):
    val = np.asarray(val, dtype=np.float32)
    if val.size != size:
        raise ValueError(f"The value must have the size = {size}")

    return val


def line_plane_intersection(plane_norm: ArrayLike,
                            plane_pt: ArrayLike,
                            line_pt1: ArrayLike,
                            line_pt2: ArrayLike) -> Optional[np.ndarray]:
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
    plane_norm = _check_value(plane_norm)
    line_pt1 = _check_value(line_pt1)
    line_pt2 = _check_value(line_pt2)

    line_vec = line_pt1 - line_pt2
    line_vec /= np.linalg.norm(line_vec)
    dot_prod = np.dot(line_vec, plane_norm)

    if dot_prod == 0:
        return None

    t = np.sum((_check_value(plane_pt) - line_pt1) * plane_norm) / dot_prod
    result = line_pt1 + t * line_vec

    return result


def plane_normal(plane_pts: ArrayLike) -> np.ndarray:
    plane_pts = _check_value(plane_pts, size=3 * len(plane_pts))

    vec1 = plane_pts[0] - plane_pts[1]
    vec2 = plane_pts[0] - plane_pts[2]
    normal_vec = np.cross(vec1, vec2)
    normal_norm = np.linalg.norm(normal_vec)

    return normal_vec / normal_norm


def vectors_angle(vec1: ArrayLike, vec2: ArrayLike) -> float:
    vec1 = _check_value(vec1)
    vec2 = _check_value(vec2)

    return np.arccos(np.dot(vec1, vec2) / (np.linalg.norm(vec1) * np.linalg.norm(vec2)))
