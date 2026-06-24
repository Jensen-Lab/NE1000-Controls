import numpy as np
import pandas as pd
import scipy as sp
import matplotlib.pyplot as plt
import os
import io
import glob
import json

channels = str(input('Channel index: '))
output_type = str(input('Output type: '))

# Channels to include in the analysis (space separated for several)
try:
    channels = list(map(lambda x: int(x), list(channels.split(' '))))
except:
    channels = [None]

# Loading values for calibration
min_length = 0
line = lambda x, m, b: m*x + b
with open('./.sensor_calibration.json') as jf:
    cal_vals = json.load(jf)
    pres_cal = lambda P: line(P[min_length:],
                              cal_vals['PressureSensor']['SensorCalibrationValue1'],
                              cal_vals['PressureSensor']['SensorCalibrationValue2'])

# Saving relevant values
pressure = []        # mean calibrated pressure per measurement
pres_err = []        # spread (std) of pressure per measurement
applied_flow = []    # applied flowrate (from syringe pump, metadata)
applied_pres = []    # applied pressure (known reference, only used for calibration)
raw_pres = []        # raw sensor readout (only used for calibration)

# Calibration ('cp') and experiment data live in separate folders, each with
# their own metadata file, so the two never get mixed up.
if output_type == 'cp':
    data_directory = './Results_calibration'
    metadata_file = './.cal_metadata.json'
else:
    data_directory = './Results_static_pressure'
    metadata_file = './.exp_metadata.json'

files = glob.glob(f'{data_directory}/*')


for file in files:
    with open(metadata_file) as jf:
        metadata = json.load(jf)
        measurement_file_data = os.path.splitext(os.path.basename(file))[0]
        if measurement_file_data not in metadata:
            continue
        channel = metadata[measurement_file_data].get("channel_index")
        q_app = metadata[measurement_file_data].get("applied_flowrate")
        p_app = metadata[measurement_file_data].get("applied_pressure")
        # Calibration is a sensor-level operation, so the channel is irrelevant
        # there; every other mode filters on the requested channel(s).
        if output_type != 'cp' and channel not in channels:
            continue

    # Reading the data files. The Arduino sends "flow,pressure" but only the
    # pressure column is used here; the flowrate is the known applied value.
    try:
        with open(file, 'rt') as text:
            data = text.read().replace('"', '')
        data = pd.read_csv(io.StringIO(data), names=['flow', 'p1'], usecols=[0, 1], header=None)
    except:
        continue

    calibrated_pressure = pres_cal(data['p1'])

    pressure.append(np.mean(calibrated_pressure))
    pres_err.append(np.std(calibrated_pressure))
    applied_flow.append(q_app)
    applied_pres.append(p_app)

    # Time series of pressure
    if 'tp' in output_type:
        plt.plot(calibrated_pressure, '.')
        plt.xlabel('Time [s]')
        plt.ylabel('Pressure [kPa]')

    # Full scatter: every pressure sample against the applied flowrate
    if output_type == 's':
        plt.scatter([q_app]*len(calibrated_pressure), calibrated_pressure,
                    c=np.linspace(0, 1, len(calibrated_pressure)), cmap='rainbow')
        plt.xlabel('Applied flowrate [mlh]')
        plt.ylabel('Pressure [kPa]')

    # Scatter of mean pressure against the applied flowrate
    if output_type == 'sm':
        plt.plot(q_app, np.mean(calibrated_pressure), 'o', c='seagreen')
        plt.xlabel('Applied flowrate [mlh]')
        plt.ylabel('Pressure [kPa]')

    # Calibration plot: known applied pressure vs raw sensor readout
    if output_type == 'cp':
        sensor_val = np.mean(data['p1'].to_numpy())
        plt.plot(p_app, sensor_val, '.', c='seagreen')
        plt.xlabel('Applied Pressure [Pa]')
        plt.ylabel('Sensor Readout [a.u.]')
        raw_pres.append(sensor_val)

#################################################################

# Calibration fit
if output_type == 'cp':
    par, _ = sp.optimize.curve_fit(line, raw_pres, applied_pres)
    print(f'SensorCalibrationValue1: {par[0]} \nSensorCalibrationValue2: {par[1]}')
    par, _ = sp.optimize.curve_fit(line, applied_pres, raw_pres)
    plt.plot(applied_pres, line(np.array(applied_pres), *par), '--', c='goldenrod')

# Estimate linear resistance: pressure vs applied flowrate
if output_type == 'r':
    par, cov = sp.optimize.curve_fit(line, applied_flow, pressure)
    print(par[0], ' + ', np.sqrt(cov[0, 0]))

# Write data to file
if len(channels) == 1 and output_type == 'w':
    print('Saving file')
    np.savetxt(f'presflow_{channels[0]}.csv',
               np.asarray([applied_flow, pressure, pres_err]).T, delimiter=',')

plt.show()
