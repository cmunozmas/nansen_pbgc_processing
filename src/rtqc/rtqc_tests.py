#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Mar  1 15:59:37 2021

@author: a33272
"""
import gsw
import math
import statistics
import numpy as np
from exporters.ctd_level0_exporter import CtdLevel0 as CtdLevel0

class Rtqc(CtdLevel0):
    def __init__(self, *args): 
        super(Rtqc, self).__init__(*args)

        
        
    def rtqc3_impossible_location_test(self, lat, lon, lat_qc, lon_qc):
        ''' The test requires that the observation latitude and
            longitude from the profile data be sensible.
            - Latitude in range –90 to 90
            - Longitude in range –180 to 180
            Action: If either latitude or longitude fails, the
            position should be flagged as bad data. 
        '''
        lat_min = -90.
        lat_max = 90.
        lon_min = -180.
        lon_max =180.
        
        if (lat_min < lat < lat_max) and (lon_min < lat < lon_max):
            if (lat_qc < 1) and (lon_qc < 1):
                lat_qc = 1
                lon_qc = 1
        else:
            if (lat_qc < 4) and (lon_qc < 4):
                lat_qc = 4
                lon_qc = 4
            
        return lat_qc, lon_qc
        

    def rtqc6_global_range_test(self, var_name, observation, anc_var_name=None, anc_observation_qc=None):
        ''' This test applies a gross filter on observed values
            for temperature and salinity. It needs to accommodate all 
            of the expected extremes encountered in the oceans.
            - Temperature in range –2.5°C to 40.0°C
            - Salinity in range 2 to 41.0
            Action: If a value fails, it should be flagged as bad
            data. If temperature and salinity values at the same
            depth both fail, both values should be flagged as bad. 
            
            -Oxygen in range umol/kg= [-5,600], ml/L = [-0.11, 13.79]
            https://repository.oceanbestpractices.org/bitstream/handle/11329/1479/oxygen.png?sequence=11&isAllowed=y
        '''        
        global_ranges = {'temp':[-2.5, 40.], 
                         'psal':[2., 41.],
                         'dox1':[-0.11, 13.79],
                         'fchla':[-0.1, 50.],
                         }
        # Temperature
        if var_name == (self.nc_varnames_map['TEMP00'] or self.nc_varnames_map['TEMP01']):
            if global_ranges['temp'][0] < observation < global_ranges['temp'][1]:
                observation_qc = 1
            elif math.isnan(observation) == True:
                observation_qc = 9
            else:
                observation_qc = 4
            anc_observation_qc = None
            
        # Salinity
        if var_name == (self.nc_varnames_map['PSAL00'] or self.nc_varnames_map['PSAL01']):
            if global_ranges['psal'][0] < observation < global_ranges['psal'][1]:
                if anc_observation_qc > 1:
                    observation_qc = 4
                    anc_observation_qc = 4
                else:
                    observation_qc = 1
                    anc_observation_qc = anc_observation_qc
            elif math.isnan(observation) == True:
                observation_qc = 9
            else:
                if anc_observation_qc > 1:
                    observation_qc = 4
                    anc_observation_qc = 4
                else:
                    observation_qc = 4
                    anc_observation_qc = anc_observation_qc

        # Dissolved Oxygen
        if var_name ==self.nc_varnames_map['DOX1']:
            if global_ranges['dox1'][0] < observation < global_ranges['dox1'][1]:
                observation_qc = 1
            elif math.isnan(observation) == True:
                observation_qc = 9
            else:
                observation_qc = 4
            anc_observation_qc = None                    

        # Fluorescence
        if var_name in [self.nc_varnames_map['FCHLA'], self.nc_varnames_map['FCHLA_CORR']]:
            if global_ranges['fchla'][0] < observation < global_ranges['fchla'][1]:
                observation_qc = 1
            elif math.isnan(observation) == True:
                observation_qc = 9
            else:
                observation_qc = 4
            anc_observation_qc = None  
                
        return observation_qc, anc_observation_qc
        
    
    def rtqc8_pressure_increasing_test(self, pressure):
        ''' This test requires that the profile has pressures that
            are monotonically increasing (assuming the
            pressures are ordered from smallest to largest).
            Action: If there is a region of constant pressure, all
            but the first of a consecutive set of constant
            pressures should be flagged as bad data. If there is
            a region where pressure reverses, all of the
            pressures in the reversed part of the profile should
            be flagged as bad data. 
        '''
        pressure_qc = [0]
        for i in range(1,len(pressure)):
            if pressure[i] > pressure[i-1]:
                pressure_qc.append(1)
            else:
                pressure_qc.append(4)
                
        return pressure_qc     

    def rtqc9_spike_test(self, var_name, var_data, var_data_qc, pres_data, anc_var_data_qc=None):
        ''' A large difference between sequential
            measurements, where one measurement is quite
            different from adjacent ones, is a spike in both size
            and gradient. The test does not consider the
            differences in depth, but assumes a sampling that
            adequately reproduces the temperature and salinity
            changes with depth. The algorithm is used on both
            the temperature and salinity profiles:
            Test value = | V2 – (V3 + V1)/2 | – | (V3 – V1) / 2 | 
            where V2 is the measurement being tested as a
            spike, and V1 and V3 are the values above and below.
            Temperature:
            The V2 value is flagged when
            - the test value exceeds 6.0°C for pressures
            less than 500 db or
            - the test value exceeds 2.0°C for pressures
            greater than or equal to 500 db
            Salinity:
            The V2 value is flagged when
            - the test value exceeds 0.9 for pressures less
            than 500 db or
            - the test value exceeds 0.3 for pressures
            greater than or equal to 500 db
            Action: Values that fail the spike test should be
            flagged as bad data. If temperature and salinity
            values at the same depth both fail, they should be
            flagged as bad data.
            
            -Oxygen 50umol/kg -> 1.149 ml/L
            https://repository.oceanbestpractices.org/bitstream/handle/11329/1479/oxygen.png?sequence=11&isAllowed=y
        '''
        var_data_qc_spike = []
        if var_name == (self.nc_varnames_map['TEMP00'] or self.nc_varnames_map['TEMP01']): 
            DEPTH_THRESH = 500.
            VAL1 = 6.
            VAL2 = 2.
            
        if var_name == (self.nc_varnames_map['PSAL00'] or self.nc_varnames_map['PSAL01']):                 
            DEPTH_THRESH = 500.
            VAL1 = 0.9
            VAL2 = 0.3        

        if var_name == self.nc_varnames_map['DOX1']:                 
            DEPTH_THRESH = 11000. #max depth range to avoid threshold
            VAL1 = 1.149
            VAL2 = 1.149
             
        if var_name not in [self.nc_varnames_map['FCHLA'], self.nc_varnames_map['FCHLA_CORR']]:  
            # first observation not evaluated by the spike test
            if var_data_qc[0] < 1:
                var_data_qc_spike.append(0)
            elif var_data_qc[0] == 9:
                var_data_qc_spike.append(9)
            else:
                var_data_qc_spike.append(var_data_qc[0])
     
            for i in range(1,len(var_data)-1):               
                V1 = var_data[i-1]
                V2 = var_data[i]
                V3 = var_data[i+1]
                test_val = abs(V2-(V3 + V1)/2) - abs((V3-V1)/2)
                
                if var_data_qc[i] == 9:
                    var_data_qc_spike.append(9)
                elif test_val > VAL1 and pres_data[i] < DEPTH_THRESH:
                    var_data_qc_spike.append(4)
                elif test_val > VAL2 and pres_data[i] >= DEPTH_THRESH:
                    var_data_qc_spike.append(4)
                else:
                    if var_data_qc[i] < 1:
                        if anc_var_data_qc[i] > 1:
                            var_data_qc_spike.append(4)
                        else:
                            var_data_qc_spike.append(1)
                    else:
                        if anc_var_data_qc[i] > 1:
                            var_data_qc_spike.append(4)
                        else:
                            var_data_qc_spike.append(var_data_qc[i])
                            
            # last observation not evaluated by the spike test
            if var_data_qc[-1] < 1:
                var_data_qc_spike.append(0)
            elif var_data_qc[-1] == 9:
                    var_data_qc_spike.append(9)
            else:
                var_data_qc_spike.append(var_data_qc[-1])       
           
        elif var_name in [self.nc_varnames_map['FCHLA'], self.nc_varnames_map['FCHLA_CORR']]:  
            #Based on IMOS recommendations: https://github.com/aodn/imos-toolbox/wiki/QCProcedures#vertical-spike-test---imosverticalspikeqc---optional
            # first 2 observations not evaluated by the spike test
            for i in range(0,2):
                if var_data_qc[i] < 1:
                    var_data_qc_spike.append(0)
                elif var_data_qc[i] == 9:
                    var_data_qc_spike.append(9)
                else:
                    var_data_qc_spike.append(var_data_qc[i])
                
            for i in range(2,len(var_data)-2):  
                V0 = var_data[i-2]
                V1 = var_data[i-1]
                V2 = var_data[i]
                V3 = var_data[i+1]
                V4 = var_data[i+2]
                running_window = np.array([V0,V1,V2,V3,V4])
                running_window_median = np.nanmedian(sorted(running_window))
                running_window_stdev = np.nanstd(running_window)
                VAL1 = abs(running_window_median) + abs(running_window_stdev)
                VAL2 = VAL1
                DEPTH_THRESH = 0
                test_val = abs(V2-(V3 + V1)/2) - abs((V3-V1)/2)
                
                if var_data_qc[i] == 9:
                    var_data_qc_spike.append(9)
                elif test_val > VAL1 and pres_data[i] < DEPTH_THRESH:
                    var_data_qc_spike.append(4)
                elif test_val > VAL2 and pres_data[i] >= DEPTH_THRESH:
                    var_data_qc_spike.append(4)
                else:
                    if var_data_qc[i] < 1:
                        if anc_var_data_qc[i] > 1:
                            var_data_qc_spike.append(4)
                        else:
                            var_data_qc_spike.append(1)
                    else:
                        if anc_var_data_qc[i] > 1:
                            var_data_qc_spike.append(4)
                        else:
                            var_data_qc_spike.append(var_data_qc[i])                
                            
            # last 2 observations not evaluated by the spike test    
            for i in range(len(var_data)-2,len(var_data)):                          
                if var_data_qc[i] < 1:
                    var_data_qc_spike.append(0)
                elif var_data_qc[i] == 9:
                        var_data_qc_spike.append(9)
                else:
                    var_data_qc_spike.append(var_data_qc[i])                 
                
        return var_data_qc_spike


        
        
    def rtqc11_gradient_test(self, var_name, var_data, var_data_qc, pres_data, anc_var_data_qc=None):
        ''' This test is failed when the difference between
            vertically adjacent measurements is too steep. The
            test does not consider the differences in depth, but
            assumes a sampling that adequately reproduces the
            temperature and salinity changes with depth. The
            algorithm is used on both the temperature and
            salinity profiles:
            Test value = | V2 – (V3 + V1)/2 |
            where V2 is the measurement being tested as a
            spike, and V1 and V3 are the values above and
            below.
            Temperature:
            The V2 value is flagged when
            - the test value exceeds 9.0°C for pressures
            less than 500 db or
            - the test value exceeds 3.0°C for pressures
            greater than or equal to 500 db
            Salinity:
            The V2 value is flagged when
            - the test value exceeds 1.5 for pressures less
            than 500 db or
            - the test value exceeds 0.5 for pressures
            greater than or equal to 500 db
            Action: Values that fail the test (i.e. value V2)
            should be flagged as bad data. If temperature and
            salinity values at the same depth both fail, they
            should both be flagged as bad data.      
            
            -Oxygen 50umol/kg -> 1.149 ml/L
            https://repository.oceanbestpractices.org/bitstream/handle/11329/1479/oxygen.png?sequence=11&isAllowed=y
        '''
        var_data_qc_gradient = []
        if var_name == (self.nc_varnames_map['TEMP00'] or self.nc_varnames_map['TEMP01']): 
            DEPTH_THRESH = 500. #dbar from pressure
            VAL1 = 9.
            VAL2 = 3.
            
        if var_name == (self.nc_varnames_map['PSAL00'] or self.nc_varnames_map['PSAL01']):                 
            DEPTH_THRESH = 500.
            VAL1 = 1.5
            VAL2 = 0.5        

        if var_name == self.nc_varnames_map['DOX1']:                 
            DEPTH_THRESH = 11000. #max depth range to avoid threshold
            VAL1 = 1.149
            VAL2 = 1.149
            
        # first observation not evaluated by the gradient test
        if var_data_qc[0] < 1:
            var_data_qc_gradient.append(0)
        elif var_data_qc[0] == 9:
            var_data_qc_gradient.append(9)
        else:
            var_data_qc_gradient.append(var_data_qc[0])
 
        for i in range(1,len(var_data)-1):               
            V1 = var_data[i-1]
            V2 = var_data[i]
            V3 = var_data[i+1]
            test_val = abs(V2 - (V3 + V1)/2)
            
            if var_data_qc[i] == 9:
                var_data_qc_gradient.append(9)                
            elif test_val > VAL1 and pres_data[i] < DEPTH_THRESH:
                var_data_qc_gradient.append(4)
            elif test_val > VAL2 and pres_data[i] >= DEPTH_THRESH:
                var_data_qc_gradient.append(4)
            else:
                if var_data_qc[i] < 1:
                    if anc_var_data_qc[i] > 1:
                        var_data_qc_gradient.append(4)
                    else:
                        var_data_qc_gradient.append(1)
                else:
                    if anc_var_data_qc[i] > 1:
                        var_data_qc_gradient.append(4)
                    else:
                        var_data_qc_gradient.append(var_data_qc[i])
                        
        # last observation not evaluated by the graient test
        if var_data_qc[-1] < 1:
            var_data_qc_gradient.append(0)
        elif var_data_qc[-1] == 9:
            var_data_qc_gradient.append(9)
        else:
            var_data_qc_gradient.append(var_data_qc[-1])            
        
        return var_data_qc_gradient        
        
        
    def rtqc12_digit_rollover_test(self, var_name, var_data, var_data_qc, pres_data, anc_var_data_qc=None):
        ''' Only so many bits are allowed to store temperature
            and salinity values in a sensor. This range is not
            always large enough to accommodate conditions
            that are encountered in the ocean. When the range
            is exceeded, stored values roll over to the lower
            end of the range. This rollover should be detected
            and compensated for when profiles are constructed
            from the data stream from the instrument. This test
            is used to ensure the rollover was properly
            detected.
            - Temperature difference between adjacent depths > 10°C
            - Salinity difference between adjacent depths > 5
            Action: Values that fail the test should be flagged
            as bad data. If temperature and salinity values at
            the same depth both fail, both values should be
            flagged as bad data. 
        ''' 
        var_data_qc_rollover = []
        if var_name == (self.nc_varnames_map['TEMP00'] or self.nc_varnames_map['TEMP01']): 
            VAL1 = 10.
            
        if var_name == (self.nc_varnames_map['PSAL00'] or self.nc_varnames_map['PSAL01']):                 
            VAL1 = 5.
     
            
        # first observation not evaluated by the spike test
        if var_data_qc[0] < 1:
            var_data_qc_rollover.append(0)
        elif var_data_qc[0] == 9:
            var_data_qc_rollover.append(9)
        else:
            var_data_qc_rollover.append(var_data_qc[0])
 
        for i in range(1,len(var_data)):               
            if var_data_qc[i] == 9:
                var_data_qc_rollover.append(9)                
            elif abs(var_data[i] - var_data[i-1]) > VAL1:
                var_data_qc_rollover.append(4)
            else:
                if var_data_qc[i] < 1:
                    if anc_var_data_qc[i] > 1:
                        var_data_qc_rollover.append(4)
                    else:
                        var_data_qc_rollover.append(1)
                else:
                    if anc_var_data_qc[i] > 1:
                        var_data_qc_rollover.append(4)
                    else:
                        var_data_qc_rollover.append(var_data_qc[i])
        
        return var_data_qc_rollover         

    def rtqc13_stuck_value_test(self, var_name, var_data, var_data_qc, pres_data, anc_var_data_qc=None):
        ''' This test looks for all measurements of temperature
            or salinity in a profile being identical.
            Action: If this occurs, all of the values of the
            affected variable should be flagged as bad data. If
            temperature and salinity are affected, all observed
            values are flagged as bad data.
            
        '''
        var_data_qc_stuck = [var_data_qc[0],var_data_qc[1],var_data_qc[2],var_data_qc[3]]
        for i in range(4,len(var_data)):
            if var_data_qc[i] == 9:
                var_data_qc_stuck.append(9)  
            else:
                V2 = var_data[i-4]
                V3 = var_data[i-3]
                V4 = var_data[i-2]
                V5 = var_data[i-1]
                V6 = var_data[i]
                
                values = [V2,V3,V4,V5,V6]
                result = values.count(values[4]) == len(values)
                
                if result == True:
                    var_data_qc_stuck.append(4)                    
                else:
                    if var_data_qc[i] < 1:
                        if anc_var_data_qc[i] > 1:
                            var_data_qc_stuck.append(4)
                        else:
                            var_data_qc_stuck.append(1)
                    else:
                        if anc_var_data_qc[i] > 1:
                            var_data_qc_stuck.append(4)
                        else:
                            var_data_qc_stuck.append(var_data_qc[i])     
                            
        return var_data_qc_stuck      
    
    def rtqc14_density_inversion_test(self, temp, temp_qc, psal, psal_qc, pres):
        ''' This test uses values of temperature and salinity at
            the same pressure level and computes the density
            (sigma0). The algorithm published in UNESCO
            Technical Papers in Marine Science #44, 1983
            should be used. Densities (sigma0) are compared at
            consecutive levels in a profile, in both directions,
            i.e. from top to bottom profile, and from bottom to
            top. Small inversion, below a threshold that can be
            region dependant, is allowed. 
            Action: from top to bottom, if the density (sigma0)
            calculated at the greater pressure is less than that
            calculated at the lesser pressure within the
            threshold by more than 0.03 kg m −3 , 
            both the temperature and salinity values
            should be flagged as bad data. 
        '''
        THRESHOLD = 0.03
        
        sig0 = gsw.density.sigma0(psal, temp)

        temp_qc_new = [temp_qc[0]]
        psal_qc_new = [psal_qc[0]]
        for i in range(1,len(sig0)):
            if (temp_qc[i] == 9) or (psal_qc[i] == 9):
                temp_qc_new.append(9)
                psal_qc_new.append(9)
            elif ((sig0[i] - sig0[i-1]) < 0) and (abs(sig0[i] - sig0[i-1]) > THRESHOLD):
                temp_qc_new.append(4)
                psal_qc_new.append(4)
            else:
                temp_qc_new.append(temp_qc[i])
                psal_qc_new.append(psal_qc[i])                
                
        return temp_qc_new, psal_qc_new