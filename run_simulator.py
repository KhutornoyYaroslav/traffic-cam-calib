import signal
import argparse
from simulation.simulator.simulator import Simulator
from simulation.simulator.configurator import Configurator
from gui.matplot.drawer import Drawer
from gui.matplot.drawers.route import RouteDrawer
from gui.matplot.drawers.car import CarSkeletonDrawer
from gui.matplot.drawers.planegrid import PlaneGrid


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

    # main loop
    time_current = time_start
    reverse_time = time_finish < time_start

    static_drawables = [] # [PlaneGrid((-5, 5), (-20, 70))]
    for route in simulator.get_routes():
        static_drawables.append(RouteDrawer(route))

    while not interrupted and time_current < time_finish:
        print(f"Update simulation at {time_current:.2f}s.")
        simulator.update(time_current)
        time_current += (-1 if reverse_time else 1) * time_step

        # draw
        dynamic_drawables = []
        for car in simulator.get_cars():
            dynamic_drawables.append(CarSkeletonDrawer(car))
        cameras = simulator.get_cameras()
        drawer.draw(cameras, static_drawables + dynamic_drawables, autoplay)

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
    parser.add_argument("-dt", "--time-step", dest="time_step", type=float, default=0.05,
                        help="Simulation time step")
    args = parser.parse_args()

    # run
    signal.signal(signal.SIGINT, signal_handler)
    run_simulator(args.config_file,
                  args.time_start,
                  args.time_finish,
                  args.time_step,
                  args.autoplay)
