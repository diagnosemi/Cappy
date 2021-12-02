import pandas as pd

from signal_processing import downsample_signal, \
    remove_baseline_wander, plot_ecg, plot_freq_spectrum, apply_butter_low_pass

# Read raw signal and convert to float and mv
raw_signal = pd.read_csv('raw_ecgs/cesar_sitting.csv')

raw_signal = raw_signal[raw_signal['raw_ecg'] != "b''"]
raw_signal['raw_ecg'] = raw_signal['raw_ecg'].apply(lambda x: float(x[:-1][2:]))
raw_ecg_signal = (raw_signal['raw_ecg']/1024./1.1*3.3-1.5).tolist()

# Downsample raw ecg signal
raw_ecg_signal = downsample_signal(raw_ecg_signal)

# Apply low pass filter on signal
raw_ecg_signal = denoise_signal(raw_ecg_signal)
raw_ecg_signal = apply_butter_low_pass(raw_ecg_signal, cutoff=100)

# Remove baseline wander with a notch filter
raw_ecg_signal = remove_baseline_wander(raw_ecg_signal)


# Remove the mean
raw_ecg_signal = raw_ecg_signal - raw_ecg_signal.mean()
plot_ecg(raw_ecg_signal, cutoff=20000, label='db6 wavelet reconstruction')
