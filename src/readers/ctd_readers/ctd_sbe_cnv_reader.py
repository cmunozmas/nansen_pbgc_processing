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
import gsw
from readers.ctd_readers.ctd_readers_base import ReadersBase as ReadersBase

class CtdSbeCnv(ReadersBase):
    def __init__(self, *args): 
        super(CtdSbeCnv, self).__init__(*args)


        return                  
            
            
    def get_input_files_list(self, files_path):        
        
        files_list = [glob.glob(e, recursive=True) for e in [files_path +'/**/*.cnv', files_path +'/**/*.CNV']]
        if len(files_list[0]) > 0:
           files_list =  files_list[0]
        else:
           files_list =  files_list[1]
        
        files_list = sorted(files_list)
        #files_list = glob.glob(files_path + '*.cnv')
        #files_list = glob.glob(files_path + 'd*.cnv')
        #files_list = glob.glob(files_path + 'u*.cnv')
        return files_list
        
        
    def load_data(self, file_path, config):
        '''Loads cnv files using seabird library.'''
        #files_list = glob.glob(files_path + 'u*.cnv')
        # if config['Settings']['CtdSbeCnvFormat'] == '0':
        #     cnv_varnames_map = self.cnv_varnames_map_dfn_v0
        # elif config['Settings']['CtdSbeCnvFormat'] == '1':
        #     cnv_varnames_map = self.cnv_varnames_map_dfn_v1
        self.varnames_map = self.set_varnames_map(config)
        

        profile = fCNV(file_path)
        attrs = profile.attrs
        attrs_names = list(profile.attrs.keys())
        
        var_names = list(profile.keys())
 
        var_dict = dict((key, []) for key in var_names)      
        
        #if self.varnames_trigger == True:
            # Set the varmane_map for each specific rawInput file
        self.varnames_map = self.set_individual_varnames_map(var_names)
              
        if 'flECO-AFL' in var_dict:
            var_dict[self.varnames_map['FCHLA']] = var_dict.pop('flECO-AFL')
        elif 'flC' in var_dict:
            var_dict[self.varnames_map['FCHLA']] = var_dict.pop('flC')  
        elif 'fluorescence' in var_dict:
            var_dict[self.varnames_map['FCHLA']] = var_dict.pop('fluorescence')             
        for var_name in var_names:
            var = profile[var_name]
            for value in var:
                if not value:
                    value = None
                if (var_name == 'flECO-AFL') or (var_name == 'flC') or (var_name == 'fluorescence'):
                    var_dict[self.varnames_map['FCHLA']].append(value)
                else:
                    var_dict[var_name].append(value)
        for key in var_dict:
            var_dict[key].reverse()

#        # Only for SOCIB datasets        
#        r = len(var_dict['LATITUDE'])        
#        var_dict['DEPTH'] = var_dict['DEPTH'][r:]        
#        var_dict['PSAL'] = var_dict['PSAL'][r:]
#        var_dict['PSAL2'] = var_dict['PSAL2'][r:]
#        del var_dict['D2-D1,d']
#        del var_dict['secS-priS']
#        del var_dict['density']
            
        if self.varnames_map['SCAN'] in var_dict:
            len_scan = len(var_dict[self.varnames_map['SCAN']])
        
        for var_name in self.varnames_map:
            if self.varnames_map[var_name] in var_dict:
                len_var = int(len(var_dict[self.varnames_map[var_name]]))
                len_factor = int(len_var/len_scan)
                len_var_unique = int(len_var/len_factor)
                var_dict[self.varnames_map[var_name]] = var_dict[self.varnames_map[var_name]][-len_var_unique:]            
            
            
        # if self.varnames_map['DOX1'] in var_dict:
        #     len_var = int(len(var_dict[self.varnames_map['DOX1']]))
        #     len_factor = int(len_var/len_scan)
        #     len_var_unique = int(len_var/len_factor)
        #     var_dict[self.varnames_map['DOX1']] = var_dict[self.varnames_map['DOX1']][-len_var_unique:]
        # if self.varnames_map['PSAL00'] in var_dict:
        #     len_var = int(len(var_dict[self.varnames_map['PSAL00']]))
        #     len_factor = int(len_var/len_scan)
        #     len_var_unique = int(len_var/len_factor)
        #     var_dict[self.varnames_map['PSAL00']] = var_dict[self.varnames_map['PSAL00']][-len_var_unique:]
        # if self.varnames_map['SVEL'] in var_dict:
        #     len_var = int(len(var_dict[self.varnames_map['SVEL']]))
        #     len_factor = int(len_var/len_scan)
        #     len_var_unique = int(len_var/len_factor)
        #     var_dict[self.varnames_map['SVEL']] = var_dict[self.varnames_map['SVEL']][-len_var_unique:]            
        # if self.varnames_map['SVEL1'] in var_dict:
        #     len_var = int(len(var_dict[self.varnames_map['SVEL1']]))
        #     len_factor = int(len_var/len_scan)
        #     len_var_unique = int(len_var/len_factor)
        #     var_dict[self.varnames_map['SVEL1']] = var_dict[self.varnames_map['SVEL1']][-len_var_unique:]             

        df = pd.DataFrame.from_dict(var_dict)
        return df, attrs

    
    def load_header_attrs(self, file_path, dataset_attrs):      
        
        def dms2dd(degrees, minutes, direction):
            ''' converts degrees and minutes to decimal degrees'''
            dd = float(degrees) + float(minutes)/60
            if direction == 'S' or direction == 'W':
                dd *= -1
            return dd;
        
        file  = open(file_path, 'r', encoding='cp1250')
        stop_trigger = False
        # Read file until the END of the cnv file headers
        while stop_trigger == False:
            line = file.readline()
            if '* Station' in line:
                dum = line[11:-1].replace(" ", "")   
                dum = dum.replace("sta", "")
                dum = dum.zfill(4) # add zeros before if they are not
                dataset_attrs['station_name'] = dum
                
            elif '* Echodepth [m]:' in line:
                dataset_attrs['station_depth'] = line[17:-1].replace(" ", "")   
            elif '* Echodepth[m]:' in line:
                dataset_attrs['station_depth'] = line[16:-1].replace(" ", "")   
            elif '* Echodepth:' in line:
                dataset_attrs['station_depth'] = line[13:-1].replace(" ", "") 
            elif '* Bottom Depth [m]:' in line:
                dataset_attrs['station_depth'] = line[20:-1].replace(" ", "")

            elif '* Latitude:' in line:
                regexp = '\* Latitude:\s+(\w{1})(\d+)\s+(\d+)'
                match = re.search(regexp, line)                
                dd = match.group(2)
                mm = match.group(3)
                comp = match.group(1)
                lat = dms2dd(dd, mm, comp)
                dataset_attrs['LATITUDE'] = lat
            elif '* Longitude:' in line:
                regexp = '\* Longitude:\s+(\w{1})(\d+)\s+(\d+)'
                match = re.search(regexp, line)                
                dd = match.group(2)
                mm = match.group(3)
                comp = match.group(1)
                lon = dms2dd(dd, mm, comp) 
                dataset_attrs['LONGITUDE'] = lon   
                
            # elif '** Log:' in line:
            #     dataset_attrs['ship_log'] = line[7:-1].replace(" ", "")  
            # elif '** Air-temp (dry):' in line:
            #     dataset_attrs['air_temp'] = line[18:-1].replace(" ", "")                  
            # elif '** Air-Temp(Dry):' in line:
            #     dataset_attrs['air_temp'] = line[17:-1].replace(" ", "") 
            # elif '** Weather Sky:' in line:
            #     reg = re.match(r"(\*\* Weather Sky:)\s*([0-9]*)\s*([0-9]*)(\n)", line)
            #     dataset_attrs['weather_code'] = reg.group(2)                  
            #     dataset_attrs['sky_code'] = reg.group(3)                
            # elif '** Wind-Dir Force:' in line:
            #     reg = re.match(r"(\*\* Wind-Dir Force:)\s*([0-9]*)\s*([0-9]*)(\n)", line)
            #     dataset_attrs['winddir_code'] = reg.group(2)                     
            #     dataset_attrs['windforce_code'] = reg.group(3)                
            # elif '** Wind-Dir Force(m/s):' in line:
            #     reg = re.match(r"(\*\* Wind-Dir Force\(m\/s\):)\s*([0-9]*)\s*([0-9]*)", line)
            #     dataset_attrs['winddir_code'] = reg.group(2)                     
            #     dataset_attrs['windforce_code'] = reg.group(3)      
            # elif '** Wind-Dir/Force:' in line:
            #     reg = re.match(r"(\*\* Wind-Dir/Force:)\s*([0-9]*)\s*([0-9]*)", line)
            #     dataset_attrs['winddir_code'] = reg.group(2)                     
            #     dataset_attrs['windforce_code'] = reg.group(3)   
            # elif '** Sea:' in line:
            #     reg = re.match(r"(\*\* Sea:)\s*([0-9]*)(\n)", line)
            #     dataset_attrs['sea_code'] = reg.group(2)           
            # elif '** Sea Ice:' in line:
            #     reg = re.match(r"(\*\* Sea Ice:)\s*([0-9]*)\s+([0-9]*)", line)
            #     dataset_attrs['sea_code'] = reg.group(2)   
                
                
                
            elif '# sensor 0 = Frequency  0  temperature' in line:
                dataset_attrs['temp00_sensor_sn'] = line[40:44].replace(" ", "") 
            elif '# sensor 1 = Frequency  1  conductivity' in line:
                dataset_attrs['cndc00_sensor_sn'] = line[41:45].replace(" ", "")                 
            elif '# sensor 2 = Frequency  2  pressure' in line:
                dataset_attrs['pres00_sensor_sn'] = line[37:42].replace(" ", "")                  
            elif '# sensor 3 = Extrnl Volt  0  Oxygen' in line:
                dataset_attrs['dox1_sensor_sn'] = line[51:55].replace(" ", "") 
                
            elif '<!-- Frequency 0, Temperature -->' in line:
                line = file.readline()
                line = file.readline()
                if '<SerialNumber>' in line:
                    dataset_attrs['temp00_sensor_sn'] = line[22:-16].replace(" ", "")  
            elif '<!-- Frequency 3, Temperature, 2 -->' in line:
                line = file.readline()
                line = file.readline()
                if '<SerialNumber>' in line:
                    dataset_attrs['temp01_sensor_sn'] = line[22:-16].replace(" ", "")                     
            elif '<!-- Frequency 1, Conductivity -->' in line:
                line = file.readline()
                line = file.readline()
                if '<SerialNumber>' in line:
                    dataset_attrs['cndc00_sensor_sn'] = line[22:-16].replace(" ", "")  
            elif '<!-- Frequency 4, Conductivity, 2 -->' in line:
                line = file.readline()
                line = file.readline()
                if '<SerialNumber>' in line:
                    dataset_attrs['cndc01_sensor_sn'] = line[22:-16].replace(" ", "")                     
            elif '<!-- Frequency 2, Pressure, Digiquartz with TC -->' in line:
                line = file.readline()
                line = file.readline()
                if '<SerialNumber>' in line:
                    dataset_attrs['pres_sensor_sn'] = line[22:-16].replace(" ", "")  
            elif ('Oxygen, SBE 43 -->') in line:
            # elif ('<!-- A/D voltage 0, Oxygen, SBE 43 -->') in line:
                line = file.readline()
                line = file.readline()
                if '<SerialNumber>' in line:
                    dataset_attrs['dox1_sensor_sn'] = line[22:-16].replace(" ", "")  
            elif (', Fluorometer, WET Labs ECO-AFL/FL -->') in line:
                line = file.readline()
                line = file.readline()
                if '<SerialNumber>' in line:
                    dataset_attrs['fchla_sensor_sn'] = line[22:-16].replace(" ", "")                      
            elif (', Fluorometer, Chelsea Aqua 3 -->') in line:
                line = file.readline()
                line = file.readline()
                if '<SerialNumber>' in line:
                    dataset_attrs['fchla_sensor_sn'] = line[22:-16].replace(" ", "")                     
            elif (', Fluorometer, Chelsea UV Aquatracka -->') in line:
                line = file.readline()
                line = file.readline()
                if '<SerialNumber>' in line:
                    dataset_attrs['fchla_sensor_sn'] = line[22:-16].replace(" ", "")                        
            elif '*END*' in line:
                stop_trigger = True

        return dataset_attrs

    def psal_from_cndc(self, cndc, temp, pres):     
        '''Derive Practical salinity for those files that has not salinity'''
        psal = gsw.SP_from_C(cndc, temp, pres)
        return psal


        