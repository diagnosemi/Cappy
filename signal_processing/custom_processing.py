import pywt
import numpy as np
import matplotlib.pyplot as plt
from scipy import signal, fftpack


# Download signal to from old to new sampling rate
def downsample_signal(x, old_fs=20500, new_fs=460):
    secs = round(len(x)/old_fs)
    samps = secs * new_fs
    return signal.resample(x, samps)


# Process raw ecg signal acquired by our hardware
def process_hardware_ecg(x):
    # Convert from string to float
    x = x[x['raw_ecg'] != "b''"]
    x['raw_ecg'] = x['raw_ecg'].apply(lambda x: float(x[:-1][2:]))

    # Convert to mv
    x = (x['raw_ecg'] / 1024. / 1.1 * 3.3 - 1.5).tolist()

    # Downsample
    x = downsample_signal(x)
    return x


# Uses a notch filter to remove baseline wander
def remove_baseline_wander(x, Q=0.005, fs=20500, cutoff=0.5):
    b, a = signal.iirnotch(cutoff, Q=Q, fs=fs)
    filtered_data = signal.filtfilt(b, a, x)
    return filtered_data


# Get mean absolute deviation of signal
def madev(d, axis=None):
    return np.mean(np.absolute(d - np.mean(d, axis)), axis)


def apply_wavelet_reconstruction_denoising(x):
    wavelet = 'sym4'
    w = pywt.Wavelet(wavelet)

    # Get max reconstruction level possible
    maxlev = pywt.dwt_max_level(len(x), w.dec_len)

    # Calculate coefficients at all levels
    coeffs = pywt.wavedec(x, wavelet, level=maxlev)

    # Calculate threshold using universal formula
    sigma = (1/0.6745) * madev(coeffs[-1])
    threshold = sigma * np.sqrt(2 * np.log(len(x)))
    threshold = 0.04

    for i in range(1, len(coeffs)):
        coeffs[i] = pywt.threshold(coeffs[i], threshold * max(coeffs[i]))
    return pywt.waverec(coeffs, wavelet)


def apply_butter_low_pass(x, fs=460, cutoff=50, order=2):
    nyq = 0.5 * fs
    normal_cutoff = cutoff / nyq
    b, a = signal.butter(order, normal_cutoff, btype='low', analog=False)
    filtered_data = signal.filtfilt(b, a, x)
    return filtered_data


def remove_mean(x):
    return x - x.mean()


# Plot signal frequency spectrum
def plot_freq_spectrum(x, fs=460):
    plt.figure(figsize=(20, 12))
    yf = fftpack.fft(x)
    xf = fftpack.fftfreq(len(x)) * fs
    plt.plot(xf, np.abs(yf))
    plt.xlabel('Hz')
    plt.show()


# Get a matplotlib object of an ECG plot
def plot_ecg(signal, label, fs=460, colour='b-', cutoff=None):
    # Convert x axis from # samples to time
    x_axis_samples = np.arange(start=0, stop=len(signal), step=1)
    x_axis_time = x_axis_samples / fs

    plt.figure(figsize=(20, 12))

    if cutoff:
        x_axis_time = x_axis_time[:cutoff]
        signal = signal[:cutoff]

    plt.plot(x_axis_time, signal, colour, label=label)
    plt.ylabel('mV')
    plt.xlabel('Time (s)')
    plt.legend(loc="upper left")
    plt.show()
