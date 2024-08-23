import numpy as np
from typing import Tuple


def eulers2rotmat(eulers: Tuple[float, float, float], order: str = 'YXZ', degrees: bool = False):
    """
    Creates rotation matrix from Euler anlges.

    Parameters:
        eulers : tuple
            Euler angles around X, Y, Z axes in radians.
        order : string
            The order of rotations to create matrix.
            Supported orders: 'XYZ', 'XZY', 'YXZ', 'YZX', 'ZXY', 'ZYX'.

    Returns:
        rot : array
            Rotation matrix with shape (3, 3).
    """
    if degrees:
        eulers = np.radians(eulers)

    st = np.sin(eulers)
    ct = np.cos(eulers)

    rx = np.array([[1, 0, 0], [0, ct[0], -st[0]], [0, st[0], ct[0]]])
    ry = np.array([[ct[1], 0, st[1]], [0, 1, 0], [-st[1], 0, ct[1]]])
    rz = np.array([[ct[2], -st[2], 0], [st[2], ct[2], 0], [0, 0, 1]])

    if order == 'XYZ':
        r = np.matmul(rx, np.matmul(ry, rz))
    elif order == 'XZY':
        r = np.matmul(rx, np.matmul(rz, ry))
    elif order == 'YXZ':
        r = np.matmul(ry, np.matmul(rx, rz))
    elif order == 'YZX':
        r = np.matmul(ry, np.matmul(rz, rx))
    elif order == 'ZXY':
        r = np.matmul(rz, np.matmul(rx, ry))
    elif order == 'ZYX':
        r = np.matmul(rz, np.matmul(ry, rx))
    else:
        raise ValueError(f"Wrong order parameter: '{order}'.")

    return r


def heading_to_eulers(heading: np.ndarray, degrees: bool = False) -> np.ndarray:
    result = np.zeros(3, np.float32)
    heading = heading / np.linalg.norm(heading)
    result[0] = -np.arcsin(heading[1])
    result[1] = np.arctan2(heading[0], heading[2])
    if degrees:
        result = np.degrees(result)

    return result
