#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Oct 12 04:12:00 2020

@author: a33272
"""
import gsw
import glob
import numpy as np
import pandas as pd
import netCDF4 as nc
from netCDF4 import Dataset
import datetime
import time
import os

#from readers.readers_base import ReadersBase as ReadersBase
from readers.ctd_sbe_cnv_reader import CtdSbeCnv as CtdSbeCnv

class CtdLevel0(CtdSbeCnv):
    def __init__(self, *args):
        super(CtdLevel0, self).__init__(*args)
        
        self.nc_varnames_map = {'TIME': 'TIME', 'TIME_QC':'TIME_QC', 'TIME_QC':'TIME_QC',
                                'LATITUDE': 'LATITUDE', 'LATITUDE_QC': 'LATITUDE_QC',                                
                                'LONGITUDE': 'LONGITUDE', 'LONGITUDE_QC': 'LONGITUDE_QC',  
                                'POSITION_QC': 'POSITION_QC',
                                
                                'CRS': 'crs',                                                              
                                'SDN_CRUISE':'SDN_CRUISE',
                                'SDN_EDMO_CODE':'SDN_EDMO_CODE',
                                'IMR_LOCAL_OBJECT_ID': 'IMR_LOCAL_OBJECT_ID',
                                'PROF_DIR': 'PROF_DIR',
                                'STATION_NAME': 'SDN_STATION',
                                'STATION_DEPTH': 'SDN_BOT_DEPTH',
                                'STATION_SHIP_LOG': 'STATION_SHIP_LOG',
                                'STATION_WEATHER': 'STATION_WEATHER',
                                'STATION_SEA': 'STATION_SEA',
                                'STATION_SKY': 'STATION_SKY',
                                'STATION_WDIR': 'STATION_WDIR',
                                'STATION_WFORCE': 'STATION_WFORCE',
                                'STATION_AIRT': 'STATION_AIRT',
                                
                                'DEPH': 'DEPTH', 'DEPH_QC': 'DEPTH_QC',
                                'PRES': 'PRES', 'PRES_QC': 'PRES_QC',
                                'PSAL00': 'PSAL00', 'PSAL00_QC': 'PSAL00_QC', 'PSAL00_CORR': 'PSAL00_CORR', 
                                'PSAL01': 'PSAL01', 'PSAL01_QC': 'PSAL01_QC', 'PSAL01_CORR': 'PSAL01_CORR', 
                                'TEMP00': 'TEMP00','TEMP00_QC': 'TEMP00_QC',                               
                                'TEMP01': 'TEMP01', 'TEMP01_QC': 'TEMP01_QC', 
                                'CNDC00': 'CNDC00', 'CNDC00_QC': 'CNDC00_QC', 'CNDC00_CORR': 'CNDC00_CORR',
                                'CNDC01': 'CNDC01', 'CNDC01_QC': 'CNDC01_QC', 'CNDC01_CORR': 'CNDC01_CORR',
                                'DOXV': 'DOXV',
                                'DOX1': 'DOX1', 'DOX1_QC': 'DOX1_QC', 'DOX1_CORR': 'DOX1_CORR',
                                'FCHLA': 'FCHLA', 'FCHLA_QC': 'FCHLA_QC',
                                #'FCHLAV': 'flECO-AFL_voltage',
                                'FCHLA_CORR': 'FCHLA_CORR','FCHLA_CORR_QC': 'FCHLA_CORR_QC',                              
                                'PAR': 'PAR', 'PAR_QC': 'PAR_QC',
                                'SIGT': 'sigma_t',
                                }        

#        self.nc_var_attrs_map = {'TEMP00_SENSOR_SN': 'TEMP00_SENSOR_SN', 
#                                }
                
        self.qc_flag = {'good': 1, 
                'no_qc': 0, 
                'suspect':3, 
                'bad': 4, 
                'missing': 9}  
        
    def create_data_out_directories(self, dir_path): 
      isdir = os.path.isdir(dir_path) 
      if not isdir:
          os.mkdir(dir_path) 
      return  
  
    def create_nc_file(self, file_path, config, config_survey, data):

        self.varnames_map = self.set_varnames_map(config)
        
        attrs_date = data['attrs']['datetime'].strftime('%Y-%m-%d')
        nc_file_name = 'EAF-NANSEN_C' + config_survey['GlobalAttrs']['CruiseId'] + '_CTD_L0_' + attrs_date + '_' + data['attrs']['station'] + '.nc'
        rootgrp = Dataset(file_path + nc_file_name, "w", format="NETCDF4")
        
        rootgrp.project = config_survey['GlobalAttrs']['Project']
        rootgrp.csr_ref_num = config_survey['VarAttrs']['SdnCsrRefNum']
        rootgrp.mission_name = config_survey['GlobalAttrs']['CruiseName']
        rootgrp.mission_start_date = config_survey.get('GlobalAttrs', 'CruiseDateStart')#str(['GlobalAttrs']['CruiseDateStart'])
        rootgrp.mission_stop_date = config_survey.get('GlobalAttrs', 'CruiseDateStop')#str(['GlobalAttrs']['CruiseSDateStop'])
        rootgrp.mission_purpose = config_survey['GlobalAttrs']['CruisePurpose']
        rootgrp.summary = config_survey['GlobalAttrs']['Abstract']
        rootgrp.title = config_survey['GlobalAttrs']['Title']
        rootgrp.citation = config_survey['GlobalAttrs']['Citation']
        rootgrp.acknowledgement = config_survey['GlobalAttrs']['Acknowledgement']
        rootgrp.license = config_survey['GlobalAttrs']['License']
        rootgrp.history = "Created " + time.ctime(time.time())
        
        rootgrp.date_created = datetime.datetime.now().strftime('%Y-%m-%dT%H:%M:%SZ') 
        rootgrp.date_modified = datetime.datetime.now().strftime('%Y-%m-%dT%H:%M:%SZ') 
        rootgrp.Conventions = config_survey['GlobalAttrs']['Conventions']
        rootgrp.standard_name_vocabulary = config_survey['GlobalAttrs']['StandardNameVocabulary']        
        rootgrp.keywords_vocabulary = config_survey['GlobalAttrs']['KeywordsVocabulary']
        rootgrp.keywords = config_survey['GlobalAttrs']['Keywords']        
        rootgrp.processing_level = 'L0 - Raw Data'
        rootgrp.principal_investigator = config_survey['GlobalAttrs']['PrincipalInvestigator']
        rootgrp.institution = config_survey['GlobalAttrs']['Institution']
        
        rootgrp.platform_vocabulary = config_survey['GlobalAttrs']['PlatformVocabulary']
        rootgrp.platform_type = config_survey['GlobalAttrs']['PlatformType']
        rootgrp.platform_deployment_ship_id_imr = config_survey['GlobalAttrs']['ImrPlatformId']
        rootgrp.platform_deployment_ship_id_ices = config_survey['GlobalAttrs']['IcesPlatformId']
        rootgrp.platform_deployment_ship_name = config_survey['GlobalAttrs']['PlatformName']
        rootgrp.platform_deployment_ship_call_sign = config_survey['GlobalAttrs']['PlatformCallSign']
        
        rootgrp.featureType = config_survey['GlobalAttrs']['FeatureType']
        rootgrp.instrument_type = config_survey['GlobalAttrs']['InstrumentType']
        rootgrp.instrument_mount = config_survey['GlobalAttrs']['InstrumentMount']
        rootgrp.instrument_serial_number = config_survey['GlobalAttrs']['InstrumentSerialNumber']
        rootgrp.manufacturer_name = config_survey['GlobalAttrs']['InstrumentManufacturerName']
        rootgrp.instrument_model = config_survey['GlobalAttrs']['InstrumentModel']
        
        rootgrp.data_assembly_center = config_survey['GlobalAttrs']['DataCentre']
        rootgrp.publisher_email = config_survey['GlobalAttrs']['DataCentreEmail']
        rootgrp.publisher_institutionr = config_survey['GlobalAttrs']['DataCentre']
        rootgrp.publisher_name = config_survey['GlobalAttrs']['PublisherName']
        rootgrp.publisher_email = config_survey['GlobalAttrs']['PublisherEmail']
        rootgrp.publisher_url = config_survey['GlobalAttrs']['PublisherUrl']

        rootgrp.contributor = config_survey['GlobalAttrs']['ContributorName']
        rootgrp.contributor_role = config_survey['GlobalAttrs']['ContributorRole']
        timestamp = data['attrs']['datetime']
        rootgrp.time_coverage_start = timestamp.strftime('%Y-%m-%dT%H:%M:%SZ')
        rootgrp.time_coverage_end = timestamp.strftime('%Y-%m-%dT%H:%M:%SZ')
        
        rootgrp.subsetVariables = 'SDN_CRUISE, SDN_EDMO_CODE, STATION_NAME, IMR_LOCAL_OBJECT_ID'
        rootgrp.cdm_profile_variables = 'IMR_LOCAL_OBJECT_ID, time, latitude, longitude'
        # Create Dimensions
        profile = rootgrp.createDimension("profile", 1)
        z = rootgrp.createDimension("z", len(data['data'][self.varnames_map['TEMP00']]))

        times = rootgrp.createVariable(self.nc_varnames_map['TIME'],"f8",("profile",))
        times.units                 = 'days since -4713-01-01T00:00:00Z'
        times.calendar              = 'julian'
        times.standard_name         = 'time'
        times.long_name             = 'Chronological Julian Date'
        times.ioos_category         = 'Time'
        times.axis                  = 'T'
        times.ancillary_variables   = self.nc_varnames_map['TIME_QC']
        times.sdn_parameter_name    = 'Julian Date (chronological)'
        times.sdn_parameter_urn     = 'SDN:P01::CJDY1101'
        times.sdn_uom_name          = 'Days'
        times.sdn_uom_urn           = 'SDN:P06::UTAA'
        times.valid_min             = 0.0
        times.valid_max             = 2500000.0
        times[:]                    = pd.Timestamp(data['attrs']['datetime']).to_julian_date()
        times.comment               = 'First value over profile measurement'
        times._Fillvalue            = float(config_survey['VarAttrs']['FillValueCmems'])  
        
        latitude                        = rootgrp.createVariable(self.nc_varnames_map['LATITUDE'],"f8",("profile",))        
        latitude.standard_name          = 'latitude'
        latitude.long_name              = 'Latitude'
        latitude.units                  = 'degrees_north'
        latitude.axis                   = 'Y'
        latitude.ancillary_variables    = self.nc_varnames_map['POSITION_QC']
        latitude.sdn_parameter_name     = 'Degrees north'
        latitude.sdn_parameter_urn      = 'SDN:P01::ALATZZ01'
        latitude.sdn_uom_name           = 'Latitude north'
        latitude.sdn_uom_urn            = 'SDN:P06::DEGN'
        latitude.ioos_category          = 'Location'
        latitude.valid_min              = -90.0
        latitude.valid_max              = 90.0                      
        latitude._Fillvalue             = float(config_survey['VarAttrs']['FillValueCmems'])       
        latitude[:]                     = data['attrs']['LATITUDE'] 
        latitude.observation_type       = 'measured'
        latitude.references             = ''
        latitude.comment                = ''
        latitude.history                = ''

        
        latitude_qc                         = rootgrp.createVariable(self.nc_varnames_map['LATITUDE_QC'],"i1",("profile",))
        latitude_qc.long_name               = 'OceanSites quality flag'
        latitude_qc.Conventions             = config_survey['QcAttrs']['OceansitesQualityControlConvention']
        latitude_qc._Fillvalue              = int(config_survey['QcAttrs']['OceansitesFillValue'])
        latitude_qc.ioos_category           = 'Quality'
        latitude_qc.valid_min               = int(config_survey['QcAttrs']['OceansitesValidMin'])
        latitude_qc.valid_max               = int(config_survey['QcAttrs']['OceansitesValidMax'])
        latitude_qc.flag_values             = config_survey['QcAttrs']['OceansitesFlagValues']
        latitude_qc.flag_meanings           = config_survey['QcAttrs']['OceansitesFlagMeanings']
        latitude_qc.references              = config_survey['QcAttrs']['OceansitesQualityControlConvention']
        latitude_qc[:]                      = self.qc_flag['no_qc']

        
        longitude                       = rootgrp.createVariable(self.nc_varnames_map['LONGITUDE'],"f8",("profile",))
        longitude.standard_name         = 'longitude'
        longitude.long_name             = 'Longitude'
        longitude.units                 = 'degrees_east'
        longitude.axis                  = 'X'
        longitude.ancillary_variables   = self.nc_varnames_map['POSITION_QC']
        longitude.sdn_parameter_name    = 'Degrees east'
        longitude.sdn_parameter_urn     = 'SDN:P01::ALONZZ01'
        longitude.sdn_uom_name          = 'Longitude east'
        longitude.sdn_uom_urn           = 'SDN:P06::DEGE'
        longitude.ioos_category         = 'Location'
        longitude[:]                    = data['attrs']['LONGITUDE'] 
        longitude.valid_min             = -180.0
        longitude.valid_max             = 180.0
        longitude._Fillvalue            = float(config_survey['VarAttrs']['FillValueCmems'])
        longitude.observation_type      = 'measured'
        longitude.references            = ''
        longitude.comment               = ''
        longitude.history               = ''

        
        longitude_qc = rootgrp.createVariable(self.nc_varnames_map['LONGITUDE_QC'],"i1",("profile",))
        longitude_qc.long_name               = 'OceanSites quality flag'
        longitude_qc.Conventions             = config_survey['QcAttrs']['OceansitesQualityControlConvention']
        longitude_qc._Fillvalue              = int(config_survey['QcAttrs']['OceansitesFillValue'])
        longitude_qc.ioos_category           = 'Quality'
        longitude_qc.valid_min               = int(config_survey['QcAttrs']['OceansitesValidMin'])
        longitude_qc.valid_max               = int(config_survey['QcAttrs']['OceansitesValidMax'])
        longitude_qc.flag_values             = config_survey['QcAttrs']['OceansitesFlagValues']
        longitude_qc.flag_meanings           = config_survey['QcAttrs']['OceansitesFlagMeanings']
        longitude_qc.references              = config_survey['QcAttrs']['OceansitesQualityControlConvention']
        longitude_qc[:]                      = self.qc_flag['no_qc']
        
        rootgrp.geospatial_lat_min = min(latitude)
        rootgrp.geospatial_lat_max = max(latitude)
        rootgrp.geospatial_lon_min = min(longitude)
        rootgrp.geospatial_lon_max = max(longitude)  

        crs                         = rootgrp.createVariable(self.nc_varnames_map['CRS'],"i",("profile",))
        crs.grid_mapping_name       = 'latitude_longitude'
        crs.epsg_code               = 'EPSG:4326'
        crs.long_name               = 'Coordinate Reference System'
        crs.semi_major_axis         = 6378137.0
        crs.inverse_flattening      = 298.257223563
        crs.ioos_category           = 'Location'
        crs[:]                      = 0
        
        nchar_sdn_cruise            = rootgrp.createDimension('nchar_sdn_cruise', len(config_survey['GlobalAttrs']['CruiseId']))
        sdn_cruise                  = rootgrp.createVariable(self.nc_varnames_map['SDN_CRUISE'],'S1',("profile","nchar_sdn_cruise",))
        sdn_cruise.long_name        = 'IMR Cruise Identifier'
        sdn_cruise._Fillvalue       = ''
        sdn_cruise.ioos_category    = 'Identifier'
        sdn_cruise[:]               = nc.stringtochar(np.array([str(config_survey['GlobalAttrs']['CruiseId'])], 'S'))

        nchar_sdn_edmo              = rootgrp.createDimension('nchar_sdn_edmo', len(config_survey['VarAttrs']['SdnEdmoCode']))
        sdn_edmo                    = rootgrp.createVariable(self.nc_varnames_map['SDN_EDMO_CODE'],'S1',("profile","nchar_sdn_edmo",))
        sdn_edmo.long_name          = 'European Directory of Marine Organisations code for the CDI partner'
        sdn_edmo._Fillvalue         = ''
        sdn_edmo.ioos_category      = 'Identifier'
        sdn_edmo[:]                 = nc.stringtochar(np.array([str(config_survey['VarAttrs']['SdnEdmoCode'])], 'S'))
        
        NUMCHARS                    = len(data['attrs'][self.varnames_map['STATION_NAME']])
        nchar_station               = rootgrp.createDimension('nchar_station', NUMCHARS)
        station                     = rootgrp.createVariable(self.nc_varnames_map['STATION_NAME'],'S1',("profile","nchar_station",))
        station.long_name           = 'IMR Station Identifier'
        station._Fillvalue          = ''
        station.ancillary_variable  = ''
        station.ioos_category       = 'Identifier'
        station[:]                  = nc.stringtoarr(data['attrs'][self.varnames_map['STATION_NAME']], NUMCHARS, 'S')
        
        nchar_imr_id                = rootgrp.createDimension('nchar_imr_id', 15)
        imr_id                      = rootgrp.createVariable(self.nc_varnames_map['IMR_LOCAL_OBJECT_ID'],'S1',("profile","nchar_imr_id",))
        imr_id.long_name            = 'IMR Data Granule Identifier'
        imr_id.cf_role              = 'profile_id'
        imr_id._Fillvalue           = ''
        imr_id.ioos_category        = 'Identifier'
        imr_id[:]                   = nc.stringtochar(np.array([config_survey['GlobalAttrs']['InstrumentType'] + '-' + config_survey['GlobalAttrs']['CruiseId'] + '-' + data['attrs'][self.varnames_map['STATION_NAME']]][0], 'S'))


        prof_dir                    = rootgrp.createVariable(self.nc_varnames_map['PROF_DIR'],"S1",("profile",))
        prof_dir.standard_name      = ''
        prof_dir.long_name          = 'Direction Of The Profile'
        prof_dir.conventions        = '«A» for ascending profile and «D» for descending profile. «M» for mean (gliders)'
        prof_dir._Fillvalue         = ''
        prof_dir.ancillary_variable = ''
        prof_dir.ioos_category      = 'Other'
        prof_dir[:]                 = 'D'

        if self.varnames_map['STATION_DEPTH'] in data['data']:        
            ecodepth                    = rootgrp.createVariable(self.nc_varnames_map['STATION_DEPTH'],"f4",("profile",))
            ecodepth.standard_name      = 'sea_floor_depth_below_sea_surface'
            ecodepth.long_name          = 'Bathymetric depth at profile measurement site'        
            ecodepth.units              = 'meters'
            ecodepth.sdn_parameter_urn  = 'SDN:P01::MBANZZZZ'
            ecodepth.sdn_parameter_name = 'Sea-floor depth (below instantaneous sea level) {bathymetric depth} in the water body'
            ecodepth.sdn_uom_urn        = 'SDN:P06::ULAA'
            ecodepth.sdn_uom_name       = 'Meters'
            ecodepth._Fillvalue         = float(config_survey['VarAttrs']['FillValueCmems'])
            ecodepth.ioos_category      = 'Bathymetry'        
            ecodepth.positive           = 'down'
            ecodepth_value              = data['attrs'][self.varnames_map['STATION_DEPTH']].replace(',','.')
            if ecodepth_value:
                ecodepth[:] = float(ecodepth_value)
            else:
                ecodepth[:] = np.nan
            ecodepth.observation_type   = 'measured'
            ecodepth.references         = ''
            ecodepth.comment            = 'Bottom depth measured by ship-based acoustic sounder at time of CTD cast. The sea_floor_depth_below_sea_surface is the vertical distance between the sea surface and the seabed as measured at a given point in space including the variance caused by tides and possibly waves.'
            ecodepth.history            = ''

        if self.varnames_map['STATION_SHIP_LOG'] in data['data']:
            log                         = rootgrp.createVariable(self.nc_varnames_map['STATION_SHIP_LOG'],"f4",("profile",))
            log.long_name               = 'ship log number'
            log._Fillvalue              = float(config_survey['VarAttrs']['FillValueCmems'])
            log.ioos_category           = 'Identifier'
            log[:]                      = float(data['attrs'][self.varnames_map['STATION_SHIP_LOG']].replace(',','.'))
            log.references              = ''
            log.comment                 = ''
            log.history                 = ''

        # airtemp                     = rootgrp.createVariable(self.nc_varnames_map['STATION_AIRT'],"f4",("profile",))
        # airtemp.standard_name       = 'air_temperature'
        # airtemp.long_name           = 'Station air temperature'
        # airtemp.units               = 'Celsius'
        # airtemp.ancillary_variable  = ''       
        # airtemp.coordinates         = self.nc_varnames_map['TIME'] + ' ' + self.nc_varnames_map['LATITUDE'] + ' ' + self.nc_varnames_map['LONGITUDE'] + ' ' + self.nc_varnames_map['DEPH']       
        # airtemp._Fillvalue          = float(config_survey['VarAttrs']['FillValueCmems'])
        # airtemp.ioos_category       = 'Meteorology'
        # airtemp.sdn_parameter_name  = 'Temperature of the atmosphere by thermometer'
        # airtemp.sdn_parameter_urn   = 'SDN:P01::CDTAZZ01'
        # airtemp.sdn_uom_name        = 'Degrees Celsius'
        # airtemp.sdn_uom_urn         = 'SDN:P06::UPAA'        
        # # airtemp.sdn_instrument_name = ''
        # # airtemp.sdn_instrument_urn  = ''
        # airtemp[:]                  = float(data['attrs'][self.varnames_map['STATION_AIRT']].replace(',','.'))
        # airtemp.observation_type    = 'measured'
        # airtemp.references          = ''
        # airtemp.comment             = 'Air temperature measured by ship meteorological station. Air temperature is the bulk temperature of the air, not the surface (skin) temperature.'
        # airtemp.history             = ''
        
        # if self.varnames_map['STATION_WEATHER'] in data['data']:
        #     weather = rootgrp.createVariable(self.nc_varnames_map['STATION_WEATHER'],"f4",("profile",))
        #     weather.units = ''
        #     weather.standard_name = ''
        #     weather.long_name = ''
        #     weather._Fillvalue = float(config_survey['VarAttrs']['FillValueCmems'])
        #     weather.ioos_category = 'Meteorology'
        #     weather.ancillary_variable = ''
        #     weather.coordinates         = self.nc_varnames_map['TIME'] + ' ' + self.nc_varnames_map['LATITUDE'] + ' ' + self.nc_varnames_map['LONGITUDE'] + ' ' + self.nc_varnames_map['DEPH']
        #     # weather.sdn_parameter_name  = ''
        #     #weather.sdn_parameter_urn   = 'SDN:P01::'
        #     # weather.sdn_uom_name        = ''
        #     #weather.sdn_uom_urn         = 'SDN:P06::'
        #     # weather.sdn_instrument_name = ''
        #     # weather.sdn_instrument_urn  = ''
        #     weather_value = data['attrs'][self.varnames_map['STATION_WEATHER']]
        #     if weather_value:
        #         weather[:] = float(weather_value)
        #     else: 
        #         weather[:] = np.nan
        #     weather.observation_type = 'observed'
        #     weather.references = ''
        #     weather.comment = ''
        #     weather.history = ''

        # if self.varnames_map['STATION_SKY'] in data['data']:
        #     sky                     = rootgrp.createVariable(self.nc_varnames_map['STATION_SKY'],"f4",("profile",))
        #     sky.units               = 'okta'
        #     sky.standard_name       = 'cloud_area_fraction'
        #     sky.long_name           = 'cloud area fraction in eighths of the sky dome covered by clouds'
        #     sky._Fillvalue          = float(config_survey['VarAttrs']['FillValueCmems'])
        #     sky.coordinates         = self.nc_varnames_map['TIME'] + ' ' + self.nc_varnames_map['LATITUDE'] + ' ' + self.nc_varnames_map['LONGITUDE'] + ' ' + self.nc_varnames_map['DEPH']         
        #     sky.ioos_category       = 'Meteorology'
        #     sky.sdn_parameter_name  = 'Cloud cover (all clouds) in the atmosphere by visual estimation and conversion to WMO code'
        #     sky.sdn_parameter_urn   = 'SDN:P01::WMOCCCAC'
        #     sky.sdn_uom_name        = 'Dimensionless'
        #     sky.sdn_uom_urn         = 'SDN:P06::UUUU'
        #     # sky.sdn_instrument_name = ''
        #     # sky.sdn_instrument_urn  = ''
        #     sky.ancillary_variable  = ''
        #     sky_value               = data['attrs'][self.varnames_map['STATION_SKY']]
        #     if sky_value:
        #         sky[:] = float(sky_value)
        #     else: 
        #         sky[:] = np.nan
        #     sky.observation_type    = 'observed'
        #     sky.reference_scale     = 'Okta scale'
        #     sky.references          = 'https://worldweather.wmo.int/oktas.htm'
        #     sky.comment             = 'Cloud amounts are generally round up to the next okta. For example ‘2 and a bit’ oktas is rounded to 3 oktas. The exception is when more than 7 but less than 8 oktas is observed – in this instance cloud amount is rounded down to 7 oktas.'
        #     sky.history             = ''

        # if self.varnames_map['STATION_SEA'] in data['data']:
        #     sea = rootgrp.createVariable(self.nc_varnames_map['STATION_SEA'],"f4",("profile",))
        #     sea.units = '1'
        #     sea.standard_name = 'sea_surface_wave_significant_height'
        #     sea.long_name = 'Sea state based on Douglas Scale'
        #     sea._Fillvalue = float(config_survey['VarAttrs']['FillValueCmems'])
        #     sea.ioos_category = 'Surface Waves'
        #     sea.ancillary_variable = ''
        #     sea.coordinates         = self.nc_varnames_map['TIME'] + ' ' + self.nc_varnames_map['LATITUDE'] + ' ' + self.nc_varnames_map['LONGITUDE'] + ' ' + self.nc_varnames_map['DEPH']                  
        #     sea.sdn_parameter_name  = 'Sea state on the water body by visual estimation and conversion to WMO code using table 3700'
        #     sea.sdn_parameter_urn   = 'SDN:P01::WMOCSSXX'
        #     sea.sdn_uom_name        = 'Dimensionless'
        #     sea.sdn_uom_urn         = 'SDN:P06::UUUU'
        #     # sea.sdn_instrument_name = ''
        #     # sea.sdn_instrument_urn  = ''
        #     sea_value = data['attrs'][self.varnames_map['STATION_SEA']]
        #     if sea_value:
        #         sea[:] = float(sea_value)
        #     else: 
        #         sea[:] = np.nan
        #     sea.observation_type    = 'observed'
        #     sea.reference_scale     = 'Douglas sea scale'
        #     sea.references          = 'SeaDatanet Library C39, World Meteorological Organisation sea states based on Douglas Sea State scale'
        #     sea.comment             = ''
        #     sea.history             = ''
        
        # wdir                        = rootgrp.createVariable(self.nc_varnames_map['STATION_WDIR'],"f4",("profile",))
        # wdir.units                  = 'degree'
        # wdir.standard_name          = 'wind_from_direction'
        # wdir.long_name              = 'Wind from direction'
        # wdir._Fillvalue             = float(config_survey['VarAttrs']['FillValueCmems'])
        # wdir.ioos_category          = 'Wind'
        # wdir.ancillary_variable     = ''
        # wdir.coordinates            = self.nc_varnames_map['TIME'] + ' ' + self.nc_varnames_map['LATITUDE'] + ' ' + self.nc_varnames_map['LONGITUDE'] + ' ' + self.nc_varnames_map['DEPH'] 
        # wdir.sdn_parameter_name     = 'Direction (from) of wind relative to True North {wind direction} in the atmosphere by port-mounted sonic anemometer and expressed at measurement altitude'
        # wdir.sdn_parameter_urn      = 'SDN:P01::AWSSOPIH'
        # wdir.sdn_uom_name           = 'Degrees'
        # wdir.sdn_uom_urn            = 'SDN:P06::UAAA'
        # # wdir.sdn_instrument_name    = ''
        # # wdir.sdn_instrument_urn     = ''
        # if data['attrs'][self.varnames_map['STATION_WDIR']] not in ['\n', '', ' ']:
        #     wdir[:] = float(data['attrs'][self.varnames_map['STATION_WDIR']])
        # else:
        #     wdir[:] = np.nan
        # wdir.observation_type       = 'measured'
        # wdir.reference_scale        = ''
        # wdir.references             = ''
        # wdir.comment                = 'Wind is defined as a two-dimensional (horizontal) air velocity vector, with no vertical component. (Vertical motion in the atmosphere has the standard name upward_air_velocity.) In meteorological reports, the direction of the wind vector is usually (but not always) given as the direction from which it is blowing (wind_from_direction) (westerly, northerly, etc.). In other contexts, such as atmospheric modelling, it is often natural to give the direction in the usual manner of vectors as the heading or the direction to which it is blowing (wind_to_direction) (eastward, southward, etc.) "from_direction" is used in the construction X_from_direction and indicates the direction from which the velocity vector of X is coming.'
        # wdir.history                = ''

        # wforce                      = rootgrp.createVariable(self.nc_varnames_map['STATION_WFORCE'],"f4",("profile",))
        # wforce.units                = '1'
        # wforce.standard_name        = 'beaufort_wind_force'
        # wforce.long_name            = 'Wind force category based on Beaufort scale'
        # wforce._Fillvalue           = float(config_survey['VarAttrs']['FillValueCmems'])
        # wforce.ioos_category        = 'Wind'
        # wforce.ancillary_variable   = ''
        # wforce.coordinates          = self.nc_varnames_map['TIME'] + ' ' + self.nc_varnames_map['LATITUDE'] + ' ' + self.nc_varnames_map['LONGITUDE'] + ' ' + self.nc_varnames_map['DEPH'] 
        # wforce.sdn_parameter_name   = 'Speed of wind {wind speed} in the atmosphere by visual estimation and conversion to Beaufort scale'
        # wforce.sdn_parameter_urn    = 'SDN:P01::WMOCWFBF'
        # wforce.sdn_uom_name         = 'Dimensionless'
        # wforce.sdn_uom_urn          = 'SDN:P06::UUUU'
        # # wforce.sdn_instrument_name  = ''
        # # wforce.sdn_instrument_urn   = ''
        # if data['attrs'][self.varnames_map['STATION_WFORCE']] not in ['\n', '', ' ']:
        #     wforce[:] = float(data['attrs'][self.varnames_map['STATION_WFORCE']])
        # else:
        #     wforce[:] = np.nan
        # wforce.observation_type     = 'observed'
        # wforce.reference_scale      = 'Beaufort scale'
        # wforce.references           = ''
        # wforce.comment              = 'Beaufort wind force" is an index assigned on the Beaufort wind force scale and relates a qualitative description of the degree of disturbance or destruction caused by wind to the speed of the wind. The Beaufort wind scale varies between 0 (qualitatively described as calm, smoke rises vertically, sea appears glassy) (wind speeds in the range 0 - 0.2 m s-1) and 12 (hurricane, wave heights in excess of 14 m) (wind speeds in excess of 32.7 m s-1).'
        # wforce.history              = ''
        if self.varnames_map['TEMP00'] in data['data']:
            temp                        = rootgrp.createVariable(self.nc_varnames_map['TEMP00'],"f4",("profile","z",))
            temp.units                  = 'Celsius'
            temp.standard_name          = 'sea_water_temperature'
            temp.long_name              = 'sea water temperature'
            temp.coordinates            = self.nc_varnames_map['TIME'] + ' ' + self.nc_varnames_map['LATITUDE'] + ' ' + self.nc_varnames_map['LONGITUDE'] + ' ' + self.nc_varnames_map['DEPH']
            temp._Fillvalue             = float(config_survey['VarAttrs']['FillValueCmems'])
            temp.ioos_category          = 'Temperature'
            temp.ancillary_variable     = self.nc_varnames_map['TEMP00_QC']
            temp.sdn_parameter_name     = 'Temperature of the water body by CTD and NO verification against independent measurements'
            temp.sdn_parameter_urn      = 'SDN:P01::TEMPCU01'
            temp.sdn_uom_name           = 'Degrees Celsius'
            temp.sdn_uom_urn            = 'SDN:P06::UPAA'
            temp.sdn_instrument_name    = 'Sea-Bird SBE 3plus (SBE 3P) temperature sensor'
            temp.sdn_instrument_urn     = 'SDN:L22::TOOL0416'
            temp[:]                     = data['data'][self.varnames_map['TEMP00']][::-1].to_numpy()
            temp.valid_min              = min(data['data'][self.varnames_map['TEMP00']])
            temp.valid_max              = max(data['data'][self.varnames_map['TEMP00']])
            temp.accuracy               = 0.001
            temp.precision              = ''
            temp.resolution             = 0.0002     
            temp.sensor_manufacturer    = 'SeaBird'
            temp.sensor_model           = 'SBE 3plus'
            if self.cnv_var_attrs_map['TEMP00_SENSOR_SN'] in data['attrs']: 
                temp.sensor_serial_number   = data['attrs'][self.cnv_var_attrs_map['TEMP00_SENSOR_SN']]
            temp.observation_type       = 'measured'
            temp.references             = ''
            temp.comment                = ''
            temp.history                = ''
            
            temp_qc = rootgrp.createVariable(self.nc_varnames_map['TEMP00_QC'],"i1",("profile","z",))
            temp_qc.long_name               = 'OceanSites quality flag'
            temp_qc.Conventions             = config_survey['QcAttrs']['OceansitesQualityControlConvention']
            temp_qc._Fillvalue              = int(config_survey['QcAttrs']['OceansitesFillValue'])
            temp_qc.ioos_category           = 'Quality'
            temp_qc.valid_min               = int(config_survey['QcAttrs']['OceansitesValidMin'])
            temp_qc.valid_max               = int(config_survey['QcAttrs']['OceansitesValidMax'])
            temp_qc.flag_values             = config_survey['QcAttrs']['OceansitesFlagValues']
            temp_qc.flag_meanings           = config_survey['QcAttrs']['OceansitesFlagMeanings']
            temp_qc.references              = config_survey['QcAttrs']['OceansitesQualityControlConvention']
            dum                             = [self.qc_flag['no_qc']] * len(data['data'][self.varnames_map['TEMP00']])
            temp_qc[:]                      = np.asarray(dum)
            
        if self.varnames_map['TEMP01'] in data['data']:
            temp                        = rootgrp.createVariable(self.nc_varnames_map['TEMP01'],"f4",("profile","z",))
            temp.units                  = 'Celsius'
            temp.standard_name          = 'sea_water_temperature'
            temp.long_name              = 'sea water temperature'
            temp.coordinates            = self.nc_varnames_map['TIME'] + ' ' + self.nc_varnames_map['LATITUDE'] + ' ' + self.nc_varnames_map['LONGITUDE'] + ' ' + self.nc_varnames_map['DEPH']
            temp._Fillvalue             = float(config_survey['VarAttrs']['FillValueCmems'])
            temp.ioos_category          = 'Temperature'
            temp.ancillary_variable     = self.nc_varnames_map['TEMP01_QC']
            temp.sdn_parameter_name     = 'Temperature of the water body by CTD and NO verification against independent measurements'
            temp.sdn_parameter_urn      = 'SDN:P01::TEMPCU01'
            temp.sdn_uom_name           = 'Degrees Celsius'
            temp.sdn_uom_urn            = 'SDN:P06::UPAA'
            temp.sdn_instrument_name    = 'Sea-Bird SBE 3plus (SBE 3P) temperature sensor'
            temp.sdn_instrument_urn     = 'SDN:L22::TOOL0416'
            temp[:]                     = data['data'][self.varnames_map['TEMP01']][::-1].to_numpy()
            temp.valid_min              = min(data['data'][self.varnames_map['TEMP01']])
            temp.valid_max              = max(data['data'][self.varnames_map['TEMP01']])
            temp.accuracy               = 0.001
            temp.precision              = ''
            temp.resolution             = 0.0002     
            temp.sensor_manufacturer    = 'SeaBird'
            temp.sensor_model           = 'SBE 3plus'
            if self.cnv_var_attrs_map['TEMP01_SENSOR_SN'] in data['attrs']:
                temp.sensor_serial_number   = data['attrs'][self.cnv_var_attrs_map['TEMP01_SENSOR_SN']]
            temp.observation_type       = 'measured'
            temp.references             = ''
            temp.comment                = ''
            temp.history                = ''
            
            temp_qc = rootgrp.createVariable(self.nc_varnames_map['TEMP01_QC'],"i1",("profile","z",))
            temp_qc.long_name               = 'OceanSites quality flag'
            temp_qc.Conventions             = config_survey['QcAttrs']['OceansitesQualityControlConvention']
            temp_qc._Fillvalue              = int(config_survey['QcAttrs']['OceansitesFillValue'])
            temp_qc.ioos_category           = 'Quality'
            temp_qc.valid_min               = int(config_survey['QcAttrs']['OceansitesValidMin'])
            temp_qc.valid_max               = int(config_survey['QcAttrs']['OceansitesValidMax'])
            temp_qc.flag_values             = config_survey['QcAttrs']['OceansitesFlagValues']
            temp_qc.flag_meanings           = config_survey['QcAttrs']['OceansitesFlagMeanings']
            temp_qc.references              = config_survey['QcAttrs']['OceansitesQualityControlConvention']
            dum                             = [self.qc_flag['no_qc']] * len(data['data'][self.varnames_map['TEMP01']])
            temp_qc[:]                      = np.asarray(dum)
            
        if self.varnames_map['PRES'] in data['data']:
            pres                        = rootgrp.createVariable(self.nc_varnames_map['PRES'],"f4",("profile","z",))
            pres.units                  = 'dbar'
            pres.standard_name          = 'sea_water_pressure'
            pres.long_name              = 'sea water pressure'
            pres._Fillvalue             = float(config_survey['VarAttrs']['FillValueCmems'])
            pres.ioos_category          = 'Pressure'
            pres.ancillary_variable     = self.nc_varnames_map['PRES_QC']
            pres.sdn_parameter_name     = 'Pressure (measured variable) exerted by the water body by semi-fixed in-situ pressure sensor and corrected to read zero at sea level'
            pres.sdn_parameter_urn      = 'SDN:P01::PREXPR01'
            pres.sdn_uom_name           = 'Decibars'
            pres.sdn_uom_urn            = 'SDN:P06::UPDB'
            pres.sdn_instrument_name    = 'Paroscientific Digiquartz depth sensors'
            pres.sdn_instrument_urn     = 'SDN:L22::TOOL0931'
            pres[:]                     = data['data'][self.varnames_map['PRES']][::-1].to_numpy()
            pres.valid_min              = min(data['data'][self.varnames_map['PRES']])
            pres.valid_max              = max(data['data'][self.varnames_map['PRES']])
            pres.accuracy               = 0.015
            pres.precision              = ''
            pres.resolution             = 0.001   
            pres.sensor_manufacturer    = 'SeaBird'
            pres.sensor_model           = 'Digiquartz'
            if self.cnv_var_attrs_map['PRES_SENSOR_SN'] in data['attrs']:
                pres.sensor_serial_number   = data['attrs'][self.cnv_var_attrs_map['PRES_SENSOR_SN']]
            pres.observation_type       = 'measured'
            pres.references             = ''
            pres.comment                = 'resolution is 0.001% of full scale. Accuracy is ± 0.015% of full scale range'
            pres.history                = ''
            
            pres_qc = rootgrp.createVariable(self.nc_varnames_map['PRES_QC'],"i1",("profile","z",))
            pres_qc.long_name               = 'OceanSites quality flag'
            pres_qc.Conventions             = config_survey['QcAttrs']['OceansitesQualityControlConvention']
            pres_qc._Fillvalue              = int(config_survey['QcAttrs']['OceansitesFillValue'])
            pres_qc.ioos_category           = 'Quality'
            pres_qc.valid_min               = int(config_survey['QcAttrs']['OceansitesValidMin'])
            pres_qc.valid_max               = int(config_survey['QcAttrs']['OceansitesValidMax'])
            pres_qc.flag_values             = config_survey['QcAttrs']['OceansitesFlagValues']
            pres_qc.flag_meanings           = config_survey['QcAttrs']['OceansitesFlagMeanings']
            pres_qc.references              = config_survey['QcAttrs']['OceansitesQualityControlConvention']
            dum                             = [self.qc_flag['no_qc']] * len(data['data'][self.varnames_map['PRES']])
            pres_qc[:]                      = np.asarray(dum)

        if self.varnames_map['PRES'] in data['data']:        
            deph                            = rootgrp.createVariable(self.nc_varnames_map['DEPH'],"f4",("profile","z",))
            deph.units                      = 'meters'
            deph.standard_name              = 'depth'
            deph.long_name                  = 'Depth'
            deph.ancillary_variable         = self.nc_varnames_map['DEPH_QC'] + ' ' + self.nc_varnames_map['DEPH_QC']
            deph._Fillvalue                 = float(config_survey['VarAttrs']['FillValueCmems'])
            deph.ioos_category              = 'Location'
            deph.axis                       = 'Z'
            deph.positive                   = 'down'
            deph.sdn_parameter_name         = 'Depth below surface of the water body'
            deph.sdn_uom_urn                = 'SDN:P01::ADEPZZ01'
            deph.sdn_uom_name               = 'Meters'
            deph.uom_urn                    = 'SDN:P06::ULAA'  
            # deph.sdn_instrument_name        = ''
            # deph.sdn_instrument_urn         = ''
            z                               = gsw.z_from_p(data['data'][self.varnames_map['PRES']], data['attrs'][self.nc_varnames_map['LATITUDE']])
            rootgrp.geospatial_vertical_min = min(abs(z))
            rootgrp.geospatial_vertical_max = max(abs(z))
            deph[:]                         = abs(z[::-1])
            deph.valid_min                  = min(z)
            deph.valid_max                  = max(z)
            deph.observation_type           = 'calculated'
            deph.references                 = ''
            deph.comment                    = ''
            deph.history                    = ''
    
            
            deph_qc                         = rootgrp.createVariable(self.nc_varnames_map['DEPH_QC'],"i1",("profile","z",))
            deph_qc.long_name               = 'OceanSites quality flag'
            deph_qc.Conventions             = config_survey['QcAttrs']['OceansitesQualityControlConvention']
            deph_qc._Fillvalue              = int(config_survey['QcAttrs']['OceansitesFillValue'])
            deph_qc.ioos_category           = 'Quality'
            deph_qc.valid_min               = int(config_survey['QcAttrs']['OceansitesValidMin'])
            deph_qc.valid_max               = int(config_survey['QcAttrs']['OceansitesValidMax'])
            deph_qc.flag_values             = config_survey['QcAttrs']['OceansitesFlagValues']
            deph_qc.flag_meanings           = config_survey['QcAttrs']['OceansitesFlagMeanings']
            deph_qc.references              = config_survey['QcAttrs']['OceansitesQualityControlConvention']
            deph_qc.comment                 = ''
            deph_qc.history                 = ''
            dum                             = [self.qc_flag['no_qc']] * len(data['data'][self.varnames_map['PRES']])
            deph_qc[:]                      = np.asarray(dum)


        if self.varnames_map['CNDC00'] in data['data']:        
            cndc                            = rootgrp.createVariable(self.nc_varnames_map['CNDC00'],"f4",("profile","z",))
            cndc.units                      = 'S m-1'
            cndc.standard_name              = 'sea_water_electrical_conductivity'
            cndc.long_name                  = 'sea water electrical conductivity'
            cndc.coordinates                = self.nc_varnames_map['TIME'] + ' ' + self.nc_varnames_map['LATITUDE'] + ' ' + self.nc_varnames_map['LONGITUDE'] + ' ' + self.nc_varnames_map['DEPH']
            cndc._Fillvalue                 = float(config_survey['VarAttrs']['FillValueCmems'])
            cndc.ioos_category              = 'Salinity'
            cndc.sdn_parameter_name         = 'Electrical conductivity of the water body by CTD'
            cndc.sdn_parameter_urn          = 'SDN:P01::CNDCST01'
            cndc.sdn_uom_name               = 'Siemens per metre'
            cndc.sdn_uom_urn                = 'SDN:P06::UECA'
            cndc.sdn_instrument_name        = 'Sea-Bird SBE 4C conductivity sensor'
            cndc.sdn_instrument_urn         = 'SDN:L22::TOOL0417'
            cndc.ancillary_variable         = self.nc_varnames_map['CNDC00_QC']
            cndc[:]                         = data['data'][self.varnames_map['CNDC00']][::-1].to_numpy()
            cndc.valid_min                  = min(data['data'][self.varnames_map['CNDC00']])
            cndc.valid_max                  = max(data['data'][self.varnames_map['CNDC00']])
            cndc.accuracy                   = 0.0003
            cndc.precision                  = ''
            cndc.resolution                 = 0.00004   
            cndc.sensor_manufacturer        = 'SeaBird'
            cndc.sensor_model               = 'SBE 4C'
            cndc.sensor_serial_number       = data['attrs'][self.cnv_var_attrs_map['CNDC00_SENSOR_SN']]
            cndc.observation_type           = 'measured'
            cndc.references                 = ''
            cndc.comment                    = ''
            cndc.history                    = ''
            
            cndc_qc = rootgrp.createVariable(self.nc_varnames_map['CNDC00_QC'],"i1",("profile","z",))
            cndc_qc.long_name               = 'OceanSites quality flag'
            cndc_qc.Conventions             = config_survey['QcAttrs']['OceansitesQualityControlConvention']
            cndc_qc._Fillvalue              = int(config_survey['QcAttrs']['OceansitesFillValue'])
            cndc_qc.ioos_category           = 'Quality'
            cndc_qc.valid_min               = int(config_survey['QcAttrs']['OceansitesValidMin'])
            cndc_qc.valid_max               = int(config_survey['QcAttrs']['OceansitesValidMax'])
            cndc_qc.flag_values             = config_survey['QcAttrs']['OceansitesFlagValues']
            cndc_qc.flag_meanings           = config_survey['QcAttrs']['OceansitesFlagMeanings']
            cndc_qc.references              = config_survey['QcAttrs']['OceansitesQualityControlConvention']
            cndc_qc.comment                 = ''
            cndc_qc.history                 = '' 
            dum = [self.qc_flag['no_qc']] * len(data['data'][self.varnames_map['CNDC00']])
            cndc_qc[:] = np.asarray(dum)   

        if self.varnames_map['CNDC01'] in data['data']:        
            cndc                            = rootgrp.createVariable(self.nc_varnames_map['CNDC01'],"f4",("profile","z",))
            cndc.units                      = 'S m-1'
            cndc.standard_name              = 'sea_water_electrical_conductivity'
            cndc.long_name                  = 'sea water electrical conductivity'
            cndc.coordinates                = self.nc_varnames_map['TIME'] + ' ' + self.nc_varnames_map['LATITUDE'] + ' ' + self.nc_varnames_map['LONGITUDE'] + ' ' + self.nc_varnames_map['DEPH']
            cndc._Fillvalue                 = float(config_survey['VarAttrs']['FillValueCmems'])
            cndc.ioos_category              = 'Salinity'
            cndc.sdn_parameter_name         = 'Electrical conductivity of the water body by CTD'
            cndc.sdn_parameter_urn          = 'SDN:P01::CNDCST01'
            cndc.sdn_uom_name               = 'Siemens per metre'
            cndc.sdn_uom_urn                = 'SDN:P06::UECA'
            cndc.sdn_instrument_name        = 'Sea-Bird SBE 4C conductivity sensor'
            cndc.sdn_instrument_urn         = 'SDN:L22::TOOL0417'
            cndc.ancillary_variable         = self.nc_varnames_map['CNDC01_QC']
            cndc[:]                         = data['data'][self.varnames_map['CNDC01']][::-1].to_numpy()
            cndc.valid_min                  = min(data['data'][self.varnames_map['CNDC01']])
            cndc.valid_max                  = max(data['data'][self.varnames_map['CNDC01']])
            cndc.accuracy                   = 0.0003
            cndc.precision                  = ''
            cndc.resolution                 = 0.00004   
            cndc.sensor_manufacturer        = 'SeaBird'
            cndc.sensor_model               = 'SBE 4C'
            cndc.sensor_serial_number       = data['attrs'][self.cnv_var_attrs_map['CNDC01_SENSOR_SN']]
            cndc.observation_type           = 'measured'
            cndc.references                 = ''
            cndc.comment                    = ''
            cndc.history                    = ''
            
            cndc_qc = rootgrp.createVariable(self.nc_varnames_map['CNDC01_QC'],"i1",("profile","z",))
            cndc_qc.long_name               = 'OceanSites quality flag'
            cndc_qc.Conventions             = config_survey['QcAttrs']['OceansitesQualityControlConvention']
            cndc_qc._Fillvalue              = int(config_survey['QcAttrs']['OceansitesFillValue'])
            cndc_qc.ioos_category           = 'Quality'
            cndc_qc.valid_min               = int(config_survey['QcAttrs']['OceansitesValidMin'])
            cndc_qc.valid_max               = int(config_survey['QcAttrs']['OceansitesValidMax'])
            cndc_qc.flag_values             = config_survey['QcAttrs']['OceansitesFlagValues']
            cndc_qc.flag_meanings           = config_survey['QcAttrs']['OceansitesFlagMeanings']
            cndc_qc.references              = config_survey['QcAttrs']['OceansitesQualityControlConvention']
            cndc_qc.comment                 = ''
            cndc_qc.history                 = '' 
            dum = [self.qc_flag['no_qc']] * len(data['data'][self.varnames_map['CNDC01']])
            cndc_qc[:] = np.asarray(dum)   
 
        if self.varnames_map['PSAL00'] in data['data']:        
            psal                            = rootgrp.createVariable(self.nc_varnames_map['PSAL00'],"f4",("profile","z",))
            psal.units                      = 'PSU'
            psal.standard_name              = 'sea_water_practical_salinity'
            psal.long_name                  = 'sea water practical salinity'
            psal.coordinates                = self.nc_varnames_map['TIME'] + ' ' + self.nc_varnames_map['LATITUDE'] + ' ' + self.nc_varnames_map['LONGITUDE'] + ' ' + self.nc_varnames_map['DEPH']
            psal._Fillvalue                 = float(config_survey['VarAttrs']['FillValueCmems'])
            psal.ioos_category              = 'Salinity'
            psal.ancillary_variable         = self.nc_varnames_map['PSAL00_QC']
            psal.sdn_parameter_name         = 'Practical salinity of the water body'
            psal.sdn_parameter_urn          = 'SDN:P01::PSLTZZ01'
            psal.sdn_uom_name               = 'Dimensionless'
            psal.sdn_uom_urn                = 'SDN:P06::UUUU'
            psal.sdn_instrument_name        = ''
            psal.sdn_instrument_urn         = ''
            psal[:]                         = data['data'][self.varnames_map['PSAL00']][::-1].to_numpy()
            psal.valid_min                  = min(data['data'][self.varnames_map['PSAL00']])
            psal.valid_max                  = max(data['data'][self.varnames_map['PSAL00']])
            psal.observation_type           = 'calculated'
            psal.reference_scale            = 'PSS-78'
            psal.references                 = config_survey['VarAttrs']['Pss78SbeRef']
            psal.comment                    = 'Salinity derived from CNDC00 and TEMP00'
            psal.history                    = ''
            
            psal_qc = rootgrp.createVariable(self.nc_varnames_map['PSAL00_QC'],"i1",("profile","z",))
            psal_qc.long_name               = 'OceanSites quality flag'
            psal_qc.Conventions             = config_survey['QcAttrs']['OceansitesQualityControlConvention']
            psal_qc._Fillvalue              = int(config_survey['QcAttrs']['OceansitesFillValue'])
            psal_qc.ioos_category           = 'Quality'
            psal_qc.valid_min               = int(config_survey['QcAttrs']['OceansitesValidMin'])
            psal_qc.valid_max               = int(config_survey['QcAttrs']['OceansitesValidMax'])
            psal_qc.flag_values             = config_survey['QcAttrs']['OceansitesFlagValues']
            psal_qc.flag_meanings           = config_survey['QcAttrs']['OceansitesFlagMeanings']
            psal_qc.references              = config_survey['QcAttrs']['OceansitesQualityControlConvention']
            psal_qc.comment                 = ''
            psal_qc.history                 = '' 
            dum = [self.qc_flag['no_qc']] * len(data['data'][self.varnames_map['PSAL00']])
            psal_qc[:] = np.asarray(dum)   

        if self.varnames_map['DOX1'] in data['data']:        
            dox1                            = rootgrp.createVariable(self.nc_varnames_map['DOX1'],"f4",("profile","z",))
            dox1.units                      = 'ml L-1'
            dox1.standard_name              = ''
            dox1.long_name                  = 'volume concentration of dissolved molecular oxygen in sea water'
            dox1.coordinates                = self.nc_varnames_map['TIME'] + ' ' + self.nc_varnames_map['LATITUDE'] + ' ' + self.nc_varnames_map['LONGITUDE'] + ' ' + self.nc_varnames_map['DEPH']
            dox1._Fillvalue                 = float(config_survey['VarAttrs']['FillValueCmems'])
            dox1.ioos_category              = 'Dissolved O2'
            dox1.ancillary_variable         = self.nc_varnames_map['DOX1_QC'] + ' ' + self.nc_varnames_map['PSAL00_QC']
            dox1.sdn_parameter_name         = 'Concentration of oxygen {O2 CAS 7782-44-7} per unit volume of the water body [dissolved plus reactive particulate phase]'
            dox1.sdn_parameter_urn          = 'SDN:P01::DOXYZZXX'
            dox1.sdn_uom_name               = 'Millilitres per litre'
            dox1.sdn_uom_urn                = 'SDN:P06::UMLL'
            dox1.sdn_instrument_name        = 'Sea-Bird SBE 43 Dissolved Oxygen Sensor'
            dox1.sdn_instrument_urn         = 'SDN:L22::TOOL0036'
            dox1[:]                         = data['data'][self.varnames_map['DOX1']][::-1].to_numpy()
            dox1.valid_min                  = min(data['data'][self.varnames_map['DOX1']])
            dox1.valid_max                  = max(data['data'][self.varnames_map['DOX1']]) 
            dox1.sensor_manufacturer        = 'SeaBird'
            dox1.sensor_model               = 'SBE 43'
            if self.cnv_var_attrs_map['DOX1_SENSOR_SN'] in data['attrs']:
                dox1.sensor_serial_number       = data['attrs'][self.cnv_var_attrs_map['DOX1_SENSOR_SN']]
            dox1.observation_type           = 'calculated'
            dox1.references                 = config_survey['VarAttrs']['DoxySbe43Ref']
            dox1.comment                    = 'Dissolved Oxygen concentration derived from DOXV, TEMP00, PRES, PSAL00'
            dox1.history                    = '' 
            
            dox1_qc                         = rootgrp.createVariable(self.nc_varnames_map['DOX1_QC'],"i1",("profile","z",))
            dox1_qc.long_name               = 'OceanSites quality flag'
            dox1_qc.Conventions             = config_survey['QcAttrs']['OceansitesQualityControlConvention']
            dox1_qc._Fillvalue              = int(config_survey['QcAttrs']['OceansitesFillValue'])
            dox1_qc.ioos_category           = 'Quality'
            dox1_qc.valid_min               = int(config_survey['QcAttrs']['OceansitesValidMin'])
            dox1_qc.valid_max               = int(config_survey['QcAttrs']['OceansitesValidMax'])
            dox1_qc.flag_values             = config_survey['QcAttrs']['OceansitesFlagValues']
            dox1_qc.flag_meanings           = config_survey['QcAttrs']['OceansitesFlagMeanings']
            dox1_qc.references              = config_survey['QcAttrs']['OceansitesQualityControlConvention']
            dox1_qc.comment                 = ''
            dox1_qc.history                 = '' 
            dum = [self.qc_flag['no_qc']] * len(data['data'][self.varnames_map['DOX1']])
            dox1_qc[:] = np.asarray(dum) 
        
        if self.varnames_map['DOXV'] in data['data']:
            doxv                            = rootgrp.createVariable(self.nc_varnames_map['DOXV'],"f4",("profile","z",))
            doxv.units                      = 'volts'
            doxv.standard_name              = ''
            doxv.long_name                  = ''
            doxv.coordinates                = self.nc_varnames_map['TIME'] + ' ' + self.nc_varnames_map['LATITUDE'] + ' ' + self.nc_varnames_map['LONGITUDE'] + ' ' + self.nc_varnames_map['DEPH']
            doxv._Fillvalue                 = float(config_survey['VarAttrs']['FillValueCmems'])
            doxv.ioos_category              = 'Dissolved O2'
            doxv.sdn_parameter_name         = 'Raw signal (voltage) of instrument output by oxygen sensor'
            doxv.sdn_parameter_urn          = 'SDN:P01::OXYOCPVL'
            doxv.sdn_uom_name               = 'Volts'
            doxv.sdn_uom_urn                = 'SDN:P06::UVLT'
            doxv.sdn_instrument_name        = 'Sea-Bird SBE 43 Dissolved Oxygen Sensor'
            doxv.sdn_instrument_urn         = 'SDN:L22::TOOL0036'
            doxv[:]                         = data['data'][self.varnames_map['DOXV']][::-1].to_numpy()
            doxv.valid_min                  = min(data['data'][self.varnames_map['DOXV']])
            doxv.valid_max                  = max(data['data'][self.varnames_map['DOXV']]) 
            doxv.sensor_manufacturer        = 'SeaBird'
            doxv.sensor_model               = 'SBE 43'
            doxv.sensor_serial_number       = data['attrs'][self.cnv_var_attrs_map['DOX1_SENSOR_SN']]
            doxv.accuracy                   = 2
            doxv.precision                  = ''
            doxv.resolution                 = ''  
            doxv.observation_type           = 'measured'
            doxv.references                 = config_survey['VarAttrs']['DoxySbe43Ref']
            doxv.comment                    = 'accuracy is ± 2% of saturation'
            doxv.history                    = ''

        if self.varnames_map['FCHLA'] in data['data']:
            fchla                           = rootgrp.createVariable(self.nc_varnames_map['FCHLA'],"f4",("profile","z",))
            fchla.units                     = 'mg m-3'
            fchla.standard_name             = 'mass_concentration_of_inferred_chlorophyll_from_relative_fluorescence_units_in_sea_water'
            fchla.long_name                 = 'Mass Concentration Of Inferred Chlorophyll From Relative Fluorescence Units In Sea Water'
            fchla.coordinates               = self.nc_varnames_map['TIME'] + ' ' + self.nc_varnames_map['LATITUDE'] + ' ' + self.nc_varnames_map['LONGITUDE'] + ' ' + self.nc_varnames_map['DEPH']
            fchla._Fillvalue                = float(config_survey['VarAttrs']['FillValueCmems'])
            fchla.ioos_category             = 'Other'
            fchla.ancillary_variable        = self.nc_varnames_map['FCHLA_QC']
            fchla.sdn_parameter_name        = 'Concentration of chlorophyll-a {chl-a CAS 479-61-8} per unit volume of the water body [particulate >unknown phase] by in-situ chlorophyll fluorometer and manufacturer\'s calibration applied'
            fchla.sdn_parameter_urn         = 'SDN:P01::CPHLPM01'
            fchla.sdn_uom_name              = 'Milligrams per cubic metre'
            fchla.sdn_uom_urn               = 'SDN:P06::UMMC'
            fchla.sdn_instrument_name       = ''
            fchla.sdn_instrument_urn        = 'SDN:L22::'
            fchla[:]                        = data['data'][self.varnames_map['FCHLA']][::-1].to_numpy()
            fchla.valid_min                 = min(data['data'][self.varnames_map['FCHLA']])
            fchla.valid_max                 = max(data['data'][self.varnames_map['FCHLA']]) 
            fchla.sensor_manufacturer       = 'SeaBird'
            fchla.sensor_model              = ''
            if self.cnv_var_attrs_map['FCHLA_SENSOR_SN'] in data['attrs']:
                fchla.sensor_serial_number      = data['attrs'][self.cnv_var_attrs_map['FCHLA_SENSOR_SN']]
            fchla.observation_type          = 'calculated'
            fchla.references                = ''
            fchla.comment                   = 'Artificial chlorophyll data computed from bio-optical sensor raw voltage measurements. The fluorometer is equipped with a 470nm peak wavelength LED to irradiate and a photodetector paired with an optical filter which measures everything that fluoresces in the region of 695nm. Originally expressed in ug/l, 1l = 0.001m3 was assumed.'
            fchla.history                   = '' 
            
            fchla_qc                         = rootgrp.createVariable(self.nc_varnames_map['FCHLA_QC'],"i1",("profile","z",))
            fchla_qc.long_name               = 'OceanSites quality flag'
            fchla_qc.Conventions             = config_survey['QcAttrs']['OceansitesQualityControlConvention']
            fchla_qc._Fillvalue              = int(config_survey['QcAttrs']['OceansitesFillValue'])
            fchla_qc.ioos_category           = 'Quality'
            fchla_qc.valid_min               = int(config_survey['QcAttrs']['OceansitesValidMin'])
            fchla_qc.valid_max               = int(config_survey['QcAttrs']['OceansitesValidMax'])
            fchla_qc.flag_values             = config_survey['QcAttrs']['OceansitesFlagValues']
            fchla_qc.flag_meanings           = config_survey['QcAttrs']['OceansitesFlagMeanings']
            fchla_qc.references              = config_survey['QcAttrs']['OceansitesQualityControlConvention']
            fchla_qc.comment                 = ''
            fchla_qc.history                 = '' 
            dum                              = [self.qc_flag['no_qc']] * len(data['data'][self.varnames_map['FCHLA']])
            fchla_qc[:]                      = np.asarray(dum) 
 

        if self.varnames_map['PAR'] in data['data']:
            par = rootgrp.createVariable(self.nc_varnames_map['PAR'],"f4",("profile","z",))
            par.units = 'umole m-2 s-1'
            par.standard_name = 'downwelling_photosynthetic_photon_flux_in_sea_water'
            par.long_name = 'downwelling_photosynthetic_photon_flux_in_sea_water'
            par.coordinates = self.nc_varnames_map['TIME'] + ' ' + self.nc_varnames_map['LATITUDE'] + ' ' + self.nc_varnames_map['LONGITUDE'] + ' ' + self.nc_varnames_map['DEPH']
            par._Fillvalue = float(config_survey['VarAttrs']['FillValueCmems'])
            par.ioos_category = 'Other'
            par.ancillary_variable = self.nc_varnames_map['PAR_QC']
            par[:] = data['data'][self.varnames_map['PAR']][::-1].to_numpy()
            par.valid_min = min(data['data'][self.varnames_map['PAR']])
            par.valid_max = max(data['data'][self.varnames_map['PAR']]) 
            par.sensor_manufacturer = 'SeaBird'
            par.sensor_model = ''
            par.sensor_serial_number = ''#data['attrs'][self.cnv_var_attrs_map['DOX1_SENSOR_SN']]
            par.observation_type = 'calculated'
            par.references = ''
            par.comment = ''
            par.history = '' 
            
            par_qc = rootgrp.createVariable(self.nc_varnames_map['PAR_QC'],"f4",("profile","z",))
            par_qc.long_name               = 'OceanSites quality flag'
            par_qc.Conventions             = config_survey['QcAttrs']['OceansitesQualityControlConvention']
            par_qc._Fillvalue              = int(config_survey['QcAttrs']['OceansitesFillValue'])
            par_qc.ioos_category           = 'Quality'
            par_qc.valid_min               = int(config_survey['QcAttrs']['OceansitesValidMin'])
            par_qc.valid_max               = int(config_survey['QcAttrs']['OceansitesValidMax'])
            par_qc.flag_values             = config_survey['QcAttrs']['OceansitesFlagValues']
            par_qc.flag_meanings           = config_survey['QcAttrs']['OceansitesFlagMeanings']
            par_qc.references              = config_survey['QcAttrs']['OceansitesQualityControlConvention']
            par_qc.comment                 = ''
            par_qc.history                 = '' 
            dum                            = [self.qc_flag['no_qc']] * len(data['data'][self.varnames_map['PAR']])
            par_qc[:]                      = np.asarray(dum) 

        
        rootgrp.close()
        return
        

        
        
        
