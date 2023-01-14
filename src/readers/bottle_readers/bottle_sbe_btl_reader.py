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
from seabird.cnv import fCNV
from datetime import datetime

from readers.bottle_readers.bottle_readers_base import ReadersBase as ReadersBase

class BottleSbeBtl(ReadersBase):
    def __init__(self, *args): 
        super(BottleSbeBtl, self).__init__(*args)

        
        return                  
            
            
    def get_input_files_list(self, files_path):
        files_list = glob.glob(files_path + '*.btl')
        return files_list
     
        
    def load_data(self, btl_file, config):
        '''Loads data from the original btl files.'''
        
        def dms2dd(degrees, minutes, direction):
            ''' converts degrees and minutes to decimal degrees'''
            dd = float(degrees) + float(minutes)/60
            if direction == 'S' or direction == 'W':
                dd *= -1
            return dd;
               
        #btl_files_list = glob.glob(btl_files_path + '*.btl')        
        
        columns = ['station', self.btl_varnames_map['LAT'], 
                   self.btl_varnames_map['LON'],                   
                   ]
        
        attrs = {}

        fname = os.path.basename(btl_file)[:-4]          
        file  = open(btl_file, 'r', encoding='cp1250')
        stop_trigger = False
    
        # Read file until the headers
        while stop_trigger == False:
            line = file.readline()
            if '* NMEA Latitude' in line:
                coord = line[18:-1]
                dd = coord[0:2]
                mm = coord[3:8]
                comp = coord[-1]
                lat = dms2dd(dd, mm, comp)
                attrs['LATITUDE'] = lat
            elif '* NMEA Longitude' in line:
                coord = line[19:-1]
                dd = coord[0:3]
                mm = coord[4:9]
                comp = coord[-1]
                lon = dms2dd(dd, mm, comp) 
                attrs['LONGITUDE'] = lon
            elif '* NMEA UTC (Time)' in line:  
                date = line[20:31] 
                date = datetime.strptime(date, '%b %d %Y')
                date = date.strftime('%Y-%m-%d')
                date = datetime.strptime(date, '%Y-%m-%d')
                attrs['datetime'] = date
            elif 'Bottle' in line:
                columns.extend(re.split(' +', line)) # split first headers using one or more spaces as separator
                columns = [x for x in columns if x.strip()] # remove empty fields in the list
                columns = [x.replace('\n','') for x in columns] # remove \n from last column name
                df = pd.DataFrame(columns=columns)
                line = file.readline() #second eader line to skip

            elif '<!-- Frequency 0, Temperature -->' in line:
                line = file.readline()
                line = file.readline()
                if '<SerialNumber>' in line:
                    attrs['temp00_sensor_sn'] = line[22:-16].replace(" ", "")  
            elif '<!-- Frequency 3, Temperature, 2 -->' in line:
                line = file.readline()
                line = file.readline()
                if '<SerialNumber>' in line:
                    attrs['temp01_sensor_sn'] = line[22:-16].replace(" ", "")                     
            elif '<!-- Frequency 1, Conductivity -->' in line:
                line = file.readline()
                line = file.readline()
                if '<SerialNumber>' in line:
                    attrs['cndc00_sensor_sn'] = line[22:-16].replace(" ", "")  
            elif '<!-- Frequency 4, Conductivity, 2 -->' in line:
                line = file.readline()
                line = file.readline()
                if '<SerialNumber>' in line:
                    attrs['cndc01_sensor_sn'] = line[22:-16].replace(" ", "")                     
            elif '<!-- Frequency 2, Pressure, Digiquartz with TC -->' in line:
                line = file.readline()
                line = file.readline()
                if '<SerialNumber>' in line:
                    attrs['pres_sensor_sn'] = line[22:-16].replace(" ", "")  
            elif ('Oxygen, SBE 43 -->') in line:
            # elif ('<!-- A/D voltage 0, Oxygen, SBE 43 -->') in line:
                line = file.readline()
                line = file.readline()
                if '<SerialNumber>' in line:
                    attrs['dox1_sensor_sn'] = line[22:-16].replace(" ", "")  
            elif (', Fluorometer, WET Labs ECO-AFL/FL -->') in line:
                line = file.readline()
                line = file.readline()
                if '<SerialNumber>' in line:
                    attrs['fchla_sensor_sn'] = line[22:-16].replace(" ", "")                      
            elif (', Fluorometer, Chelsea Aqua 3 -->') in line:
                line = file.readline()
                line = file.readline()
                if '<SerialNumber>' in line:
                    attrs['fchla_sensor_sn'] = line[22:-16].replace(" ", "")                     
            elif (', Fluorometer, Chelsea UV Aquatracka -->') in line:
                line = file.readline()
                line = file.readline()
                if '<SerialNumber>' in line:
                    attrs['fchla_sensor_sn'] = line[22:-16].replace(" ", "")                        
            elif '# bottlesum_ox_tau_correction = yes' in line:
                stop_trigger = True        

        # Read data after header
        while stop_trigger == True:
            line = file.readline() 
            if line == '':
               stop_trigger = False 
            else:       
               if '    Bottle' in line:
                   columns.extend(re.split(' +', line)) # split first headers using one or more spaces as separator
                   columns = [x for x in columns if x.strip()] # remove empty fields in the list
                   columns = [x.replace('\n','') for x in columns] # remove \n from last column name
                   df = pd.DataFrame(columns=columns)
                   line = file.readline() #second eader line to skip
               else:                    
                   data_line = [fname[3:]]          
                   data_line.append(str(lat))
                   data_line.append(str(lon))
                   data_line.extend(re.split('  +', line[:-7]))
                   data_line  = [x for x in data_line if x.strip()]
                   df = df.append(pd.Series(data_line, index=df.columns), ignore_index=True)
        #           data[fname] = re.split('  +', line)
        #           data[fname] = [x for x in data[fname] if x.strip()]
                   line = file.readline() # skip severy second line of data
              
        file.close()
        df[self.btl_varnames_map['STATION_ID']] = df[self.btl_varnames_map['STATION_ID']].astype(int)
        df[self.btl_varnames_map['STATION_ID']] = df[self.btl_varnames_map['STATION_ID']].astype(str)
        df[self.btl_varnames_map['BOTTLE_NUM']] = df[self.btl_varnames_map['BOTTLE_NUM']].astype(int)
        df[self.btl_varnames_map['BOTTLE_NUM']] = df[self.btl_varnames_map['BOTTLE_NUM']].astype(str)
        return df, attrs        

