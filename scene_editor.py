import json
import argparse
import numpy as np
import matplotlib.pyplot as plt
from scipy.interpolate import interp1d


class SceneEditor:
    def __init__(self,
                 grid_rows: int,
                 grid_cols: int,
                 grid_step: float = 3.75,
                 num_nodes: int = 128):
        self.num_nodes = num_nodes
        self.default_speed = 10.0
        self.routes = [[]]
        self.routes_speeds = [self.default_speed]
        self.cur_route_idx = 0
        self.x_ticks = np.arange(0, grid_cols * grid_step, grid_step)
        self.y_ticks = np.arange(0, grid_rows * grid_step, grid_step)
        self.fig, self.ax = plt.subplots(nrows=1, ncols=1, figsize=(8, 8))
        self.fig.canvas.mpl_connect('button_press_event', self.on_button_press)
        self.fig.canvas.mpl_connect('key_press_event', self.on_keyboard_press)

    def run(self):
        self.clear_canvas()
        plt.show()

    def add_route_node(self, x: float, y: float):
        pts = self.routes[self.cur_route_idx]
        pts.append((x, y))

    def del_route_node(self, x: float, y: float, dist_thresh: float = 2.5):
        pts = self.routes[self.cur_route_idx]
        best_idx = None
        best_dist = 1e9
        for idx, pt in enumerate(pts):
            dist = np.linalg.norm([x - pt[0], y - pt[1]])
            if dist < best_dist:
                best_dist = dist
                best_idx = idx
        if (best_idx is not None) and (best_dist < dist_thresh):
            pts.pop(best_idx)

    def on_button_press(self, event):
        if (event.xdata is None) or (event.ydata is None):
            return
        if event.button == 1:
            self.add_route_node(event.xdata, event.ydata)
        if event.button == 3:
            self.del_route_node(event.xdata, event.ydata)
        self.redraw()

    def on_keyboard_press(self, event):
        # create new route
        if event.key == ' ':
            cur_route = self.routes[self.cur_route_idx]
            if len(cur_route):
                self.routes.append([])
                self.routes_speeds.append(self.default_speed)
                self.cur_route_idx = len(self.routes) - 1
        # to next route
        if event.key == '.':
            if self.cur_route_idx < len(self.routes) - 1:
                self.cur_route_idx += 1
        # to prev route
        if event.key == ',':
            if self.cur_route_idx > 0:
                self.cur_route_idx -= 1
        # increse route speed
        if event.key == '+':
            self.routes_speeds[self.cur_route_idx] += 0.5
        # decrease route speed
        if event.key == '-':
            self.routes_speeds[self.cur_route_idx] -= 0.5
        self.redraw()

    def redraw(self):
        self.clear_canvas()
        for route_idx, (route, speed) in enumerate(zip(self.routes, self.routes_speeds)):
            if len(route):
                pts = np.array(route)
                self.ax.plot(pts[:, 0], pts[:, 1], color='r', lw=1, alpha=0.5)
                self.ax.scatter(pts[:, 0], pts[:, 1], color='r', s=[2.0])
                try:
                    curve = self.interpolate_route(pts, self.num_nodes)
                    self.ax.plot(*curve.T, '-', label=f"route id: {route_idx}. speed: {speed:.2f} mps")
                    self.ax.legend(title='routes', loc='upper right')
                except:
                    pass
        self.ax.set_title(f"cur route idx: {self.cur_route_idx}. total routes: {len(self.routes)}")
        self.fig.canvas.draw_idle()

    def clear_canvas(self):
        self.ax.cla()
        self.ax.set_aspect('equal')
        self.ax.set_xlim(self.x_ticks[0], self.x_ticks[-1])
        self.ax.set_ylim(self.y_ticks[0], self.y_ticks[-1])
        self.ax.set_xticks(self.x_ticks, rotation=90)
        self.ax.set_yticks(self.y_ticks)
        self.ax.grid(True)
        plt.xticks(rotation=90)

    def interpolate_route(self, route: np.ndarray, num_points: int = 128):
        distance = np.cumsum(np.sqrt(np.sum(np.diff(route, axis=0)**2, axis=1)))
        distance = np.insert(distance, 0, 0) / distance[-1]
        alphas = np.linspace(0, 1, num_points)
        interpolator =  interp1d(distance, route, kind='cubic', axis=0)
        interpolated_points = interpolator(alphas)
        return interpolated_points

    def export(self, path: str, car_models_dir: str = ""):
        # prepare routes
        result_routes = []
        for route_idx, (route, speed) in enumerate(zip(self.routes, self.routes_speeds)):
            if not len(route):
                continue
            points = np.array(route)
            try:
                # prepare waypoints
                waypoints = self.interpolate_route(points, self.num_nodes)
                ys = np.zeros((len(waypoints), 1))
                waypoints = np.concatenate([waypoints, ys], -1)
                zs = np.copy(waypoints[:, 1])
                waypoints[:, 1] = waypoints[: ,2]
                waypoints[:, 2] = zs

                # prepare dts
                dts = []
                for i in range(0, len(waypoints) - 1):
                    dist = np.linalg.norm(waypoints[i] - waypoints[i + 1])
                    dts.append(dist / speed)

                # append to results
                result_routes.append({
                    "loop": True,
                    "waypoints": waypoints.tolist(),
                    "dts": dts
                })
            except:
                print(f"Failed to export route with id {route_idx}. Failed to interpolate route.")
                continue

        # prepare cars
        result_cars = []
        for idx in range(len(result_routes)):
            result_cars.append({
                "route_id": idx,
                "randomize_model": True
            })

        # write to file
        data = {
            "car_models_path": car_models_dir,
            "cars": result_cars,
            "routes": result_routes
            }
        with open(path, 'w') as f:
            json.dump(data, f, indent=4)


if __name__ == '__main__':
    # parse args
    parser = argparse.ArgumentParser(description='Traffic Scene Simulator')
    parser.add_argument("-o", "--output-path", dest="output_path", type=str, default="data/routes/route_test_2.json",
                        help="Path to output JSON file")
    parser.add_argument("--grid-rows", dest="grid_rows", type=int, default=30,
                        help="Number of grid rows")
    parser.add_argument("--grid-cols", dest="grid_cols", type=int, default=30,
                        help="Number of grid columns")
    parser.add_argument("--grid-step", dest="grid_step", type=float, default=3.75,
                        help="Size of grid cell")
    parser.add_argument("--num-nodes", dest="num_nodes", type=int, default=128,
                        help="Number of interpolation nodes")
    args = parser.parse_args()

    # run
    editor = SceneEditor(args.grid_rows,
                         args.grid_cols,
                         args.grid_step,
                         args.num_nodes)
    editor.run()
    editor.export(args.output_path, "data/car_models/")
