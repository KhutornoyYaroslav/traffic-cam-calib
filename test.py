import numpy as np
from simulation.routing.route import Route


waypoints = [
    [0.0, 0.0, 0.0],
    [0.0, 1.0, 1.0],
    [0.0, 2.0, 2.0]
]
route = Route(waypoints)

wp = route.interpolate(2.8)
print(wp)