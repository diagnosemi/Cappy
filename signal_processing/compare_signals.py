import pickle
import pandas as pd
from custom_processing import process_hardware_ecg, apply_wavelet_reconstruction_denoising, apply_butter_low_pass,\
    remove_baseline_wander, remove_mean, downsample_signal
from feature_extraction import compute_snr, compute_mean_ptp, compute_qrs_ratio, compute_power, compute_max_psd_freq

# Load PTB data
with open('raw_ptb_data', 'rb') as f:
    raw_ptb_data = pickle.load(f)
    f.close()

# Create df to store analyzed signals
healthy_controls = ['patient155', 'patient263', 'patient264', 'patient170', 'patient182']
our_data = ['simona', 'cesar']
df = pd.DataFrame(columns=healthy_controls+our_data)

# Extract data for 5 healthy controls: patient155, patient263, patient264, patient170, patient182 and save to df
# For each patient just take 115 seconds (that is max amount of time common for all signals)
for hc in healthy_controls:
    patient = raw_ptb_data[hc]
    recording = list(patient.keys())[0]
    signal = patient[recording]['i']
    # Downsample to 460Hz from 1kHz
    signal = downsample_signal(signal, old_fs=1000)
    # Only preserve 115 seconds ~= 52900
    df[hc] = signal[:52900]

# Add our own raw data to df: downsample and take middle 115 secs to match length of PTB data
lower_bound = 60 * 460
upper_bound = int((60+115) * 460)
simona_sitting =\
    process_hardware_ecg(pd.read_csv('../ecg_acquisition/raw_ecgs/simona_sitting.csv'))[lower_bound:upper_bound]
df['simona'] = simona_sitting
cesar_sitting =\
    process_hardware_ecg(pd.read_csv('../ecg_acquisition/raw_ecgs/cesar_sitting.csv'))[lower_bound:upper_bound]
df['cesar'] = cesar_sitting

# Perform signal processing on all signals in df
# Apply denoising filters on signal: use lower cutoff freq for our raw data because it's noisier
df = df.apply(lambda x: apply_wavelet_reconstruction_denoising(x), axis=0)
df[healthy_controls] = df[healthy_controls].apply(lambda x: apply_butter_low_pass(x, cutoff=75), axis=0)
df[our_data] = df[our_data].apply(lambda x: apply_butter_low_pass(x), axis=0)

# Remove baseline wander
df = df.apply(lambda x: remove_baseline_wander(x), axis=0)

# Remove mean
df = df.apply(lambda x: remove_mean(x), axis=0)

# Create df to store summary statistics (dB)
summary_df_cols = ['Signal to Noise Ratio (dB)', 'Mean Peak-to-Peak Amplitude (mV)',
                   'Mean QRS to Signal Ratio', 'Total Power (mV)', 'Max PSD (mV^2/Hz)', 'Frequency of Max PSD (Hz)']
summary_df = pd.DataFrame(columns=summary_df_cols, index=healthy_controls + our_data)

# Extract features for all signals and replace in df
for p in df.columns:
    patient_signal = df[p]
    signal_to_noise_ratio = compute_snr(patient_signal)
    mean_peak_to_peak_amplitude = compute_mean_ptp(patient_signal)
    mean_qrs_to_signal_ratio = compute_qrs_ratio(patient_signal)
    total_power = compute_power(patient_signal)
    max_psd, freq_of_max_psd = compute_max_psd_freq(patient_signal)

    summary_df.loc[p, 'Signal to Noise Ratio (dB)'] = signal_to_noise_ratio
    summary_df.loc[p, 'Mean Peak-to-Peak Amplitude (mV)'] = mean_peak_to_peak_amplitude
    summary_df.loc[p, 'Mean QRS to Signal Ratio'] = mean_qrs_to_signal_ratio
    summary_df.loc[p, 'Total Power (mV)'] = total_power
    summary_df.loc[p, 'Max PSD (mV^2/Hz)'] = max_psd
    summary_df.loc[p, 'Frequency of Max PSD (Hz)'] = freq_of_max_psd
