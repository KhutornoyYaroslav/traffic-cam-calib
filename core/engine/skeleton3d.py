import numpy as np


class Skeleton3d():
    """
    Skeleton3d represents an object in 3d space as a set of nodes and edges.

    Parameters:
        nodes : array
            XYZ coordinates of skeleton nodes with shape (N, 3).
    """
    def __init__(self,
                 nodes: np.ndarray,
                 edges: np.ndarray,
                 pose: np.ndarray = np.zeros(3, dtype=np.float32),
                 eulers: np.ndarray = np.zeros(3, dtype=np.float32)):
        self.nodes = nodes
        self.edges = edges
        self.pose = pose
        self.eulers = eulers

    def centroid(self) -> np.ndarray:
       return np.mean(self.nodes, axis=0)
    
    def set_pose(self, x: float = 0.0, y: float = 0.0, z: float = 0.0):
        self.pose = np.array([x, y, z], dtype=np.float32)

    def translate(self, x: float = 0.0, y: float = 0.0, z: float = 0.0):
        self.pose += np.array([x, y, z], dtype=np.float32)

    def set_eulers(self, x: float = 0.0, y: float = 0.0, z: float = 0.0):
        self.eulers = np.array([x, y, z], dtype=np.float32) 
        self.eulers %= 360.0

    def rotate(self, x: float = 0.0, y: float = 0.0, z: float = 0.0):
        self.eulers += np.array([x, y, z], dtype=np.float32) 
        self.eulers %= 360.0
