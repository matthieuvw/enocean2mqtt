# -*- encoding: utf-8 -*-
import yaml
import logging
import logging.handlers
import argparse
from enocean2mqtt.communicator import Communicator

def init_logging(level=logging.DEBUG, log_file_path=None):

    formatter = logging.Formatter('%(asctime)s %(levelname)8s %(name)s - %(message)s')

    logger = logging.getLogger()
    logger.setLevel(level)

    stream_handler = logging.StreamHandler()
    stream_handler.setLevel(level)
    stream_handler.setFormatter(formatter)
    logger.addHandler(stream_handler)

    if log_file_path:
        file_handler = logging.handlers.TimedRotatingFileHandler(log_file_path, when="midnight", interval=1)
        file_handler.suffix = "%Y%m%d"
        file_handler.setLevel(level)
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)

def launch():

    parser = argparse.ArgumentParser()
    parser.add_argument('-c', '--config', help='Config file path', dest='config_file_path', required=True)
    parser.add_argument("-v", "--verbose", help="increase output verbosity", action="store_true")
    parser.add_argument("--log-file", help="log file path", dest='log_file_path', required=False)
    args = parser.parse_args()

    level = logging.DEBUG if args.verbose else logging.INFO

    init_logging(level=level, log_file_path=args.log_file_path)

    with open(args.config_file_path, 'r') as yaml_file:
        config = yaml.safe_load(yaml_file)

    enocean_mqtt = Communicator(config)
    enocean_mqtt.start()

if __name__ == '__main__':
    launch()
