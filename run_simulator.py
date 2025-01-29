import signal
import argparse
from tqdm import tqdm
from simulation.simulator import Simulator, Configurator
from gui.matplot.drawer import Drawer
from gui.matplot.drawers import RouteDrawer, KeypointsDrawer
from simulation.dumper.writer import DumpWriter


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
                  total_cars: int,
                  time_step: float,
                  autoplay: bool = True,
                  draw_mode: bool = True) -> bool:
    global interrupted
    interrupted = False

    # create simulator
    simulator = Simulator()
    configurator = Configurator(simulator)
    configurator.configurate(config_path)

    # create gui/dumper
    if draw_mode:
        drawer = Drawer(on_keyboard_press=on_keyboard_press, plt_cols=2)
        static_drawables = []
        for route in simulator.get_routes():
            static_drawables.append(RouteDrawer(route))
    else:
        dumper = DumpWriter()
        dumper.init(output_root="/home/yaroslav/repos/traffic-cam-calib/data/dumps/sim5")
        dumper.copy_config(config_path)

    # main loop
    print(f"Simulation progress (cars: current/total)")
    pbar = tqdm(total=int(total_cars))

    cur_cars = 0
    frame_cnt = 0
    time_current = 0.0   

    while not interrupted and cur_cars < total_cars:
        # update scene
        simulator.update(time_current)
        time_current += time_step

        # get objects
        camera = simulator.get_camera()
        cars = simulator.get_projected_cars(camera, only_visible_nodes=True)

        car_model_names = [c[0].get_model_name() for c in cars]
        car_keypoints = [c[1] for c in cars]
        car_brects = [c[2] for c in cars]
        car_masks = [c[3] for c in cars]

        # draw/dump
        if draw_mode:
            dynamic_drawables = []
            for keypoints in car_keypoints:
                dynamic_drawables.append(KeypointsDrawer(keypoints))
            drawer.draw({"": camera}, static_drawables + dynamic_drawables, autoplay)
        else:
            dumper.write_frame_data(frame_idx=frame_cnt,
                                    frame_size=(camera.img_w, camera.img_h),
                                    car_keypoints=car_keypoints,
                                    car_brects=car_brects,
                                    car_masks=car_masks,
                                    car_model_names=car_model_names)

        # update counters
        frame_cnt += 1
        cur_cars += len(cars)
        pbar.update(len(cars))

    print(f"Simulation finished.")
    return True


def str2bool(s):
    return s.lower() in ('true', '1')


if __name__ == '__main__':
    # parse args
    parser = argparse.ArgumentParser(description='Traffic Scene Simulator')
    parser.add_argument("-c", "--config-file", dest="config_file", type=str, default="config/simulation/sim_test.json",
                        help="Path to config file")
    parser.add_argument("-a", "--autoplay", dest="autoplay", type=str2bool, default=1,
                        help="Wheter to autoplay or by key press")
    parser.add_argument("-d", "--draw-mode", dest="draw_mode", type=str2bool, default=1,
                        help="Wheter to draw scene or dump jsons")
    parser.add_argument("--total-cars", dest="total_cars", type=int, default=250,
                        help="Total number of cars to generate")
    parser.add_argument("--time-step", dest="time_step", type=float, default=0.05,
                        help="Time step (FPS of camera)")
    args = parser.parse_args()

    # run
    signal.signal(signal.SIGINT, signal_handler)
    run_simulator(args.config_file,
                  args.total_cars,
                  args.time_step,
                  args.autoplay,
                  args.draw_mode)
