import alphatims.bruker
import alphatims.utils
from ms_peak_picker import pick_peaks
from lxml import etree as et
import sqlite3
import numpy as np
import pandas as pd
import os
import sys
import itertools


# Function for itertools.groupby() to sort dictionaries based on key.
def key_func_frames(k):
    return k['parent_frame']


# Function for itertools.groupby() to sort dictionaries based on key.
def key_func_scans(k):
    return k['parent_scan']


# Centroid MS1 spectrum using ms_peak_picker algorithm.
def centroid_ms1_spectrum(scan):
    mz_array = scan['mz_values'].values
    intensity_array = scan['intensity_values'].values
    peak_list = pick_peaks(mz_array, intensity_array, fit_type='quadratic', peak_mode='profile')
    mz_array = [i.mz for i in list(peak_list.peaks)]
    intensity_array = [i.intensity for i in list(peak_list.peaks)]
    return mz_array, intensity_array


# Parse MS1 spectrum and output to dictionary containing necessary data.
def parse_ms1_scan(scan, frame_num, input_filename, groupby, centroided=True):
    # Centroid spectrum if True.
    if centroided == True:
        mz_array, intensity_array = centroid_ms1_spectrum(scan)
    elif centroided == False:
        mz_array = scan['mz_values'].values.tolist()
        intensity_array = scan['intensity_values'].values.tolist()

    # Set up .tdf database connection.
    con = sqlite3.connect(os.path.join(input_filename, 'analysis.tdf'))
    # Get polarity.
    query = 'SELECT * FROM Properties WHERE Frame == ' + str(frame_num)
    query_df = pd.read_sql_query(query, con)
    # Close connection to database.
    con.close()
    # Property 1229 == Mode_IonPolarity; alternatively maybe use 1098 == TOF_IonPolarity?
    polarity_value = list(set(query_df.loc[query_df['Property'] == 1229]['Value'].values.tolist()))
    if len(polarity_value) == 1:
        polarity_value = polarity_value[0]
        if int(polarity_value) == 0:
            polarity = 'positive scan'
        elif int(polarity_value == 1):
            polarity = 'negative scan'

    # Get row containing base peak information.
    base_peak_row = scan.sort_values(by='intensity_values', ascending=False).iloc[0]
    scan_dict = {'scan_number': None,
                 'mz_array': mz_array,
                 'intensity_array': intensity_array,
                 'scan_type': 'MS1 spectrum',
                 'polarity': polarity,
                 'centroided': centroided,
                 'retention_time': float(list(set(scan['rt_values_min'].values.tolist()))[0]),
                 'total_ion_current': sum(scan['intensity_values'].values.tolist()),
                 'base_peak_mz': float(base_peak_row['mz_values']),
                 'base_peak_intensity': float(base_peak_row['intensity_values']),
                 'ms_level': 1,
                 'high_mz': float(max(scan['mz_values'].values.tolist())),
                 'low_mz': float(min(scan['mz_values'].values.tolist())),
                 'parent_frame': 0,
                 'parent_scan': None}

    # Spectrum has single mobility value if grouped by scans (mobility).
    if groupby == 'scan':
        mobility = list(set(scan['mobility_values'].values.tolist()))
        if len(mobility) == 1:
            scan_dict['mobility'] = mobility[0]
        scan_dict['parent_scan'] = int(list(set(scan['scan_indices'].values.tolist()))[0])
    # Spectrum has array of mobility values if grouped by frame (retention time).
    elif groupby == 'frame':
        scan_dict['mobility_array'] = scan['mobility_values']
    return scan_dict


# Get all MS2 scans. Based in part on alphatims.bruker.save_as_mgf().
def parse_ms2_scans(raw_data, input_filename, groupby, centroided=True, centroiding_window=5,
                    keep_n_most_abundant_peaks=-1):
    # Check to make sure timsTOF object is valid.
    if raw_data.acquisition_mode != 'ddaPASEF':
        return None

    # Set up precursor information and get values for precursor indexing.
    (spectrum_indptr,
     spectrum_tof_indices,
     spectrum_intensity_values) = raw_data.index_precursors(centroiding_window=centroiding_window,
                                                            keep_n_most_abundant_peaks=keep_n_most_abundant_peaks)
    mono_mzs = raw_data.precursors.MonoisotopicMz.values
    average_mzs = raw_data.precursors.AverageMz.values
    charges = raw_data.precursors.Charge.values
    charges[np.flatnonzero(np.isnan(charges))] = 0
    charges = charges.astype(np.int64)
    rtinseconds = raw_data.rt_values[raw_data.precursors.Parent.values]
    intensities = raw_data.precursors.Intensity.values
    mobilities = raw_data.mobility_values[raw_data.precursors.ScanNumber.values.astype(np.int64)]
    parent_frames = raw_data.precursors.Parent.values
    parent_scans = np.floor(raw_data.precursors.ScanNumber.values)

    # Set up .tdf database connection.
    con = sqlite3.connect(os.path.join(input_filename, 'analysis.tdf'))

    list_of_scan_dicts = []
    for index in alphatims.utils.progress_callback(range(1, raw_data.precursor_max_index)):
        start = spectrum_indptr[index]
        end = spectrum_indptr[index + 1]

        # Remove MS2 scan if empty.
        if raw_data.mz_values[spectrum_tof_indices[start:end]].size != 0 or spectrum_intensity_values[start:end] != 0:
            if not np.isnan(mono_mzs[index - 1]):
                # Get isolation width and collision energy from Properties table in .tdf file.
                query = 'SELECT * FROM PasefFrameMsMsInfo WHERE Precursor = ' + str(index) +\
                        ' GROUP BY Precursor, IsolationMz, IsolationWidth, ScanNumBegin, ScanNumEnd'
                query_df = pd.read_sql_query(query, con)
                # Check to make sure there's only one hit. Exit with error if not.
                if query_df.shape[0] != 1:
                    print('PasefFrameMsMsInfo Precursor ' + str(index) + ' dataframe has more than one row.')
                    sys.exit(1)
                collision_energy = int(query_df['CollisionEnergy'].values.tolist()[0])
                # note: isolation widths are slightly off from what is given in alphatims dataframes.
                half_isolation_width = float(query_df['IsolationWidth'].values.tolist()[0]) / 2
                # Get polarity.
                query = 'SELECT * FROM PasefFrameMsMsInfo WHERE Precursor = 1'
                query_df = pd.read_sql_query(query, con)
                query2 = 'SELECT * FROM Properties WHERE Frame BETWEEN ' +\
                         str(min(query_df['Frame'].values.tolist())) + ' AND ' +\
                         str(max(query_df['Frame'].values.tolist()))
                query_df2 = pd.read_sql_query(query2, con)
                # Property 1229 == Mode_IonPolarity; alternatively maybe use 1098 == TOF_IonPolarity?
                polarity_value = list(set(query_df2.loc[query_df2['Property'] == 1229]['Value'].values.tolist()))
                if len(polarity_value) == 1:
                    polarity_value = polarity_value[0]
                    if int(polarity_value) == 0:
                        polarity = 'positive scan'
                    elif int(polarity_value == 1):
                        polarity = 'negative scan'

                scan_dict = {'scan_number': None,
                             'mz_array': raw_data.mz_values[spectrum_tof_indices[start:end]],
                             'intensity_array': spectrum_intensity_values[start:end],
                             'scan_type': 'MSn spectrum',
                             'polarity': polarity,
                             'centroided': centroided,
                             'retention_time': float(rtinseconds[index - 1] / 60),  # in min
                             'total_ion_current': sum(spectrum_intensity_values[start:end]),
                             'ms_level': 2,
                             'target_mz': average_mzs[index - 1],
                             'isolation_lower_offset': half_isolation_width,
                             'isolation_upper_offset': half_isolation_width,
                             'selected_ion_mz': float(mono_mzs[index - 1]),
                             'selected_ion_intensity': float(intensities[index - 1]),
                             'selected_ion_mobility': float(mobilities[index - 1]),
                             'charge_state': int(charges[index - 1]),
                             'collision_energy': collision_energy,
                             'parent_frame': parent_frames[index - 1],
                             'parent_scan': int(parent_scans[index - 1])}

                # Get base peak information.
                if spectrum_intensity_values[start:end].size != 0:
                    base_peak_index = spectrum_intensity_values[start:end].argmax()
                    scan_dict['base_peak_mz'] = float(raw_data.mz_values[spectrum_tof_indices[start:end]][base_peak_index])
                    scan_dict['base_peak_intensity'] = float(spectrum_intensity_values[base_peak_index])

                # Get high and low spectrum m/z values.
                if raw_data.mz_values[spectrum_tof_indices[start:end]].size != 0:
                    scan_dict['high_mz'] = float(max(raw_data.mz_values[spectrum_tof_indices[start:end]]))
                    scan_dict['low_mz'] = float(min(raw_data.mz_values[spectrum_tof_indices[start:end]]))

                list_of_scan_dicts.append(scan_dict)

    # Close connection to database.
    con.close()

    ms2_scans_dict = {}
    # Loop through frames.
    for key, value in itertools.groupby(list_of_scan_dicts, key_func_frames):
        if groupby == 'scan':
            # Loop through scans.
            for key2, value2 in itertools.groupby(list(value), key_func_scans):
                ms2_scans_dict['f' + str(key) + 's' + str(key2)] = list(value2)
        elif groupby == 'frame':
            ms2_scans_dict[key] = list(value)

    return ms2_scans_dict


# Extract all scan information including acquisition parameters, m/z, intensity, and mobility arrays/values
# from dataframes for each scan.
def parse_raw_data(raw_data, ms1_frames, input_filename, groupby):
    # Get all MS2 scans into dictionary.
    # keys == parent scan
    # values == list of scan dicts containing all the MS2 product scans for a given parent scan
    ms2_scans_dict = parse_ms2_scans(raw_data, input_filename, groupby)

    # Get all MS1 scans into dictionary.
    ms1_scans_dict = {}
    for frame_num in ms1_frames:
        if groupby == 'scan':
            ms1_scans = sorted(list(set(raw_data[frame_num]['scan_indices'])))
            for scan_num in ms1_scans:
                parent_scan = raw_data[frame_num, scan_num].sort_values(by='mz_values')
                ms1_scans_dict['f' + str(frame_num) + 's' + str(scan_num)] = parse_ms1_scan(parent_scan, frame_num,
                                                                                            input_filename, groupby)
        elif groupby == 'frame':
            parent_scan = raw_data[frame_num].sort_values(by='mz_values')
            ms1_scans_dict[frame_num] = parse_ms1_scan(parent_scan, frame_num, input_filename, groupby)

    return ms1_scans_dict, ms2_scans_dict
