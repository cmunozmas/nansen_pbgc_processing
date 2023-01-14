#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Sep 27 15:10:05 2022

@author: a33272
"""
import netCDF4 as nc

from rtqc.rtqc_tests import Rtqc
from exporters.ctd_nc_exporters.ctd_level0_exporter import CtdLevel0 as CtdLevel0
import exporters.ctd_nc_exporters.ctd_level0_exporter as ctd_level0_exporter
import rtqc.rtqc_tests as rtqc_tests

class RtqcManager(Rtqc, CtdLevel0):
    def __init__(self, *args):
        super(RtqcManager, self).__init__(*args)
        
                
        self.qc_flag = {'good': 1, 
                'no_qc': 0, 
                'suspect':3, 
                'bad': 4, 
                'missing': 9}  
        
       
        
        
    def perform_rtqc(self, file_path, data, config_survey): 
        exporter = ctd_level0_exporter.CtdLevel0(config_survey)
        rtqc = rtqc_tests.Rtqc(config_survey)
        
        dataset_nc = nc.Dataset(file_path, 'r+')
        vars_list = list(dataset_nc.variables.keys())
        dataset_nc.processing_level = 'L1A - Automatic RT Quality Controlled data'
    
        # # QC refereces
        # var_name_qc = exporter.nc_varnames_map['TEMP00_OS_QC']
        # dataset_nc.variables[var_name_qc].quality_control_convention = dataset_nc.variables[var_name_qc].quality_control_convention + ' ' + config['QcAttrs']['QcRefDatameq']
        # var_name_qc = exporter.nc_varnames_map['PSAL00_OS_QC']
        # dataset_nc.variables[var_name_qc].quality_control_convention = dataset_nc.variables[var_name_qc].quality_control_convention + ' ' + config['QcAttrs']['QcRefDatameq']
        # var_name_qc = exporter.nc_varnames_map['PRES_OS_QC']
        # dataset_nc.variables[var_name_qc].quality_control_convention = dataset_nc.variables[var_name_qc].quality_control_convention + ' ' + config['QcAttrs']['QcRefDatameq']
        # var_name_qc = exporter.nc_varnames_map['DOX1_OS_QC']
        # dataset_nc.variables[var_name_qc].quality_control_convention = dataset_nc.variables[var_name_qc].quality_control_convention + ' ' + config['QcAttrs']['QcRefDatameq'] + ' ' + config['QcAttrs']['QcRefArgoBgc'] + ' ' + config['QcAttrs']['QcRefArgoBgcCheatsheets']
    
        
        # RTQC3 Impossible Location Test
        if self.nc_varnames_map['LATITUDE'] in vars_list:
            lat = dataset_nc.variables[exporter.nc_varnames_map['LATITUDE']][:]
            lon = dataset_nc.variables[exporter.nc_varnames_map['LONGITUDE']][:]
            lat_qc = dataset_nc.variables[exporter.nc_varnames_map['LATITUDE_QC']][:]
            lon_qc = dataset_nc.variables[exporter.nc_varnames_map['LONGITUDE_QC']][:]
            lat_qc, lon_qc = rtqc.rtqc3_impossible_location_test(lat, lon, lat_qc, lon_qc)    
            dataset_nc.variables[exporter.nc_varnames_map['LATITUDE_QC']][:] = lat_qc
            dataset_nc.variables[exporter.nc_varnames_map['LONGITUDE_QC']][:] = lat_qc
        
        # RTQC6 Global Range Test
        # Temperature
        if self.nc_varnames_map['TEMP00'] in vars_list:
            var_name = exporter.nc_varnames_map['TEMP00']
            var_name_qc = exporter.nc_varnames_map['TEMP00_QC']
            temp = dataset_nc.variables[var_name][:][0]
            temp_qc = []
            for observation in temp:
                observation_qc, anc_observation_qc = rtqc.rtqc6_global_range_test(var_name, observation)
                temp_qc.append(observation_qc)
                
            dataset_nc.variables[var_name_qc][:] = temp_qc
    
        # Salinity
        if self.nc_varnames_map['PSAL00'] in vars_list:
            var_name = exporter.nc_varnames_map['PSAL00']
            var_name_qc = exporter.nc_varnames_map['PSAL00_QC']
            anc_var_name = exporter.nc_varnames_map['TEMP00']
            psal = dataset_nc.variables[var_name][:][0]
            psal_qc = []
            
            for i in range(0,len(psal)):   
                observation = dataset_nc.variables[exporter.nc_varnames_map['PSAL00']][0][i]
                anc_observation_qc = dataset_nc.variables[exporter.nc_varnames_map['TEMP00_QC']][0][i]
                observation_qc, anc_observation_qc_new = rtqc.rtqc6_global_range_test(var_name, observation, anc_var_name, anc_observation_qc)
                psal_qc.append(observation_qc)
                dataset_nc.variables[exporter.nc_varnames_map['TEMP00_QC']][0][i] = anc_observation_qc_new
            dataset_nc.variables[var_name_qc][:] = psal_qc        
            
        # Dissolved Oxygen
        if self.nc_varnames_map['DOX1'] in vars_list: 
            var_name = exporter.nc_varnames_map['DOX1']
            var_name_qc = exporter.nc_varnames_map['DOX1_QC']
            doxy = dataset_nc.variables[var_name][:][0]
            doxy_qc = []
            for observation in doxy:
                observation_qc, anc_observation_qc = rtqc.rtqc6_global_range_test(var_name, observation)
                doxy_qc.append(observation_qc)       
            dataset_nc.variables[var_name_qc][:] = doxy_qc
    
        # Fluorescence
        if self.nc_varnames_map['FCHLA'] in vars_list: 
            var_name = exporter.nc_varnames_map['FCHLA']
            var_name_qc = exporter.nc_varnames_map['FCHLA_QC']
            fchla = dataset_nc.variables[var_name][:][0]
            fchla_qc = []
            for observation in fchla:
                observation_qc, anc_observation_qc = rtqc.rtqc6_global_range_test(var_name, observation)
                fchla_qc.append(observation_qc)       
            dataset_nc.variables[var_name_qc][:] = fchla_qc
            
        # RTQC8 Pressure Increasing Test
        if self.nc_varnames_map['PRES'] in vars_list:
            pres = dataset_nc.variables[exporter.nc_varnames_map['PRES']][:][0]         
            pres_qc = rtqc.rtqc8_pressure_increasing_test(pres)    
            dataset_nc.variables[exporter.nc_varnames_map['PRES_QC']][:] = pres_qc   
        
    
        #RTQC9 Spike Test
        #Temperature
        if self.nc_varnames_map['TEMP00'] in vars_list:
            var_name = exporter.nc_varnames_map['TEMP00']
            var_name_qc = exporter.nc_varnames_map['TEMP00_QC']
            temp_qc = dataset_nc.variables[var_name_qc][:][0]
            #temp = dataset_nc.variables[var_name][:] 
            pres = dataset_nc.variables[exporter.nc_varnames_map['PRES']][:][0] 
            temp_qc_spike = rtqc.rtqc9_spike_test(var_name, temp, temp_qc, pres, temp_qc)
            dataset_nc.variables[var_name_qc][:] = temp_qc_spike
    
        #salinity
        if self.nc_varnames_map['PSAL00'] in vars_list:           
            var_name = exporter.nc_varnames_map['PSAL00']
            var_name_qc = exporter.nc_varnames_map['PSAL00_QC']
            anc_var_name_qc = exporter.nc_varnames_map['TEMP00_QC']
            temp_qc = dataset_nc.variables[anc_var_name_qc][:][0]
            psal_qc = dataset_nc.variables[var_name_qc][:][0]
            psal = dataset_nc.variables[var_name][:][0] 
            pres = dataset_nc.variables[exporter.nc_varnames_map['PRES']][:][0] 
            psal_qc_spike = rtqc.rtqc9_spike_test(var_name, psal, psal_qc, pres, temp_qc)
            dataset_nc.variables[var_name_qc][:] = psal_qc_spike
    
        #Dissolved Oxygen
        if self.nc_varnames_map['DOX1'] in vars_list:
            var_name = exporter.nc_varnames_map['DOX1']
            var_name_qc = exporter.nc_varnames_map['DOX1_QC']
            doxy_qc = dataset_nc.variables[var_name_qc][:][0]
            doxy = dataset_nc.variables[var_name][:][0] 
            pres = dataset_nc.variables[exporter.nc_varnames_map['PRES']][:][0]
            doxy_qc_spike = rtqc.rtqc9_spike_test(var_name, doxy, doxy_qc, pres, temp_qc)
            dataset_nc.variables[var_name_qc][:] = doxy_qc_spike
    
        #Fchla
        if self.nc_varnames_map['FCHLA'] in vars_list:
            var_name = exporter.nc_varnames_map['FCHLA']
            var_name_qc = exporter.nc_varnames_map['FCHLA_QC']
            fchla_qc = dataset_nc.variables[var_name_qc][:][0]
            fchla = dataset_nc.variables[var_name][:][0] 
            pres = dataset_nc.variables[exporter.nc_varnames_map['PRES']][:][0]
            fchla_qc_spike = rtqc.rtqc9_spike_test(var_name, fchla, fchla_qc, pres, temp_qc)
            dataset_nc.variables[var_name_qc][:] = fchla_qc_spike
        
        #RTQC11 Gradient Test
        #Temperature
        if self.nc_varnames_map['TEMP00'] in vars_list:            
            var_name = exporter.nc_varnames_map['TEMP00']
            var_name_qc = exporter.nc_varnames_map['TEMP00_QC']
            temp_qc = dataset_nc.variables[var_name_qc][:][0]
            #temp = dataset_nc.variables[var_name][:] 
            pres = dataset_nc.variables[exporter.nc_varnames_map['PRES']][:][0]
            temp_qc_gradient = rtqc.rtqc11_gradient_test(var_name, temp, temp_qc, pres, temp_qc)
            dataset_nc.variables[var_name_qc][:] = temp_qc_gradient
    
        #salinity
        if self.nc_varnames_map['PSAL00'] in vars_list:            
            var_name = exporter.nc_varnames_map['PSAL00']
            var_name_qc = exporter.nc_varnames_map['PSAL00_QC']
            anc_var_name_qc = exporter.nc_varnames_map['TEMP00_QC']
            temp_qc = dataset_nc.variables[anc_var_name_qc][:][0]
            psal_qc = dataset_nc.variables[var_name_qc][:][0]
            psal = dataset_nc.variables[var_name][:][0]
            pres = dataset_nc.variables[exporter.nc_varnames_map['PRES']][:][0]
            psal_qc_gradient = rtqc.rtqc11_gradient_test(var_name, psal, psal_qc, pres, temp_qc)
            dataset_nc.variables[var_name_qc][:] = psal_qc_gradient   
    
        #Dissolved Oxygen
        if self.nc_varnames_map['DOX1'] in vars_list:
            var_name = exporter.nc_varnames_map['DOX1']
            var_name_qc = exporter.nc_varnames_map['DOX1_QC']
            doxy_qc = dataset_nc.variables[var_name_qc][:][0]
            doxy = dataset_nc.variables[var_name][:][0] 
            pres = dataset_nc.variables[exporter.nc_varnames_map['PRES']][:][0] 
            doxy_qc_gradient = rtqc.rtqc11_gradient_test(var_name, doxy, doxy_qc, pres, temp_qc)
            dataset_nc.variables[var_name_qc][:] = doxy_qc_gradient
        
        #RTQC12 Digit Rollover Test
        #Temperature
        if self.nc_varnames_map['TEMP00'] in vars_list:            
            var_name = exporter.nc_varnames_map['TEMP00']
            var_name_qc = exporter.nc_varnames_map['TEMP00_QC']
            temp_qc = dataset_nc.variables[var_name_qc][:][0]
            #temp = dataset_nc.variables[var_name][:] 
            pres = dataset_nc.variables[exporter.nc_varnames_map['PRES']][:][0] 
            temp_qc_rollover = rtqc.rtqc12_digit_rollover_test(var_name, temp, temp_qc, pres, temp_qc)
            dataset_nc.variables[var_name_qc][:] = temp_qc_rollover
    
        #salinity
        if self.nc_varnames_map['PSAL00'] in vars_list:            
            var_name = exporter.nc_varnames_map['PSAL00']
            var_name_qc = exporter.nc_varnames_map['PSAL00_QC']
            anc_var_name_qc = exporter.nc_varnames_map['TEMP00_QC']
            temp_qc = dataset_nc.variables[anc_var_name_qc][:][0]
            psal_qc = dataset_nc.variables[var_name_qc][:][0]
            psal = dataset_nc.variables[var_name][:][0] 
            pres = dataset_nc.variables[exporter.nc_varnames_map['PRES']][:][0] 
            psal_qc_rollover = rtqc.rtqc12_digit_rollover_test(var_name, psal, psal_qc, pres, temp_qc)
            dataset_nc.variables[var_name_qc][:] = psal_qc_rollover       
        
        #RTQC13 Stuck value Test
        #Temperature
        if self.nc_varnames_map['TEMP00'] in vars_list:
            var_name = exporter.nc_varnames_map['TEMP00']
            var_name_qc = exporter.nc_varnames_map['TEMP00_QC']
            temp_qc = dataset_nc.variables[var_name_qc][:][0]
            #temp = dataset_nc.variables[var_name][:] 
            pres = dataset_nc.variables[exporter.nc_varnames_map['PRES']][:][0] 
            temp_qc_stuck = rtqc.rtqc13_stuck_value_test(var_name, temp, temp_qc, pres, temp_qc)
            dataset_nc.variables[var_name_qc][:] = temp_qc_stuck
    
        #salinity
        if self.nc_varnames_map['PSAL00'] in vars_list:            
            var_name = exporter.nc_varnames_map['PSAL00']
            var_name_qc = exporter.nc_varnames_map['PSAL00_QC']
            anc_var_name_qc = exporter.nc_varnames_map['TEMP00_QC']
            temp_qc = dataset_nc.variables[anc_var_name_qc][:][0]
            psal_qc = dataset_nc.variables[var_name_qc][:][0]
            psal = dataset_nc.variables[var_name][:][0] 
            pres = dataset_nc.variables[exporter.nc_varnames_map['PRES']][:][0] 
            psal_qc_stuck = rtqc.rtqc13_stuck_value_test(var_name, psal, psal_qc, pres, temp_qc)
            dataset_nc.variables[var_name_qc][:] = psal_qc_stuck    
        
        
        #RTQC14 Density Inversion Test
        if self.nc_varnames_map['TEMP00'] in vars_list:
            var_name = exporter.nc_varnames_map['TEMP00']
            var_name_qc = exporter.nc_varnames_map['TEMP00_QC']
            temp_qc = dataset_nc.variables[var_name_qc][:][0]
            #temp = dataset_nc.variables[var_name][:] 
            pres = dataset_nc.variables[exporter.nc_varnames_map['PRES']][:][0] 
            var_name = exporter.nc_varnames_map['PSAL00']
            var_name_qc = exporter.nc_varnames_map['PSAL00_QC']
            psal_qc = dataset_nc.variables[var_name_qc][:][0]
            psal = dataset_nc.variables[var_name][:][0]     
            temp_qc_new, psal_qc_new = rtqc.rtqc14_density_inversion_test(temp, temp_qc, psal, psal_qc, pres)    
            dataset_nc.variables[exporter.nc_varnames_map['TEMP00_QC']][:] = temp_qc_new
            dataset_nc.variables[exporter.nc_varnames_map['PSAL00_QC']][:] = psal_qc_new
        
        
        dataset_nc.close()        
        
        
        return  
  