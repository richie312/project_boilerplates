import os
import glob
import shutil
import sys


import pandas as pd

from src.common_utils.general import dneclear, grid_search, append_all
from src.common_utils.readers import Reader
from src.model.insight_analysis import (
    lineage_insights,
    lineage_analysis,
    grid_insights,
    bumapper,
    workload_analysis,
)
from src.model.insight_analysis import bom_usage, artifact_90, workload_insights
from src.src_context import data_dir

# from src.merge.merge_username import Merge
from src.common_utils.loggers import logger
from src.common_utils.general import get_event_and_logs
from src.common_utils.general import lsf_sas

# from src.common_utils.aws_services import upload_to_aws


class Pipeline:
    """
    Pipeline class takes the input from main script and run the pipeline
    for different environment like local, dev, qa and production.

    This instance initialises with spark context,params(config_data) &
    environment mode.
    """

    def __init__(self, params, config):
        self.config_data = config
        self.env = params["env"]
        self.storage = params["storage"]
        self.InOutMap = params["InOutMap"]
        self.input_path = os.path.join(
            data_dir, self.config_data["asia_asset"]["input"]
        )
        self.output_path = os.path.join(
            data_dir, self.config_data["asia_asset"]["output_path"]
        )
        self.file_adapter = Reader(self.input_path, self.config_data)

    def run(self):
        # load the environment config

        Error_Path = os.path.join(
            self.input_path, self.config_data["asia_asset"]["Error_Path"]
        )
        path_map = os.path.join(
            self.input_path, self.config_data["asia_asset"]["path_map"]
        )
        sas_usage_file = self.config_data["asia_asset"]["sas_usage_file"]
        bucket = self.config_data["aws_services"]["s3_bucket"]
        logger.info("Config Information loaded.")

        #   Initiating the Reader Instance
        lsf_output, sas_bus_unit = self.meta_retriver()
        final_output = self.sas_parser(lsf_output)
        self.analyzer(final_output, sas_bus_unit)

    def meta_retriver(self):

        all_files = []
        lsf_output = pd.DataFrame()
        batch_no = 0
        number_of_files = 0
        batch_size = 100
        # Collect Events file from log folder location or .event files
        if type(self.config_data["asia_asset"]["log_location"]) == list:
            for path in self.config_data["asia_asset"]["log_location"]:
                path_loc = os.path.dirname(path)
                temp_files = Reader.log_dir_reader(path_loc)
                all_files.extend(temp_files)
            # event_files,log_files = get_event_and_logs(all_files)
            logger.info(
                "Collecting event files for {env} environment.".format(env=self.env)
            )
        elif type(self.config_data["asia_asset"]["log_location"]) == str:
            all_files = glob.glob(
                os.path.join(
                    self.input_path, self.config_data["asia_asset"]["log_location"]
                )
            )
            # event_files,log_files = get_event_and_logs(all_files)
            logger.info(
                "Collecting event files for {env} environment.".format(env=self.env)
            )
        logger.info("Total no of files {0}".format(len(all_files)))
        # logger.info("Running lsf reader for {env} environment".format(env=self.env))
        while number_of_files < len(all_files):
            event_files, log_files = get_event_and_logs(
                all_files[number_of_files : number_of_files + batch_size]
            )
            if event_files is not None:
                lsf_output_event = self.file_adapter.lsf_reader(event_files)
            else:
                lsf_output_event = pd.DataFrame()
            if log_files is not None:
                lsf_output_log = self.file_adapter.log_reader(log_files)
            else:
                lsf_output_log = pd.DataFrame()
            lsf_output = pd.concat([lsf_output, lsf_output_log, lsf_output_event])
            number_of_files += batch_size
            batch_no += 1
            logger.info("metaretriver batch number is {0}".format(batch_no))
        lsf_output = pd.concat(
            [
                lsf_output,
                lsf_sas(lsf_output, self.config_data["asia_asset"]["code_location"]),
            ]
        )
        logger.info(
            "Running adsreader reader for {env} environment".format(env=self.env)
        )
        sas_bus_unit = self.file_adapter.adsreader(lsf_output)
        return lsf_output, sas_bus_unit

    def sas_parser(self, lsf_output):
        # calling sas_reader
        batch_no = 0
        number_of_files = 0
        batch_size = 100
        final_output = pd.DataFrame()
        while number_of_files < lsf_output[lsf_output.columns[0]].count():
            # logger.info("Running sasreader reader for {env} environment".format(env=self.env))

            sas_output = self.file_adapter.sas_reader(
                lsf_output[number_of_files : number_of_files + batch_size],
                self.config_data,
            )
            # calling egp_reader
            # logger.info("Running egpreader reader for {env} environment".format(env=self.env))
            egp_output = self.file_adapter.egp_reader(
                lsf_output[number_of_files : number_of_files + batch_size],
                self.config_data,
            )
            # #calling sas_output
            # logger.info("Running union map operation for sas and egp output for {env} environment".format(env=self.env))
            final_output = pd.concat([final_output, sas_output, egp_output])
            number_of_files += batch_size
            batch_no += 1
            logger.info("sas parser batch number is {0}".format(batch_no))

        return final_output

    def analyzer(self, final_output, sas_bus_unit):
        # calling libname_reader
        batch_no = 0
        number_of_files = 0
        batch_size = 100
        ref_batch_size = 100
        while number_of_files < final_output[final_output.columns[0]].count():

            temp_final_output = final_output[
                number_of_files : number_of_files + ref_batch_size
            ]
            logger.info(
                "Running libname reader reader for {env} environment".format(
                    env=self.env
                )
            )
            libname_output, table_details = self.file_adapter.libname_reader(
                temp_final_output, self.InOutMap
            )
            # logger.info(len(libname_output))
            # #calling grid_search_output
            if libname_output is None or libname_output.empty:
                logger.info("no libname found in batch no {0}".format(batch_no))
                ref_batch_size += 5
                continue
            logger.info(
                "Running grid search for {env} environment".format(env=self.env)
            )
            grid_search_output = grid_search(temp_final_output)
            # #calling dne_output
            # logger.info("Running dne clear for {env} environment".format(env=self.env))
            # dne_output = dneclear(lsf_output)
            # #calling bumapper for sas output
            logger.info(
                "Running BU Mapper operation on sas_output for {env} environment".format(
                    env=self.env
                )
            )
            merge_output_bumapped = bumapper(
                self.input_path, temp_final_output, "merge_output", sas_bus_unit
            )
            # #calling bumapper for libname output
            logger.info(
                "Running BU Mapper operation on libname_output for {env} environment".format(
                    env=self.env
                )
            )
            libname_output_bumapped = bumapper(
                self.input_path, libname_output, "libname_output", sas_bus_unit
            )
            # #calling bumapper for grid output
            logger.info(
                "Running BU Mapper operation on grid_search_output for {env} environment".format(
                    env=self.env
                )
            )
            grid_output_bumapped = bumapper(
                self.input_path, grid_search_output, "distributed_grid", sas_bus_unit
            )
            logger.info(
                "Running workload insight for {env} environment".format(env=self.env)
            )
            workload = workload_insights(merge_output_bumapped)
            # #calling lineage_insights
            logger.info(
                "Running lineage insight for {env} environment".format(env=self.env)
            )
            lineage = lineage_insights(libname_output_bumapped)
            # #calling grid_insights
            logger.info(
                "Running grid insight for {env} environment".format(env=self.env)
            )
            grid = grid_insights(grid_output_bumapped)
            # #calling workload_analysis
            logger.info(
                "Running workload analysis for {env} environment".format(env=self.env)
            )
            workload_overview = workload_analysis(workload, grid, self.config_data)
            # #calling lineage_analysis
            logger.info(
                "Running lineage analysis for {env} environment".format(env=self.env)
            )
            lineage_overview = lineage_analysis(workload_overview, lineage)
            # #calling artifact_90
            logger.info(
                "Running artifact 90 for {env} environment".format(env=self.env)
            )
            workload_dnd, lineage_dnd = artifact_90(
                self.input_path, workload_overview, lineage_overview
            )
            # #calling bom_usage
            logger.info(
                "Generating BOM(Bill of material) Report for {env} environment".format(
                    env=self.env
                )
            )
            bom_usage_dnd, workload_dnd_usg, lineage_dnd_usg = bom_usage(
                workload_dnd, lineage_dnd, self.input_path
            )
            logger.info("All reports bom, lineage and workload generated.")
            ##################################################################

            # Converting final dataframes to csvs
            workload_dnd_usg = workload_dnd_usg.drop_duplicates()
            lineage_dnd_usg.drop_duplicates(inplace=True)
            logger.info(
                "Writing Workload Analysis Report for {env} environment".format(
                    env=self.env
                )
            )
            workload_dnd_usg.to_csv(
                self.output_path + "/workload_dnd_{0}.csv".format(batch_no), index=None
            )
            logger.info(
                "Writing Lineage Overview Report for {env} environment".format(
                    env=self.env
                )
            )
            lineage_dnd_usg.to_csv(
                self.output_path + "/lineage_dnd_{0}.csv".format(batch_no), index=None
            )
            logger.info(
                "Writing Bill Of Material usage Report for {env} environment".format(
                    env=self.env
                )
            )
            bom_usage_dnd.to_csv(
                self.output_path + "/bom_usage_dnd_{0}.csv".format(batch_no), index=None
            )
            logger.info(
                "Writing Table Detail Report for {env} environment".format(env=self.env)
            )
            table_details.to_csv(
                self.output_path + "/table_details_{0}.csv".format(batch_no), index=None
            )

            number_of_files += ref_batch_size
            batch_no += 1
            if ref_batch_size != batch_size:
                ref_batch_size = batch_size
            logger.info("analyzer batch number is {0}".format(batch_no))

        try:
            shutil.rmtree("temp")
            logger.info("Removing cache from temp dir,if exist!.")
        except FileNotFoundError:
            logger.info("There is no temp directory found. Exiting the system.")
        append_all(self.output_path)
