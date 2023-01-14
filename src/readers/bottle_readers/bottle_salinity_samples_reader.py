#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Oct 12 04:12:00 2020

@author: a33272
"""
import os
import re
import glob
import numpy as np
import pandas as pd

from readers.bottle_readers.bottle_readers_base import ReadersBase as ReadersBase

class BottleSalinitySamples(ReadersBase):
    def __init__(self, *args): 
        super(BottleSalinitySamples, self).__init__(*args)

        
        return                  
            
            
    # def get_input_files_list(self, files_path):
    #     files_list = glob.glob(files_path + '*.xlsx')
    #     return files_list
     
    # def load_data(self, file, df): 
    #     '''Loads data from portasal analysis results contained in a xlsx file and returns it in a dataframe
    #     @param self: instance from BottleSalinitySamples class
    #     @param file: path to csv file
    #     @return: dataframe with contents of the xlsx file'''
        
    #     df_samples = pd.read_excel(open(file, 'rb'), sheet_name='export') 
    #     df = df.append(df_samples, ignore_index=True)
    #     df.reset_index(drop=True)
        
    #     #df = pd.read_csv(file, header=0,sep='\t')
    #     return df
                
    # def list_stations(self, df):
    #     '''Lists all stations available from the salinity samples datafarme.'''
    #     stations_list = list(df[self.psal_ref_varnames_map['STATION_ID']].unique())
    #     return stations_list

    # def join_psal_ref_with_btl(self, portasal_df, btl_df):
    #     ''' Join btl data with portasal data in a single dataframe, so btl data and portasal data are grouped by same bottle and sample ID.
    #     @param self: instance from SalinityFieldCalib class
    #     @param portasal_df: portasal analysis results dataframe
    #     @param btl_df: btl data dataframe
    #     @return: joined dataframes'''

        
    #     btl_df[self.psal_ref_varnames_map['PSAL_INSITU_AVG']] = np.empty((len(btl_df),1),dtype=np.float64) 
    #     btl_df[self.psal_ref_varnames_map['PSAL_INSITU_AVG_QC']] = np.empty((len(btl_df),1),dtype=np.int64) 
        
    #     portasal_df = portasal_df.reset_index(drop=True)
    #     for i in range(len(portasal_df)):
    #         portasal_psal_value = str(portasal_df.loc[i, self.psal_ref_varnames_map['PSAL_INSITU_AVG']]) 
    #         portasal_psal_qc_value = str(portasal_df.loc[i, self.psal_ref_varnames_map['PSAL_INSITU_AVG_QC']])
    #         btl_df[self.psal_ref_varnames_map['PSAL_INSITU_AVG']][btl_df.Bottle == str(portasal_df.loc[i, self.psal_ref_varnames_map['BOTTLE_NUM']])] = portasal_psal_value         
    #         btl_df[self.psal_ref_varnames_map['PSAL_INSITU_AVG_QC']][btl_df.Bottle == str(portasal_df.loc[i, self.psal_ref_varnames_map['BOTTLE_NUM']])] = portasal_psal_qc_value
    #     btl_df[self.psal_ref_varnames_map['PSAL_INSITU_AVG']].replace(0,np.nan,inplace=True)
    #     btl_df[self.psal_ref_varnames_map['PSAL_INSITU_AVG_QC']].replace(0,9,inplace=True)
    #     return btl_df