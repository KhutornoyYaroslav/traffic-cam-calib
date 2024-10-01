import os
import json
import numpy as np
from glob import glob
import matplotlib.pyplot as plt
from matplotlib.axes import Axes
from scipy import stats
from numpy.typing import ArrayLike
from typing import Dict, List


FONT = {'family': 'serif',
        'color':  'darkred',
        'weight': 'normal',
        'size': 10,
        }


def plot_hist(ax: Axes, x: ArrayLike, weights: ArrayLike, title: str = "", hist_bins: int = 64, kde_samples: int = 1024):
    # ax.set_title(title)
    ax.hist(x, bins=hist_bins, density=True,  color=(1.0, 0.0, 0.0), alpha=0.2)
    
    # if not np.isclose(np.sum(x), 0.0, 1e-3):
    if True:
        xs = np.linspace(np.min(x), np.max(x), kde_samples)
        if not len(weights):
            weights = None
        kde = stats.gaussian_kde(x, bw_method='scott', weights=weights)
        ys = kde.pdf(xs)
        kde_xy = np.stack([xs, ys], 1)
        ax.plot(kde_xy[:, 0], kde_xy[:, 1], color=(1.0, 0.4, 0.4), lw=1)

        x_best = np.min(x) + (np.argmax(ys) / 1024) * (np.max(x) - np.min(x))
        ax.vlines([x_best], [0.0], [np.max(ys)], colors=[(1.0, 0.4, 0.4)], lw=1, linestyles='dashed')
        # ax.set_xticks(ax.get_xticks() + [x_best])

        ax.set_title(title + f" = {x_best:.2f}", fontdict=FONT)


def plot_scalars(scalars: Dict[str, ArrayLike], weights: ArrayLike, name_filter = [], plot_size: int = 8):
    scalars_names = list(scalars.keys())
    names_to_plot = [n for n in name_filter if n in scalars_names]
    if not len(names_to_plot):
        names_to_plot = scalars_names
 
    plot_num = len(names_to_plot)
    plot_cols = int(plot_num**0.5)
    plot_rows = int(np.ceil(plot_num / plot_cols))

    fig, axes = plt.subplots(nrows=plot_rows, ncols=plot_cols, figsize=(plot_size, plot_size))
    plt.tight_layout(pad=2.0)

    for plot_id, name in enumerate(names_to_plot):
        ax = axes.flatten()[plot_id] if isinstance(axes, np.ndarray) else axes
        plot_hist(ax, scalars[name], weights, name)
    plt.show()


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


def parse_scalar_results(result_data: List[dict]) -> Dict[str, list]:
    results = {}

    for data in result_data:
        for name, value in data.get("result", {}).items():
            if name in results:
                results[name].append(value)
            else:
                results[name] = [value]

    return results


def eval_model_matching(dump_data: List[dict], result_data: List[dict], dist_thresh: float = 0.5) -> float:
    result_data_sorted = sorted(result_data, key=lambda item: item["frameid"])
    dump_data_sorted = sorted(dump_data, key=lambda item: item["id"])

    matches = []
    for dump_frame in dump_data_sorted:
        frame_idx = dump_frame["id"]

        for result_frame in result_data_sorted:
            if frame_idx != result_frame["frameid"]:
                continue

            car = result_frame.get("car", {})
            points2d = [kp["point"] for kp in car.get("keypoints", [])]
            points2d = np.stack(points2d, 0)
            center2d = np.mean(points2d, 0)
            
            for dump_car in dump_frame.get("cars", []):
                dump_points2d = [kp["point"] for kp in dump_car.get("keypoints", [])]
                dump_points2d = np.stack(dump_points2d, 0)
                dump_center2d = np.mean(dump_points2d, 0)

                dist = np.linalg.norm(center2d - dump_center2d)
                if dist < dist_thresh:
                    matches.append(dump_car["model_name"] == result_frame["result"]["model_name"])

    if len(matches):
        return np.sum(matches) / len(matches)
    else:
        return 0.0


if __name__ == "__main__":
    dumps_root = "data/dumps/sim4/frames"
    results_file = "data/debug_results/sim4/sim4.json"
    result_data = read_result_data(results_file)
    dump_data = read_dump_data(dumps_root)

    models_match_score = eval_model_matching(dump_data, result_data)
    print(f"Models matching score: {np.round(100.0 * models_match_score).astype(np.int32)}%")

    scalars = parse_scalar_results(result_data)

    if 'yr' in scalars:
        scalars['yr'] = [s % 180.0 for s in scalars['yr']]

    if 'model' in scalars:
        scalars['model'] = [int(s) for s in scalars['model']]

    plot_scalars(scalars, weights=[], name_filter=['fovh', 'xr', 'k1', 'yr', 'h', 'zr'])
