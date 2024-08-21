import numpy as np
from engine.common.transformable import Transformable

tr = Transformable()
tr.pose = (0.0, 1.0, 10.0)
print(tr.pose)
tr.translate(y=-1.0)
print(tr.pose)

