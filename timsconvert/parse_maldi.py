from timsconvert.constants import *
import numpy as np
import pandas as pd
import logging


def parse_maldi_plate_map(plate_map_filename):
    plate_map = pd.read_csv(plate_map_filename, header=None)
    plate_dict = {}
    for index, row in plate_map.itterrows():
        for count, value in enumerate(row, start=1):
            plate_dict[chr(index + 65) + str(count)] = value
    return plate_dict


def parse_maldi_tsf(tsf_data, centroid):
    logging.info(get_timestamp() + ':' + 'Parsing MALDI spectra...')
    list_of_frames_dict = tsf_data.frames.to_dict(orient='records')
    if tsf_data.framemsmsinfo is not None:
        list_of_framemsmsinfo_dict = tsf_data.framemsmsinfo.to_dict(orient='records')
    list_of_scan_dicts = []
    for index, row in tsf_data.maldiframeinfo.iterrows():
        frames_dict = [i for i in list_of_frames_dict if int(i['Id']) == int(row['Frame'])][0]
        index_buf, intensity_array = tsf_data.read_line_spectrum(int(row['Frame']))
        mz_array = tsf_data.index_to_mz(int(row['Frame']), index_buf)

        if mz_array.size != 0 and intensity_array.size != 0:
            base_peak_index = np.where(intensity_array == np.max(intensity_array))

            if tsf_data.meta_data['MaldiApplicationType'] == 'SingleSpectra':
                coords = row['SpotName']
            elif tsf_data.meta_data['MaldiApplicationType'] == 'Imaging':
                coords = []
                coords.append(int(row['XIndexPos']))
                coords.append(int(row['YIndexPos']))
                if 'ZIndexPos' in tsf_data.maldiframeinfo.columns:
                    coords.append(int(row['ZIndexPos']))
                coords = tuple(coords)

            scan_dict = {'scan_number': None,
                         'mz_array': mz_array,
                         'intensity_array': intensity_array,
                         'coord': coords,
                         'polarity': frames_dict['Polarity'],
                         'centroided': centroid,
                         'retention_time': 0,
                         'total_ion_current': sum(intensity_array),
                         'base_peak_mz': float(mz_array[base_peak_index]),
                         'base_peak_intensity': float(intensity_array[base_peak_index]),
                         'high_mz': float(max(mz_array)),
                         'low_mz': float(min(mz_array))}

            if int(frames_dict['MsMsType']) in MSMS_TYPE_CATEGORY['ms1']:
                scan_dict['scan_type'] = 'MS1 spectrum'
                scan_dict['ms_level'] = 1
            elif int(frames_dict['MsMsType']) in MSMS_TYPE_CATEGORY['ms2']:
                framemsmsinfo_dict = [i for i in list_of_framemsmsinfo_dict if int(i['Frame']) == int(row['Frame'])][0]
                scan_dict['scan_type'] = 'MSn spectrum'
                scan_dict['ms_level'] = 2
                scan_dict['target_mz'] = framemsmsinfo_dict['TriggerMass']
                half_isolation_width = float(framemsmsinfo_dict['IsolationWidth']) / 2
                scan_dict['isolation_lower_offset'] = half_isolation_width
                scan_dict['isolation_upper_offset'] = half_isolation_width
                scan_dict['selected_ion_mz'] = framemsmsinfo_dict['TriggerMass']
                # no selected ion intensity
                # no selected ion mobility
                # no charge state
                scan_dict['collision_energy'] = framemsmsinfo_dict['CollisionEnergy']
                # no parent frame or scan

            list_of_scan_dicts.append(scan_dict)
    return list_of_scan_dicts


def parse_maldi_tdf(tdf_data, groupby, encoding, centroid):
    logging.info(get_timestamp() + ':' + 'Parsing MALDI-TIMS spectra...')
    list_of_frames_dict = tdf_data.frames.to_dict(orient='records')
    if tdf_data.framemsmsinfo is not None:
        list_of_framemsmsinfo_dict = tdf_data.framemsmsinfo.to_dict(orient='records')
    list_of_scan_dicts = []

    # force groupby frame for imaging. splitting up by scans adds too much dimensionality
    if tdf_data.meta_data['MaldiApplicationType'] == 'Imaging':
        groupby = 'frame'

    for index, row in tdf_data.maldiframeinfo.iterrows():
        frames_dict = [i for i in list_of_frames_dict if int(i['Id']) == int(row['Frame'])][0]
        if groupby == 'scan':
            for scan_num in range(0, int(frames_dict['NumScans']) + 1):
                scans = tdf_data.read_scans(int(row['Frame']), scan_num, scan_num + 1)
                if len(scans) == 1:
                    index_buf, intensity_array = scans[0]
                elif len(scans) != 1:
                    print('Too Many Scans.')
                    sys.exit(1)
                mz_array = tdf_data.index_to_mz(int(row['Frame']), index_buf)

                if mz_array.size != 0 and intensity_array.size != 0:
                    base_peak_index = np.where(intensity_array == np.max(intensity_array))

                    if tdf_data.meta_data['MaldiApplicationType'] == 'SingleSpectra':
                        coords = row['SpotName']
                    elif tdf_data.meta_data['MaldiApplicationType'] == 'Imaging':
                        coords = []
                        coords.append(int(row['XIndexPos']))
                        coords.append(int(row['YIndexPos']))
                        if 'ZIndexPos' in tdf_data.maldiframeinfo.columns:
                            coords.append(int(row['ZIndexPos']))
                        coords = tuple(coords)

                    scan_dict = {'scan_number': None,
                                 'mz_array': mz_array,
                                 'intensity_array': intensity_array,
                                 'coord': coords,
                                 'mobility': tdf_data.scan_num_to_oneoverk0(int(row['Frame']), np.array([scan_num]))[0],
                                 'polarity': frames_dict['Polarity'],
                                 'centroided': centroid,
                                 'retention_time': 0,
                                 'total_ion_current': sum(intensity_array),
                                 'base_peak_mz': mz_array[base_peak_index][0].astype(float),
                                 'base_peak_intensity': intensity_array[base_peak_index][0].astype(float),
                                 'high_mz': float(max(mz_array)),
                                 'low_mz': float(min(mz_array))}

                    if int(frames_dict['MsMsType']) in MSMS_TYPE_CATEGORY['ms1']:
                        scan_dict['scan_type'] = 'MS1 spectrum'
                        scan_dict['ms_level'] = 1
                    elif int(frames_dict['MsMsType']) in MSMS_TYPE_CATEGORY['ms2']:
                        framemsmsinfo_dict = [i for i in list_of_framemsmsinfo_dict
                                              if int(i['Frame']) == int(row['Frame'])][0]
                        scan_dict['scan_type'] = 'MSn spectrum'
                        scan_dict['ms_level'] = 2
                        scan_dict['target_mz'] = framemsmsinfo_dict['TriggerMass']
                        half_isolation_width = float(framemsmsinfo_dict['IsolationWidth']) / 2
                        scan_dict['isolation_lower_offset'] = half_isolation_width
                        scan_dict['isolation_upper_offset'] = half_isolation_width
                        scan_dict['selected_ion_mz'] = framemsmsinfo_dict['TriggerMass']
                        # no selected ion intensity
                        # no selected ion mobility
                        # no charge state
                        scan_dict['collision_energy'] = framemsmsinfo_dict['CollisionEnergy']
                        # no parent frame or scan

                    list_of_scan_dicts.append(scan_dict)

        elif groupby == 'frame':
            mz_array, intensity_array = tdf_data.extract_centroided_spectrum_for_frame_v2(int(row['Frame']),
                                                                                          int(frames_dict['NumScans']),
                                                                                          encoding)

            if mz_array.size != 0 and intensity_array.size != 0:
                base_peak_index = np.where(intensity_array == np.max(intensity_array))

                if tdf_data.meta_data['MaldiApplicationType'] == 'SingleSpectra':
                    coords = row['SpotName']
                elif tdf_data.meta_data['MaldiApplicationType'] == 'Imaging':
                    coords = []
                    coords.append(int(row['XIndexPos']))
                    coords.append(int(row['YIndexPos']))
                    if 'ZIndexPos' in tdf_data.maldiframeinfo.columns:
                        coords.append(int(row['ZIndexPos']))
                    coords = tuple(coords)

                scan_dict = {'scan_number': None,
                             'mz_array': mz_array,
                             'intensity_array': intensity_array,
                             'coord': coords,
                             'mobility_array': tdf_data.scan_num_to_oneoverk0(int(row['Frame']),
                                                                              np.array(list(range(1, int(frames_dict['NumScans'])+1)))),
                             'polarity': frames_dict['Polarity'],
                             'centroided': centroid,
                             'retention_time': 0,
                             'total_ion_current': sum(intensity_array),
                             'base_peak_mz': mz_array[base_peak_index][0].astype(float),
                             'base_peak_intensity': intensity_array[base_peak_index][0].astype(float),
                             'high_mz': float(max(mz_array)),
                             'low_mz': float(min(mz_array))}

                if int(frames_dict['MsMsType']) in MSMS_TYPE_CATEGORY['ms1']:
                    scan_dict['scan_type'] = 'MS1 spectrum'
                    scan_dict['ms_level'] = 1
                elif int(frames_dict['MsMsType']) in MSMS_TYPE_CATEGORY['ms2']:
                    framemsmsinfo_dict = [i for i in list_of_framemsmsinfo_dict
                                          if int(i['Frame']) == int(row['Frame'])][0]
                    scan_dict['scan_type'] = 'MSn spectrum'
                    scan_dict['ms_level'] = 2
                    scan_dict['target_mz'] = framemsmsinfo_dict['TriggerMass']
                    half_isolation_width = float(framemsmsinfo_dict['IsolationWidth']) / 2
                    scan_dict['isolation_lower_offset'] = half_isolation_width
                    scan_dict['isolation_upper_offset'] = half_isolation_width
                    scan_dict['selected_ion_mz'] = framemsmsinfo_dict['TriggerMass']
                    # no selected ion intensity
                    # no selected ion mobility
                    # no charge state
                    scan_dict['collision_energy'] = framemsmsinfo_dict['CollisionEnergy']
                    # no parent frame or scan

                list_of_scan_dicts.append(scan_dict)
    return list_of_scan_dicts


if __name__ == '__main__':
    logger = logging.getLogger(__name__)
