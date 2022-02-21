import pywt
import numpy as np
import pandas as pd
from scipy import signal


# Fill null values in a list using linear interpolation
def fill_nan(x):
    x_series = pd.Series(x)
    x_series = x_series.astype(float).interpolate()
    return x_series.tolist()


# Downsample signal from old to new sampling rate
def downsample_signal(x, old_fs=20500, new_fs=460):
    secs = round(len(x)/old_fs)
    samps = secs * new_fs
    return signal.resample(x, samps)


# Process raw ecg signal acquired by our hardware
def process_hardware_ecg(x, old_fs=20500):
    # Convert from string to float
    x = x[x['raw_ecg'] != "b''"]
    x['raw_ecg'] = x['raw_ecg'].apply(lambda x: float(x[:-1][2:]))

    # Convert to mv
    x = (x['raw_ecg'] / 1024. / 1.1 * 3.3 - 1.5).tolist()

    # Downsample
    x = downsample_signal(x, old_fs=old_fs)
    return x


# Apply DWT with sym4 wavelets
def apply_wavelet_reconstruction_denoising(x):
    wavelet = 'sym4'
    w = pywt.Wavelet(wavelet)

    # Get max reconstruction level possible
    maxlev = pywt.dwt_max_level(len(x), w.dec_len)

    # Calculate coefficients at all levels
    coeffs = pywt.wavedec(x, wavelet, level=maxlev)

    # Calculate threshold using universal formula
    madev = np.mean(np.absolute(coeffs[-1] - np.mean(coeffs[-1], None)), None)
    sigma = (1/0.6745) * madev
    threshold = sigma * np.sqrt(2 * np.log(len(x)))
    # threshold = 0.04

    for i in range(1, len(coeffs)):
        coeffs[i] = pywt.threshold(coeffs[i], threshold * max(coeffs[i]))
    return pywt.waverec(coeffs, wavelet)


# Apply butterworth LPF with cutoff 50Hz
def apply_butter_low_pass(x, fs=460, cutoff=50, order=2):
    nyq = 0.5 * fs
    normal_cutoff = cutoff / nyq
    b, a = signal.butter(order, normal_cutoff, btype='low', analog=False)
    filtered_data = signal.filtfilt(b, a, x)
    return filtered_data


# Uses a notch filter to remove baseline wander
def remove_baseline_wander(x, Q=0.005, fs=20500, cutoff=0.5):
    b, a = signal.iirnotch(cutoff, Q=Q, fs=fs)
    filtered_data = signal.filtfilt(b, a, x)
    return filtered_data
