#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Oct  5 08:02:46 2022

@author: a33272
"""
import glob
import pandas as pd
import numpy as np

class ReadersBase():
    def __init__(self, config, *args):  

        self.varnames_map = None
   

        self.bottle_varnames_map_dfn_odv = {'PRES': 'PRE',
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

        self.bottle_varnames_map_imrop = {'PRES': 'PRE',
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

        # self.bottle_varnames_map_s2d = {'STATION_ID': 'Station',
        #                               'SAMPLE_ID': 'Sample ID',
        #                               'BOTTLE_NUM': 'Niskin',
        #                               'DATE': 'Date',
        #                               'TIME': 'Time',
        #                               'LAT': 'Latitude',
        #                               'LON': 'Longitude',
        #                               'DEPH':'Depth',
        #                               'PSAL00': 'Salinity',
        #                               'TEMP00': 'Temperature',
        #                               'DOX1': 'Dissolved Oxygen',
        #                               'PH': 'pH 25°C',
        #                               'STATION_DEPTH': 'bot.depth',
        #                               'PSAL_INSITU_AVG': 'avg_psal',
        #                               'PSAL_INSITU_DIFF': 'diff_psal',
        #                               'RESIDUALS_PSAL00': 'residuals_psal00',
        #                               'RESIDUALS_PSAL00_CORR': 'residuals_psal00_corr',
        #                        }        
        self.btl_varnames_map = {'STATION_ID': 'station',
                                  'DATE': 'Date',
                                  'BOTTLE_NUM': 'Bottle',
                                  'PRES': 'PrDM',
                                  'DEPH': 'DepSW',
                                  'PSAL00': 'Sal00',
                                  'PSAL01': None,
                                  'TEMP00': 'T090C', 
                                  'TEMP01': None,
                                  'CNDC00': 'C0S/m',
                                  'CNDC01': None,
                                  'DOXV': 'Sbeox0V',
                                  'DOX1': 'Sbeox0ML/L',
                                  'FCHLA': 'FlECO-AFL',
                                  #'FCHLA': 'FlCUVA',
                                  'LAT': 'LATITUDE',
                                  'LON': 'LONGITUDE',
                                  'STATION_DEPTH': 'Bot. Depth [m]',
                                  'STATION_SHIP_LOG': None,
                                }

        self.btl_var_attrs_map = {'TEMP00_SENSOR_SN': 'temp00_sensor_sn',
                                  'TEMP01_SENSOR_SN': 'temp01_sensor_sn',
                                  'CNDC00_SENSOR_SN': 'cndc00_sensor_sn',
                                  'CNDC01_SENSOR_SN': 'cndc01_sensor_sn',
                                  'PRES_SENSOR_SN': 'pres_sensor_sn',
                                  'DOX1_SENSOR_SN': 'dox1_sensor_sn',
                                  'FCHLA_SENSOR_SN': 'fchla_sensor_sn',
                                  }    
        
        self.psal_ref_varnames_map = {'STATION_ID': 'Station',
                                      'SAMPLE_ID': 'Sal_Bottle',
                                      'BOTTLE_NUM': 'Niskin',
                                      'PSAL_INSITU_AVG': 'Bottle_Ave',
                                      'PSAL_INSITU_DIFF': 'Bottle_Sal1-Sal2',
                                      'PSAL_INSITU_AVG_QC': 'Flag',

                                     }         

        self.dox_ref_varnames_map = {'STATION_ID': 'Station',
                                      'SAMPLE_ID': 'O2_flask',
                                      'BOTTLE_NUM': 'Bottle',
                                      'DOX_INSITU': 'Winkler',                                      
                                      'DOX_INSITU_QC': 'SeaDataNet_Flag',
                                     }  

        self.chla_ref_varnames_map = {'STATION_ID': 'Station',
                                      'SAMPLE_ID': 'Sample ID',
                                      'BOTTLE_NUM': 'Niskin',                                                                     
                                      'FCHLA_INSITU': 'Chlorophyll a µg/l', 
                                      'FCHLA_INSITU_QC': 'ChlA Flag',
                                     }           
        
        self.talk_ref_varnames_map = {'STATION_ID': 'Station',
                                      'SAMPLE_ID': 'Sample ID',
                                      'BOTTLE_NUM': 'Niskin',
                                      'TALK_INSITU': 'Total Alkalinity',                                      
                                      'TALK_INSITU_QC': 'Talk Flag',
                                      }

        self.ph_ref_varnames_map = {'STATION_ID': 'Station',
                                      'SAMPLE_ID': 'Sample ID',
                                      'BOTTLE_NUM': 'Niskin',
                                      'PH_INSITU': 'pH 25°C',                                      
                                      'PH_INSITU_QC': 'Sample Flag',
                                      }                                      




    def get_input_files_list(self, files_path, file_format):
        files_list = glob.glob(files_path + file_format)
        return files_list

    def load_data_from_xls(self, file, df): 
        '''Loads data from psal, dox, talk, chla and pH analysis results contained in a xlsx or xlsm file and returns it in a dataframe
        @param self: instance from ReadersBase class
        @param file: path to xlsm file
        @return: dataframe with contents of the xlsx/xlsm file'''
        
        df_samples = pd.read_excel(open(file, 'rb'), sheet_name='export', header=[0]) 
        df = df.append(df_samples, ignore_index=True)
        df.reset_index(drop=True)

        return df
    

    def list_stations(self, df, varname_map_station_id):
        '''Lists all stations available from the different psal, dox, talk, chla and pH samples datafarmes.
        @param self: instance from ReadersBase class
        @param df: dataframe containing parrticular variable bottle samples
        @param varname_map_station_id: mapped STATION_ID variable name depending on the type of sample
        @return: dataframe with contents of the xlsx/xlsm file'''
        
        stations_list = list(df[varname_map_station_id].unique())
        
        return stations_list


    def subset_samples_per_station(self, station_id, df, varname_map_station_id, subset_name, dataset):
        '''Subsets the input sample (psal, dox, talk, chla and pH) dataframe for a specific station_id.
        @param self: instance from ReadersBase class
        @param df: dataframe containing parrticular variable bottle samples with all stations
        @param varname_map_station_id: mapped STATION_ID variable name depending on the type of sample
        @subset_name: name for the key that will contain the subset per each station
        @dataset: dictionary containing exisiting station_id subsets
        @return: dictionary containing the station_id subset'''
        
        station_df = df.copy()
        station_df = station_df[station_df[varname_map_station_id] == station_id]
        
        station_name = 'sta' + str(station_id).zfill(4)
        dataset[station_name] = {}
        dataset[station_name][subset_name] = station_df    
        return dataset


    def join_ref_with_btl(self, ref_df, btl_df, varname_map, varname_qc_map, varname_map_bottle_num):
        ''' Join btl data with pH data in a single dataframe, so btl data and pH data are grouped by same bottle and sample ID.
        @param self: instance from BottlePhSamples class
        @param ref_df: pH analysis results dataframe
        @param btl_df: btl data dataframe
        @return: joined dataframes'''
       
        btl_df[varname_map] = np.empty((len(btl_df),1),dtype=np.float64) 
        btl_df[varname_qc_map] = np.empty((len(btl_df),1),dtype=np.int64) 
        
        ref_df = ref_df.reset_index(drop=True)
        for i in range(len(ref_df)):
            ref_value = str(ref_df.loc[i, varname_map]) 
            ref_qc_value = str(ref_df.loc[i, varname_qc_map])
            btl_df[varname_map][btl_df.Bottle == str(ref_df.loc[i, varname_map_bottle_num])] = ref_value         
            btl_df[varname_qc_map][btl_df.Bottle == str(ref_df.loc[i, varname_map_bottle_num])] = ref_qc_value
        btl_df[varname_map].replace(0,np.nan,inplace=True)
        btl_df[varname_qc_map].replace(0,9,inplace=True)
        
        return btl_df
                                      
    # def set_varnames_map(self, config):
    #     if config['Settings']['IncludeSbeBtl'] == '1':
    #         self.varnames_map = self.cnv_varnames_map_dfn_v0
    
    
    # def get_varnames_map(self):        
    #     return self.varnames_map        