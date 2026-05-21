import numpy as np
import pandas as pd
import scipy as sp
import matplotlib.pyplot as plt
import os
import io
import glob
import json

ignore_type = str(input('Channel index: '))
output_type = str(input('Output type: '))

# Selecetion correct data files
try:
    ignore_type = list(map(lambda x:int(x),list(ignore_type.split(' '))))
except:
    ignore_type = [None]

# Loading values for calibration
min_length = 0
line = lambda x,m,b:m*x+b
with open('./.sensor_calibration.json') as jf:
    cal_vals = json.load(jf)
    flow_cal = lambda Q:line(Q[min_length:],cal_vals['FlowrateSensor']['SensorCalibrationValue1'],cal_vals['FlowrateSensor']['SensorCalibrationValue2'])
    pres_cal = lambda P:line(P[min_length:],cal_vals['PressureSensor']['SensorCalibrationValue1'],cal_vals['PressureSensor']['SensorCalibrationValue2'])


# Saving relevant values
pressure = []
flowrate = []
flow_err = []
p_app__ = []
raw_pres = []
raw_flow = []

data_directory = './Results_static_pressure'
files = glob.glob(f'{data_directory}/*')


for i,file in enumerate(files):
    full_path = data_directory+file
    with open('./.exp_metadata.json') as jf:
        metadata = json.load(jf)
        measurement_file_data = file.split('/')[-1].split('.')[0]
        channel = metadata[measurement_file_data]["channel_index"]
        p_app = metadata[measurement_file_data]["applied_pressure"]
        if channel not in ignore_type:
            continue

    # Reading the data files
    try:
        with open(file,'rt') as text:
            data = text.read().replace('"','')
        data = pd.read_csv(io.StringIO(data),names=['flow','p1'],usecols=[0,1],header=None)
    except:
        continue

    calibrated_pressure = pres_cal(data['p1'])
    calibrated_flowrate = flow_cal(data['flow'])

    pressure.append(np.mean(calibrated_pressure))
    flowrate.append(np.mean(calibrated_flowrate))

    par,_ = sp.optimize.curve_fit(lambda x,m,b:m*x+b,calibrated_pressure,calibrated_flowrate)
    error = np.sqrt(np.var(calibrated_flowrate)+np.var(calibrated_pressure)*par[0]**2)
    flow_err.append(error)
    p_app__.append(p_app)
    
    # Time series of data
    if output_type=='tf':
        plt.plot(flow_cal(data['flow'].to_numpy()),'.')
        plt.xlabel('Time [s]')
        plt.ylabel('Flowrate [mlh]')

    if 'tp' in output_type:
        plt.plot(pres_cal(data['p1'].to_numpy(),p_app),'.')
        if 'tpp'==output_type:
            plt.plot(calibrated_pressure,'.')
        plt.xlabel('Time [s]')
        plt.ylabel('Pressure [kPa]')

    # Full scatter of data
    if output_type=='s':
        plot_p = calibrated_pressure
        plot_q = flow_cal(data['flow'].to_numpy())
        plt.scatter(plot_p,plot_q,c=np.linspace(0,1,len(plot_p)),cmap='rainbow')
        plt.ylabel('Flowrate [mlh]')
        plt.xlabel('Pressure [kPa]')

    # Scatter of mean values
    if output_type=='sm':
        plt.plot(np.mean(calibrated_pressure),np.mean(flow_cal(data['flow'].to_numpy())),'o',c='crimson' if channel==ignore_type[0] else 'seagreen')
        plt.xlabel('Pressure [kPa]')
        plt.ylabel('Flowrate [mlh]')

    # Calibration plots
    if output_type=='cp':
        sensor_val = np.mean(data['p1'].to_numpy())
        plt.plot(p_app,sensor_val,'.',c='seagreen')
        plt.xlabel('Applied Pressure [Pa]')
        plt.ylabel('Sensor Readout [a.u.]')
        raw_pres.append(sensor_val)

    if output_type=='cf':
        sensor_val = np.mean(data['flow'].to_numpy())
        plt.plot(p_app,sensor_val,'.',c='seagreen')
        plt.xlabel('Applied Flowrate [mlh]')
        plt.ylabel('Sensor Readout [a.u.]')
        raw_flow.append(sensor_val)

#################################################################      
        
# Calibration plots
if output_type=='cp':
    par,_ = sp.optimize.curve_fit(line,raw_pres,p_app__)
    print(f'SensorCalibrationValue1: {par[0]} \nSensorCalibrationValue2: {par[1]}')
    par,_ = sp.optimize.curve_fit(line,p_app__,raw_pres)
    plt.plot(p_app__,line(np.array(p_app__),*par),'--',c='goldenrod')

if output_type=='cf':
    flow__ = 10*np.array(p_app__)
    par,_ = sp.optimize.curve_fit(line,raw_flow,flow__)
    print(f'SensorCalibrationValue1: {par[0]} \nSensorCalibrationValue2: {par[1]}')
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

plt.show()
