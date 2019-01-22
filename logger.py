import logging
import os


def setupLogger(name):
    logLocation = "logs"
    if not os.path.isdir(logLocation):
        os.mkdir(logLocation)
    logPath = os.path.join(logLocation, "{}.txt".format(name))

    formatter = logging.Formatter(fmt='%(asctime)s - %(levelname)s - %(module)s - %(message)s')

    logging.basicConfig(level=logging.INFO)
    logger = logging.getLogger(name)
    handler = logging.FileHandler(logPath)
    handler.setLevel(logging.INFO)
    handler.setFormatter(formatter)
    logger.addHandler(handler)


    return logger





