import tensorflow as tf
from .utils import downsample_signal, process_hardware_ecg, \
    apply_wavelet_reconstruction_denoising, apply_butter_low_pass, remove_baseline_wander


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


def classify_ecg(x):
    model = tf.keras.models.load_model('../ml_model')
    result = model.predict(x)
    return result
