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
import pandas as pd

import readers.bottle_readers.bottle_readers_base as bottle_readers_base
import readers.bottle_readers.bottle_sbe_btl_reader as bottle_sbe_btl_reader
import readers.bottle_readers.bottle_salinity_samples_reader as bottle_salinity_samples_reader
import readers.bottle_readers.bottle_oxygen_samples_reader as bottle_oxygen_samples_reader
import readers.bottle_readers.bottle_talk_samples_reader as bottle_talk_samples_reader
import readers.bottle_readers.bottle_chla_samples_reader as bottle_chla_samples_reader
import readers.bottle_readers.bottle_ph_samples_reader as bottle_ph_samples_reader

import exporters.bottle_nc_exporters.bottle_level0_exporter as bottle_level0_exporter

import utils.load_netcdf as load_netcdf
import utils.plot_utils as plotutils

import sys
sys.path.append('/home/a33272/Documents/python/nansen_pbgc_processing/')


package_path = '/home/a33272/Documents/python/'
# Load config file
config_path = package_path + 'nansen_pbgc_processing/config/'
config_pbgc_path = package_path + 'pbgc_field_calib/config/'
config = configparser.ConfigParser()
config.read(config_path + 'config.ini')
cruise_id_list = config['Settings']['CruiseId'].split(',')

for cruise_id in cruise_id_list:
    data_in_path = config['Settings']['DataInPathBottle'] + cruise_id + '/rawInput/'
    data_in_path_btl = data_in_path + 'ctd/'
    data_in_path_salinity_samples = data_in_path + 'salinity_samples/'
    data_in_path_oxygen_samples = data_in_path + 'oxygen_samples/'
    data_in_path_talk_samples = data_in_path + 'talk_samples/'
    data_in_path_chla_samples = data_in_path + 'chla_samples/'
    data_in_path_ph_samples = data_in_path + 'ph_samples/'
    
    data_out_path =  config['Settings']['DataOutPathBottle']
    config_survey = configparser.ConfigParser()
    config_survey.read(config_path + 'config_' + cruise_id + '.ini', encoding= 'utf-8')
    config_field_calib = configparser.ConfigParser()
    config_field_calib.read(config_pbgc_path + 'config_' + cruise_id + '.ini', encoding= 'utf-8')


    # Initialize related processing classes
    base_reader = bottle_readers_base.ReadersBase(config)
    reader_btl = bottle_sbe_btl_reader.BottleSbeBtl(config)  
    reader_salinity_samples = bottle_salinity_samples_reader.BottleSalinitySamples(config) 
    reader_oxygen_samples = bottle_oxygen_samples_reader.BottleOxygenSamples(config)
    reader_talk_samples = bottle_talk_samples_reader.BottleTotalAlkalinitySamples(config)
    reader_chla_samples = bottle_chla_samples_reader.BottleChlaSamples(config)
    reader_ph_samples = bottle_ph_samples_reader.BottlePhSamples(config)
    
    exporter = bottle_level0_exporter.BottleLevel0(config_survey)
    nc_load = load_netcdf.LoadNetCDF
    
    # Load btl rawInput data
    btl_format = int(config['Settings']['IncludeSbeBtl'])
    if btl_format == 0:
       continue 
    elif btl_format == 1:
        files_list_btl = reader_btl.get_input_files_list(data_in_path_btl)        
        
    dataset_btl = {}
    for file_path in files_list_btl:
        if btl_format == 0:
            continue
        elif btl_format == 1:           
            btl_df, btl_attrs = reader_btl.load_data(file_path, config)

        station = 'sta' + file_path[-8:-4]
        #station = file_path.rsplit('/', 1)[1][1:-4]
        dataset_btl[station] = {}
        dataset_btl[station]['data_btl'] = btl_df
        dataset_btl[station]['attrs_btl'] = btl_attrs
        dataset_btl[station]['attrs_btl']['station'] = station 

    dataset = dataset_btl
    
    # Load SALINITY samples rawInput data
    dataset_salinity_samples = {}
    salinity_samples_df  = pd.DataFrame()
    
    files_list_salinity_samples = base_reader.get_input_files_list(data_in_path_salinity_samples, '*.xlsx') 
       
    for file_path in files_list_salinity_samples:
        salinity_samples_df = base_reader.load_data_from_xls(file_path, salinity_samples_df)         
        
    salinity_samples_stations_list = base_reader.list_stations(df = salinity_samples_df, 
                                                               varname_map_station_id = base_reader.psal_ref_varnames_map['STATION_ID'])
    
    for station_id in salinity_samples_stations_list:
        dataset_salinity_samples = base_reader.subset_samples_per_station(station_id = station_id, 
                                               df = salinity_samples_df, 
                                               varname_map_station_id = base_reader.psal_ref_varnames_map['STATION_ID'], 
                                               subset_name = 'data_salinity_samples', 
                                               dataset = dataset_salinity_samples)
         
    for station in dataset_salinity_samples:  
        if station in dataset_btl.keys():
            dataset[station]['data_salinity_samples'] = dataset_salinity_samples[station]['data_salinity_samples']
            dataset[station]['data_btl'] = base_reader.join_ref_with_btl(ref_df = dataset[station]['data_salinity_samples'], 
                                                                         btl_df = dataset[station]['data_btl'],
                                                                         varname_map = base_reader.psal_ref_varnames_map['PSAL_INSITU_AVG'],
                                                                         varname_qc_map = base_reader.psal_ref_varnames_map['PSAL_INSITU_AVG_QC'],
                                                                         varname_map_bottle_num = base_reader.psal_ref_varnames_map['BOTTLE_NUM'])      
        
        
    # Load OXYGEN samples rawInput data
    dataset_oxygen_samples = {}
    oxygen_samples_df  = pd.DataFrame()
    
    files_list_oxygen_samples = base_reader.get_input_files_list(data_in_path_oxygen_samples, '*.xlsx') 
       
    for file_path in files_list_oxygen_samples:
        oxygen_samples_df = base_reader.load_data_from_xls(file_path, oxygen_samples_df)         
        
    oxygen_samples_stations_list = base_reader.list_stations(df = oxygen_samples_df, 
                                                               varname_map_station_id = base_reader.dox_ref_varnames_map['STATION_ID'])
    
    for station_id in oxygen_samples_stations_list:
        dataset_oxygen_samples = base_reader.subset_samples_per_station(station_id = station_id, 
                                               df = oxygen_samples_df, 
                                               varname_map_station_id = base_reader.dox_ref_varnames_map['STATION_ID'], 
                                               subset_name = 'data_oxygen_samples', 
                                               dataset = dataset_oxygen_samples)
         
    for station in dataset_oxygen_samples:  
        if station in dataset_btl.keys():
            dataset[station]['data_oxygen_samples'] = dataset_oxygen_samples[station]['data_oxygen_samples']
            dataset[station]['data_btl'] = base_reader.join_ref_with_btl(ref_df = dataset[station]['data_oxygen_samples'], 
                                                                         btl_df = dataset[station]['data_btl'],
                                                                         varname_map = base_reader.dox_ref_varnames_map['DOX_INSITU'],
                                                                         varname_qc_map = base_reader.dox_ref_varnames_map['DOX_INSITU_QC'],
                                                                         varname_map_bottle_num = base_reader.dox_ref_varnames_map['BOTTLE_NUM'])           
        
    # Load TOTAL ALKALINITY samples rawInput data
    dataset_talk_samples = {}
    talk_samples_df  = pd.DataFrame()
    
    files_list_talk_samples = base_reader.get_input_files_list(data_in_path_talk_samples, '*.xlsm') 
       
    for file_path in files_list_talk_samples:
        talk_samples_df = base_reader.load_data_from_xls(file_path, talk_samples_df)         
        
    talk_samples_stations_list = base_reader.list_stations(df = talk_samples_df, 
                                                               varname_map_station_id = base_reader.talk_ref_varnames_map['STATION_ID'])
    
    for station_id in talk_samples_stations_list:
        dataset_talk_samples = base_reader.subset_samples_per_station(station_id = station_id, 
                                               df = talk_samples_df, 
                                               varname_map_station_id = base_reader.talk_ref_varnames_map['STATION_ID'], 
                                               subset_name = 'data_talk_samples', 
                                               dataset = dataset_talk_samples)
         
    for station in dataset_talk_samples:  
        if station in dataset_btl.keys():
            dataset[station]['data_talk_samples'] = dataset_talk_samples[station]['data_talk_samples']
            dataset[station]['data_btl'] = base_reader.join_ref_with_btl(ref_df = dataset[station]['data_talk_samples'], 
                                                                         btl_df = dataset[station]['data_btl'],
                                                                         varname_map = base_reader.talk_ref_varnames_map['TALK_INSITU'],
                                                                         varname_qc_map = base_reader.talk_ref_varnames_map['TALK_INSITU_QC'],
                                                                         varname_map_bottle_num = base_reader.talk_ref_varnames_map['BOTTLE_NUM'])         

    # Load CHLOROPHYLL A samples rawInput data
    dataset_chla_samples = {}
    chla_samples_df  = pd.DataFrame()
    
    files_list_chla_samples = base_reader.get_input_files_list(data_in_path_chla_samples, '*.xlsm') 
       
    for file_path in files_list_chla_samples:
        chla_samples_df = base_reader.load_data_from_xls(file_path, chla_samples_df)         
        
    chla_samples_stations_list = base_reader.list_stations(df = chla_samples_df, 
                                                               varname_map_station_id = base_reader.chla_ref_varnames_map['STATION_ID'])
    
    for station_id in chla_samples_stations_list:
        dataset_chla_samples = base_reader.subset_samples_per_station(station_id = station_id, 
                                               df = chla_samples_df, 
                                               varname_map_station_id = base_reader.chla_ref_varnames_map['STATION_ID'], 
                                               subset_name = 'data_chla_samples', 
                                               dataset = dataset_chla_samples)
         
    for station in dataset_chla_samples:  
        if station in dataset_btl.keys():
            dataset[station]['data_chla_samples'] = dataset_chla_samples[station]['data_chla_samples']
            dataset[station]['data_btl'] = base_reader.join_ref_with_btl(ref_df = dataset[station]['data_chla_samples'], 
                                                                         btl_df = dataset[station]['data_btl'],
                                                                         varname_map = base_reader.chla_ref_varnames_map['FCHLA_INSITU'],
                                                                         varname_qc_map = base_reader.chla_ref_varnames_map['FCHLA_INSITU_QC'],
                                                                         varname_map_bottle_num = base_reader.chla_ref_varnames_map['BOTTLE_NUM'])           

    # Load PH samples rawInput data
    dataset_ph_samples = {}
    ph_samples_df  = pd.DataFrame()
    
    files_list_ph_samples = base_reader.get_input_files_list(data_in_path_ph_samples, '*.xlsm') 
       
    for file_path in files_list_ph_samples:
        ph_samples_df = base_reader.load_data_from_xls(file_path, ph_samples_df)         
        
    ph_samples_stations_list = base_reader.list_stations(df = ph_samples_df, 
                                                               varname_map_station_id = base_reader.ph_ref_varnames_map['STATION_ID'])
    
    for station_id in ph_samples_stations_list:
        dataset_ph_samples = base_reader.subset_samples_per_station(station_id = station_id, 
                                               df = ph_samples_df, 
                                               varname_map_station_id = base_reader.ph_ref_varnames_map['STATION_ID'], 
                                               subset_name = 'data_ph_samples', 
                                               dataset = dataset_ph_samples)
         
    for station in dataset_ph_samples:  
        if station in dataset_btl.keys():
            dataset[station]['data_ph_samples'] = dataset_ph_samples[station]['data_ph_samples']
            dataset[station]['data_btl'] = base_reader.join_ref_with_btl(ref_df = dataset[station]['data_ph_samples'], 
                                                                         btl_df = dataset[station]['data_btl'],
                                                                         varname_map = base_reader.ph_ref_varnames_map['PH_INSITU'],
                                                                         varname_qc_map = base_reader.ph_ref_varnames_map['PH_INSITU_QC'],
                                                                         varname_map_bottle_num = base_reader.ph_ref_varnames_map['BOTTLE_NUM'])  


            
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
    
    # # Copy L0 to L1    
    # data_out_path_L1A = data_out_path + 'L1A/'
    # exporter.create_data_out_directories(data_out_path_L1A)
    # files_list = glob.glob(data_out_path_L0 + '*.nc') 
    # for f in os.listdir(data_out_path_L1A):
    #     os.remove(os.path.join(data_out_path_L1A, f))   
    # for file_path in files_list: 
    #     file_name = os.path.basename(file_path)
    #     file_name_new = file_name.replace('L0', 'L1A')
    #     shutil.copy(data_out_path_L0 + file_name, data_out_path_L1A + file_name_new)
      
    # # Load L1 netCDF and perform QC
    # files_list = glob.glob(data_out_path_L1A + '*L1A*.nc')
    # for file_path in files_list: 
    #     rtqc_manager.perform_rtqc(file_path, dataset[station], config_survey)
     









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