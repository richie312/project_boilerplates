# Import python libraries for code execution:
import os
from src.src_context import data_dir
from src.common_utils.loggers import logger


def produce_csv(func):
    def inner1(*args, **kwargs):
        # Initialize the directory
        if not os.path.exists(os.path.join(data_dir, "output")):
            os.makedirs(os.path.join(data_dir, "output"))
        logger.info("Created the output directory.")
        output_path = os.path.join(data_dir, "output")
        # getting the returned value
        df, filename = func(*args, **kwargs)
        df.to_csv(os.path.join(output_path, filename))

    return inner1
