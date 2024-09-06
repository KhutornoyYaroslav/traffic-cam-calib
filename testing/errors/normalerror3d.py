import numpy as np


class NormalError3d():
    def __init__(self,
                 x_mean: float = 0., x_std: float = 0.,
                 y_mean: float = 0., y_std: float = 0.,
                 z_mean: float = 0., z_std: float = 0.):
        self.x_mean = x_mean
        self.x_std = x_std
        self.y_mean = y_mean
        self.y_std = y_std
        self.z_mean = z_mean
        self.z_std = z_std

    def rand(self) -> np.ndarray:
        x = np.random.normal(self.x_mean, self.x_std, 1)
        y = np.random.normal(self.y_mean, self.y_std, 1)
        z = np.random.normal(self.z_mean, self.z_std, 1)

        return np.concatenate([x, y, z], 0)
    
    def from_json(self, data: dict):
        self.x_mean = data.get("x_mean", self.x_mean)
        self.x_std = data.get("x_std", self.x_std)
        self.y_mean = data.get("y_mean", self.y_mean)
        self.y_std = data.get("y_std", self.y_std)
        self.z_mean = data.get("z_mean", self.z_mean)
        self.z_std = data.get("z_std", self.z_std)

        return self