#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Mar  2 09:05:14 2021

@author: a33272
"""

import netCDF4

from readers.ctd_sbe_cnv_reader import CtdSbeCnv as CtdSbeCnv
from exporters.ctd_level0_exporter import CtdLevel0 as CtdLevel0

class LoadNetCDF(CtdLevel0):
    def __init__(self, *args):
        super(LoadNetCDF, self).__init__(*args)

    def load_nc_file(self, file_path):
        data = {}
        with netCDF4.Dataset(file_path) as nc:
            data['lat'] = nc.variables[self.nc_varnames_map['LATITUDE']][:] 
            data['lat_qc'] = nc.variables[self.nc_varnames_map['LATITUDE_QC']][:]
            data['lon'] = nc.variables[self.nc_varnames_map['LONGITUDE']][:] 
            data['lon_qc'] = nc.variables[self.nc_varnames_map['LONGITUDE_QC']][:]
            data['temp'] = nc.variables[self.nc_varnames_map['TEMP00']][:]
            data['temp_qc'] = nc.variables[self.nc_varnames_map['TEMP00_QC']][:]
            data['psal'] = nc.variables[self.nc_varnames_map['PSAL00']][:]
            data['psal_qc'] = nc.variables[self.nc_varnames_map['PSAL00_QC']][:]
            data['pres'] = nc.variables[self.nc_varnames_map['PRES']][:]
            data['depth'] = nc.variables[self.nc_varnames_map['DEPH']][:]
            data['dox'] = nc.variables[self.nc_varnames_map['DOX1']][:]
            data['dox_qc'] = nc.variables[self.nc_varnames_map['DOX1_QC']][:]
            data['dox_corr'] = nc.variables[self.nc_varnames_map['DOX1_CORR']][:]
            dum = [ str(s, encoding='UTF-8') for s in nc.variables[self.nc_varnames_map['STATION_NAME']][:] ]
            data['station'] = ''.join(dum)
        return data