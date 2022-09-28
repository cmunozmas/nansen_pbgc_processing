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


class CtdQuickcastOdv:
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
       
                   
            
            
    def get_input_files_list(self, files_path):
        files_list = glob.glob(files_path + '*.txt')

        return files_list
        
        
    def load_data(self, file_path, config):
        '''Loads odv files produced fro quickcast.'''
            
        return df, attrs

    

