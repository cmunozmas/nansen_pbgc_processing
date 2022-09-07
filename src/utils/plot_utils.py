#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu May 20 12:35:43 2021

@author: a33272
"""

from bokeh.plotting import ColumnDataSource, figure, output_file, show
from bokeh.layouts import row
import utils.load_netcdf as load_netcdf
import numpy as np


def plot_station_profile(file_path, figs_path, df, df_original, residuals_info_corr, config):  
          
    # Plot results for each station separate
    #prepare data
    data = load_netcdf.LoadNetCDF(config).load_nc_file(file_path)
    for item in data.keys():
        if type(data[item]) != str:
            if data[item].size > 1:
                data[item] = data[item].transpose()
                data[item] = np.reshape(data[item], (len(data[item]),))
                data[item] = data[item].tolist()   
                
    TOOLS = "hover, help, box_zoom, reset"
    TOOLTIPS = [
        ("index", "$index"),
        ("(x,y)", "($x, $y)"),
        ("date", "@date"),
    ]
                
    station_name = str(int(data['station']))
    if df['station'].str.contains(station_name).any():
        # profile_time = data[station]['metadata']['datetime']
        output_file(figs_path + station_name + '_dox.html')
        s1 = figure(plot_width=800, plot_height=800, tooltips=TOOLTIPS, background_fill_color="#fafafa", tools=TOOLS, title= 'DOX - ' + station_name)
        s1.square(df_original['Winkler'][df_original['station']==station_name], df_original['PrDM'][df_original['station']==station_name], 
                  color='red', alpha=0.8, fill_color=None, size=8,
                  muted_color='red', muted_alpha=0.2, legend=station_name + ' - bottle samples original')     
        s1.square(df['Winkler'][df['station']==station_name], df['PrDM'][df['station']==station_name], 
                  color='green', alpha=0.8, fill_color=None, size=8,
                  muted_color='green', muted_alpha=0.2, legend=station_name + ' - bottle samples used for correction')  
        s1.triangle(df_original['Sbeox0ML/L'][df_original['station']==station_name], df_original['PrDM'][df_original['station']==station_name], 
                  color='black', alpha=0.8, fill_color='black', size=8,
                  muted_color='black', muted_alpha=0.2, legend=station_name + ' - upcast btl measurement')  
        s1.circle(data['dox'], data['pres'], 
                  color='navy', alpha=0.8,
                  muted_color='navy', muted_alpha=0.4, legend=station_name + ' - downcast CTD measurements')  
        s1.circle(data['dox'][data['dox_qc']==0], data['pres'][data['dox_qc']==0], 
                  color='blue', alpha=0.8,
                  muted_color='blue', muted_alpha=0.4, legend=station_name + ' - qc flag 0')  
        s1.circle(data['dox'][data['dox_qc']==1], data['pres'][data['dox_qc']==1], 
                  color='green', alpha=0.8,
                  muted_color='green', muted_alpha=0.4, legend=station_name + ' - qc flag 1')  
        s1.circle(data['dox'][data['dox_qc']==4], data['pres'][data['dox_qc']==4], 
                  color='red', alpha=0.8,
                  muted_color='red', muted_alpha=0.2, legend=station_name + ' - qc flag 4')  
        s1.line(data['dox'], data['pres'], line_width=2, color='blue', alpha=0.4,
                muted_color='green', muted_alpha=0.2, legend = station_name + ' - downcast dox')  
        s1.line(data['dox_corr'], data['pres'], line_width=2, color='green', alpha=0.4,
                muted_color='green', muted_alpha=0.2, legend = station_name + ' - downcast dox_corr')   
       
        s2 = figure(plot_width=400, plot_height=800, tooltips=TOOLTIPS, background_fill_color="#fafafa", tools=TOOLS, title= 'PSAL - ' + station_name)     
        s2.line(data['psal'], data['pres'], line_width=2, color='navy', alpha=0.4,
                muted_color='navy', muted_alpha=0.2)  
        s2.circle(data['psal'][data['psal_qc']==0], data['pres'][data['psal_qc']==0], 
                  color='navy', alpha=0.8,
                  muted_color='navy', muted_alpha=0.4, legend=station_name + ' - qc flag 0')  
        s2.circle(data['psal'][data['psal_qc']==1], data['pres'][data['psal_qc']==1], 
                  color='green', alpha=0.8,
                  muted_color='green', muted_alpha=0.4, legend=station_name + ' - qc flag 1')  
        s2.circle(data['psal'][data['psal_qc']==4], data['pres'][data['psal_qc']==4], 
                  color='red', alpha=0.8,
                  muted_color='red', muted_alpha=0.2, legend=station_name + ' - qc flag 4')  
     
        s3 = figure(plot_width=400, plot_height=800, tooltips=TOOLTIPS, background_fill_color="#fafafa", tools=TOOLS, title= 'TEMP - ' + station_name)     
        s3.circle(data['temp'][data['temp_qc']==0], data['pres'][data['temp_qc']==0], 
                  color='navy', alpha=0.8,
                  muted_color='navy', muted_alpha=0.4, legend=station_name + ' - qc flag 0')  
        s3.circle(data['temp'][data['temp_qc']==1], data['pres'][data['temp_qc']==1], 
                  color='green', alpha=0.8,
                  muted_color='green', muted_alpha=0.4, legend=station_name + ' - qc flag 1')  
        s3.circle(data['temp'][data['temp_qc']==4], data['pres'][data['temp_qc']==4], 
                  color='red', alpha=0.8,
                  muted_color='red', muted_alpha=0.2, legend=station_name + ' - qc flag 4')  
        s3.line(data['temp'], data['pres'], line_width=2, color='navy', alpha=0.4,
                muted_color='navy', muted_alpha=0.2)             
    
        s1.legend.click_policy="hide"
        s1.legend.location = 'bottom_right'
        s2.legend.click_policy="hide"
        s2.legend.location = 'bottom_right'  
        s3.legend.click_policy="hide"
        s3.legend.location = 'bottom_right'  
        
        s1.y_range.flipped = True 
        s2.y_range.flipped = True 
        s3.y_range.flipped = True 
        show(row(s1, s2, s3))
        
        return data
    
    
def plot_all_station_profiles(files_list, figs_path, df, df_original, residuals_info_corr, config):  

    TOOLS = "hover, help, box_zoom, reset"
    TOOLTIPS = [
        ("index", "$index"),
        ("(x,y)", "($x, $y)"),
        ("date", "@date"),
    ]
    s1 = figure(plot_width=800, plot_height=800, tooltips=TOOLTIPS, background_fill_color="#fafafa", tools=TOOLS, title= 'DOX')
    s2 = figure(plot_width=800, plot_height=800, tooltips=TOOLTIPS, background_fill_color="#fafafa", tools=TOOLS, title= 'DOX_CORR') 
    
    for file_path in files_list:      
        # Plot results for each station separate
        data = load_netcdf.LoadNetCDF(config).load_nc_file(file_path)
    
        station_name = str(int(data['station']))
    
        # profile_time = data[station]['metadata']['datetime']
        output_file(figs_path + 'all_stations_dox.html')
        # s1 = figure(plot_width=800, plot_height=800, tooltips=TOOLTIPS, background_fill_color="#fafafa", tools=TOOLS, title= 'DOX - ' + station_name)
        # s1.square(df_original['Winkler'][df_original['station']==station_name], df_original['PrDM'][df_original['station']==station_name], 
        #           color='red', alpha=0.8, fill_color=None, size=8,
        #           muted_color='red', muted_alpha=0.2, legend=station_name + ' - bottle samples original')     
        # s1.square(df['Winkler'][df['station']==station_name], df['PrDM'][df['station']==station_name], 
        #           color='green', alpha=0.8, fill_color=None, size=8,
        #           muted_color='green', muted_alpha=0.2, legend=station_name + ' - bottle samples used for correction')  
        # s1.circle(data['dox'], data['pres'], 
        #           color='navy', alpha=0.8,
        #           muted_color='navy', muted_alpha=0.4, legend=station_name + ' - measurements')  
        # s1.circle(data['dox'][data['dox_qc']==0], data['pres'][data['dox_qc']==0], 
        #           color='blue', alpha=0.8,
        #           muted_color='blue', muted_alpha=0.4, legend=station_name + ' - qc flag 0')  
        # s1.circle(data['dox'][data['dox_qc']==1], data['pres'][data['dox_qc']==1], 
        #           color='green', alpha=0.8,
        #           muted_color='green', muted_alpha=0.4, legend=station_name + ' - qc flag 1')  
        # s1.circle(data['dox'][data['dox_qc']==4], data['pres'][data['dox_qc']==4], 
        #           color='red', alpha=0.8,
        #           muted_color='red', muted_alpha=0.2, legend=station_name + ' - qc flag 4')  
        s1.line(data['dox'], data['pres'], line_width=2, color='blue', alpha=0.4,
                muted_color='green', muted_alpha=0.2, legend = station_name)  
        s2.line(data['dox_corr'], data['pres'], line_width=2, color='green', alpha=0.4,
                muted_color='green', muted_alpha=0.2, legend = station_name)   
       
        # s2 = figure(plot_width=400, plot_height=800, tooltips=TOOLTIPS, background_fill_color="#fafafa", tools=TOOLS, title= 'PSAL - ' + station_name)     
        # s2.line(data['psal'], data['pres'], line_width=2, color='navy', alpha=0.4,
        #         muted_color='navy', muted_alpha=0.2)  
        # s2.circle(data['psal'][data['psal_qc']==0], data['pres'][data['psal_qc']==0], 
        #           color='navy', alpha=0.8,
        #           muted_color='navy', muted_alpha=0.4, legend=station_name + ' - qc flag 0')  
        # s2.circle(data['psal'][data['psal_qc']==1], data['pres'][data['psal_qc']==1], 
        #           color='green', alpha=0.8,
        #           muted_color='green', muted_alpha=0.4, legend=station_name + ' - qc flag 1')  
        # s2.circle(data['psal'][data['psal_qc']==4], data['pres'][data['psal_qc']==4], 
        #           color='red', alpha=0.8,
        #           muted_color='red', muted_alpha=0.2, legend=station_name + ' - qc flag 4')  
     
           

    s1.legend.click_policy="hide"
    s1.legend.location = 'bottom_right'
    s2.legend.click_policy="hide"
    s2.legend.location = 'bottom_right'  
    
    s1.y_range.flipped = True 
    s2.y_range.flipped = True 

    show(row(s1, s2))
       
    return data