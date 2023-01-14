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

class BottlePhSamples(ReadersBase):
    def __init__(self, *args): 
        super(BottlePhSamples, self).__init__(*args)

        return                  
            
            
    # def get_input_files_list(self, files_path):
    #     files_list = glob.glob(files_path + '*.xlsm')
    #     return files_list
     
    # def load_data(self, file, df): 
    #     '''Loads data from pH analysis results contained in a xlsm file and returns it in a dataframe
    #     @param self: instance from BottlePhSamples class
    #     @param file: path to xlsm file
    #     @return: dataframe with contents of the xlsx file'''
        
    #     df_samples = pd.read_excel(open(file, 'rb'), sheet_name='export', header=[0]) 
    #     df = df.append(df_samples, ignore_index=True)
    #     df.reset_index(drop=True)

        
    #     #df = pd.read_csv(file, header=0,sep='\t')
    #     return df
                
    # def list_stations(self, df):
    #     '''Lists all stations available from the pH samples datafarme.'''
    #     stations_list = list(df[self.ph_ref_varnames_map['STATION_ID']].unique())
    #     return stations_list

    # def join_ph_ref_with_btl(self, ref_df, btl_df):
    #     ''' Join btl data with pH data in a single dataframe, so btl data and pH data are grouped by same bottle and sample ID.
    #     @param self: instance from BottlePhSamples class
    #     @param ref_df: pH analysis results dataframe
    #     @param btl_df: btl data dataframe
    #     @return: joined dataframes'''

        
    #     btl_df[self.ph_ref_varnames_map['PH_INSITU']] = np.empty((len(btl_df),1),dtype=np.float64) 
    #     btl_df[self.ph_ref_varnames_map['PH_INSITU_QC']] = np.empty((len(btl_df),1),dtype=np.int64) 
        
    #     ref_df = ref_df.reset_index(drop=True)
    #     for i in range(len(ref_df)):
    #         ref_value = str(ref_df.loc[i, self.ph_ref_varnames_map['PH_INSITU']]) 
    #         ref_qc_value = str(ref_df.loc[i, self.ph_ref_varnames_map['PH_INSITU_QC']])
    #         btl_df[self.ph_ref_varnames_map['PH_INSITU']][btl_df.Bottle == str(ref_df.loc[i, self.ph_ref_varnames_map['BOTTLE_NUM']])] = ref_value         
    #         btl_df[self.ph_ref_varnames_map['PH_INSITU_QC']][btl_df.Bottle == str(ref_df.loc[i, self.ph_ref_varnames_map['BOTTLE_NUM']])] = ref_qc_value
    #     btl_df[self.ph_ref_varnames_map['PH_INSITU']].replace(0,np.nan,inplace=True)
    #     btl_df[self.ph_ref_varnames_map['PH_INSITU_QC']].replace(0,9,inplace=True)
    #     return btl_df