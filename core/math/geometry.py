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


def plane_normal(plane_pts: np.ndarray) -> np.ndarray:
    # TODO: add description
    if len(plane_pts) < 3:
        raise ValueError("plane_pts must have at least three points")

    vec1 = plane_pts[0] - plane_pts[1]
    vec2 = plane_pts[0] - plane_pts[2]
    normal_vec = np.cross(vec1, vec2)
    normal_norm = np.linalg.norm(normal_vec)

    return normal_vec / normal_norm


def vectors_angle(vec1: np.ndarray, vec2: np.ndarray) -> float:
    # TODO: add description
    return np.arccos(np.dot(vec1, vec2) / (np.linalg.norm(vec1) * np.linalg.norm(vec2)))
