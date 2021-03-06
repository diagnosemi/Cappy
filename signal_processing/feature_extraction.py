import numpy as np
import neurokit2 as nk
from math import log10
from scipy import signal
from sklearn.preprocessing import MinMaxScaler


# Use pan tompkins algorithm to separate signal into n beats
def apply_pan_tompkins_old(x, n_beats=110, fs=460, left_data=0.25, right_data=0.5):
    _, rpeaks = nk.ecg_peaks(x, sampling_rate=fs)

    # Select 0.25 seconds left of peak and 0.5 seconds right of beat
    cleaned_signal_dict = {}
    for peak in rpeaks['ECG_R_Peaks']:
        left_index = int(left_data*fs)
        right_index = int(right_data*fs)
        cleaned_signal_dict.update({peak: x[peak - left_index:peak + right_index]})

    # If n_beats is defined, returned those beats
    if n_beats and n_beats <= len(cleaned_signal_dict):
        # Get index of middle beat
        i = int(len(cleaned_signal_dict) / 2)
        half_n_beats = int(n_beats / 2)
        valid_keys = list(cleaned_signal_dict.keys())[i - half_n_beats:i + half_n_beats]
        return {key: val for key, val in cleaned_signal_dict.items() if key in valid_keys}

    # Otherwise return all beats except first and last
    valid_keys = list(cleaned_signal_dict.keys())[1:-1]
    return {key: val for key, val in cleaned_signal_dict.items() if key in valid_keys}


# Use pan tompkins algorithm to separate signal into n beats
def apply_pan_tompkins(x, n_beats=10, beat_length=512, fs=460, standardize=False):
    _, rpeaks = nk.ecg_peaks(x, sampling_rate=fs)
    
    # Standardize if necessary
    if standardize:
        scaler = MinMaxScaler()
        x = np.reshape(x, [-1, 1])
        x = scaler.fit_transform(x)
        x = np.reshape(x, [-1])

    # Create dict of peaks no longer than peak_length
    cleaned_signal_dict = {}
    peaks = rpeaks['ECG_R_Peaks']
    
    # Loop through all the peaks
    for i in range(len(peaks)):
        # Get current peak
        current_peak = rpeaks['ECG_R_Peaks'][i]
        
        # If current peak is the last peak, set the last peak to be last sample of signal
        if i == len(peaks) - 1:
            next_peak = len(x) - 1
        # Otherwise next peak is next peak in the peaks list
        else:
            # Get current and next peak
            next_peak = rpeaks['ECG_R_Peaks'][i + 1]
        
        # Check if distance to next peak is less than the required beat length
        if (next_peak - current_peak) < beat_length:
            # If so, compute additional zeros we need to add to fill the beat
            additional_zeros = beat_length - (next_peak - current_peak)
            additional_zeros_list = np.zeros(additional_zeros)
            
            # Add the signal plus additional zeros to form entire beat
            total_beat = np.concatenate((x[current_peak:next_peak], additional_zeros_list))
            cleaned_signal_dict.update({current_peak: total_beat})
        
        # Otherwise just return the signal within the required beat length
        else:
            total_beat = x[current_peak:current_peak + beat_length]
            cleaned_signal_dict.update({current_peak: total_beat})
            
    # If n_beats is defined, returned those beats
    if n_beats and n_beats <= len(cleaned_signal_dict):
        # Get index of middle beat
        i = int(len(cleaned_signal_dict) / 2)
        half_n_beats = int(n_beats / 2)
        valid_keys = list(cleaned_signal_dict.keys())[i - half_n_beats:i + half_n_beats]
        return {key: val for key, val in cleaned_signal_dict.items() if key in valid_keys}

    # Otherwise return all beats except first and last
    valid_keys = list(cleaned_signal_dict.keys())[1:-1]
    return {key: val for key, val in cleaned_signal_dict.items() if key in valid_keys}


# Compute signal to noise ratio on each beat and return average in mV or dB
def compute_snr(x, fs=460, in_db=True):
    # Get R peaks 
    peaks = apply_pan_tompkins(x, n_beats=None)
    
    # Loop across all R peaks and compute mean Vpp signal and Vpp noise
    vpp_signal_ecg = []
    vpp_noise_ecg = []
    
    for p in list(peaks.keys()):
        # Compute vpp signal
        signal = peaks[p]
        vpp_signal = np.ptp(signal)
        vpp_signal_ecg.append(vpp_signal)
        
        # Compute vpp noise using the last 0.15 seconds of ecg beat
        samples = int(fs*0.15)
        noise_interval = signal[-samples:]
        vpp_noise = np.ptp(noise_interval)
        vpp_noise_ecg.append(vpp_noise)
    
    snr_ecg = np.mean(vpp_signal_ecg) / np.mean(vpp_noise_ecg)

    # Return in dB or mV
    if in_db:
        return 20 * log10(snr_ecg)
    return snr_ecg


# Compute mean peak-to-peak amplitude across entire signal in mV
def compute_mean_ptp(x):
    # Get R peaks 
    peaks = apply_pan_tompkins(x, n_beats=None)
    
    vpp_signal_ecg = []
    for p in list(peaks.keys()):
        # Compute vpp signal
        signal = peaks[p]
        vpp_signal = np.ptp(signal)
        vpp_signal_ecg.append(vpp_signal)
    return np.mean(vpp_signal_ecg)


# Compute mean qrs to signal width ratio
def compute_qrs_ratio(x, fs=460, length_of_beat=0.75):
    # Find Q and S peaks
    _, rpeaks = nk.ecg_peaks(x, sampling_rate=fs)
    _, waves_peak = nk.ecg_delineate(x, rpeaks, sampling_rate=fs, method="peak")
    
    # Compute diff across Q and S peaks
    Q_waves = waves_peak['ECG_Q_Peaks']
    S_waves = waves_peak['ECG_S_Peaks']
    diff = [s - q for s, q in zip(S_waves, Q_waves)]
    
    # Divide the diff by 0.75 seconds (length of 1 beat in samples)
    duration_samples = int(length_of_beat*fs)
    ratio = [i/duration_samples for i in diff if not np.isnan(i)]
    return sum(ratio)/len(ratio)


# Compute power of signal
def compute_power(x):
    return sum(abs(x)**2)/(2*len(x))


# Compute frequency with max power
def compute_max_psd_freq(x, fs=460):
    f, pxx_den = signal.periodogram(x, fs)
    f = f.tolist()
    pxx_den = pxx_den.tolist()
    max_power = max(pxx_den)
    index_max_power = pxx_den.index(max_power)
    freq_max_power = f[index_max_power]
    return max_power, freq_max_power
