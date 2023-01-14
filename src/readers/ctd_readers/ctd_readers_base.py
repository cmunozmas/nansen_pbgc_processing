#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Oct  5 08:02:46 2022

@author: a33272
"""


class ReadersBase():
    def __init__(self, config, *args):  

        self.varnames_map = None
        self.varnames_trigger = True
        self.cnv_varnames_map_dfn_v0 = {'SCAN':['scan'],
                                 'PRES': ['PRES', 'pr'],
                                 'PSAL00': ['PSAL','sal00'],
                                 'PSAL01': ['PSAL2'],
                                 'TEMP00': ['temperature', 't068','t0'],
                                 'TEMP01': ['t168C'], 
                                 'CNDC00': ['CNDC','c0','c0S/m'],
                                 'CNDC01': ['CNDC2'],
                                 'DOXV': ['oxygenvoltage'],
                                 'DOX1': ['oxygen_ml_L','oxML/L'],
                                 'FCHLA': ['flC','flECO-AFL','fluorescence'],
                                 'FCHLA_CORR': ['flECO-AFL_corr'],                                 
                                 'PAR': ['par'],
                                 'SIGT': ['sigma_t'],
                                 'SVEL': ['avgsvCM'],
                                 'SVEL1': ['soundspeed','svW'],
                                }          
     
        # self.cnv_var_attrs_map_dfn_v0 = {'TEMP00_SENSOR_SN': 'temp00_sensor_sn',
        #                           'CNDC00_SENSOR_SN': 'cndc00_sensor_sn',
        #                           'PRES_SENSOR_SN': 'pres_sensor_sn',
        #                           'DOX1_SENSOR_SN': 'dox1_sensor_sn',
        #                           'FCHLA_SENSOR_SN': 'fchla_sensor_sn',
        #                                  }
        

        self.cnv_varnames_map_dfn_v1 = {'SCAN':'scan',
                                        'PRES': 'PRES',
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
                                 #'FCHLA': 'flC',/test_data/ctd/procOutput/research_vessel/ctd/1996/1996410/L1A/EAF-NANSEN_C1996410_CTD_L1A_1996-10-12_sta0993.nc
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

        self.cnv_varnames_map_dfn_odv = {'PRES': 'PRE',
                                 'PSAL00': 'SAL',
                                 'PSAL01': 'SAL.1',
                                 'TEMP00': 'TEM', 
                                 'TEMP01': 'TEM.1',
                                 'DOXV': None,
                                 'DOX1': 'OXY',
                                 'FCHLA': 'FLU',                                 
                                 'PAR': 'PAR',
                                 'CNDC00': None,
                                 'CNDC01': None,
                                 'ALT': 'ALT',
                                 'STATION_DEPTH': 'Bot. Depth [m]',  
                                 'STATION_NAME': 'station_name',
                                 'STATION_SHIP_LOG': None,
                                }        

        self.cnv_varnames_map_imrop = {'PRES': 'PRE',
                                 'PSAL00': 'SAL',
                                 'PSAL01': None,
                                 'TEMP00': 'TEM', 
                                 'TEMP01': None,
                                 'DOXV': None,
                                 'DOX1': 'OXY',
                                 'FCHLA': 'FLU',                                 
                                 'PAR': None,
                                 'CNDC00': None,
                                 'CNDC01': None,
                                 'ALT': None,
                                 'STATION_DEPTH': 'Bot. Depth [m]',  
                                 'STATION_NAME': 'station_name',
                                 'STATION_SHIP_LOG': None,
                                }           
        
    def set_varnames_map(self, config):
        if config['Settings']['CtdFormat'] == '0':
            self.varnames_map = self.cnv_varnames_map_dfn_v0
        elif config['Settings']['CtdFormat'] == '1':
            self.varnames_map = self.cnv_varnames_map_dfn_v1
        elif config['Settings']['CtdFormat'] == '2':
            self.varnames_map = self.cnv_varnames_map_dfn_odv    
        elif config['Settings']['CtdFormat'] == '3':
            self.varnames_map = self.cnv_varnames_map_imrop              
        return self.varnames_map    
    
    def get_varnames_map(self):        
        return self.varnames_map       
    
    def set_individual_varnames_map(self, data_dict_varnames):
        '''Reduces the possible varnames of the varnames_map to 1 possible varname contained in loaded data'''
        #data_dict_varnames = list(data_dict.keys())
        self.varnames_map = self.varnames_map.copy()
        for key in self.varnames_map:
            varname = [value for value in self.varnames_map[key] if value in data_dict_varnames]
            if len(varname) > 0:
                self.varnames_map[key] = varname[0]
            else:
                self.varnames_map[key] = None
        #self.varnames_trigger = False
        self.varnames_trigger = True
        
        
        return self.varnames_map