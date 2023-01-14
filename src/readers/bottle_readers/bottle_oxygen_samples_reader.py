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

class BottleOxygenSamples(ReadersBase):
    def __init__(self, *args): 
        super(BottleOxygenSamples, self).__init__(*args)

        return                  
            
            
    # def get_input_files_list(self, files_path):
    #     files_list = glob.glob(files_path + '*.xlsx')
    #     return files_list
     
    # def load_data(self, file, df): 
    #     '''Loads data from oxygen titration analysis results contained in a xlsx file and returns it in a dataframe
    #     @param self: instance from BottleOxygenSamples class
    #     @param file: path to xlsx file
    #     @return: dataframe with contents of the xlsx file'''
        
    #     df_samples = pd.read_excel(open(file, 'rb'), sheet_name='export' ) 
    #     df = df.append(df_samples, ignore_index=True)
    #     df.reset_index(drop=True)
        
    #     #df = pd.read_csv(file, header=0,sep='\t')
    #     return df
                
    # def list_stations(self, df):
    #     '''Lists all stations available from the oxygen samples datafarme.'''
    #     stations_list = list(df[self.dox_ref_varnames_map['STATION_ID']].unique())
    #     return stations_list

    # def join_dox_ref_with_btl(self, ref_df, btl_df):
    #     ''' Join btl data with oxygen titration data in a single dataframe, so btl data and titration data are grouped by same bottle and sample ID.
    #     @param self: instance from BottleOxygenSamples class
    #     @param ref_df: titration analysis results dataframe
    #     @param btl_df: btl data dataframe
    #     @return: joined dataframes'''

        
    #     btl_df[self.dox_ref_varnames_map['DOX_INSITU']] = np.empty((len(btl_df),1),dtype=np.float64) 
    #     btl_df[self.dox_ref_varnames_map['DOX_INSITU_QC']] = np.empty((len(btl_df),1),dtype=np.int64) 
        
    #     ref_df = ref_df.reset_index(drop=True)
    #     for i in range(len(ref_df)):
    #         ref_value = str(ref_df.loc[i, self.dox_ref_varnames_map['DOX_INSITU']]) 
    #         ref_qc_value = str(ref_df.loc[i, self.dox_ref_varnames_map['DOX_INSITU_QC']])
    #         btl_df[self.dox_ref_varnames_map['DOX_INSITU']][btl_df.Bottle == str(ref_df.loc[i, self.dox_ref_varnames_map['BOTTLE_NUM']])] = ref_value         
    #         btl_df[self.dox_ref_varnames_map['DOX_INSITU_QC']][btl_df.Bottle == str(ref_df.loc[i, self.dox_ref_varnames_map['BOTTLE_NUM']])] = ref_qc_value
    #     btl_df[self.dox_ref_varnames_map['DOX_INSITU']].replace(0,np.nan,inplace=True)
    #     btl_df[self.dox_ref_varnames_map['DOX_INSITU_QC']].replace(0,9,inplace=True)
    #     return btl_df