import pandas as pd
import wfdb
import os


# Format data for one patient
def get_formatted_patient_data(patient_id, folder_path):
    # Create list to store recording names for patient
    ecg_records_list = []

    # Get a list of all ecg recordings for the patient
    patient_folder_path = folder_path + "/" + patient_id
    for ecg_recording in os.listdir(patient_folder_path):
        ecg_recording = ecg_recording.split('.')[0]
        ecg_records_list.append(ecg_recording)
        ecg_records_list = list(set(ecg_records_list))

    # Create dict to store dfs of data from each recording
    patient_recording_data = {}

    # For each ecg recording, process record
    ecg_count = 1
    for recording in ecg_records_list:
        recording_data = wfdb.rdrecord(patient_folder_path + "/" + recording)
        recording_data = recording_data.__dict__

        # Extract relevant clinical data from comments
        comments = recording_data["comments"]

        # Skip ecg signal if it has no diagnostic class
        skip = False
        for comment in comments:
            if "Reason for admission" in comment:
                diagnosis = comment.split(":")[1].strip()
                if diagnosis == 'n/a':
                    skip = True
                    break
                elif diagnosis == 'Myocardial infarction':
                    diagnostic_class = 'mi'
                elif diagnosis == 'Healthy control':
                    diagnostic_class = 'norm'
                else:
                    diagnostic_class = 'non_mi'
        if skip:
            continue

        # Extract signal data
        lead_names = recording_data['sig_name']
        signals = recording_data['p_signal']

        # Create recording df
        recording_df = pd.DataFrame(signals, columns=lead_names)
        recording_df['patient_id'] = patient_id
        recording_df['recording_id'] = recording
        recording_df['diagnostic_class'] = diagnostic_class

        # Replace "no" with None to standardize
        recording_df.replace({"no": None}, inplace=True)

        # Add df to patient recording data dict
        recording_key = patient_id + '_ecg_id_' + str(ecg_count)
        patient_recording_data[recording_key] = recording_df
        ecg_count += 1
    return patient_recording_data


# Get nested dict: recording id --> record df
def get_formatted_ptb_data():
    # Load folder path where PTB data is stored from environment variable
    ptb_folder_path = os.getenv('PTB_FOLDER_PATH')

    # Get a list of all patients
    patients = []
    for file in os.listdir(ptb_folder_path):
        if 'patient' in file:
            patients.append(file)

    # Loop through all patients and create a dict with record id as key and one df per recording
    total_patient_data = {}
    for patient in patients:
        patient_data = get_formatted_patient_data(patient, ptb_folder_path)
        total_patient_data.update(patient_data)
    return total_patient_data
