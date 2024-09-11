import signal
import argparse
from simulation.simulator.simulator import Simulator
from simulation.simulator.configurator import Configurator
from gui.matplot.drawer import Drawer
from gui.matplot.drawers.route import RouteDrawer
from gui.matplot.drawers.car import CarSkeletonDrawer
from gui.matplot.drawers.planegrid import PlaneGrid

from calibration.pnp.optimization.reproj import ReprojSolver
from glob import glob
from core.objects.carskeleton3d import CarSkeleton3d, LABELS

from core.camera.camera import Camera

def signal_handler(sig, frame):
    global interrupted
    interrupted = True


def str2bool(s):
    return s.lower() in ('true', '1')


def on_keyboard_press(event):
    global interrupted
    if event.key == 'q':
        interrupted = True


def run_simulator(config_path: str,
                  time_start: float,
                  time_finish: float,
                  time_step: float,
                  autoplay: bool = True):
    global interrupted
    interrupted = False

    # create simulator
    simulator = Simulator()
    configurator = Configurator(simulator)
    configurator.configurate(config_path)

    # create gui
    drawer = Drawer(on_keyboard_press=on_keyboard_press, plt_cols=2)
    drawer2 = Drawer(on_keyboard_press=on_keyboard_press, plt_cols=2)

    # create solver
    car_models = []
    for model_file in sorted(glob("data/car_models/*.json")):
        car = CarSkeleton3d()
        car.load_from_file(model_file, LABELS)
        car_models.append(car)
    bounds = [(-10.0, 0.0), (-30.0, 0.0), (-10.0, 10.0), (1.0, 120.0), (0.0, 360.0), (0, len(car_models) - 1)]

    # main loop
    time_current = time_start
    reverse_time = time_finish < time_start

    static_drawables = [] # [PlaneGrid((-5, 5), (-20, 70))]
    for route in simulator.get_routes():
        static_drawables.append(RouteDrawer(route))

    while not interrupted and time_current < time_finish:
        # print(f"Update simulation at {time_current:.2f}s.")
        simulator.update(time_current)
        time_current += (-1 if reverse_time else 1) * time_step

        # calibrate
        camera = list(simulator.get_cameras().values())[0]
        # camera_res = None
        cars_2d = []
        for car in simulator.get_cars():
            car2d = car.get_projection(camera, only_visible_nodes=True)
            cars_2d.append(car2d)
        if len(cars_2d) == 2:
            solver = ReprojSolver(camera.img_w, camera.img_h, bounds, car_models)
            results = solver.solve(cars_2d)
            # print('results: ')
            print("cam_ty: {:.2f}\tcam_rx: {:.2f}\tcam_rz: {:.2f}\tcam_fx: {:.2f}".format(*results[:4]))

            # camera_res = Camera(aov_h=results[3],
            #                     img_size=(camera.img_w, camera.img_h),
            #                     pose=(camera.pose[0], results[0], camera.pose[2]),
            #                     eulers=(results[1], camera.eulers[1], results[2]))

        # draw
        # dynamic_drawables = []
        # for car in simulator.get_cars():
        #     dynamic_drawables.append(CarSkeletonDrawer(car))
        # cameras = simulator.get_cameras()
        # drawer.draw(cameras, static_drawables + dynamic_drawables, autoplay)

        # if camera_res is not None:
        #     drawer2.draw({'res_cam': camera_res}, static_drawables + dynamic_drawables, autoplay)

    print(f"Simulation finished.")


if __name__ == "__main__":
    # parse args
    parser = argparse.ArgumentParser(description='Traffic Scene Simulator')
    parser.add_argument("-c", "--config-file", dest="config_file", type=str, default="config/simulation/sim_1.json",
                        help="Path to config file")
    parser.add_argument("-a", "--autoplay", dest="autoplay", type=str2bool, default='True',
                        help="Wheter to autoplay or by key press")
    parser.add_argument("-ts", "--time-start", dest="time_start", type=float, default=0.0,
                        help="Simulation start timestamp")
    parser.add_argument("-tf", "--time-finish", dest="time_finish", type=float, default=100.0,
                        help="Simulation finish timestamp")
    parser.add_argument("-dt", "--time-step", dest="time_step", type=float, default=0.2,
                        help="Simulation time step")
    args = parser.parse_args()

    # run
    signal.signal(signal.SIGINT, signal_handler)
    run_simulator(args.config_file,
                  args.time_start,
                  args.time_finish,
                  args.time_step,
                  args.autoplay)
