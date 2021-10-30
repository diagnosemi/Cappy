import pickle
import pandas as pd
from custom_processing import process_hardware_ecg, apply_wavelet_reconstruction_denoising, apply_butter_low_pass,\
    remove_baseline_wander, remove_mean, plot_ecg

# Load PTB data
with open('raw_ptb_data', 'rb') as f:
    raw_ptb_data = pickle.load(f)
    f.close()

# Create df to store analyzed signals
healthy_controls = ['patient155', 'patient263', 'patient264', 'patient239', 'patient155']
our_data = ['simona', 'cesar']

df = pd.DataFrame(columns=healthy_controls+our_data)
# Extract data for 5 healthy controls: patient155, patient263, patient264, patient239, patient155 and save to df
for hc in healthy_controls:
    patient = raw_ptb_data[hc]
    recording = list(patient.keys())[0]
    signal = patient[recording]['i']
    df[hc] = signal

# Add our own raw data to df: downsample and take middle 115.2 secs to match length of PTB data
lower_bound = 60 * 1000
upper_bound = int((60+115.2) * 1000)
simona_sitting =\
    process_hardware_ecg(pd.read_csv('../ecg_acquisition/raw_ecgs/simona_sitting.csv'))[lower_bound:upper_bound]
df['simona'] = simona_sitting
cesar_sitting =\
    process_hardware_ecg(pd.read_csv('../ecg_acquisition/raw_ecgs/cesar_sitting.csv'))[lower_bound:upper_bound]
df['cesar'] = simona_sitting

# Perform signal processing on all signals in df
# Apply denoising filters on signal
df = df.apply(lambda x: apply_wavelet_reconstruction_denoising(x), axis=0)
df = df.apply(lambda x: apply_butter_low_pass(x), axis=0)

# Remove baseline wander
df = df.apply(lambda x: remove_baseline_wander(x), axis=0)

# Remove mean
df = df.apply(lambda x: remove_mean(x), axis=0)

#plot_ecg(df['patient263'], label='patient263')
plot_ecg(df['simona'], label='simona')

## In summary, need to do diff preprocessing for both sets. Need to set higher threshold for lpf wavelet reconstruction for our signals
