import serial as srl
import time
import csv
from pumpcontrols import pump
import numpy as np
import pm_client
# import matplotlib.pyplot as plt
# import matplotlib.animation as animation

ser = srl.Serial('/dev/ttyACM0',250000,timeout=2)
ser.flushInput()
time.sleep(5)


p = pump('/dev/ttyUSB0',2400,delay=0.1)
time.sleep(2)
p.buzzer(2)

ipadress = '***'
username = '***'
password = '***'

camera = pm_client.ssh(ipadress,username,password)
camera.open_shell()

rates = np.linspace(5,50,10)

for rate in rates:

	p.direction(1)
	p.rate(rate)
	p.start()


	for  _ in range(20):
		t0 = time.time()
		ser_bytes = ser.readline()
		decoded_bytes = (ser_bytes[0:len(ser_bytes)-2].decode("utf-8"))
		print(decoded_bytes)
		t1 = time.time()
		try:
			time.sleep(1-(t1-t0))
		except:
			time.sleep(0.1)

	fname = f'Cal_Results/{int(rate)}mlh_dir1.csv'
	for _ in range(100):
		t0 = time.time()
		ser_bytes = ser.readline()
		decoded_bytes = (ser_bytes[0:len(ser_bytes)-2].decode("utf-8"))
		print(decoded_bytes)
		with open(fname,"a") as f:
			writer = csv.writer(f,delimiter=",")
			writer.writerow([decoded_bytes])
		t1 = time.time()
		print(t1-t0)
		try:
			time.sleep(2-(t1-t0))
		except:
			time.sleep(0.1)
		
	print('Measurement finished')
	
	p.stop()
	p.buzzer()
	time.sleep(10)
	camera.send_shell('~/CSI_Camera/take_image.py')
	time.sleep(10)
	
	p.direction(-1)
	p.rate(rate)
	p.start()


	for  _ in range(20):
		t0 = time.time()
		ser_bytes = ser.readline()
		decoded_bytes = (ser_bytes[0:len(ser_bytes)-2].decode("utf-8"))
		print(decoded_bytes)
		t1 = time.time()
		try:
			time.sleep(1.5-(t1-t0))
		except:
			time.sleep(0.1)

	fname = f'Cal_Results/{int(rate)}mlh_dir2.csv'
	for _ in range(100):
		t0 = time.time()
		ser_bytes = ser.readline()
		decoded_bytes = (ser_bytes[0:len(ser_bytes)-2].decode("utf-8"))
		print(decoded_bytes)
		with open(fname,"a") as f:
			writer = csv.writer(f,delimiter=",")
			writer.writerow([decoded_bytes])
		t1 = time.time()
		try:
			time.sleep(1.6-(t1-t0))
		except:
			time.sleep(0.1)
		
	print('Measurement finished')
	
	p.stop()
	p.buzzer()
	time.sleep(10)
	camera.send_shell('~/CSI_Camera/take_image.py')
	
	
