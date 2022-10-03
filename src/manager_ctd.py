#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Oct 12 14:01:00 2020

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
import readers.ctd_sbe_cnv_reader as ctd_sbe_cnv_reader
import readers.ctd_quickcast_odv_reader as ctd_quickcast_odv_reader
import exporters.ctd_level0_exporter as ctd_level0_exporter
import exporters.ctd_level1C_exporter as ctd_level1C_exporter
import rtqc.rtqc_tests as rtqc_tests
import rtqc.manager_rtqc_ctd as manager_rtqc_ctd
import utils.load_netcdf as load_netcdf
import utils.plot_utils as plotutils

import sys
sys.path.append('/home/a33272/Documents/python/')
import pbgc_field_calib.src.manager_salinity as salinity_field_calibration
import pbgc_field_calib.src.manager_oxygen as oxygen_field_calibration
import pbgc_field_calib.src.manager_chla as chla_field_calibration


package_path = '/home/a33272/Documents/python/'
# Load config file
config_path = package_path + 'nansen_pbgc_processing/config/'
config_pbgc_path = package_path + 'pbgc_field_calib/config/'
config = configparser.ConfigParser()
config.read(config_path + 'config.ini')
cruise_id_list = config['Settings']['CruiseId'].split(',')

for cruise_id in cruise_id_list:
    data_in_path = config['Settings']['DataInPath'] + cruise_id + '/rawInput/'
    data_out_path =  config['Settings']['DataOutPath']
    config_survey = configparser.ConfigParser()
    config_survey.read(config_path + 'config_' + cruise_id + '.ini')
    config_field_calib = configparser.ConfigParser()
    config_field_calib.read(config_pbgc_path + 'config_' + cruise_id + '.ini')
    # config_field_calib_json = configparser.ConfigParser()
    # config_field_calib.read(config_pbgc_path + 'config_' + cruise_id + '.json')  

    # Initialize related processing classes
    reader = ctd_sbe_cnv_reader.CtdSbeCnv(config)  
    reader_odv = ctd_quickcast_odv_reader.CtdQuickcastOdv(config)
    exporter = ctd_level0_exporter.CtdLevel0(config_survey)
    exporter1 = ctd_level1C_exporter.CtdLevel1C(config_survey)
    rtqc_manager = manager_rtqc_ctd.RtqcManager(config_survey)
    nc_load = load_netcdf.LoadNetCDF
    
    # Load rawInput data
    ctd_format = int(config['Settings']['CtdFormat'])
    if (ctd_format == 0) or (ctd_format == 1):
        reader.set_cnv_varnames_map(config)
        files_list = reader.get_input_files_list(data_in_path)
    elif ctd_format == 2:
        reader_odv.set_cnv_varnames_map(config)
        files_list = reader_odv.get_input_files_list(data_in_path)
            
    dataset = {}
    for file_path in files_list:
        if (config['Settings']['CtdFormat'] == 0) or (config['Settings']['CtdFormat'] == 1):
            data_df, attrs = reader.load_data(file_path, config)
        elif config['Settings']['CtdFormat'] == 2:
            data_df, attrs = reader_odv.load_data(file_path, config)
            
        station = 'sta' + file_path[-8:-4]
        #station = file_path.rsplit('/', 1)[1][1:-4]
        dataset[station] = {}
        dataset[station]['data'] = data_df
        dataset[station]['attrs'] = attrs
        dataset[station]['attrs']['station'] = station 
        dataset[station]['attrs'] = reader.load_header_attrs(file_path, dataset[station]['attrs'])
    
    #Export L0 NetCDF
    exporter.create_data_out_directories(data_out_path)
    data_out_path_year = data_out_path + config_survey['GlobalAttrs']['CruiseId'][0:4]
    exporter.create_data_out_directories(data_out_path_year)
    data_out_path = data_out_path_year + '/' + config_survey['GlobalAttrs']['CruiseId'] + '/'
    exporter.create_data_out_directories(data_out_path)
    data_out_path_L0 = data_out_path + 'L0/'
    exporter.create_data_out_directories(data_out_path_L0)
    for f in os.listdir(data_out_path_L0):
        os.remove(os.path.join(data_out_path_L0, f))
    for station in dataset:
        exporter.create_nc_file(data_out_path_L0, config, config_survey, dataset[station])
    
    # Copy L0 to L1    
    data_out_path_L1A = data_out_path + 'L1A/'
    exporter.create_data_out_directories(data_out_path_L1A)
    files_list = glob.glob(data_out_path_L0 + '*.nc') 
    for f in os.listdir(data_out_path_L1A):
        os.remove(os.path.join(data_out_path_L1A, f))   
    for file_path in files_list: 
        file_name = os.path.basename(file_path)
        file_name_new = file_name.replace('L0', 'L1A')
        shutil.copy(data_out_path_L0 + file_name, data_out_path_L1A + file_name_new)
      
    # Load L1 netCDF and perform QC
    files_list = glob.glob(data_out_path_L1A + '*L1A*.nc')
    for file_path in files_list:        
        rtqc_manager.perform_rtqc(file_path, config_survey)
     









# ## ---------------------------------------------------------------------------------------------------

# # Copy L1A to L1C    
# data_out_path_L1C = data_out_path + 'L1C/'
# exporter.create_data_out_directories(data_out_path_L1C)
# files_list = glob.glob(data_out_path_L1A + '*L1A*.nc')    
# for f in os.listdir(data_out_path_L1C):
#     os.remove(os.path.join(data_out_path_L1C, f))   
# for file_path in files_list: 
#     file_name = os.path.basename(file_path)
#     file_name_new = file_name.replace('L1A', 'L1C')
#     shutil.copy(data_out_path_L1A + file_name, data_out_path_L1C + file_name_new)

# # Call the field_calibration_toolbox and export coeffs for salinity
# # Load L1C netCDF and and apply correction results
# files_list = glob.glob(data_out_path_L1C + '*L1C*.nc')
# for file_path in files_list:   
#     dataset_nc = nc.Dataset(file_path, 'r+')
#     dataset_nc.processing_level = 'Level 1C – Field Calibrated, RT/DM QC data'
#     dataset_nc.close()




# # ## -------------------------------------------------------------------------------------------------------------------
# # # Salinity calibration
# # join_df, salinity_residuals_info_corr = salinity_field_calibration.process_salinity(config_field_calib)
# # for file_path in files_list:     
# #     var_name = exporter.nc_varnames_map['CNDC00_CORR']
# #     exporter1.create_corrected_vars(var_name, file_path, salinity_residuals_info_corr, config, config_field_calib)
# #     var_name = exporter.nc_varnames_map['PSAL00_CORR']
# #     exporter1.create_corrected_vars(var_name, file_path, salinity_residuals_info_corr, config, config_field_calib)    
    
# # #Oxygen calibration
# # join_df, join_df_original, oxygen_residuals_info_corr = oxygen_field_calibration.process_oxygen(config_field_calib)
# # for file_path in files_list:  
# #     var_name = exporter.nc_varnames_map['DOX1_CORR']
# #     dox_corr = exporter1.create_corrected_vars(var_name=var_name, 
# #                                                 file_path=file_path, 
# #                                                 correction_metadata=oxygen_residuals_info_corr, 
# #                                                 config=config, 
# #                                                 config_field_calib=config_field_calib) #(var_name, file_path, oxygen_residuals_info_corr, config, config_field_calib)         
# # for file_path in files_list:
# #     data = plotutils.plot_station_profile(file_path, oxygen_field_calibration.oxygen_field_calib.PhChFieldCalib(config_field_calib).figs_path, join_df, join_df_original, oxygen_residuals_info_corr, config)
# # # plotutils.plot_all_station_profiles(files_list, oxygen_field_calibration.oxygen_field_calib.PhChFieldCalib(config_field_calib).figs_path, join_df, join_df_original, oxygen_residuals_info_corr, config)


# # # Chlorophyll calibration
# # join_df, join_df_original, chla_residuals_info_corr, stations_list, cnv_data_dict = chla_field_calibration.process_chla(config_field_calib)
# # for file_path in files_list: 
# #     for station in stations_list:
# #         if str(station) in str(int(file_path[-7:-3])):
# #             var_name = exporter.nc_varnames_map['FCHLA_CORR']
# #             station
# #             exporter1.create_corrected_vars(var_name=var_name, 
# #                                             file_path=file_path, 
# #                                             correction_metadata=chla_residuals_info_corr, 
# #                                             config=config, 
# #                                             config_field_calib=config_field_calib, 
# #                                             dataset_cnv=cnv_data_dict,
# #                                             station=station)  
    

    
# #             dataset_nc = nc.Dataset(file_path, 'r+')    
            
# #             # RTQC6 Global Range Test    
# #             # Fluorescence
# #             var_name = exporter.nc_varnames_map['FCHLA_CORR']
# #             var_name_qc = exporter.nc_varnames_map['FCHLA_CORR_OS_QC']
# #             fchla = dataset_nc.variables[var_name][:]
# #             fchla_qc = []
# #             for observation in fchla:
# #                 observation_qc, anc_observation_qc = rtqc.rtqc6_global_range_test(var_name, observation)
# #                 fchla_qc.append(observation_qc)       
# #             dataset_nc.variables[var_name_qc][:] = fchla_qc        
            
# #             #RTQC9 Spike Test
# #             #Fchla
# #             var_name = exporter.nc_varnames_map['FCHLA_CORR']
# #             var_name_qc = exporter.nc_varnames_map['FCHLA_CORR_OS_QC']
# #             fchla_qc = dataset_nc.variables[var_name_qc][:][0]
# #             fchla = dataset_nc.variables[var_name][:]
# #             pres = dataset_nc.variables[exporter.nc_varnames_map['PRES']][:][0]
# #             fchla_qc_spike = rtqc.rtqc9_spike_test(var_name, fchla, fchla_qc, pres, 0)
# #             dataset_nc.variables[var_name_qc][:] = fchla_qc_spike
            
# #             dataset_nc.close()