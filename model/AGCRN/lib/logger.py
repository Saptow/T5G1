import os
import logging
from datetime import datetime

def get_logger(root, name=None, debug=True, args=None):
    logger = logging.getLogger(name)
    logger.setLevel(logging.DEBUG)

    # Prevent duplicate handlers in recursive or repeated runs
    if logger.hasHandlers():
        logger.handlers.clear()

    formatter = logging.Formatter('%(asctime)s: %(message)s', "%Y-%m-%d %H:%M")
    console_handler = logging.StreamHandler()
    console_handler.setFormatter(formatter)

    if debug:
        console_handler.setLevel(logging.DEBUG)
        logger.addHandler(console_handler)
    else:
        console_handler.setLevel(logging.INFO)
        logger.addHandler(console_handler)

        logfile = os.path.join(root, 'run.log')
        print('Create Log File in: ', logfile)
        file_handler = logging.FileHandler(logfile, mode='w')
        file_handler.setLevel(logging.DEBUG)
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)

    return logger