#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Mar  4 09:22:43 2021

@author: a33272
"""

import netCDF4 as nc
import gsw
import numpy as np
import datetime

from exporters.ctd_nc_exporters.ctd_level0_exporter import CtdLevel0 as CtdLevel0


class CtdLevel1C(CtdLevel0):
    def __init__(self, *args):
        super(CtdLevel1C, self).__init__(*args)

    
    #def create_corrected_vars(self, var_name, file_path, correction_metadata, config, config_field_calib):
    def create_corrected_vars(self, **kwargs):
        dataset_nc = nc.Dataset(kwargs['file_path'], 'r+')
        
        dataset_nc.date_created = datetime.datetime.now().strftime('%Y-%m-%dT%H%M%SZ') 
        dataset_nc.date_modified = datetime.datetime.now().strftime('%Y-%m-%dT%H%M%SZ')
        
        temp = dataset_nc.variables[self.nc_varnames_map['TEMP00']][:]
        pres = dataset_nc.variables[self.nc_varnames_map['PRES']][:]
        psal = dataset_nc.variables[self.nc_varnames_map['PSAL00']][:]
        
        if kwargs['var_name'] == self.nc_varnames_map['CNDC00_CORR']:
            cndc_corr = dataset_nc.createVariable(kwargs['var_name'],"f4",("z",))        
            cndc_corr.units = 'mS cm-1'
            cndc_corr.standard_name = 'sea_water_electrical_conductivity'
            cndc_corr.ancillary_variable = self.nc_varnames_map['CNDC00_QC']
            cndc_corr.ioos_category = 'Salinity'
            cndc_corr.comment =  ''
            cndc_corr.field_calibration_scale_factor = kwargs['correction_metadata']['slope_coef']
            cndc_corr.calibration_equation = 'CNDC00_CORR = calibration_slope * CNDC00' 
            cndc_corr.observation_type = 'corrected_measurements'
            cndc_corr.references = kwargs['config']['QcAttrs']['QcRefSOCIB']
            cndc =  gsw.conversions.C_from_SP(psal, temp, pres)
            cndc_corrected = cndc * kwargs['correction_metadata']['slope_coef']
            dataset_nc.variables[self.nc_varnames_map['CNDC00_CORR']][:] = cndc_corrected
            
        elif kwargs['var_name'] == self.nc_varnames_map['PSAL00_CORR']:
            psal_corr = dataset_nc.createVariable(var_name,"f4",("z",))
            psal_corr.units = 'PSU'
            psal_corr.standard_name = 'sea_water_salinity'
            psal_corr.ancillary_variable = self.nc_varnames_map['PSAL00_QC']
            psal_corr.ioos_category = 'Salinity'
            comment_str =  '''Outliers removal process during  the calibration with field samples: 
                1) Manual: Removed all data points which were flagged during the salinometer anaylsis, and all data points < 10 m along with other obvious outliers. 
                2) Removed all data points where the difference between sensors (residuals) is larger than 0.01 from the mean difference. 
                3) Removed all residual data points that deviate more than {0}*stds from mean. 
                4) removed all residual data points that deviate more than {1}*stds from the new mean.
                Uncertainty values are provided using the standard deviation of the residual salinities comparing the samples measurement with the sensor measurments.
                The mean value of the residual salinities is {2}'''
                
            psal_corr.comment =  comment_str.format(config_field_calib['SalinitySettings']['OutliersStd1'], 
                                                    config_field_calib['SalinitySettings']['OutliersStd2'],
                                                    str(correction_metadata['mean_residual'])
                                                    )
            psal_corr.references = config['QcAttrs']['QcRefSOCIB']
            psal_corr.field_calibration_uncertainty =  correction_metadata['std_residual']


            cndc_corr_mS = dataset_nc.variables[self.nc_varnames_map['CNDC00_CORR']][:] 
            psal_corrected = gsw.conversions.SP_from_C(cndc_corr_mS, temp, pres) # reecalculate salinity using cndc_corr            
            dataset_nc.variables[self.nc_varnames_map['PSAL00_CORR']][:] = psal_corrected
            var_corr = psal_corrected

        elif kwargs['var_name'] == self.nc_varnames_map['DOX1_CORR']:
            dox1_corr = dataset_nc.createVariable(self.nc_varnames_map['DOX1_CORR'],"f4",("z",))        
            dox1_corr.units = 'ml L-1'
            dox1_corr.standard_name = 'volume_concentration_of_dissolved_molecular_oxygen_in_sea_water'
            dox1_corr.ancillary_variable = self.nc_varnames_map['DOX1_QC']
            dox1_corr.ioos_category = 'Dissolved O2'
            comment_str =  '''Outliers removal process during  the calibration with field samples: 
                1) Manual: Removed all data points which were flagged during the titration anaylsis, and all data points < 10 m along with other obvious outliers. 
                2) Removed all data points where the difference between sensors (residuals) is larger than 0.1 from the mean difference. 
                3) Removed all residual data points that deviate more than {0}*stds from mean. 
                4) removed all residual data points that deviate more than {1}stds from the new mean.
                Uncertainty values are provided using the standard deviation of the residual dissolved oxygen comparing the samples measurement with the sensor measurments.
                The mean value of the residual dissolved oxygen is {2}'''
                
            dox1_corr.comment =  comment_str.format(kwargs['config_field_calib']['OxygenSettings']['OutliersStd1'], 
                                                    kwargs['config_field_calib']['OxygenSettings']['OutliersStd2'],
                                                    str(kwargs['correction_metadata']['mean_residual'])
                                                    )
            dox1_corr.references = kwargs['config']['QcAttrs']['QcRefSbeDox']
            dox1_corr.field_calibration_uncertainty = kwargs['correction_metadata']['std_residual']
            dox1_corr.field_calibration_scale_factor = kwargs['correction_metadata']['slope_coef']
            dox1_corr.calibration_equation = 'Murphy-Larson equation: Soc * [V - Voffset + Taucor(V,T,P)] * Tcor(T) * Pcor(P,T) * OxSOL(T,S)' 
            dox1_corr.observation_type = 'corrected_measurements'
            
            Voff    = float(kwargs['config_field_calib']['OxygenSettings']['Voff'])
            A0      = float(kwargs['config_field_calib']['OxygenSettings']['A0'])
            B0      = float(kwargs['config_field_calib']['OxygenSettings']['B0'])
            C0      = float(kwargs['config_field_calib']['OxygenSettings']['C0'])
            D0      = float(kwargs['config_field_calib']['OxygenSettings']['D0'])
            D1      = float(kwargs['config_field_calib']['OxygenSettings']['D1'])
            D2      = float(kwargs['config_field_calib']['OxygenSettings']['D2'])
            E0      = float(kwargs['config_field_calib']['OxygenSettings']['E0'])
            tau20   = float(kwargs['config_field_calib']['OxygenSettings']['tau20'])
            H1      = float(kwargs['config_field_calib']['OxygenSettings']['H1'])
            H2      = float(kwargs['config_field_calib']['OxygenSettings']['H2'])
            H3      = float(kwargs['config_field_calib']['OxygenSettings']['H3'])
            

            dox_volt = dataset_nc.variables[self.nc_varnames_map['DOXV']][:]
            diff_volt_time = 0.0033
            ptemp = gsw.pt0_from_t(psal, temp, pres)
            prho_exact = gsw.pot_rho_t_exact(psal, temp, pres, 0)
            tauTP = tau20*D0*(np.exp(D1*pres + D2*(temp-20)))
            tauTP = 0
            dox_sol_TS = gsw.O2sol_SP_pt(psal, ptemp) #/ 44.6596 
            
            TERM1 = dox_volt + Voff + (tauTP * diff_volt_time )
            TERM2 = 1 + A0*temp + B0*temp**2 + C0*temp**3 
            TERM3 = np.exp(E0*pres/(temp+273.15))
            
            dox_umolkg = kwargs['correction_metadata']['slope_coef'] * TERM1  * dox_sol_TS * TERM2 * TERM3
            dox_mlL = dox_umolkg / 44660 * prho_exact # convert umol/kg to ml/L OOI docs
            dataset_nc.variables[self.nc_varnames_map['DOX1_CORR']][:] = dox_mlL
            var_corr = dox_mlL

        elif kwargs['var_name'] == self.nc_varnames_map['FCHLA_CORR']:
            fchla_corr = dataset_nc.createVariable(self.nc_varnames_map['FCHLA_CORR'],"f4",("z",))        
            fchla_corr.units = 'mg m-3'
            fchla_corr.standard_name = ''
            fchla_corr.ancillary_variable = self.nc_varnames_map['FCHLA_QC']
            fchla_corr.ioos_category = 'Other'
            comment_str =  ''' '''
                
            fchla_corr.comment =  comment_str.format(kwargs['config_field_calib']['ChlaSettings']['OutliersStd1'], 
                                                    kwargs['config_field_calib']['ChlaSettings']['OutliersStd2'],
                                                    str(kwargs['correction_metadata']['mean_residual'])
                                                    )
            fchla_corr.references = kwargs['config']['QcAttrs']['QcRefSbeDox']
            fchla_corr.field_calibration_uncertainty = kwargs['correction_metadata']['std_residual']
            fchla_corr.field_calibration_scale_factor = kwargs['correction_metadata']['sf_new']
            fchla_corr.field_calibration_offset = kwargs['correction_metadata']['dc_new']
            fchla_corr.calibration_equation = '(FCHLA * scale_factor) + offset'
            fchla_corr.observation_type = 'corrected_measurements'
            
            #fchla = dataset_nc.variables[self.nc_varnames_map['FCHLA']][:]
            #slope = kwargs['correction_metadata']['sf_new']
            #offset = kwargs['correction_metadata']['dc_new']
            station = 'sta' + str(kwargs['station']).zfill(4)
            dataset_nc.variables[self.nc_varnames_map['FCHLA_CORR']][:] = kwargs['dataset_cnv'][station][self.cnv_varnames_map['FCHLA_CORR']]   
            #dataset_nc.variables[self.nc_varnames_map['FCHLA_CORR']][:] = (fchla * slope) + offset
            #var_corr = (fchla * slope) + offset
            
            fchla_corr_qc                         = dataset_nc.createVariable(self.nc_varnames_map['FCHLA_CORR_QC'],"i1",("profile","z",))
            fchla_corr_qc.long_name               = 'OceanSites quality flag'
            fchla_corr_qc.Conventions             = kwargs['config']['QcAttrs']['OceansitesQualityControlConvention']
            fchla_corr_qc._Fillvalue              = int(kwargs['config']['QcAttrs']['OceansitesFillValue'])
            fchla_corr_qc.ioos_category           = 'Quality'
            fchla_corr_qc.valid_min               = int(kwargs['config']['QcAttrs']['OceansitesValidMin'])
            fchla_corr_qc.valid_max               = int(kwargs['config']['QcAttrs']['OceansitesValidMax'])
            fchla_corr_qc.flag_values             = kwargs['config']['QcAttrs']['OceansitesFlagValues']
            fchla_corr_qc.flag_meanings           = kwargs['config']['QcAttrs']['OceansitesFlagMeanings']
            fchla_corr_qc.references              = kwargs['config']['QcAttrs']['OceansitesQualityControlConvention']
            fchla_corr_qc.comment                 = ''
            fchla_corr_qc.history                 = '' 
            dum                                   = [self.qc_flag['no_qc']] * len(kwargs['dataset_cnv'][station][self.cnv_varnames_map['FCHLA_CORR']])
            fchla_corr_qc[:]                      = np.asarray(dum) 
            
        dataset_nc.close()
        #return var_corr
        
        