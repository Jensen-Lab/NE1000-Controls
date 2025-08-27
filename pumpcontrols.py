import numpy as np
import serial
import time


def unit_convert(units):
	if units=='mlh':
		unit = 'MH'
	elif units=='ulh':
		unit = 'UH'
	elif units=='mlm':
		unit = 'MM'
	elif units=='ulm':
		unit = 'UM'
	else:
		unit = units

	return unit

class pump:
	def __init__(self,port,baud=600,delay=0.1):
		self.ser = serial.Serial(port,baud,parity=serial.PARITY_NONE, bytesize=8,stopbits=1)
		self.sleep = lambda:time.sleep(delay)

	def comms(self,text_com):
		self.ser.write(text_com.encode() + b'\r\n')
		self.sleep()

	def start(self):
		self.comms('RUN')

	def stop(self):
		self.comms('STP')

	def diameter(self,diameter=None):
		self.comms(f'DIA {diameter}')

	def buzzer(self,n_buz=1):
		self.comms(f'BUZ 1 {n_buz}')

	def reset(self):
		self.comms('RESET')

	def rate(self,rate=0,units='mlh'):
		unit = unit_convert(units)
		self.comms(f'RAT {rate} {unit}')

	def direction(self,direction=0):
		if direction==1:
			dircom = 'INF'
		elif direction==-1:
			dircom = 'WDR'
		elif direction==0:
			dircom = 'REV'
		else:
			raise ValueError('Invalid Direction')
		self.comms(f'DIR {dircom}')

	def increment(self,rate_increase=0,units='mlh'):
		unit = unit_convert(units)
		self.comms(f'INC {rate_increase} {unit}')