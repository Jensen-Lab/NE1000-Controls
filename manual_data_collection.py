import keyboard
import serial as srl
import time
import csv
import numpy as np
import glob
import os

ser = srl.Serial('/dev/ttyACM0',250000,timeout=2)
ser.flushInput()
time.sleep(5)

parent_folder = './Results_static_pressure'

os.makedirs(parent_folder,exist_ok=True)

iterator = len(glob.glob(os.path.join(parent_folder,"measurement_*.csv")))

def printout1():
    os.system('clear')
    ser_bytes = ser.readline()
    decoded_bytes = (ser_bytes[0:len(ser_bytes)-2].decode("utf-8"))
    print('Welcome to data manual data acquisition')
    print(f'Current readout is: {decoded_bytes}')
    print('Hold (s) to start measurement')
    time.sleep(1)

def printout2():
    for i in range(5):
        os.system('clear')
        ser_bytes = ser.readline()
        decoded_bytes = (ser_bytes[0:len(ser_bytes)-2].decode("utf-8"))
        print(f'Waiting 5s to start measurement: {5-i}')
        print(f'Current readout is: {decoded_bytes}')
        print('Please be patient...')
        time.sleep(1)

def printout3(decoded_bytes):
    os.system('clear')
    print('Data collection is now active!')
    print(f'Current readout is: {decoded_bytes}')
    print('Hold (q) to quit measurement')
    time.sleep(1)
    

while True:
    # Wait for experiment to commence
    while not keyboard.is_pressed('s'):
        printout1()

    iterator+=1
    printout2()
        
    while not keyboard.is_pressed('q'):
        ser_bytes = ser.readline()
        decoded_bytes = (ser_bytes[0:len(ser_bytes)-2].decode("utf-8"))
        printout3(decoded_bytes)
        with open(os.path.join(parent_folder,f'measurement_{int(iterator)}.csv'),"a") as f:
            writer = csv.writer(f,delimiter=",")
            writer.writerow([decoded_bytes])

        
        
