import logging
import sys


def setup_logger(logfile_name: str = "mqttcobot.log"):
    logger = logging.getLogger("logger")
    logger.setLevel(logging.INFO)

    console_handler = logging.StreamHandler(sys.stdout)
    file_handler = logging.FileHandler(logfile_name)

    formatter = logging.Formatter("[%(levelname)s - %(asctime)s]: %(message)s")
    console_handler.setFormatter(formatter)
    file_handler.setFormatter(formatter)

    if not logger.hasHandlers():
        logger.addHandler(console_handler)
        logger.addHandler(file_handler)
    logger.propagate = False
    return logger
