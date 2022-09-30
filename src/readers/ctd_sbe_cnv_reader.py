#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Oct 12 04:12:00 2020

@author: a33272
"""
import re
import glob
import numpy as np
import pandas as pd
from seabird.cnv import fCNV


class CtdSbeCnv:
    def __init__(self, config): 
        #Sself.main_path      = config['Path']['MainPath']
       
        self.cnv_varnames_map = {}
        self.cnv_varnames_map_dfn_v0 = {'PRES': 'PRES',
                                 'PSAL00': 'PSAL',
                                 'TEMP00': 'temperature', 
                                 'TEMP01': 't168C', 
                                 'CNDC00': 'CNDC',
                                 'CNDC01': 'CNDC2',
                                 'DOXV': 'oxygenvoltage',
                                 'DOX1': 'oxygen_ml_L',
                                 'FCHLA': 'flECO-AFL',
                                 'FCHLA_CORR': 'flECO-AFL_corr',                                 
                                 'PAR': 'par',
                                 'SIGT': 'sigma_t',
                                 'STATION_DEPTH': 'station_depth',
                                 'STATION_SHIP_LOG': 'ship_log',
                                 'STATION_AIRT': 'air_temp',
                                 'STATION_WEATHER': 'weather_code',
                                 'STATION_SKY': 'sky_code',
                                 'STATION_SEA': 'sea_code',
                                 'STATION_NAME': 'station_name',
                                 'STATION_WDIR': 'winddir_code',
                                 'STATION_WFORCE': 'windforce_code',                                
                                }          
     
        # self.cnv_var_attrs_map_dfn_v0 = {'TEMP00_SENSOR_SN': 'temp00_sensor_sn',
        #                           'CNDC00_SENSOR_SN': 'cndc00_sensor_sn',
        #                           'PRES_SENSOR_SN': 'pres_sensor_sn',
        #                           'DOX1_SENSOR_SN': 'dox1_sensor_sn',
        #                           'FCHLA_SENSOR_SN': 'fchla_sensor_sn',
        #                                  }
        

        self.cnv_varnames_map_dfn_v1 = {'PRES': 'PRES',
                                 'PSAL00': 'PSAL',
                                 'PSAL01': 'PSAL2',
                                 'TEMP00': 'TEMP', 
                                 'TEMP01': 'TEMP2',
                                 'CNDC00': 'CNDC',
                                 'CNDC01': 'CNDC2',
                                 'DOXV': 'oxygenvoltage',
                                 'DOX1': 'oxygen_ml_L',
                                 #'FCHLA': 'Fluo',
                                 'FCHLA': 'flECO-AFL',
                                 #'FCHLA': 'flC',
                                 #'FCHLAV': 'flECO-AFL_voltage',
                                 'FCHLA_CORR': 'flECO-AFL_corr',                                 
                                 'PAR': 'par',
                                 'SIGT': 'sigma_t',
                                 'STATION_DEPTH': 'station_depth',
                                 'STATION_SHIP_LOG': 'ship_log',
                                 'STATION_AIRT': 'air_temp',
                                 'STATION_WEATHER': 'weather_code',
                                 'STATION_SKY': 'sky_code',
                                 'STATION_SEA': 'sea_code',
                                 'STATION_NAME': 'station_name',
                                 'STATION_WDIR': 'winddir_code',
                                 'STATION_WFORCE': 'windforce_code',                                
                                }          
       
    
        self.cnv_var_attrs_map = {'TEMP00_SENSOR_SN': 'temp00_sensor_sn',
                                  'TEMP01_SENSOR_SN': 'temp01_sensor_sn',
                                  'CNDC00_SENSOR_SN': 'cndc00_sensor_sn',
                                  'CNDC01_SENSOR_SN': 'cndc01_sensor_sn',
                                  'PRES_SENSOR_SN': 'pres_sensor_sn',
                                  'DOX1_SENSOR_SN': 'dox1_sensor_sn',
                                  'FCHLA_SENSOR_SN': 'fchla_sensor_sn',
                                  }
                

    def set_cnv_varnames_map(self, config):
        if config['Settings']['CtdFormat'] == '0':
            self.cnv_varnames_map = self.cnv_varnames_map_dfn_v0
        elif config['Settings']['CtdFormat'] == '1':
            self.cnv_varnames_map = self.cnv_varnames_map_dfn_v1
                   
            
            
    def get_input_files_list(self, files_path):
        files_list = glob.glob(files_path + '*.cnv')
        #files_list = glob.glob(files_path + 'd*.cnv')
        #files_list = glob.glob(files_path + 'u*.cnv')
        return files_list
        
        
    def load_data(self, file_path, config):
        '''Loads cnv files using seabird library.'''
        #files_list = glob.glob(files_path + 'u*.cnv')
        # if config['Settings']['CtdSbeCnvFormat'] == '0':
        #     cnv_varnames_map = self.cnv_varnames_map_dfn_v0
        # elif config['Settings']['CtdSbeCnvFormat'] == '1':
        #     cnv_varnames_map = self.cnv_varnames_map_dfn_v1
            
        profile = fCNV(file_path)
        attrs = profile.attrs
        attrs_names = list(profile.attrs.keys())
        
        var_names = list(profile.keys())
 
        var_dict = dict((key, []) for key in var_names)      
              
        if 'flECO-AFL' in var_dict:
            var_dict[self.cnv_varnames_map['FCHLA']] = var_dict.pop('flECO-AFL')
        elif 'flC' in var_dict:
            var_dict[self.cnv_varnames_map['FCHLA']] = var_dict.pop('flC')  
        elif 'fluorescence' in var_dict:
            var_dict[self.cnv_varnames_map['FCHLA']] = var_dict.pop('fluorescence')             
        for var_name in var_names:
            var = profile[var_name]
            for value in var:
                if not value:
                    value = None
                if (var_name == 'flECO-AFL') or (var_name == 'flC') or (var_name == 'fluorescence'):
                    var_dict[self.cnv_varnames_map['FCHLA']].append(value)
                else:
                    var_dict[var_name].append(value)
        for key in var_dict:
            var_dict[key].reverse()

#        # Only for SOCIB datasets        
#        r = len(var_dict['LATITUDE'])        
#        var_dict['DEPTH'] = var_dict['DEPTH'][r:]        
#        var_dict['PSAL'] = var_dict['PSAL'][r:]
#        var_dict['PSAL2'] = var_dict['PSAL2'][r:]
#        del var_dict['D2-D1,d']
#        del var_dict['secS-priS']
#        del var_dict['density']

        
        df = pd.DataFrame.from_dict(var_dict)
        return df, attrs

    
    def load_header_attrs(self, file_path, dataset_attrs):       
        file  = open(file_path, 'r', encoding='cp1250')
        stop_trigger = False
        # Read file until the END of the cnv file headers
        while stop_trigger == False:
            line = file.readline()
            if '** Station:' in line:
                dum = line[11:-1].replace(" ", "")   
                dum = dum.replace("sta", "")
                dum = dum.zfill(4) # add zeros before if they are not
                dataset_attrs['station_name'] = dum
                
            elif '** Echodepth [m]:' in line:
                dataset_attrs['station_depth'] = line[17:-1].replace(" ", "")   
            elif '** Echodepth[m]:' in line:
                dataset_attrs['station_depth'] = line[16:-1].replace(" ", "")   
            elif '** Echodepth:' in line:
                dataset_attrs['station_depth'] = line[13:-1].replace(" ", "") 
            elif '** Bottom Depth [m]:' in line:
                dataset_attrs['station_depth'] = line[20:-1].replace(" ", "")
            elif '** Log:' in line:
                dataset_attrs['ship_log'] = line[7:-1].replace(" ", "")  
            elif '** Air-temp (dry):' in line:
                dataset_attrs['air_temp'] = line[18:-1].replace(" ", "")                  
            elif '** Air-Temp(Dry):' in line:
                dataset_attrs['air_temp'] = line[17:-1].replace(" ", "") 
            elif '** Weather Sky:' in line:
                reg = re.match(r"(\*\* Weather Sky:)\s*([0-9]*)\s*([0-9]*)(\n)", line)
                dataset_attrs['weather_code'] = reg.group(2)                  
                dataset_attrs['sky_code'] = reg.group(3)                
            elif '** Wind-Dir Force:' in line:
                reg = re.match(r"(\*\* Wind-Dir Force:)\s*([0-9]*)\s*([0-9]*)(\n)", line)
                dataset_attrs['winddir_code'] = reg.group(2)                     
                dataset_attrs['windforce_code'] = reg.group(3)                
            elif '** Wind-Dir Force(m/s):' in line:
                reg = re.match(r"(\*\* Wind-Dir Force\(m\/s\):)\s*([0-9]*)\s*([0-9]*)", line)
                dataset_attrs['winddir_code'] = reg.group(2)                     
                dataset_attrs['windforce_code'] = reg.group(3)      
            elif '** Wind-Dir/Force:' in line:
                reg = re.match(r"(\*\* Wind-Dir/Force:)\s*([0-9]*)\s*([0-9]*)", line)
                dataset_attrs['winddir_code'] = reg.group(2)                     
                dataset_attrs['windforce_code'] = reg.group(3)   
            elif '** Sea:' in line:
                reg = re.match(r"(\*\* Sea:)\s*([0-9]*)(\n)", line)
                dataset_attrs['sea_code'] = reg.group(2)           
            elif '** Sea Ice:' in line:
                reg = re.match(r"(\*\* Sea Ice:)\s*([0-9]*)\s+([0-9]*)", line)
                dataset_attrs['sea_code'] = reg.group(2)                   
            elif '<!-- Frequency 0, Temperature -->' in line:
                line = file.readline()
                line = file.readline()
                if '<SerialNumber>' in line:
                    dataset_attrs['temp00_sensor_sn'] = line[22:-16].replace(" ", "")  
            elif '<!-- Frequency 3, Temperature, 2 -->' in line:
                line = file.readline()
                line = file.readline()
                if '<SerialNumber>' in line:
                    dataset_attrs['temp01_sensor_sn'] = line[22:-16].replace(" ", "")                     
            elif '<!-- Frequency 1, Conductivity -->' in line:
                line = file.readline()
                line = file.readline()
                if '<SerialNumber>' in line:
                    dataset_attrs['cndc00_sensor_sn'] = line[22:-16].replace(" ", "")  
            elif '<!-- Frequency 4, Conductivity, 2 -->' in line:
                line = file.readline()
                line = file.readline()
                if '<SerialNumber>' in line:
                    dataset_attrs['cndc01_sensor_sn'] = line[22:-16].replace(" ", "")                     
            elif '<!-- Frequency 2, Pressure, Digiquartz with TC -->' in line:
                line = file.readline()
                line = file.readline()
                if '<SerialNumber>' in line:
                    dataset_attrs['pres_sensor_sn'] = line[22:-16].replace(" ", "")  
            elif ('Oxygen, SBE 43 -->') in line:
            # elif ('<!-- A/D voltage 0, Oxygen, SBE 43 -->') in line:
                line = file.readline()
                line = file.readline()
                if '<SerialNumber>' in line:
                    dataset_attrs['dox1_sensor_sn'] = line[22:-16].replace(" ", "")  
            elif (', Fluorometer, WET Labs ECO-AFL/FL -->') in line:
                line = file.readline()
                line = file.readline()
                if '<SerialNumber>' in line:
                    dataset_attrs['fchla_sensor_sn'] = line[22:-16].replace(" ", "")                      
            elif (', Fluorometer, Chelsea Aqua 3 -->') in line:
                line = file.readline()
                line = file.readline()
                if '<SerialNumber>' in line:
                    dataset_attrs['fchla_sensor_sn'] = line[22:-16].replace(" ", "")                     
            elif (', Fluorometer, Chelsea UV Aquatracka -->') in line:
                line = file.readline()
                line = file.readline()
                if '<SerialNumber>' in line:
                    dataset_attrs['fchla_sensor_sn'] = line[22:-16].replace(" ", "")                        
            elif '*END*' in line:
                stop_trigger = True




        return dataset_attrs