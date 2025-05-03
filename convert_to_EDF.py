import pandas as pd
import numpy as np
import pyedflib
from pyedflib import FILETYPE_EDF
from datetime import datetime
import sys
import os

def csv_to_edf(csv_filename, edf_filename=None, apply_filtering=False, apply_detrend=False):
    """
    Convert a CSV file with EEG data to EDF format.

    Parameters:
    -----------
    csv_filename : str
        Path to the input CSV file
    edf_filename : str, optional
        Path to the output EDF file. If None, will use the same name as the CSV file but with .edf extension.
    apply_filtering : bool, optional
        Whether to apply filtering to the signals. Default is False.
    apply_detrend : bool, optional
        Whether to remove DC offset from signals. Default is False.
    """
    if edf_filename is None:
        edf_filename = os.path.splitext(csv_filename)[0] + '.edf'

    # Read the CSV file
    print(f"Reading CSV file: {csv_filename}")
    df = pd.read_csv(csv_filename)

    # Extract channel names and data
    channel_names = df.columns.tolist()[:-1]  # All columns except timestamp
    timestamp_col = df.columns[-1]
    n_channels = len(channel_names)

    # Calculate sampling frequency based on timestamps
    timestamps = df[timestamp_col].values
    sampling_freq = 1000.0 / np.mean(np.diff(timestamps))  # Hz
    print(f"Estimated sampling frequency: {sampling_freq:.2f} Hz")

    # Prepare data for EDF
    signal_headers = []
    for i, channel in enumerate(channel_names):
        signal_headers.append({
            'label': channel,
            'dimension': 'uV',
            'sample_frequency': sampling_freq,
            'physical_max': df[channel].max(),
            'physical_min': df[channel].min(),
            'digital_max': 32767,
            'digital_min': -32768,
            'transducer': 'Gold plated dry electrode',
            'prefilter': 'None'
        })

    # Prepare EDF header
    header = {
        'technician': '',
        'recording_additional': '',
        'patientname': '',
        'patient_additional': '',
        'patientcode': '',
        'equipment': 'Converted from CSV',
        'admincode': '',
        'sex': '',
        'startdate': datetime.now(),
        'birthdate': ''
    }

    # Create EDF file
    print(f"Creating EDF file: {edf_filename}")
    with pyedflib.EdfWriter(edf_filename, n_channels=n_channels, file_type=FILETYPE_EDF) as f:
        f.setSignalHeaders(signal_headers)
        f.setHeader(header)

        # Write each signal
        for i, channel in enumerate(channel_names):
            data = df[channel].values
            # Print some statistics about the raw data
            print(f"Channel {channel} raw data - min: {np.min(data):.2f}, max: {np.max(data):.2f}, mean: {np.mean(data):.2f}")
            f.writePhysicalSamples(data)

    print(f"Successfully converted {csv_filename} to {edf_filename}")
    return edf_filename

def main():
    if len(sys.argv) < 2:
        print("Usage: python convert_to_EDF.py <input_csv_file> [output_edf_file]")
        return

    csv_filename = sys.argv[1]
    edf_filename = sys.argv[2] if len(sys.argv) > 2 else None

    csv_to_edf(csv_filename, edf_filename)

if __name__ == "__main__":
    main()
