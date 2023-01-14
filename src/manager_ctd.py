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
import multiprocessing as mp

import readers.ctd_readers.ctd_sbe_cnv_reader as ctd_sbe_cnv_reader
import readers.ctd_readers.ctd_sbe_quickcast_odv_reader as ctd_quickcast_odv_reader
import readers.ctd_readers.ctd_accessdbtable_imrop_reader as ctd_accessdbtable_imrop_reader
import readers.ctd_readers.ctd_readers_base as ctd_readers_base
import exporters.ctd_nc_exporters.ctd_level0_exporter as ctd_level0_exporter
import exporters.ctd_nc_exporters.ctd_level1C_exporter as ctd_level1C_exporter
import rtqc.rtqc_tests as rtqc_tests
import rtqc.manager_rtqc_ctd as manager_rtqc_ctd
import utils.load_netcdf as load_netcdf
import utils.plot_utils as plotutils

import sys
sys.path.append('/home/a33272/Documents/python/nansen_pbgc_processing/')
# import pbgc_field_calib.src.manager_salinity as salinity_field_calibration
# import pbgc_field_calib.src.manager_oxygen as oxygen_field_calibration
# import pbgc_field_calib.src.manager_chla as chla_field_calibration


package_path = '/home/a33272/Documents/python/'
# Load config file
config_path = package_path + 'nansen_pbgc_processing/config/'
config_pbgc_path = package_path + 'pbgc_field_calib/config/'
config = configparser.ConfigParser()
config.read(config_path + 'config.ini')
cruise_id_list = config['Settings']['CruiseId'].split(',')

#cruise_id_list = ['1957501', '1958501', '1959501', '1974501', '1975401', '1975402', '1975403', '1975501', '1976401', '1976402', '1976403', '1976501', '1976504', '1977401', '1977402', '1977403', '1977501', '1978401', '1978402', '1978404', '1978501', '1979401', '1979403', '1979404', '1979405', '1979501', '1980401', '1980402', '1980403', '1980404', '1980405', '1980406', '1980407', '1980408', '1980409', '1981404', '1981405', '1981407', '1981409', '1981410', '1981411', '1982401', '1982402', '1982403', '1982404', '1982405', '1982406', '1982407', '1983402', '1983403', '1983404', '1983405', '1983406', '1983407', '1983408', '1983409', '1983410', '1984401', '1984402', '1984403', '1984404', '1984405', '1984407', '1984409', '1984410', '1984501', '1985401', '1985402', '1985403', '1985404', '1985405', '1985406', '1985407', '1985408', '1985501', '1985502', '1986401', '1986402', '1986403', '1986404', '1986405', '1986406', '1986501', '1986502', '1986503', '1987401', '1987402', '1987403', '1987404', '1987501', '1987502', '1988401', '1988402', '1988403', '1988404', '1988501', '1988502', '1989401', '1989402', '1989403', '1989404', '1989405', '1989406', '1989407', '1989501', '1990401', '1990402', '1990403', '1990404', '1990405', '1990406', '1990501', '1990502', '1991401', '1991402', '1991403', '1991404', '1991405', '1991406', '1991407', '1991501', '1991502', '1991503', '1992401', '1992402', '1992403', '1992404', '1992405', '1992406', '1992408', '1992409', '1992410', '1992501', '1992502', '1992503', '1993401', '1993402', '1993403', '1993404', '1993405', '1993406', '1993501', '1994401', '1994402', '1994403', '1994404', '1994405', '1994406', '1994407', '1994408', '1994409', '1994501', '1995401', '1995402', '1995403', '1995404', '1995405', '1995406', '1995407', '1995408', '1995409', '1995410', '1996401', '1996402', '1996403', '1996404', '1996405', '1996406', '1996407', '1996408', '1996409', '1996410', '1996411', '1997401', '1997402', '1997403', '1997404', '1997405', '1997406', '1997407', '1997408', '1997409', '1998401', '1998402', '1998403', '1998404', '1998405', '1998406', '1998407', '1998408', '1998409', '1998410', '1998411', '1998412', '1998413', '1998414', '1998501', '1998502', '1999401', '1999402', '1999403', '1999404', '1999405', '1999406', '1999407', '1999408', '1999409', '1999410', '1999411', '1999412', '1999501', '2000401', '2000402', '2000403', '2000404', '2000405', '2000406', '2000407', '2000408', '2000409', '2000410', '2000411', '2000412', '2000501', '2001401', '2001402', '2001403', '2001404', '2001405', '2001406', '2001407', '2001408', '2001409', '2001410', '2001411', '2001412', '2001501', '2002401', '2002402', '2002403', '2002405', '2002406', '2002407', '2002408', '2002409', '2002410', '2002411', '2002501', '2003401', '2003404', '2003405', '2003407', '2003408', '2003409', '2003412', '2003501', '2004401', '2004403', '2004404', '2004405', '2004406', '2004407', '2004408', '2004409', '2004410', '2004411', '2004412', '2004413', '2004501', '2005402', '2005404', '2005405', '2005406', '2005407', '2005408', '2005409', '2005410', '2005411', '2005501', '2005502', '2006401', '2006402', '2006403', '2006405', '2006406', '2006407', '2006408', '2006409', '2006411', '2006501', '2007401', '2007403', '2007404', '2007405', '2007406', '2007408', '2007409', '2007502', '2008401', '2008402', '2008403', '2008404', '2008405', '2008406', '2008407', '2008408', '2008409', '2008501', '2009401', '2009402', '2009403', '2009404', '2009405', '2009406', '2009407', '2009408', '2009409', '2009410', '2009501', '2010401', '2010402', '2010403', '2010404', '2010405', '2010406', '2010407', '2010408', '2010409', '2010410', '2011401', '2011402', '2011403', '2011404', '2011405', '2011406', '2011407', '2011408', '2011409', '2011410', '2012401', '2012402', '2012403', '2012404', '2012405', '2012406', '2012407', '2012408', '2012901', '2013401', '2013402', '2013403', '2013404', '2013405', '2013406', '2013408', '2013409', '2014401', '2014402', '2014403', '2014404', '2014405', '2014406', '2015401', '2015402', '2015403', '2015404', '2015405', '2015406', '2015407', '2015408', '2015409', '2015901', '2016401', '2016404', '2016405', '2016406', '2016901', '2017401', '2017402', '2017403', '2017404', '2017405', '2017406', '2017407', '2017408', '2017409', '2017410', '2018401', '2018402', '2018403', '2018404', '2018405', '2018406', '2018407', '2018408', '2018409', '2018410', '2018411', '2018412', '2019401', '2019402', '2019403', '2019404', '2019405', '2019406', '2019407', '2019408', '2019409', '2019411', '2019412', '2019413', '2019414', '2019415', '2020401', '2020402', '2021401', '2021407', '2022401', '2022402', '2022403', '2022404', '2022405', '2022406', '2022407', '2022409', '2022410', '2022411']
# Define an output queue
output = mp.Queue()

def process_surveys(config, cruise_id, output):
    #for cruise_id in cruise_id_list:
    print('Processing SurveyID  --  ' + cruise_id)
    data_in_path = config['Settings']['DataInPathCtd'] + cruise_id + '/rawInput/ctd/'
    data_out_path =  config['Settings']['DataOutPathCtd']
    config_survey = configparser.ConfigParser()
    config_survey.read(config_path + 'config_' + cruise_id + '.ini', encoding= 'utf-8')
    config_field_calib = configparser.ConfigParser()
    config_field_calib.read(config_pbgc_path + 'config_' + cruise_id + '.ini', encoding= 'utf-8')
    # config_field_calib_json = configparser.ConfigParser()
    # config_field_calib.read(config_pbgc_path + 'config_' + cruise_id + '.json')    

    # Initialize related processing classes
    reader = ctd_sbe_cnv_reader.CtdSbeCnv(config)  
    reader_odv = ctd_quickcast_odv_reader.CtdQuickcastOdv(config)
    reader_imrop = ctd_accessdbtable_imrop_reader.CtdAccessDbImrop(config)
    base_reader = ctd_readers_base.ReadersBase(config)
    exporter = ctd_level0_exporter.CtdLevel0(config_survey)
    exporter1 = ctd_level1C_exporter.CtdLevel1C(config_survey)
    rtqc_manager = manager_rtqc_ctd.RtqcManager(config_survey)
    nc_load = load_netcdf.LoadNetCDF
    
    # Load rawInput data
    ctd_format = int(config['Settings']['CtdFormat'])
    if (ctd_format == 0) or (ctd_format == 1):
        files_list = reader.get_input_files_list(data_in_path)
    elif ctd_format == 2:
        files_list_all = reader_odv.get_input_files_list(cruise_id, data_in_path)
        files_list = reader_odv.get_input_station_files_list(data_in_path)
        if not files_list:
            reader_odv.split_survey_odv_into_stations(files_list_all[0], data_in_path, config)
        files_list = reader_odv.get_input_station_files_list(data_in_path)
    elif ctd_format == 3:
        files_list = reader_imrop.get_input_files_list(cruise_id, data_in_path)
        reader_imrop.split_survey_imrop_into_stations(files_list[0], data_in_path, config)
        files_list = reader_imrop.get_input_station_files_list(data_in_path)
        
    dataset = {}
    for file_path in files_list:
        print('----  Loading cnv file --  ' + file_path)
        if (ctd_format == 0) or (ctd_format == 1):
            data_df, attrs = reader.load_data(file_path, config)
        elif ctd_format == 2:           
            data_df, attrs = reader_odv.load_data(file_path, config)
        elif ctd_format == 3:           
            data_df, attrs = reader_imrop.load_data(file_path, config)            
            
        station = 'sta' + file_path[-8:-4]
        #station = file_path.rsplit('/', 1)[1][1:-4]
        dataset[station] = {}
        dataset[station]['data'] = data_df
        dataset[station]['attrs'] = attrs
        dataset[station]['attrs']['station'] = station 
        if (ctd_format == 0) or (ctd_format == 1):
            dataset[station]['attrs'] = reader.load_header_attrs(file_path, dataset[station]['attrs'])
        elif ctd_format == 2:
            dataset[station]['attrs'] = reader_odv.load_header_attrs(data_df, dataset[station]['attrs']) 
        elif ctd_format == 3:
            dataset[station]['attrs'] = reader_imrop.load_header_attrs(data_df, dataset[station]['attrs']) 
    
        # Derive salinity in case it does not exist in the rawInput files
        if (ctd_format == 0) or (ctd_format == 1):
            if reader.varnames_map['CNDC00'] in dataset[station]['data']:
                if reader.varnames_map['PSAL00'] not in dataset[station]['data']:
                    cndc = dataset[station]['data'][reader.varnames_map['CNDC00']]
                    temp = dataset[station]['data'][reader.varnames_map['TEMP00']]
                    pres = dataset[station]['data'][reader.varnames_map['PRES']]
                    psal = reader.psal_from_cndc(cndc, temp, pres)
                    dataset[station]['data'][reader.varnames_map['PSAL00']] = psal
            elif reader.varnames_map['CNDC01'] in dataset[station]['data']:
                if reader.varnames_map['PSAL01'] not in dataset[station]['data']:
                    cndc = dataset[station]['data'][reader.varnames_map['CNDC01']]
                    temp = dataset[station]['data'][reader.varnames_map['TEMP01']]
                    pres = dataset[station]['data'][reader.varnames_map['PRES']]
                    psal = reader.psal_from_cndc(cndc, temp, pres)
                    dataset[station]['data'][reader.varnames_map['PSAL01']] = psal       
            
    #Export L0 NetCDF
    exporter.create_data_out_directories(data_out_path)
    if (ctd_format == 0) or (ctd_format == 1) or (ctd_format == 2):
        data_out_path_year = data_out_path + config_survey['GlobalAttrs']['CruiseId'][0:4]
    elif (ctd_format == 3):
        data_out_path_year = data_out_path + config_survey['GlobalAttrs']['CruiseId'][3:7]
        
    exporter.create_data_out_directories(data_out_path_year)
    data_out_path = data_out_path_year + '/' + config_survey['GlobalAttrs']['CruiseId'] + '/'
    exporter.create_data_out_directories(data_out_path)
    data_out_path_L0 = data_out_path + 'L0/'
    exporter.create_data_out_directories(data_out_path_L0)
    for f in os.listdir(data_out_path_L0):
        os.remove(os.path.join(data_out_path_L0, f))
    for station in dataset:
        output.put(exporter.create_nc_file(data_out_path_L0, config, config_survey, dataset[station]))
    
    # Copy L0 to L1    
    data_out_path_L1A = data_out_path + 'L1A/'
    exporter.create_data_out_directories(data_out_path_L1A)
    files_list = glob.glob(data_out_path_L0 + '*.nc') 
    for f in os.listdir(data_out_path_L1A):
        os.remove(os.path.join(data_out_path_L1A, f))   
    for file_path in files_list: 
        file_name = os.path.basename(file_path)
        file_name_new = file_name.replace('L0', 'L1A')
        output.put( shutil.copy(data_out_path_L0 + file_name, data_out_path_L1A + file_name_new))
      
    # Load L1 netCDF and perform QC
    files_list = sorted(glob.glob(data_out_path_L1A + '*L1A*.nc'))
    for file_path in files_list: 
        print ('----- PERFORMING RTQC IN STATION   --   ' + file_path)
        output.put(rtqc_manager.perform_rtqc(file_path, dataset[station], config_survey))
     


# Setup a list of processes that we want to run
processes = [mp.Process(target=process_surveys, args=(config, cruise_id, output)) for cruise_id in cruise_id_list]

# Run processes
for p in processes:
    p.start()

# Exit the completed processes
for p in processes:
    p.join()
    p.terminate()


# # Get process results from the output queue
# results = [output.get() for p in processes]
# print(results)    






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