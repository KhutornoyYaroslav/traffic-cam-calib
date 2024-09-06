import signal
import argparse
from testing.tester import Tester
from testing.configurator import Configurator


def signal_handler(sig, frame):
    global tester
    tester.interrupt()


def str2bool(s):
    return s.lower() in ('true', '1')


def run_tester(config_path: str):
    global tester
    tester = Tester()
    configurator = Configurator(tester)
    configurator.configurate(config_path)
    signal.signal(signal.SIGINT, signal_handler)
    tester.run()


if __name__ == "__main__":
    # parse args
    parser = argparse.ArgumentParser(description='Camera Calibration Testing')
    parser.add_argument("-c", "--config-file", dest="config_file", type=str, default="config/testing/test_1.json",
                        help="Path to config file")
    args = parser.parse_args()

    # run
    run_tester(args.config_file)
