#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Dec  3 08:30:12 2021

@author: a33272
"""
import os
import glob
import shutil
import numpy as np
import logging
import argparse
import configparser
import netCDF4 as nc
import readers.met_dfn_api_reader as met_dfn_api_reader
import exporters.ctd_level0_exporter as ctd_level0_exporter
import exporters.ctd_level1C_exporter as ctd_level1C_exporter
import rtqc.rtqc_tests as rtqc_tests
import utils.load_netcdf as load_netcdf
import utils.plot_utils as plotutils


cruise_id = '2021407'

# Load config file
config_path = '/home/a33272/Documents/python/nansen_pbgc_processing/config/'

config = configparser.ConfigParser()
config.read(config_path + 'config_' + cruise_id + 'met.ini')

data_in_path = '/test_data/met/' + cruise_id + '/rawInput/'
data_out_path = '/test_data/met/procOutput/' + cruise_id + '/'


# Initialize related processing classes
reader = met_dfn_api_reader.MeteoDfnApi(config)  
# exporter = ctd_level0_exporter.CtdLevel0(config)
# exporter1 = ctd_level1C_exporter.CtdLevel1C(config)
# rtqc = rtqc_tests.Rtqc(config)
# nc_load = load_netcdf.LoadNetCDF

# Load meteo data from API
files_list = reader.get_input_files_list(data_in_path)
dataset = {}
for file_path in files_list:
    df_json = reader.load_data(file_path)
    df = reader.json_to_df(df_json)
    # df.AIR_PRES = qa.convert_units(df.AIR_PRES, 1000)

# Export to csv
df.to_csv(data_out_path + '/csv/test.csv')
    
# Export L0 NetCDF

# Copy L0 to L1 


# Load L1 netCDF and perform QC


