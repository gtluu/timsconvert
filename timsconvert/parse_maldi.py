from timsconvert.constants import *
import numpy as np
import pandas as pd
import logging


# Parse MALDI plate map from CSV file.
def parse_maldi_plate_map(plate_map_filename):
    plate_map = pd.read_csv(plate_map_filename, header=None)
    plate_dict = {}
    for index, row in plate_map.iterrows():
        for count, value in enumerate(row, start=1):
            plate_dict[chr(index + 65) + str(count)] = value
    return plate_dict


# Get either quasi-profile or centroid spectrum.
# Returns an m/z array and intensity array.
def extract_maldi_tsf_spectrum_arrays(tsf_data, mode, frame, profile_bins, encoding):
    if encoding == 32:
        encoding_dtype = np.float32
    elif encoding == 64:
        encoding_dtype = np.float64

    if mode == 'raw' or mode == 'centroid':
        index_buf, intensity_array = tsf_data.read_line_spectrum(frame)
        mz_array = tsf_data.index_to_mz(frame, index_buf)
        return mz_array, intensity_array
    elif mode == 'profile':
        index_buf, intensity_array = tsf_data.read_profile_spectrum(frame)
        intensity_array = np.array(intensity_array, dtype=encoding_dtype)
        mz_array = tsf_data.index_to_mz(frame, index_buf)
        if profile_bins != 0:
            mz_acq_range_lower = float(mz_array[0])
            mz_acq_range_upper = float(mz_array[-1])
            bins = np.linspace(mz_acq_range_lower, mz_acq_range_upper, profile_bins, dtype=encoding_dtype)
            unique_indices, inverse_indices = np.unique(np.digitize(mz_array, bins), return_inverse=True)
            bin_counts = np.bincount(inverse_indices)
            np.place(bin_counts, bin_counts < 1, [1])
            mz_array = np.bincount(inverse_indices, weights=mz_array) / bin_counts
            intensity_array = np.bincount(inverse_indices, weights=intensity_array)
        return mz_array, intensity_array


# Get either raw (slightly modified implementation that gets centroid spectrum), quasi-profile, or centroid spectrum.
# Returns an m/z array and intensity array.
def extract_maldi_tdf_spectrum_arrays(tdf_data, mode, multiscan, frame, scan_begin, scan_end, profile_bins, encoding):
    if encoding == 32:
        encoding_dtype = np.float32
    elif encoding == 64:
        encoding_dtype = np.float64

    if mode == 'raw':
        if not multiscan:
            scans = tdf_data.read_scans(frame, scan_begin, scan_end)
            if len(scans) == 1:
                index_buf, intensity_array = scans[0]
            elif len(scans) != 1:
                sys.exit(1)
            mz_array = tdf_data.index_to_mz(frame, index_buf)
            return mz_array, intensity_array
        elif multiscan:
            mz_array, intensity_array = tdf_data.extract_spectrum_for_frame_v2(frame, scan_begin, scan_end, encoding)
            return mz_array, intensity_array
    elif mode == 'profile':
        index_buf, intensity_array = tdf_data.extract_profile_spectrum_for_frame(frame, scan_begin, scan_end)
        intensity_array = np.array(intensity_array, dtype=encoding_dtype)
        mz_array = tdf_data.index_to_mz(frame, index_buf)
        if profile_bins != 0:
            mz_acq_range_lower = float(mz_array[0])
            mz_acq_range_upper = float(mz_array[-1])
            bins = np.linspace(mz_acq_range_lower, mz_acq_range_upper, profile_bins, dtype=encoding_dtype)
            unique_indices, inverse_indices = np.unique(np.digitize(mz_array, bins), return_inverse=True)
            bin_counts = np.bincount(inverse_indices)
            np.place(bin_counts, bin_counts < 1, [1])
            mz_array = np.bincount(inverse_indices, weights=mz_array) / bin_counts
            intensity_array = np.bincount(inverse_indices, weights=intensity_array)
        return mz_array, intensity_array
    elif mode == 'centroid':
        mz_array, intensity_array = tdf_data.extract_centroided_spectrum_for_frame(frame, scan_begin, scan_end)
        mz_array = np.array(mz_array, dtype=encoding_dtype)
        intensity_array = np.array(intensity_array, dtype=encoding_dtype)
        return mz_array, intensity_array


def parse_maldi_tsf(tsf_data, frame_start, frame_stop, mode, ms2_only, profile_bins, encoding):
    if encoding == 32:
        encoding_dtype = np.float32
    elif encoding == 64:
        encoding_dtype = np.float64

    #list_of_frames_dict = tsf_data.frames.to_dict(orient='records')
    #list_of_maldiframeinfo_dict = tsf_data.maldiframeinfo.to_dict(orient='records')
    #if tsf_data.framemsmsinfo is not None:
    #    list_of_framemsmsinfo_dict = tsf_data.framemsmsinfo.to_dict(orient='records')
    list_of_scan_dicts = []

    if mode == 'profile':
        centroided = False
    elif mode == 'centroid' or mode == 'raw':
        centroided = True

    for frame in range(frame_start, frame_stop):
        #frames_dict = [i for i in list_of_frames_dict if int(i['Id']) == frame][0]
        frames_dict = tsf_data.frames[tsf_data.frames['Id'] == frame].to_dict(orient='records')[0]
        #maldiframeinfo_dict = [i for i in list_of_maldiframeinfo_dict if int(i['Frame'] == frame)][0]
        maldiframeinfo_dict = tsf_data.maldiframeinfo[tsf_data.maldiframeinfo['Frame'] ==
                                                      frame].to_dict(orient='records')[0]

        if tsf_data.meta_data['MaldiApplicationType'] == 'SingleSpectra':
            coords = maldiframeinfo_dict['SpotName']
        elif tsf_data.meta_data['MaldiApplicationType'] == 'Imaging':
            coords = []
            coords.append(int(maldiframeinfo_dict['XIndexPos']))
            coords.append(int(maldiframeinfo_dict['YIndexPos']))
            if 'ZIndexPos' in tsf_data.maldiframeinfo.columns:
                coords.append(int(maldiframeinfo_dict['ZIndexPos']))
            coords = tuple(coords)

        if int(frames_dict['MsMsType']) in MSMS_TYPE_CATEGORY['ms1']:
            if ms2_only == False:
                mz_array, intensity_array = extract_maldi_tsf_spectrum_arrays(tsf_data, mode, frame, profile_bins,
                                                                              encoding)

                if mz_array.size != 0 and intensity_array.size != 0 and mz_array.size == intensity_array.size:
                    base_peak_index = np.where(intensity_array == np.max(intensity_array))

                    scan_dict = {'scan_number': None,
                                 'scan_type': 'MS1 spectrum',
                                 'ms_level': 1,
                                 'mz_array': mz_array,
                                 'intensity_array': intensity_array,
                                 'coord': coords,
                                 'polarity': frames_dict['Polarity'],
                                 'centroided': centroided,
                                 'retention_time': 0,
                                 'total_ion_current': sum(intensity_array),
                                 'base_peak_mz': mz_array[base_peak_index][0].astype(float),
                                 'base_peak_intensity': intensity_array[base_peak_index][0].astype(float),
                                 'high_mz': float(max(mz_array)),
                                 'low_mz': float(min(mz_array)),
                                 'frame': frame}
                    list_of_scan_dicts.append(scan_dict)
        elif int(frames_dict['MsMsType']) in MSMS_TYPE_CATEGORY['ms2']:
            #framemsmsinfo_dict = [i for i in list_of_framemsmsinfo_dict
            #                      if int(i['Frame']) == int(maldiframeinfo_dict['Frame'])][0]
            framemsmsinfo_dict = tsf_data.framemsmsinfo[tsf_data.framemsmsinfo['Frame'] ==
                                                        maldiframeinfo_dict['Frame']].to_dict(orient='records')[0]

            mz_array, intensity_array = extract_maldi_tsf_spectrum_arrays(tsf_data, mode, frame, profile_bins,
                                                                          encoding)

            if mz_array.size != 0 and intensity_array.size != 0 and mz_array.size == intensity_array.size:
                base_peak_index = np.where(intensity_array == np.max(intensity_array))

                scan_dict = {'scan_number': None,
                             'scan_type': 'MSn spectrum',
                             'ms_level': 2,
                             'mz_array': mz_array,
                             'intensity_array': intensity_array,
                             'coord': coords,
                             'polarity': frames_dict['Polarity'],
                             'centroided': centroided,
                             'retention_time': 0,
                             'total_ion_current': sum(intensity_array),
                             'base_peak_mz': mz_array[base_peak_index][0].astype(float),
                             'base_peak_intensity': intensity_array[base_peak_index][0].astype(float),
                             'high_mz': float(max(mz_array)),
                             'low_mz': float(min(mz_array)),
                             'target_mz': float(framemsmsinfo_dict['TriggerMass']),
                             'isolation_lower_offset': float(framemsmsinfo_dict['IsolationWidth']) / 2,
                             'isolation_upper_offset': float(framemsmsinfo_dict['IsolationWidth']) / 2,
                             'selected_ion_mz': float(framemsmsinfo_dict['TriggerMass']),
                             'charge_state': framemsmsinfo_dict['PrecursorCharge'],
                             'collision_energy': framemsmsinfo_dict['CollisionEnergy']}
                list_of_scan_dicts.append(scan_dict)

    return list_of_scan_dicts


def parse_maldi_tdf(tdf_data, frame_start, frame_stop, mode, ms2_only, exclude_mobility, profile_bins, encoding):
    if encoding == 32:
        encoding_dtype = np.float32
    elif encoding == 64:
        encoding_dtype = np.float64

    #list_of_frames_dict = tdf_data.frames.to_dict(orient='records')
    #list_of_maldiframeinfo_dict = tdf_data.maldiframeinfo.to_dict(orient='records')
    #if tdf_data.framemsmsinfo is not None:
    #    list_of_framemsmsinfo_dict = tdf_data.framemsmsinfo.to_dict(orient='records')
    list_of_scan_dicts = []

    if mode == 'profile':
        centroided = False
        exclude_mobility = True
    elif mode == 'centroid' or mode == 'raw':
        centroided = True

    for frame in range(frame_start, frame_stop):
        #frames_dict = [i for i in list_of_frames_dict if int(i['Id']) == frame][0]
        frames_dict = tdf_data.frames[tdf_data.frames['Id'] == frame].to_dict(orient='records')[0]
        #maldiframeinfo_dict = [i for i in list_of_maldiframeinfo_dict if int(i['Frame'] == frame)][0]
        maldiframeinfo_dict = tdf_data.maldiframeinfo[tdf_data.maldiframeinfo['Frame'] ==
                                                      frame].to_dict(orient='records')[0]

        if tdf_data.meta_data['MaldiApplicationType'] == 'SingleSpectra':
            coords = maldiframeinfo_dict['SpotName']
        elif tdf_data.meta_data['MaldiApplicationType'] == 'Imaging':
            coords = []
            coords.append(int(maldiframeinfo_dict['XIndexPos']))
            coords.append(int(maldiframeinfo_dict['YIndexPos']))
            if 'ZIndexPos' in tdf_data.maldiframeinfo.columns:
                coords.append(int(maldiframeinfo_dict['ZIndexPos']))
            coords = tuple(coords)

        if int(frames_dict['MsMsType']) in MSMS_TYPE_CATEGORY['ms1']:
            if ms2_only == False:
                if exclude_mobility == False:
                    frame_mz_arrays = []
                    frame_intensity_arrays = []
                    frame_mobility_arrays = []
                    for scan_num in range(0, int(frames_dict['NumScans'])):
                        mz_array, intensity_array = extract_maldi_tdf_spectrum_arrays(tdf_data,
                                                                                      mode,
                                                                                      True,
                                                                                      frame,
                                                                                      scan_num,
                                                                                      scan_num + 1,
                                                                                      profile_bins,
                                                                                      encoding)
                        if mz_array.size != 0 and intensity_array.size != 0 and mz_array.size == intensity_array.size:
                            mobility = tdf_data.scan_num_to_oneoverk0(frame, np.array([scan_num]))[0]
                            mobility_array = np.repeat(mobility, mz_array.size)

                            frame_mz_arrays.append(mz_array)
                            frame_intensity_arrays.append(intensity_array)
                            frame_mobility_arrays.append(mobility_array)
                    if frame_mz_arrays and frame_intensity_arrays and frame_mobility_arrays:
                        frames_array = np.stack((np.concatenate(frame_mz_arrays, axis=None),
                                                 np.concatenate(frame_intensity_arrays, axis=None),
                                                 np.concatenate(frame_mobility_arrays, axis=None)),
                                                axis=-1)
                        frames_array = np.unique(frames_array[np.argsort(frames_array[:, 0])], axis=0)
                        base_peak_index = np.where(frames_array[:, 1] == np.max(frames_array[:, 1]))
                        scan_dict = {'scan_number': None,
                                     'scan_type': 'MS1 spectrum',
                                     'ms_level': 1,
                                     'mz_array': frames_array[:, 0],
                                     'intensity_array': frames_array[:, 1],
                                     'mobility': None,
                                     'mobility_array': frames_array[:, 2],
                                     'coord': coords,
                                     'polarity': frames_dict['Polarity'],
                                     'centroided': centroided,
                                     'retention_time': 0,
                                     'total_ion_current': sum(frames_array[:, 1]),
                                     'base_peak_mz': frames_array[:, 0][base_peak_index][0].astype(float),
                                     'base_peak_intensity': frames_array[:, 1][base_peak_index][0].astype(float),
                                     'high_mz': float(max(frames_array[:, 0])),
                                     'low_mz': float(min(frames_array[:, 0])),
                                     'frame': frame}
                        list_of_scan_dicts.append(scan_dict)
                elif exclude_mobility == True:
                    mz_array, intensity_array = extract_maldi_tdf_spectrum_arrays(tdf_data,
                                                                                  mode,
                                                                                  True,
                                                                                  frame,
                                                                                  0,
                                                                                  int(frames_dict['NumScans']),
                                                                                  profile_bins,
                                                                                  encoding)

                    if mz_array.size != 0 and intensity_array.size != 0 and mz_array.size == intensity_array.size:
                        base_peak_index = np.where(intensity_array == np.max(intensity_array))

                        scan_dict = {'scan_number': None,
                                     'scan_type': 'MS1 spectrum',
                                     'ms_level': 1,
                                     'mz_array': mz_array,
                                     'intensity_array': intensity_array,
                                     'mobility': None,
                                     'mobility_array': None,
                                     'coord': coords,
                                     'polarity': frames_dict['Polarity'],
                                     'centroided': centroided,
                                     'retention_time': 0,
                                     'total_ion_current': sum(intensity_array),
                                     'base_peak_mz': mz_array[base_peak_index][0].astype(float),
                                     'base_peak_intensity': intensity_array[base_peak_index][0].astype(float),
                                     'high_mz': float(max(mz_array)),
                                     'low_mz': float(min(mz_array)),
                                     'frame': frame}
                        list_of_scan_dicts.append(scan_dict)
        elif int(frames_dict['MsMsType']) in MSMS_TYPE_CATEGORY['ms2']:
            #framemsmsinfo_dict = [i for i in list_of_framemsmsinfo_dict
            #                      if int(i['Frame']) == int(maldiframeinfo_dict['Frame'])][0]
            framemsmsinfo_dict = tdf_data.framemsmsinfo[tdf_data.framemsmsinfo['Frame'] ==
                                                        maldiframeinfo_dict['Frame']].to_dict(orient='records')[0]
            mz_array, intensity_array = extract_maldi_tdf_spectrum_arrays(tdf_data,
                                                                          mode,
                                                                          True,
                                                                          frame,
                                                                          0,
                                                                          int(frames_dict['NumScans']),
                                                                          profile_bins,
                                                                          encoding)

            if mz_array.size != 0 and intensity_array.size != 0 and mz_array.size == intensity_array.size:
                base_peak_index = np.where(intensity_array == np.max(intensity_array))

                scan_dict = {'scan_number': None,
                             'scan_type': 'MSn spectrum',
                             'ms_level': 2,
                             'mz_array': mz_array,
                             'intensity_array': intensity_array,
                             'coord': coords,
                             'polarity': frames_dict['Polarity'],
                             'centroided': centroided,
                             'retention_time': 0,
                             'total_ion_current': sum(intensity_array),
                             'base_peak_mz': mz_array[base_peak_index][0].astype(float),
                             'base_peak_intensity': intensity_array[base_peak_index][0].astype(float),
                             'high_mz': float(max(mz_array)),
                             'low_mz': float(min(mz_array)),
                             'target_mz': float(framemsmsinfo_dict['TriggerMass']),
                             'isolation_lower_offset': float(framemsmsinfo_dict['IsolationWidth']) / 2,
                             'isolation_upper_offset': float(framemsmsinfo_dict['IsolationWidth']) / 2,
                             'selected_ion_mz': float(framemsmsinfo_dict['TriggerMass']),
                             'charge_state': framemsmsinfo_dict['PrecursorCharge'],
                             'collision_energy': framemsmsinfo_dict['CollisionEnergy']}
                list_of_scan_dicts.append(scan_dict)

    return list_of_scan_dicts
