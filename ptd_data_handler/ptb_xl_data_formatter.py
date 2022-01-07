import pandas as pd
import wfdb
import os
import json


# Function to create a dict mapping mi, non-mi and norm to scp disease acronyms
def assign_diagnostic_label(x, scp_mapping):
    # Convert string to dict
    scp_codes = json.loads(x['scp_codes'].replace("\'", "\""))

    # Get all scp_codes greater than 50
    scp_codes = {k: v for (k, v) in scp_codes.items() if v >= 50}

    if not scp_codes:
        return 'bad_ecg'

    # Check if any SCP code is in MI class
    if any(elem in scp_codes for elem in scp_mapping['mi']):
        return 'mi'

    # Check if any SCP code is in non MI class
    if any(elem in scp_codes for elem in scp_mapping['non_mi']):
        return 'non_mi'

    # Otherwise it is a healthy individual
    return 'norm'


# Function to create a df with recording and diagnostic label for each ecg_id
def get_formatted_ecg_data(ecg_metadata, ptb_xl_folder_path):
    # Extract metadata about the ecg
    ecg_id = ecg_metadata['ecg_id']
    strat_fold = ecg_metadata['strat_fold']
    diagnostic_class = ecg_metadata['diagnostic_class']
    patient_folder_path = ptb_xl_folder_path + "/" + ecg_metadata['filename_hr']

    # Read in the ECG
    recording_data = wfdb.rdrecord(patient_folder_path)
    recording_data = recording_data.__dict__

    # Create df using leads from ECG
    lead_names = recording_data['sig_name']
    signals = recording_data['p_signal']
    recording_df = pd.DataFrame(signals, columns=lead_names)
    recording_df['strat_fold'] = strat_fold
    recording_df['diagnostic_class'] = diagnostic_class
    return recording_df


# Function to create a dict of ecg_ids and dataframe with the metadata from the ptb_xl database
def get_formatted_ptb_xl_data():
    # Load folder path where PTB_XL data is stored from environment variable
    ptb_xl_folder_path = os.getenv('PTB_XL_FOLDER_PATH')

    # Read in scp_statements.csv and create mapping of SCP code to MI, non-MI, healthy
    scp_statements = pd.read_csv(ptb_xl_folder_path + '/scp_statements.csv')
    scp_statements['diagnostic_label'] = scp_statements.apply(
        lambda x: 'norm' if x['diagnostic_class'] == 'NORM' else ('mi' if x['diagnostic_class'] == 'MI' else 'non_mi'),
        axis=1)
    scp_mapping = scp_statements.groupby('diagnostic_label')['Unnamed: 0'].apply(lambda x: x.tolist()).to_dict()

    # Read in ptbxl_database.csv and get rid of rows based on scp_codes col:
    # 1. If values in dict are less than 50, discard row
    # 2. If MI is a remaining value, label as MI
    # 3. Otherwise label healthy or non-MI
    ptb_xl_df = pd.read_csv(ptb_xl_folder_path + '/ptbxl_database.csv')
    ptb_xl_df = ptb_xl_df[['ecg_id', 'scp_codes', 'strat_fold', 'filename_hr']]
    ptb_xl_df['diagnostic_class'] = ptb_xl_df.apply(lambda x: assign_diagnostic_label(x, scp_mapping), axis=1)
    ptb_xl_df = ptb_xl_df[ptb_xl_df['diagnostic_class'] != 'bad_ecg']

    # Loop through all ecgs and create a dict with ecg id as key and one df per recording
    total_ecg_data = {}
    for i, r in ptb_xl_df.iterrows():
        ecg_data = get_formatted_ecg_data(r, ptb_xl_folder_path)
        ecg_string_id = 'ecg_id_' + str(r['ecg_id'])
        total_ecg_data[ecg_string_id] = ecg_data
    return total_ecg_data
