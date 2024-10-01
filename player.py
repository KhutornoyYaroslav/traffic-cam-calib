import os
import json
import signal
import numpy as np
from glob import glob
import matplotlib.pyplot as plt
from matplotlib.axes import Axes
from numpy.typing import ArrayLike
from typing import Dict, List, Tuple

from core.camera import Camera
from core.objects import CarSkeleton3d
from simulation.dumper.writer import EXPORT_LABELS_ORDER
from gui.matplot.drawers import CarSkeletonDrawer


def signal_handler(sig, frame):
    global interrupted
    interrupted = True


def on_keyboard_press(event):
    global interrupted
    if event.key == 'q':
        interrupted = True


def read_result_data(filepath: str) -> List[dict]:
    data = []
    with open(filepath, "r") as f:
        for line in f.read().splitlines():
            data.append(json.loads(line))

    return data


def read_dump_data(rootdir: str, filename_template = "frame_*.json") -> List[dict]:
    data = []
    files = sorted(glob(os.path.join(rootdir, filename_template)))
    for file in files:
        with open(file, "r") as f:
            data.append(json.load(f))

    return data


def draw_frame(canvas: Axes,
               framesize: Tuple[int, int],
               result_frame_data: List[dict],
               car_models: List[str]):
    canvas.cla()
    canvas.set_xlim(0, framesize[0])
    canvas.set_ylim(0, framesize[1])
    canvas.invert_yaxis()
    canvas.set_aspect('equal')
    canvas.axis('off')

    for data in result_frame_data:
        car = data.get("car", {})
        result = data.get("result", {})
        points2d = car.get("keypoints", [])
        points2d = dict([(EXPORT_LABELS_ORDER[p["klass"]], p["point"]) for p in points2d])

        # create camera
        camera = Camera(aov_h=result["fovh"],
                        img_size=framesize,
                        pose=(0, -result["h"], 0),
                        eulers=(result['xr'], 0.0, result['zr']))

        car3d = CarSkeleton3d()
        car3d.load_from_file(car_models[int(result["model"])])
        car3d.rotate(y=result["yr"] - 180.0)
        
        # calc cars world position
        x_mean, z_mean = [], []
        for label, ref_point2d in points2d.items():
            ref_point3d = car3d.world_node(label)
            plane_norm = np.array([0, -1.0, 0])
            plane_orig = np.array([0, ref_point3d[1], 0])
            point3d = camera.unproject_point(ref_point2d, plane_norm, plane_orig)
            if point3d is None:
                continue
            xyz = point3d - ref_point3d
            x_mean.append(xyz[0])
            z_mean.append(xyz[2])
        if not len(x_mean):
            print("Failed to find car x, z coordinates")

        x_mean = np.mean(x_mean)
        z_mean = np.mean(z_mean)
        car3d.translate(x=x_mean, z=z_mean)

        car_drawer = CarSkeletonDrawer(car3d)
        car_drawer.draw(canvas, camera)


if __name__ == "__main__":
    global interrupted
    interrupted = False

    signal.signal(signal.SIGINT, signal_handler)

    results_file = "data/debug_results/sim4/sim4.json"
    dumps_files_dir = "data/dumps/sim4/frames"

    car_models = sorted(glob("data/car_models/*.json"))

    # read result data and sort by frame index
    result_data = read_result_data(results_file)
    result_data = sorted(result_data, key=lambda item: item["frameid"])

    # read dump data
    dump_data = read_dump_data(dumps_files_dir)
    dump_data = sorted(dump_data, key=lambda item: item["id"])

    # draw frame by frame
    fig, ax = plt.subplots(nrows=1, ncols=1, figsize=(8, 8))
    fig.canvas.mpl_connect('key_press_event', on_keyboard_press)

    max_frame_idx = result_data[-1]["frameid"]
    for frame_idx in range(max_frame_idx):
        if interrupted:
            break
        result_frame_data = []
        framesize = []
        for d in result_data:
            if d["frameid"] == frame_idx:
                result_frame_data.append(d)
                framesize = d["framesize"]

        # dump_frame_data = None
        # for d in dump_data:
        #     if d["id"] == frame_idx:
        #         dump_frame_data = d

        if not len(result_frame_data): # or dump_frame_data is None:
            continue

        print(frame_idx)
        draw_frame(ax, framesize, result_frame_data, car_models)
        fig.canvas.draw_idle()
        plt.waitforbuttonpress(0.01) # (0.01 if autoplay else 0)