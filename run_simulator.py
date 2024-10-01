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
                  time_start: float,
                  time_finish: float,
                  time_step: float,
                  autoplay: bool = True) -> bool:
    global interrupted
    interrupted = False

    # create simulator
    simulator = Simulator()
    configurator = Configurator(simulator)
    configurator.configurate(config_path)

    # create gui
    drawer = Drawer(on_keyboard_press=on_keyboard_press, plt_cols=2)

    # create dumper
    dumper = DumpWriter()
    dumper.init(output_root="/home/yaroslav/repos/traffic-cam-calib/data/dumps/sim4")
    dumper.copy_config(config_path)

    # main loop
    time_current = time_start
    reverse_time = time_finish < time_start

    static_drawables = []
    for route in simulator.get_routes():
        static_drawables.append(RouteDrawer(route))

    print(f"Simulation progress (frames: current/total)")
    pbar = tqdm(total=int((time_finish - time_current) / time_step))

    frame_cnt = 0
    while not interrupted and time_current < time_finish:
        # update scene
        simulator.update(time_current)
        time_current += (-1 if reverse_time else 1) * time_step

        # get objects
        camera = simulator.get_camera()
        cars = simulator.get_projected_cars(camera, only_visible_nodes=True)
        
        # dump
        car_model_names = [c[0].get_model_name() for c in cars]
        car_keypoints = [c[1] for c in cars]
        car_brects = [c[2] for c in cars]
        car_masks = [c[3] for c in cars]
        dumper.write_frame_data(frame_idx=frame_cnt,
                                frame_size=(camera.img_w, camera.img_h),
                                car_keypoints=car_keypoints,
                                car_brects=car_brects,
                                car_masks=car_masks,
                                car_model_names=car_model_names)

        # # draw
        # dynamic_drawables = []
        # for keypoints in car_keypoints:
        #     dynamic_drawables.append(KeypointsDrawer(keypoints))
        # drawer.draw({"": camera}, static_drawables + dynamic_drawables, autoplay)

        frame_cnt += 1
        pbar.update(1)

    print(f"Simulation finished.")
    return True


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
