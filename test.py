import numpy as np
from simulation.scene.scene import Scene
from simulation.scene.reader import SceneReader


scene = Scene()
scene_reader = SceneReader(scene)
scene_reader.read("config/scene/scene_1.json")
