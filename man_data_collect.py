import serial as srl
import time
import csv
import glob
import os
import threading

# ⚠ Adjust this if your port name is different in WSL (e.g. '/dev/ttyS3' or similar)
ser = srl.Serial('/dev/ttyACM0', 250000, timeout=2)
ser.flushInput()
time.sleep(5)

parent_folder = './Results_static_pressure'
os.makedirs(parent_folder, exist_ok=True)

iterator = len(glob.glob(os.path.join(parent_folder, "measurement_*.csv")))

stop_measurement = False  # flag controlled by input() thread


def printout1():
    os.system('clear')
    ser_bytes = ser.readline()
    decoded_bytes = ser_bytes[0:len(ser_bytes)-2].decode("utf-8", errors="ignore")
    print('Welcome to manual data acquisition')
    print(f'Current readout is: {decoded_bytes}')
    print("Type 's' and press Enter to start measurement, or 'x' + Enter to exit.")
    time.sleep(1)


def printout2():
    for i in range(5):
        os.system('clear')
        ser_bytes = ser.readline()
        decoded_bytes = ser_bytes[0:len(ser_bytes)-2].decode("utf-8", errors="ignore")
        print(f'Waiting 5s to start measurement: {5 - i}')
        print(f'Current readout is: {decoded_bytes}')
        print('Please be patient...')
        time.sleep(1)


def printout3(decoded_bytes):
    os.system('clear')
    print('Data collection is now active!')
    print(f'Current readout is: {decoded_bytes}')
    print("Type 'q' and press Enter in the console to stop measurement.")
    time.sleep(0.5)


def wait_for_stop():
    """
    Runs in a background thread, waits for 'q' + Enter to stop measurement.
    """
    global stop_measurement
    while True:
        cmd = input().strip().lower()
        if cmd == 'q':
            stop_measurement = True
            break


while True:
    # Wait for experiment to commence
    printout1()
    cmd = input("> ").strip().lower()

    if cmd == 'x':
        print("Exiting.")
        break
    if cmd != 's':
        continue  # anything else: re-show screen

    iterator += 1
    printout2()

    # Start background thread that waits for 'q'
    stop_measurement = False
    stopper_thread = threading.Thread(target=wait_for_stop, daemon=True)
    stopper_thread.start()

    # Measurement loop
    measurement_filename = os.path.join(parent_folder, f'measurement_{int(iterator)}.csv')

    print(f"Writing data to: {measurement_filename}")
    print("Type 'q' + Enter at any time to stop.\n")

    with open(measurement_filename, "a", newline="") as f:
        writer = csv.writer(f, delimiter=",")

        while not stop_measurement:
            ser_bytes = ser.readline()
            decoded_bytes = ser_bytes[0:len(ser_bytes)-2].decode("utf-8", errors="ignore")
            printout3(decoded_bytes)
            writer.writerow([decoded_bytes])

    print("Measurement stopped. Returning to main menu...")
    time.sleep(1)

ser.close()
