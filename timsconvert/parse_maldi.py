from timsconvert.constants import *
import numpy as np
import pandas as pd
import logging


# Parse MALDI plate map from CSV file.
def parse_maldi_plate_map(plate_map_filename):
    plate_map = pd.read_csv(plate_map_filename, header=None)
    plate_dict = {}
    for index, row in plate_map.itterrows():
        for count, value in enumerate(row, start=1):
            plate_dict[chr(index + 65) + str(count)] = value
    return plate_dict


# Get either raw (slightly modified implementation that gets centroid spectrum), quasi-profile, or centroid spectrum.
# Returns an m/z array and intensity array.
def extract_maldi_tsf_spectrum_arrays(tsf_data, mode, frame, encoding):
    if encoding == 32:
        encoding_dtype = np.float32
    elif encoding == 64:
        encoding_dtype = np.float64

    if mode == 'raw' or mode == 'centroid':
        index_buf, intensity_array = tsf_data.read_line_spectrum(frame)
        mz_array = tsf_data.index_to_mz(frame, index_buf)
        return mz_array, intensity_array
    elif mode == 'profile':
        intensity_array = np.array(tsf_data.read_profile_spectrum(frame), dtype=encoding_dtype)
        mz_acq_range_lower = float(tsf_data.meta_data['MzAcqRangeLower'])
        mz_acq_range_upper = float(tsf_data.meta_data['MzAcqRangeUpper'])
        step_size = (mz_acq_range_upper - mz_acq_range_lower) / len(intensity_array)
        mz_array = np.arange(mz_acq_range_lower, mz_acq_range_upper, step_size, dtype=encoding_dtype)
        return mz_array, intensity_array


def parse_maldi_tsf(tsf_data, frame_start, frame_end, mode, ms2_only, encoding):
    if encoding == 32:
        encoding_dtype = np.float32
    elif encoding == 64:
        encoding_dtype = np.float64

    logging.info(get_timestamp() + ':' + 'Parsing MALDI spectra')
    list_of_frames_dict = tsf_data.frames.to_dict(orient='records')
    list_of_maldiframeinfo_dict = tsf_data.maldiframeinfo.to_dict(orient='records')
    if tsf_data.framemsmsinfo is not None:
        list_of_framemsmsinfo_dict = tsf_data.framemsmsinfo.to_dict(orient='records')
    list_of_scan_dicts = []

    if mode == 'profile':
        centroided = False
    elif mode == 'centroid' or mode == 'raw':
        centroided = True

    for frame in range(frame_start, frame_end):
        frames_dict = [i for i in list_of_frames_dict if int(i['Id']) == frame][0]
        maldiframeinfo_dict = [i for i in list_of_maldiframeinfo_dict if int(i['Frame'] == frame)][0]
        if mode == 'raw':
            logging.info(get_timestamp() + ':' + 'TSF file detected. Only export in profile or centroid mode are '
                                                 'supported. Defaulting to centroid mode.')

        if int(frames_dict['MsMsType']) in MSMS_TYPE_CATEGORY['ms1']:
            if ms2_only == False:
                mz_array, intensity_array = extract_maldi_tsf_spectrum_arrays(tsf_data, mode, frame, encoding)

                if mz_array.size != 0 and intensity_array.size != 0:
                    base_peak_index = np.where(intensity_array == np.max(intensity_array))

                    if tsf_data.meta_data['MaldiApplicationType'] == 'SingleSpectra':
                        coords = maldiframeinfo_dict['SpotName']
                    elif tsf_data.meta_data['MaldiApplicationType'] == 'Imaging':
                        coords = []
                        coords.append(int(maldiframeinfo_dict['XIndexPos']))
                        coords.append(int(maldiframeinfo_dict['YIndexPos']))
                        if 'ZIndexPos' in tsf_data.maldiframeinfo.columns:
                            coords.append(int(maldiframeinfo_dict['ZIndexPos']))
                        coords = tuple(coords)

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
            framemsmsinfo_dict = [i for i in list_of_framemsmsinfo_dict
                                  if int(i['Frame']) == int(maldiframeinfo_dict['Frame'])][0]

            mz_array, intensity_array = extract_maldi_tsf_spectrum_arrays(tsf_data, mode, frame, encoding)

            if mz_array.size != 0 and intensity_array.size != 0:
                base_peak_index = np.where(intensity_array == np.max(intensity_array))

                if tsf_data.meta_data['MaldiApplicationType'] == 'SingleSpectra':
                    coords = maldiframeinfo_dict['SpotName']
                elif tsf_data.meta_data['MaldiApplicationType'] == 'Imaging':
                    coords = []
                    coords.append(int(maldiframeinfo_dict['XIndexPos']))
                    coords.append(int(maldiframeinfo_dict['YIndexPos']))
                    if 'ZIndexPos' in tsf_data.maldiframeinfo.columns:
                        coords.append(int(maldiframeinfo_dict['ZIndexPos']))
                    coords = tuple(coords)

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


if __name__ == '__main__':
    logger = logging.getLogger(__name__)
