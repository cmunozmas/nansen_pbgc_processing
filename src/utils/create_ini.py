#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Nov 11 16:20:36 2022

@author: a33272
"""
import os

survey_list = [2008404]
file_out_path = '/home/a33272/Documents/python/nansen_pbgc_processing/config/'
file_in_path = '/test_data/ctd/'

template = '''

[Path]
MainPath: /home/a33272/Documents/python/nansen_importers/
ProcessingLogPath: /home/a33272/Documents/python/nansen_importers/log/processing.log


[GlobalAttrs]
Project: EAF-Nansen Programme
CruiseId: 
CruiseName: 
CruisePurpose:
CruiseDateStart: 
CruiseDateStop: 
  
PlatformVocabulary: ICES Ship Codes
PlatformType: Research Vessel
PlatformName: R/V Dr. Fridtjof Nansen
ImrPlatformId: 4
IcesPlatformId: 58D4
PlatformCallSign: NA
PrincipalInvestigator:
PrincipalInvestigatorEmail: 
Institution: 
Citation:
Acknowledgement: These data were collected through the scientific surveys with the R/V Dr Fridtjof Nansen as part of the collaboration between the EAF-Nansen Programme and NAME OF COUNTRY/COUNTRIES/OR RFMO WHERE SURVEY TOOK PLACE. The EAF-Nansen Programme is a partnership between the Food and Agriculture Organization of the United Nations (FAO), the Norwegian Agency for Development Cooperation (Norad), and the Institute of Marine Research (IMR), Norway for sustainable management of the fisheries of partner countries.
CtdTitle: CTD profile data
CtdAbstract: Single station CTD profile data belonging to the EAF-NANSEN Programme, survey
BottleTitle: CTD profile water bottle samples data
BottleAbstract: Single station CTD profile water samples data belonging to the EAF-NANSEN Programme, survey
License: https://nansen-surveys.imr.no/doku.php?id=data_policy
Conventions: CF-1.8, ACDD-1.3, OceanSITES Manual 1.4, SeaDataNet
KeywordsVocabulary: GCMD:GCMD Keywords, CF:NetCDF COARDS Climate and Forecast Standard Names
Keywords:EARTH SCIENCE > OCEANS > OCEAN CHEMISTRY > OXYGEN, EARTH SCIENCE > OCEANS > OCEAN PRESSURE > WATER PRESSURE, EARTH SCIENCE > OCEANS > OCEAN TEMPERATURE > WATER TEMPERATURE, EARTH SCIENCE >, OCEANS > SALINITY/DENSITY > CONDUCTIVITY, EARTH SCIENCE > OCEANS > SALINITY/DENSITY > SALINITY
StandardNameVocabulary: CF Standard Name Table v77
NcVersion:netCDF-4
Doi:

FeatureType: Profile
DataCentre: Global Development Research Group, Institute of Marine Research, Norway (IMR)
DataCentreEmail: nansen_data@hi.no
ContributorName: 
ContributorRole: 
PublisherName: Global Development Research Group, Institute of Marine Research, Norway (IMR)
PublisherUrl: https://www.hi.no/en/hi/forskning/research-groups-1/marine-research-in-developing-countries
PublisherEmail:nansen_data@hi.no
InstrumentSerialNumber:
InstrumentType:CT
InstrumentMount:
InstrumentManufacturerName:
InstrumentModel:

[VarAttrs]
SdnEdmoCode: 
SdnCsrRefNum: 
DoxySbe43Ref: Seabird application note AN64: SBE 43 Dissolved Oxygen Sensor - Background Information, Deployment Recommendations, and Cleaning and Storage (www.seabird.com/application-notes)
Pss78SbeRef: Seabird Application Note AN14: 1978 Practical Salinity Scale (https://www.seabird.com/application-notes)
FillValueCmems: 9.96921e+36
UncertaintyComment: 

[QcAttrs]
OceansitesQualityControlConvention: OceanSites reference table 2
OceansitesFillValue: -128
OceansitesValidMin: 0
OceansitesValidMax: 9
OceansitesFlagValues: 0, 1, 2, 3, 4, 5, 6, 7, 8, 9
OceansitesFlagMeanings: no_qc_performed good_data probably_good_data bad_data_that_are_potentially_correctable bad_data value_changed not_used nominal_value interpolated_value missing_value

SdnQualityControlConvention: SeaDataNet measurand qualifier flags
SdnFillValue: 57
SdnValidMin: 48
SdnValidMax: 65
SdnFlagValues: 48, 49, 50, 51, 52, 53, 54, 55, 56, 57, 65
SdnFlagMeanings: no_quality_control good_value probably_good_value probably_bad_value bad_value changed_value value_below_detection value_in_excess interpolated_value missing_value value_phenomenon_uncertain
EurogoosQualityControlRef: EuroGOOS DATA-MEQ Working Group flag scale.
OceansitesQualityControlRef: 
SdnQualityControlRef: 


QcRefSOCIB: Salinity calibration reference: Seabird application note AN31 (www.seabird.com/application-notes). 
QcRefSbeDox: SBE 43 Dissolved Oxygen Sensor Calibration and Data Corrections - Seabird application note AN64-2 (www.seabird.com/application-notes). 
QcRefDatameq: EuroGOOS DATA-MEQ Working Group (2010) Recommendations for in-situ data Near Real Time Quality Control [Version 1.2]. EuroGOOS, 23pp. DOI: http://dx.doi.org/10.25607/OBP-214.
QcRefArgoBgc: Thierry Virginie, Bittig Henry, The Argo-Bgc Team (2018). Argo quality control manual for dissolved oxygen concentration. https://doi.org/10.13155/46542.
QcRefArgoBgcCheatsheets: Baldry, K. (ed.) (2021) Biogeochemical Argo Cheat Sheets: Data distribution, Quality control and GDAC, Chlorophyll-a, Optical backscatter, pH, Irradiance, Oxygen, Nitrate. Hobart, Tasmania, Institute of Marine and Antarctic Studies, 8pp. DOI: http://dx.doi.org/10.25607/OBP-981.

'''

for survey in survey_list:
    survey_str = str(survey)
    survey_data_in_path = file_in_path + survey_str + '/'
    if survey_data_in_path not in file_in_path:
        os.mkdir(survey_data_in_path)
        os.mkdir(survey_data_in_path + 'rawInput/')
        os.mkdir(survey_data_in_path + 'rawInput/ctd/')    
    settings_list = ['CruiseId:', 'CtdAbstract:', 'BottleAbstract:']
    with open(file_out_path + 'config_' + survey_str + '.ini','w') as file:
        for line in template.split('\n'):
            if any(ext in line for ext in settings_list):
                file.write(line + ' ' + survey_str + '\n')
            else:
                file.write(line + '\n')

