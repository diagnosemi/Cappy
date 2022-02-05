import tensorflow as tf
import numpy as np
import pandas as pd
from .utils import downsample_signal, process_hardware_ecg, \
    apply_wavelet_reconstruction_denoising, apply_butter_low_pass,\
    remove_baseline_wander, apply_pan_tompkins


# Clean one ECG signal: downsample, remove noise and baseline wander
def apply_preprocessing(x, old_fs, new_fs=460, lpf_cutoff=50, is_ptb_data=True):
    # If it is a PTB signal, downsample immediately
    if is_ptb_data:
        # Downsample signal
        x = downsample_signal(x, old_fs=old_fs, new_fs=new_fs)

    # If it is our raw ECG data, convert to mV then downsample
    else:
        x = process_hardware_ecg(x, old_fs=old_fs)

    # Apply DWT
    x = apply_wavelet_reconstruction_denoising(x)

    # Apply LPF
    x = apply_butter_low_pass(x, fs=new_fs, cutoff=lpf_cutoff)

    # Remove baseline wander
    x = remove_baseline_wander(x)

    # Remove mean
    x -= x.mean()
    return x


def prep_model_input(ecg):
    # Select 8 beats from the signal
    ecg_peaks = apply_pan_tompkins(ecg, n_beats=8, standardize=True)

    # Append all beats to a np array
    ecg_beats = np.array([p for p in ecg_peaks.values()])

    # Shuffle the sequence of beats
    df = pd.DataFrame(np.reshape(ecg_beats, [8, 512]))
    df = df.sample(frac=1).reset_index(drop=True)
    ecg_beats = df.to_numpy()
    ecg_beats = np.reshape(ecg_beats, [1, 8, 512, 1])
    return ecg_beats


def classify_ecg_cnn_lstm(ecg):
    # Select only 8 beats from signal
    model_data = prep_model_input(ecg)

    # Load model and run prediction algo on ecg
    model = tf.keras.models.load_model('app/ml_model')
    result = model.predict(model_data)

    # Format the result
    mi_risk = result[0][0]
    other_cvd_risk = result[0][1]
    healthy_risk = result[0][2]
    print("RESULT")
    print(result, type(result))
    print(mi_risk, type(mi_risk))
    print(other_cvd_risk, type(other_cvd_risk))
    print(healthy_risk, type(healthy_risk))
    response = {'mi_risk': mi_risk,
                'other_cvd_risk': other_cvd_risk,
                'healthy_risk': healthy_risk}
    print(response)
    print(type(response))
    return response
