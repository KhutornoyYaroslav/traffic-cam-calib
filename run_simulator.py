import signal
import argparse
from simulation.simulator import Simulator
from simulation.configurator import Configurator


def signal_handler(sig, frame):
    global simulator
    simulator.interrupt()


def str2bool(s):
    return s.lower() in ('true', '1')


def run_simulator(config_path: str, autoplay: bool = True):
    global simulator
    simulator = Simulator()
    configurator = Configurator(simulator)
    configurator.configurate(config_path)
    signal.signal(signal.SIGINT, signal_handler)
    simulator.run(autoplay)


if __name__ == "__main__":
    # parse args
    parser = argparse.ArgumentParser(description='Traffic Scene Simulator')
    parser.add_argument("-c", "--config-file", dest="config_file", type=str, default="config/simulation/sim_1.json",
                        help="Path to config file")
    parser.add_argument("-a", "--autoplay", dest="autoplay", type=str2bool, default='True',
                        help="Wheter to autoplay or by key press")
    args = parser.parse_args()

    # run
    run_simulator(args.config_file, args.autoplay)
