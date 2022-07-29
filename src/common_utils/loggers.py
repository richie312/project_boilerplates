import logging, os
from logging.handlers import RotatingFileHandler

project_name = ""
# create logger
logger = logging.getLogger(project_name)
logger.setLevel(logging.DEBUG)

# create console handler and set level to debug
ch = logging.StreamHandler()
ch.setLevel(logging.DEBUG)
handler = RotatingFileHandler(project_name + ".log", maxBytes=10000000, backupCount=100)
logger.addHandler(handler)
# create formatter
formatter = logging.basicConfig(
    handlers=[handler],
    level=logging.DEBUG,
    format="[%(asctime)s] %(levelname)s [%(name)s.%(funcName)s:%(lineno)d] %(message)s",
    datefmt="%Y-%m-%dT%H:%M:%S",
)
# add formatter to ch
ch.setFormatter(formatter)
# add ch to logger
logger.addHandler(ch)
