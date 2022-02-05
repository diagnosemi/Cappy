import numpy as np
import neurokit2 as nk
from sklearn.preprocessing import MinMaxScaler


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
