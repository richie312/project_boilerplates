import argparse
from src.common_utils.loggers import logger
from config.config_file import config_data



def main():
    # Read the arguments
    parser = argparse.ArgumentParser()
    parser.add_argument("--env", help="environment name; local, dev, qa and prod.", default="local", required=False)
    args = parser.parse_args()
    params = {"env":args.env}
    # Run Pipeline
    logger.info("Running the pipeline for {} environment".format(args.env))
    Pipeline(params,config).run()
    logger.info("Pipeline run is completed.")

if __name__ == "__main__":
    main()
