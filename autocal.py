from pumpcontrols import pump
import serial as srl
import time
import csv
import numpy as np
import scipy as sp

sensor_cal = lambda Q:(Q-1.67861472)/1.78242045 # calibrate output values from sensor

def autocalibrate(pci,sensor,d0=[10,30],threshold=1):
    pci.buzzer(3)

    d = (d0[1]-d0[0])/2 # initial guess

    while dia_quality>threshold:
        pci.diameter(d)

        pci.direction(1)
        pci.rate(50)
        pci.start()
        time.sleep(30)

        t_end = time.time() + 60
        measurements = []
        while time.time() <= t_end
            try:
                ser_bytes = sensor.readline()
                decoded_bytes = (ser_bytes[0:len(ser_bytes)-2].decode("utf-8"))
                flow_rate = decoded_bytes.split(',')[0]
                measurements.append(sensor_cal(flow_rate))
            finally:
                time.sleep(1)

        pci.stop()

        measurements = np.array(measurements)
        dia_quality = np.sum(((50-np.mean(measurements))**2)/np.var(measurements))

        if dia_quality>threshold:
            d = sp.stats.truncnorm.rvs(d0[0],d0[1],loc=d,scale=dia_quality)