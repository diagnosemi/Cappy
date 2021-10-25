import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

# Read raw signal and convert to float
raw_signal = pd.read_csv('raw_ecg.csv')
raw_signal['raw_ecg'] = raw_signal['raw_ecg'].apply(lambda x: float(x[:-1][2:]))
raw_signal['ecg_mv'] = raw_signal['raw_ecg']/1024./1.1*3.3-1.5
#raw_signal['mean_ecg'] = raw_signal['ecg_mv'] - raw_signal['ecg_mv'].mean()

# Using a sampling rate of 20.5kHz
x_axis_samples = np.arange(start=0, stop=raw_signal.shape[0], step=1)
sampling_freq = 20500
x_axis_time = x_axis_samples/20500

# Plot x and y
cutoff = 20500*15
col = 'ecg_mv'
y = raw_signal[col][:cutoff]
x = x_axis_time[:cutoff]

plt.plot(x, y)
plt.show()



