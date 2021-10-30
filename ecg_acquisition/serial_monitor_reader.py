import serial
import csv
import time

ecg = []
ser = serial.Serial("/dev/cu.usbmodem1201", 9600)
ser.reset_input_buffer()
t_end_60 = time.time() + 240
samples_per_sec = []
while time.time() < t_end_60:
    t_end_1 = time.time() + 1
    data_in_sec = []
    while time.time() < t_end_1:
        data = str(ser.readline().strip())
        data_in_sec.append(data)
    samples_per_sec.append(len(data_in_sec))
    ecg += data_in_sec

file_name = "raw_ecgs/simona_laying.csv"
with open(file_name, "w") as csvfile:
    filewriter = csv.writer(csvfile)
    values = zip(ecg)
    filewriter.writerow(["raw_ecg"])
    filewriter.writerows(values)
csvfile.close()
