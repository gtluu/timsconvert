from timsconvert.constants import *
from timsconvert.timestamp import *
import numpy as np
import sys
import logging


def parse_lcms_tdf(tdf_data, frames_df, ms1_groupby, centroid, ms2_only, encoding):
    logging.info(get_timestamp() + ':' + 'Parsing LC-TIMS-MS/MS spectra...')
    list_of_frames_dict = tdf_data.frames.to_dict(orient='records')
    if tdf_data.pasefframemsmsinfo is not None:
        list_of_pasefframemsmsinfo_dict = tdf_data.pasefframemsmsinfo.to_dict(orient='records')
    if tdf_data.precursors is not None:
        list_of_precursors_dict = tdf_data.precursors.to_dict(orient='records')
    list_of_parent_scan_dicts = []
    list_of_product_scan_dicts = []

    for index, row in frames_df.iterrows():
        frames_dict = [i for i in list_of_frames_dict if int(i['Id']) == int(row['Id'])][0]

        if ms1_groupby == 'scan':
            if frames_dict['MsMsType'] in MSMS_TYPE_CATEGORY['ms1']:
                if ms2_only == False:
                    for scan_num in range(0, int(frames_dict['NumScans']) + 1):
                        scans = tdf_data.read_scans(int(row['Id']), scan_num, scan_num + 1)
                        if len(scans) == 1:
                            index_buf, intensity_array = scans[0]
                        elif len(scans) != 1:
                            logging.warning(get_timestamp() + ':' + 'Too Many Scans.')
                            sys.exit(1)
                        mz_array = tdf_data.index_to_mz(int(row['Id']), index_buf)

                        if mz_array.size != 0 and intensity_array.size != 0:
                            base_peak_index = np.where(intensity_array == np.max(intensity_array))

                            scan_dict = {'scan_number': int(scan_num),
                                         'scan_type': 'MS1 spectrum',
                                         'ms_level': 1,
                                         'mz_array': mz_array,
                                         'intensity_array': intensity_array,
                                         'mobility': tdf_data.scan_num_to_oneoverk0(int(row['Id']), np.array([scan_num]))[0],
                                         'polarity': frames_dict['Polarity'],
                                         'centroided': centroid,
                                         'retention_time': float(frames_dict['Time']),
                                         'total_ion_current': sum(intensity_array),
                                         'base_peak_mz': mz_array[base_peak_index][0].astype(float),
                                         'base_peak_intensity': intensity_array[base_peak_index][0].astype(float),
                                         'high_mz': float(max(mz_array)),
                                         'low_mz': float(min(mz_array)),
                                         'frame': int(row['Id'])}
                            list_of_parent_scan_dicts.append(scan_dict)
            elif frames_dict['MsMsType'] in MSMS_TYPE_CATEGORY['ms2']:
                pasefframemsmsinfo_dicts = [i for i in list_of_pasefframemsmsinfo_dict
                                           if int(i['Frame']) == int(row['Id'])]
                for pasefframemsmsinfo_dict in pasefframemsmsinfo_dicts:
                    precursor_dict = [i for i in list_of_precursors_dict
                                      if int(i['Id']) == int(pasefframemsmsinfo_dict['Precursor'])][0]
                    scan_begin = pasefframemsmsinfo_dict['ScanNumBegin']
                    scan_end = pasefframemsmsinfo_dict['ScanNumEnd']
                    mz_array, intensity_array = tdf_data.extract_spectrum_for_frame_v2(int(row['Id']),
                                                                                       scan_begin,
                                                                                       scan_end,
                                                                                       encoding)
                    if mz_array.size != 0 and intensity_array.size != 0:
                        base_peak_index = np.where(intensity_array == np.max(intensity_array))

                        scan_dict = {'scan_number': None,
                                     'scan_type': 'MSn spectrum',
                                     'ms_level': 2,
                                     'mz_array': mz_array,
                                     'intensity_array': intensity_array,
                                     'mobility_array': tdf_data.scan_num_to_oneoverk0(int(row['Id']),
                                                                                      np.array(list(range(scan_begin,
                                                                                                          scan_end)))),
                                     'polarity': frames_dict['Polarity'],
                                     'centroided': centroid,
                                     'retention_time': float(frames_dict['Time']),
                                     'total_ion_current': sum(intensity_array),
                                     'base_peak_mz': mz_array[base_peak_index][0].astype(float),
                                     'base_peak_intensity': intensity_array[base_peak_index][0].astype(float),
                                     'high_mz': float(max(mz_array)),
                                     'low_mz': float(min(mz_array)),
                                     'target_mz': pasefframemsmsinfo_dict['IsolationMz'],
                                     'isolation_lower_offset': float(pasefframemsmsinfo_dict['IsolationWidth']) / 2,
                                     'isolation_upper_offset': float(pasefframemsmsinfo_dict['IsolationWidth']) / 2,
                                     'selected_ion_mz': pasefframemsmsinfo_dict['IsolationMz'],
                                     'selected_ion_intensity': precursor_dict['Intensity'],
                                     'selected_ion_mobility': precursor_dict['Mobility'],
                                     'charge_state': precursor_dict['Charge'],
                                     'collision_energy': pasefframemsmsinfo_dict['CollisionEnergy'],
                                     'parent_frame': int(precursor_dict['Parent']),
                                     'parent_scan': int(scan_begin)}
                        list_of_product_scan_dicts.append(scan_dict)
        elif ms1_groupby == 'frame':
            if frames_dict['MsMsType'] in MSMS_TYPE_CATEGORY['ms1']:
                if ms2_only == False:
                    mz_array, intensity_array = tdf_data.extract_spectrum_for_frame_v2(int(row['Id']),
                                                                                       0,
                                                                                       int(frames_dict['NumScans']),
                                                                                       encoding)
                    if mz_array.size != 0 and intensity_array.size != 0:
                        base_peak_index = np.where(intensity_array == np.max(intensity_array))

                        scan_dict = {'scan_number': None,
                                     'scan_type': 'MS1 spectrum',
                                     'ms_level': 1,
                                     'mz_array': mz_array,
                                     'intensity_array': intensity_array,
                                     'mobility_array': tdf_data.scan_num_to_oneoverk0(int(row['Id']),
                                                                                      np.array(list(range(1, int(frames_dict['NumScans'])+1)))),
                                     'polarity': frames_dict['Polarity'],
                                     'centroided': centroid,
                                     'retention_time': float(frames_dict['Time']),
                                     'total_ion_current': sum(intensity_array),
                                     'base_peak_mz': mz_array[base_peak_index][0].astype(float),
                                     'base_peak_intensity': intensity_array[base_peak_index][0].astype(float),
                                     'high_mz': float(max(mz_array)),
                                     'low_mz': float(min(mz_array)),
                                     'frame': int(row['Id'])}
                        list_of_parent_scan_dicts.append(scan_dict)
            elif frames_dict['MsMsType'] in MSMS_TYPE_CATEGORY['ms2']:
                pasefframemsmsinfo_dicts = [i for i in list_of_pasefframemsmsinfo_dict
                                            if int(i['Frame']) == int(row['Id'])]
                for pasefframemsmsinfo_dict in pasefframemsmsinfo_dicts:
                    precursor_dict = [i for i in list_of_precursors_dict
                                      if int(i['Id']) == int(pasefframemsmsinfo_dict['Precursor'])][0]
                    scan_begin = pasefframemsmsinfo_dict['ScanNumBegin']
                    scan_end = pasefframemsmsinfo_dict['ScanNumEnd']
                    mz_array, intensity_array = tdf_data.extract_spectrum_for_frame_v2(int(row['Id']),
                                                                                       scan_begin,
                                                                                       scan_end,
                                                                                       encoding)
                    if mz_array.size != 0 and intensity_array.size != 0:
                        base_peak_index = np.where(intensity_array == np.max(intensity_array))

                        scan_dict = {'scan_number': None,
                                     'scan_type': 'MSn spectrum',
                                     'ms_level': 2,
                                     'mz_array': mz_array,
                                     'intensity_array': intensity_array,
                                     'mobility_array': tdf_data.scan_num_to_oneoverk0(int(row['Id']),
                                                                                      np.array(list(range(scan_begin,
                                                                                                          scan_end)))),
                                     'polarity': frames_dict['Polarity'],
                                     'centroided': centroid,
                                     'retention_time': float(frames_dict['Time']),
                                     'total_ion_current': sum(intensity_array),
                                     'base_peak_mz': mz_array[base_peak_index][0].astype(float),
                                     'base_peak_intensity': intensity_array[base_peak_index][0].astype(float),
                                     'high_mz': float(max(mz_array)),
                                     'low_mz': float(min(mz_array)),
                                     'target_mz': pasefframemsmsinfo_dict['IsolationMz'],
                                     'isolation_lower_offset': float(pasefframemsmsinfo_dict['IsolationWidth']) / 2,
                                     'isolation_upper_offset': float(pasefframemsmsinfo_dict['IsolationWidth']) / 2,
                                     'selected_ion_mz': pasefframemsmsinfo_dict['IsolationMz'],
                                     'selected_ion_intensity': precursor_dict['Intensity'],
                                     'selected_ion_mobility': precursor_dict['Mobility'],
                                     'charge_state': precursor_dict['Charge'],
                                     'collision_energy': pasefframemsmsinfo_dict['CollisionEnergy'],
                                     'parent_frame': int(precursor_dict['Parent'])}
                        list_of_product_scan_dicts.append(scan_dict)
    return list_of_parent_scan_dicts, list_of_product_scan_dicts


if __name__ == '__main__':
    logger = logging.getLogger(__name__)
