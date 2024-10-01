import numpy as np


class NormalError2d():
    def __init__(self,
                 x_mean: float = 0., x_std: float = 0.,
                 y_mean: float = 0., y_std: float = 0.):
        self.x_mean = x_mean
        self.x_std = x_std
        self.y_mean = y_mean
        self.y_std = y_std

    def rand(self) -> np.ndarray:
        x = np.random.normal(self.x_mean, self.x_std, 1)
        y = np.random.normal(self.y_mean, self.y_std, 1)

        return np.concatenate([x, y], 0)

    @staticmethod
    def from_json(data: dict):
        return NormalError2d(
            x_mean=data.get("x_mean", 0.),
            x_std=data.get("x_std", 0.),
            y_mean=data.get("y_mean", 0.),
            y_std=data.get("y_std", 0.)
        )
