import os
import glob
import unittest
import pandas as pd
from src.common_utils.utils import produce_csv
from src.src_context import data_dir, config_dir
from config.config_file import config_data




class TestReaders(unittest.TestCase):
    def setUp(self):
        self.env = "local"
        self.config_data = config_data[self.env]
        self.input_path = os.path.join(data_dir, self.config_data['asia_asset']['input'])
        self.output_dir = os.path.join(data_dir,"output")

    @produce_csv
    def test_abc_module(self):
        pass