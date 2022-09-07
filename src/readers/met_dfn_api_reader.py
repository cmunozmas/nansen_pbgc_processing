#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Dec  3 08:35:15 2021

@author: a33272
"""

import re
import glob
import numpy as np
import pandas as pd
import json
import requests
from datetime import datetime



class MeteoDfnApi:
    def __init__(self, config): 
        #self.main_path      = config['Path']['MainPath']
        self.api_web_url = 'http://toktlogger-nansen.hi.no/api/'

        #self.api_web_url = 'http://toktlogger-nansen.hi.no/api/instrumentData/inPeriod?after=2021-12-04T12%3A55%3A36.023Z&before=2021-12-04T13%3A55%3A36.023Z&mappingIds=longitude%2Clatitude%2Cairpressure%2Cairtemp%2CSolar%20rad%2Chumidity%2Cwinddirection%2Cwindspeed%2Cdirection_gyro%2CVessel%20speed&format=json


        
        self.mappingnavn_map = {'LON': 'longitude',
                                'LAT': 'latitude',
                                'TRUE_TRACK': 'direction_gyro',
                                'GROUND_SPEED': 'Vessel speed',
                                'AIR_TEMP': 'airtemp',
                                'SOLAR_RAD': 'Solar rad',
                                'WIND_SPEED': 'windspeed',
                                'WIND_DIR': 'winddirection',
                                'REL_HUM': 'humidity',
                                'AIR_PRES' : 'airpressure', 
                                }
        
        self.df_columns = ['DATE', 'TIME'] + list(self.mappingnavn_map.keys())

    # def get_input_files_list(self, files_path):
    #     files_list = glob.glob(files_path + '*.json')
    #     return files_list
        
    def load_data(self, file_path):
        '''Loads json file extracted from API'''
        df_json = pd.read_json(file_path)
        return df_json

    def set_url(self, date_start, date_end):
        date_start = date_start.replace(':','%3A') +'.023Z'
        date_end = date_end.replace(':','%3A') +'.023Z'
        url = self.api_web_url + 'instrumentData/inPeriod?after=' + date_start + '&before=' + date_end + '&mappingIds=longitude%2Clatitude%2Cairpressure%2Cairtemp%2CSolar%20rad%2Chumidity%2Cwinddirection%2Cwindspeed%2Cdirection_gyro%2CVessel%20speed&format=json'
        return url
    
    def execute_api_query(self, url):
        response = requests.get(url)
        data = response.json()
        return data
    
    def json_to_df(self, df_json):
        # create new dataframe with specific column names
        df = (df_json.groupby(['timestamp','mappingName']).numericValue.first().unstack())
        df = df.reset_index()
        df.timestamp = np.array(df.timestamp, dtype='datetime64[m]')
        df=df.groupby('timestamp').mean()
        df = df.reset_index()        
        return df