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

# flow_cal = lambda Q:Q[300:]*0.89456928+2.1059525 old cal for previous flow sensor
flow_cal = lambda Q:Q[min_length:]*0.48877946-0.09915247
pres_cal = lambda P:(P[min_length:]-48585.84344079)/-246.26589948
no_cal = lambda A:A

pressure = []
flowrate = []
pressure_0 = []
flowrate_0 = []
flow_err = []
height__ = []

data_directory = './Results_static_pressure/Results_static_pressure'

files = glob.glob('./Results_static_pressure/Results_static_pressure/*')

def time_dep_pres_effect(pressure,H,a):
    pressure = sp.ndimage.gaussian_filter(pressure,30)
    R = H+a*np.gradient(pressure,1)
    return R*pressure

line = lambda x,m,b:m*x+b

run_only_once = 1

for i,file in enumerate(files):#[-14:-8]:
    full_path = data_directory+file
    with open('./.exp_metadata.json') as jf:
        metadata = json.load(jf)
        nozzle = metadata[file[50:65]]["nozzle"]
        height = metadata[file[50:65]]["height"]
        if nozzle not in ignore_type:
            continue

    # Reading the data files
    try:
        with open(file,'rt') as text:
            data = text.read().replace('"','')
        data = pd.read_csv(io.StringIO(data),names=['flow','p1','p0'],header=None)
    except:
        continue

    # Addimg mean values to array
    # pressure.append(np.mean(pres_cal(data['p1']))-11e3 if nozzle==31 else np.mean(pres_cal(data['p1']))+11e3)
    # pressure.append(np.mean(pres_cal(data['p1'])))
    # if nozzle==31:
    #     pressure.append(np.mean(pres_cal(data['p1'])*1.05266531e-03-1.13215117e+01))
    # elif nozzle==32:
    #     pressure.append(np.mean(pres_cal(data['p1'])*1.16430115e-03+1.26498804e+01))
    # else:
    pressure.append(np.mean(pres_cal(data['p1'])))
    flowrate.append(np.mean(flow_cal(data['flow'])))

    par,_ = sp.optimize.curve_fit(lambda x,m,b:m*x+b,pres_cal(data['p1']),flow_cal(data['flow']))
    error = np.sqrt(np.var(flow_cal(data['flow']))+np.var(pres_cal(data['p1']))*par[0]**2)
    flow_err.append(error)
    height__.append(height/10)

    # Time series of data
    if output_type=='tf':
        plt.plot(flow_cal(data['flow'].to_numpy()),'.')
        plt.xlabel('Time [s]')
        plt.ylabel('Flowrate [mlh]')

    if 'tp' in output_type:
        plt.plot(pres_cal(data['p1'].to_numpy())/1e3,'.')
        if 'tpp'==output_type:
            plt.plot(sp.ndimage.gaussian_filter(pres_cal(data['p1'].to_numpy())/1e3,20),'.')
        plt.xlabel('Time [s]')
        plt.ylabel('Pressure [kPa]')

    # Full scatter of data
    if output_type=='s':
        plot_p = pres_cal(data['p1'].to_numpy())/1e3
        plot_q = flow_cal(data['flow'].to_numpy())
        plot_h = np.array([height for _,_ in enumerate(plot_p)])/10
        # plt.plot(flow_cal(data['flow'].to_numpy()),pres_cal(data['p1'].to_numpy())/1e3,'.',c='goldenrod')
        # plt.plot(pres_cal(data['p1'].to_numpy())/1e3,flow_cal(data['flow'].to_numpy()),'.',c='goldenrod')
        # plt.plot(np.mean(plot_p),np.mean(plot_q),'o',c='crimson')
        plt.scatter(plot_p,plot_q,c=np.linspace(0,1,len(plot_p)),cmap='rainbow')
        if i==0:
            plt.colorbar()

        x = np.linspace(0,8,1000)
        y = 279.9130506*((x*1000)/(x*1000 + 11886.85768471))
        y2 = 270.05940778*((x*1000)/(x*1000 + 9424.09518119))
        # plt.plot(x,y,'.')
        # plt.plot(x,y2,'.')

        plt.ylabel('Flowrate [mlh]')
        plt.xlabel('Pressure [kPa]')

    if output_type=='sm':
        plt.plot(np.mean(pres_cal(data['p1'].to_numpy())/1e3),np.mean(flow_cal(data['flow'].to_numpy())),'o',c='crimson' if nozzle==ignore_type[0] else 'seagreen')
        plt.xlabel('Pressure (scaled, non-centered values)')
        plt.ylabel('Flowrate [mlh]')
        # plt.plot(np.abs(np.mean(pres_cal(data['p1'].to_numpy())/1e3)),np.abs(np.mean(flow_cal(data['flow'].to_numpy()))),'o',c='crimson' if nozzle==ignore_type[0] else 'seagreen')


    if 'fit' in output_type:
        flow_data = flow_cal(data['flow'].to_numpy())
        pres_data = pres_cal(data['p1'].to_numpy())/1000#/height
        # par,_ = sp.optimize.curve_fit(time_dep_pres_effect,pres_data,flow_data)
        par,_ = sp.optimize.curve_fit(line,pres_data[900:],flow_data[900:])
        # par,_ = sp.optimize.curve_fit(line,pres_data,flow_data)
        print(par)
        plt.plot(pres_data,flow_data,'.')
        # plt.plot(pres_data,time_dep_pres_effect(pres_data,*par),'.')
        plt.plot(pres_data,line(pres_data,*par),'.')
        plt.xlabel('Pressuse [Pa]')
        plt.ylabel('Flowrate [mlh]')
        if output_type=='ffit' and run_only_once==0:
            full_range_flow = np.load('./full_range_flow_9.npy')
            full_range_pres = np.load('./full_range_pres_9.npy')
            par,_ = sp.optimize.curve_fit(line,full_range_pres,full_range_flow)
            print(full_range_pres)
            plt.plot(full_range_pres,full_range_flow,'.',c='cornflowerblue')
            plt.plot(full_range_pres,line(full_range_pres,*par),'--',c='crimson')
            run_only_once=1

    if output_type=='c':
        corr = np.corrcoef(data['flow'],data['p1'])
        print(corr)

pressure = np.array(pressure)
plt.show()
plt.plot(height__,pressure,'.')

par,cov = sp.optimize.curve_fit(lambda x,m,b,a:a*x**2+m*x+b,height__,pressure*9.96444152e-04+9)

print(par)

# np.savetxt(f'height_pres_{ignore_type[0]}.csv',np.asarray([height__,pressure]).T,delimiter=',')

# np.savetxt(f'presflow_{ignore_type[0]}.csv',np.asarray([flowrate,pressure,flow_err]).T,delimiter=',')

# plt.legend()
plt.show()