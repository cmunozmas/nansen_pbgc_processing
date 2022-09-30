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
       

        self.cnv_varnames_map_dfn_odv = {'PRES': 'PRE',
                                 'PSAL00': 'SAL',
                                 'PSAL01': 'SAL1',
                                 'TEMP00': 'TEM', 
                                 'TEMP01': 'TEM1', 
                                 'DOX1': 'OXY',
                                 'FCHLA': 'FLU',                                 
                                 'PAR': 'PAR',
                                 'STATION_DEPTH': 'station_depth',
                               
                                }          
     
        # self.cnv_var_attrs_map = {'TEMP00_SENSOR_SN': 'temp00_sensor_sn',
        #                           'CNDC00_SENSOR_SN': 'cndc00_sensor_sn',
        #                           'PRES_SENSOR_SN': 'pres_sensor_sn',
        #                           'DOX1_SENSOR_SN': 'dox1_sensor_sn',
        #                           'FCHLA_SENSOR_SN': 'fchla_sensor_sn',
        #                                   }
       
                   
            
    def set_cnv_varnames_map(self, config):
        if config['Settings']['CtdFormat'] == '2':
            self.cnv_varnames_map = self.cnv_varnames_map_dfn_odv

            
    def get_input_files_list(self, files_path):
        files_list = glob.glob(files_path + '*.txt')

        return files_list
        
        
    def load_data(self, file_path, config):
        '''Loads odv files produced fro quickcast.'''
            
        return df, attrs

    

