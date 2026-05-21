import numpy as np
import pandas as pd
import scipy as sp
import matplotlib.pyplot as plt
import os
import io
import glob
import json

output_type = str(input('Output (time(tp/tf)/scatter(s)): '))
ignore_type = str(input('Ignore nozzles: '))
try:
    ignore_type = list(map(lambda x:int(x),list(ignore_type.split(' '))))
except:
    ignore_type = [None]

# Selecetion correct data files

min_length = 0
line = lambda x,m,b:m*x+b

# flow_cal = lambda Q:Q[300:]*0.89456928+2.1059525 old cal for previous flow sensor
flow_cal = lambda Q:line(Q[min_length:],0.86072889,-2.49415216)
pres_cal = lambda P,h:line(P[min_length:],-5.10247957e-06,1.53065778e+00) if h>0 else line(P[min_length:],9.20808975e-05,-2.76466579e+01)
no_cal = lambda A:A

pressure = []
flowrate = []
flow_err = []
height__ = []
raw_pres = []
raw_flow = []

data_directory = './Results_static_pressure/Results_static_pressure'
files = glob.glob('./Results_static_pressure/Results_static_pressure/*')


for i,file in enumerate(files):
    full_path = data_directory+file
    with open('./.exp_metadata.json') as jf:
        metadata = json.load(jf)
        nozzle = metadata[file[50:66]]["nozzle"]
        height = metadata[file[50:66]]["height"]
        if nozzle not in ignore_type:
            continue

    # Reading the data files
    try:
        with open(file,'rt') as text:
            data = text.read().replace('"','')
        data = pd.read_csv(io.StringIO(data),names=['flow','p1'],usecols=[0,2],header=None)
    except:
        continue

    pressure.append(np.mean(pres_cal(data['p1'],height)))
    flowrate.append(np.mean(flow_cal(data['flow'])))

    par,_ = sp.optimize.curve_fit(lambda x,m,b:m*x+b,pres_cal(data['p1'],height),flow_cal(data['flow']))
    error = np.sqrt(np.var(flow_cal(data['flow']))+np.var(pres_cal(data['p1'],height))*par[0]**2)
    flow_err.append(error)
    height__.append(height/10)
    
    # Time series of data
    if output_type=='tf':
        plt.plot(flow_cal(data['flow'].to_numpy()),'.')
        plt.xlabel('Time [s]')
        plt.ylabel('Flowrate [mlh]')

    if 'tp' in output_type:
        plt.plot(pres_cal(data['p1'].to_numpy(),height),'.')
        if 'tpp'==output_type:
            plt.plot(sp.ndimage.gaussian_filter(pres_cal(data['p1'].to_numpy(),height),20),'.')
        plt.xlabel('Time [s]')
        plt.ylabel('Pressure [kPa]')

    # Full scatter of data
    if output_type=='s':
        plot_p = pres_cal(data['p1'].to_numpy(),height)
        plot_q = flow_cal(data['flow'].to_numpy())
        plot_h = np.array([height for _,_ in enumerate(plot_p)])/10
        plt.scatter(plot_p,plot_q,c=np.linspace(0,1,len(plot_p)),cmap='rainbow')
        if i==0:
            plt.colorbar()
        plt.ylabel('Flowrate [mlh]')
        plt.xlabel('Pressure [kPa]')

    # Scatter of mean values
    if output_type=='sm':
        plt.plot(np.mean(pres_cal(data['p1'].to_numpy(),height)),np.mean(flow_cal(data['flow'].to_numpy())),'o',c='crimson' if nozzle==ignore_type[0] else 'seagreen')
        plt.xlabel('Pressure [kPa]')
        plt.ylabel('Flowrate [mlh]')

    # Calibration plots
    if output_type=='cp':
        sensor_val = np.mean(data['p1'].to_numpy())
        plt.plot(height/10,sensor_val,'.',c='seagreen')
        plt.xlabel('Applied Pressure [Pa]')
        plt.ylabel('Sensor Readout [a.u.]')
        raw_pres.append(sensor_val)

    if output_type=='cf':
        sensor_val = np.mean(data['flow'].to_numpy())
        plt.plot(height,sensor_val,'.',c='seagreen')
        plt.xlabel('Applied Flowrate [mlh]')
        plt.ylabel('Sensor Readout [a.u.]')
        raw_flow.append(sensor_val)

#################################################################      
        
# Calibration plots
if output_type=='cp':
    par,_ = sp.optimize.curve_fit(line,raw_pres,height__)
    print(par)
    par,_ = sp.optimize.curve_fit(line,height__,raw_pres)
    plt.plot(height__,line(np.array(height__),*par),'--',c='goldenrod')

if output_type=='cf':
    flow__ = 10*np.array(height__)
    par,_ = sp.optimize.curve_fit(line,raw_flow,flow__)
    print(par)
    par,_ = sp.optimize.curve_fit(line,flow__,raw_flow)
    plt.plot(flow__,line(flow__,*par),'--',c='goldenrod')

# Estimate linear resistance
if output_type=='r':
    par,cov = sp.optimize.curve_fit(line,flowrate,pressure)
    print(par[0],' + ',np.sqrt(cov[0,0]))

# Write data to file
if len(ignore_type)==1 and output_type=='w':
    print('Saving file')
    np.savetxt(f'presflow_{ignore_type[0]}.csv',np.asarray([pressure,flowrate,flow_err]).T,delimiter=',')

if len(ignore_type)==1 and output_type=='wn':
    print('Saving file')
    pressure = list(map(lambda x:x-19.5,pressure))
    np.savetxt(f'presflow_{ignore_type[0]}.csv',np.asarray([pressure,flowrate,flow_err]).T,delimiter=',')

plt.show()