#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Oct  6 14:44:26 2022

@author: a33272
"""


import glob
import numpy as np
import pandas as pd
from readers.readers_base import ReadersBase as ReadersBase

class CtdAccessDbImrop(ReadersBase):
    def __init__(self, *args): 
        super(CtdAccessDbImrop, self).__init__(*args)

        return
         
    def get_input_files_list(self, cruise_id, files_path):
        files_list = glob.glob(files_path + cruise_id + '.txt')
        return files_list

    def get_input_station_files_list(self, files_path):
        files_list = glob.glob(files_path + 'Sta*.txt')
        return files_list
        
    def split_survey_imrop_into_stations(self, files_list, data_in_path, config):
        self.varnames_map = self.set_varnames_map(config)
        # open the all survey_csv file
        df = pd.DataFrame()
        df = pd.read_csv(files_list, delimiter='\t')
        df = df.fillna(method='ffill')

         # change the cruise type to string
        df= df.astype({"Cruise": str})

        # change the station type to int
        df= df.astype({"Station": int})

         #Change the date column to datetime
        df.rename(columns = {'yyyy-mm-dd hh:mm':'Date'}, inplace = True)
        df['Date']= pd.to_datetime(df['Date'])

        if self.varnames_map['FCHLA'] in df.columns:
              df.loc[~(df[self.varnames_map['FCHLA']] > 0), self.varnames_map['FCHLA']]=np.nan
        if self.varnames_map['TEMP00'] in df.columns:      
            df.loc[~(df[self.varnames_map['TEMP00']] > 0), self.varnames_map['TEMP00']]=np.nan
        if self.varnames_map['TEMP01'] in df.columns:      
            df.loc[~(df[self.varnames_map['TEMP01']] > 0), self.varnames_map['TEMP01']]=np.nan
        if self.varnames_map['PSAL00'] in df.columns:    
            df.loc[~(df[self.varnames_map['PSAL00']] > 0), self.varnames_map['PSAL00']]=np.nan
        if self.varnames_map['PSAL01'] in df.columns:    
            df.loc[~(df[self.varnames_map['PSAL01']] > 0), self.varnames_map['PSAL01']]=np.nan
        if self.varnames_map['ALT'] in df.columns:    
            df.loc[~(df[self.varnames_map['ALT']] > 0), self.varnames_map['ALT']]=np.nan            
        if self.varnames_map['PAR'] in df.columns:  
            df.loc[~(df[self.varnames_map['PAR']] > 0), self.varnames_map['PAR']]=np.nan
        if self.varnames_map['DOX1'] in df.columns:            
            df.loc[~(df[self.varnames_map['DOX1']] > 0), self.varnames_map['DOX1']]=np.nan

        # split 
        data= pd.DataFrame()
        for i in df['Station']:
            data= df.loc[df['Station'] == i]
            data.to_csv(data_in_path + 'Sta' + str(i).zfill(4) +'.txt', index=None, sep='\t')
        
        return
    
    
    def load_data(self, file_path, config):
        '''Loads stations files'''
        
        self.varnames_map = self.set_varnames_map(config)
        
        df = pd.DataFrame()
        df = pd.read_csv(file_path, delimiter='\t')

        df['Date']= pd.to_datetime(df['Date'], format='%Y%m%d %H:%M:%S')
        # select the first row of the df
        df_a= df.copy()
        df_a = df_a.iloc[:1]
       
        # clean every column different than lat, lon, date, station, cruise
        if self.varnames_map['FCHLA'] in df_a.columns:
            df_a = df_a.drop(self.varnames_map['FCHLA'], axis = 1)              
        if self.varnames_map['TEMP00'] in df_a.columns:      
            df_a = df_a.drop(self.varnames_map['TEMP00'], axis = 1) 
        if self.varnames_map['TEMP01'] in df_a.columns:      
            df_a = df_a.drop(self.varnames_map['TEMP01'], axis = 1) 
        if self.varnames_map['PSAL00'] in df_a.columns:    
            df_a = df_a.drop(self.varnames_map['PSAL00'], axis = 1) 
        if self.varnames_map['PSAL01'] in df_a.columns:    
            df_a = df_a.drop(self.varnames_map['PSAL01'], axis = 1) 
        if self.varnames_map['ALT'] in df_a.columns:    
            df_a = df_a.drop(self.varnames_map['ALT'], axis = 1)             
        if self.varnames_map['PAR'] in df_a.columns:  
            df_a = df_a.drop(self.varnames_map['PAR'], axis = 1) 
        if self.varnames_map['DOX1'] in df_a.columns:            
            df_a = df_a.drop(self.varnames_map['DOX1'], axis = 1) 
        if self.varnames_map['DOX1'] in df_a.columns:            
            df_a = df_a.drop(self.varnames_map['DOX1'], axis = 1)             
        if self.varnames_map['STATION_DEPTH'] in df_a.columns:            
            df_a = df_a.drop(self.varnames_map['STATION_DEPTH'], axis = 1)             
            
        #df_a = df_a.drop(["Bot. Depth [m]", 'Cruise', "PRE", 'TEM', 'SAL', 'OXY', 'FLU', 'PAR','TEM.1', 'SAL.1', 'ALT'], axis = 1) 
          # REPLACE station by filename
        df_a = df_a.astype({"Station": str})
        df_a['Station'] = df_a['Station'].replace([df_a['Station'][0]],'Sta0' + df_a['Station'][0] + '.txt')
       
         # rename column names
        df_a= df_a.rename(columns={'Station':'Filename', 'Longitude [degrees_east]':'LONGITUDE', 'Latitude [degrees_north]':'LATITUDE', 'Date':'datetime'})
         
          # df row into dict cqlled qttrs
        attrs=  df_a.to_dict(orient='records')
        attrs = attrs[0]
        return df, attrs

    def load_header_attrs(self, df, attrs):  
        
        attrs[self.varnames_map['STATION_DEPTH']] = df[self.varnames_map['STATION_DEPTH']].iat[0]
        attrs[self.varnames_map['STATION_DEPTH']] = str(attrs[self.varnames_map['STATION_DEPTH']])
        attrs[self.varnames_map['STATION_NAME']] = attrs['station'][3::].zfill(4)
        return attrs
        

