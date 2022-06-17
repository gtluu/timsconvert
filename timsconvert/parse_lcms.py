from timsconvert.constants import *
from timsconvert.init_bruker_dll import *
import numpy as np
import sys
import logging


# Get either quasi-profile or centroid spectrum.
def extract_lcms_baf_spectrum_arrays(baf_data, frame_dict, mode, profile_bins, encoding):
    if encoding == 32:
        encoding_dtype = np.float32
    elif encoding == 64:
        encoding_dtype = np.float64

    if mode == 'raw' or mode == 'centroid':
        mz_array = np.array(baf_data.read_array_double(frame_dict['LineMzId']), dtype=encoding_dtype)
        intensity_array = np.array(baf_data.read_array_double(frame_dict['LineIntensityId']), dtype=encoding_dtype)
        return mz_array, intensity_array
    elif mode == 'profile':
        mz_array = np.array(baf_data.read_array_double(frame_dict['ProfileMzId']), dtype=encoding_dtype)
        intensity_array = np.array(baf_data.read_array_double(frame_dict['ProfileIntensityId']),
                                   dtype=encoding_dtype)
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
def extract_lcms_tdf_spectrum_arrays(tdf_data, mode, multiscan, frame, scan_begin, scan_end, profile_bins, encoding):
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


def parse_lcms_baf(baf_data, frame_start, frame_stop, mode, ms2_only, profile_bins, encoding):
    if encoding == 32:
        encoding_dtype = np.float32
    elif encoding == 64:
        encoding_dtype = np.float64

    #if mode == 'raw':
    #    logging.info(get_timestamp() + ':' + 'TSF file detected. Only export in profile or centroid mode are '
    #                                         'supported. Defaulting to centroid mode.')

    #list_of_frames_dict = baf_data.frames.to_dict(orient='records')
    #list_of_acquisitionkeys_dict = baf_data.acquisitionkeys.to_dict(orient='records')
    list_of_parent_scans = []
    list_of_product_scans = []

    if mode == 'profile':
        centroided = False
    elif mode == 'centroid' or mode == 'raw':
        centroided = True

    for frame in range(frame_start, frame_stop):
        #frames_dict = [i for i in list_of_frames_dict if int(i['Id']) == frame][0]
        frames_dict = baf_data.frames[baf_data.frames['Id'] == frame].to_dict(orient='records')[0]
        #acquisitionkey_dict = [i for i in list_of_acquisitionkeys_dict
        #                       if int(i['Id'] == int(frames_dict['AcquisitionKey']))][0]
        acquisitionkey_dict = baf_data.acquisitionkeys[baf_data.acquisitionkeys['Id'] ==
                                                       frames_dict['AcquisitionKey']].to_dict(orient='records')[0]

        # Polarity == 0 -> 'positive'; Polarity == 1 -> 'negative"?
        if int(acquisitionkey_dict['Polarity']) == 0:
            polarity = '+'
        elif int(acquisitionkey_dict['Polarity']) == 1:
            polarity = '-'

        # AcquisitionKey: 1 == MS1, 2 == MS/MS; MsLevel == 0 -> 1, MsLevel == 1 -> 2
        if int(acquisitionkey_dict['MsLevel']) == 0:
            if ms2_only == False:
                mz_array, intensity_array = extract_lcms_baf_spectrum_arrays(baf_data, frames_dict, mode, profile_bins,
                                                                             encoding)

                if mz_array.size != 0 and intensity_array.size != 0 and mz_array.size == intensity_array.size:
                    base_peak_index = np.where(intensity_array == np.max(intensity_array))

                    scan_dict = {'scan_number': None,
                                 'scan_type': 'MS1 spectrum',
                                 'ms_level': 1,
                                 'mz_array': mz_array,
                                 'intensity_array': intensity_array,
                                 'polarity': polarity,
                                 'centroided': centroided,
                                 'retention_time': float(frames_dict['Rt']) / 60,
                                 'total_ion_current': sum(intensity_array),
                                 'base_peak_mz': mz_array[base_peak_index][0].astype(float),
                                 'base_peak_intensity': intensity_array[base_peak_index][0].astype(float),
                                 'high_mz': float(max(mz_array)),
                                 'low_mz': float(min(mz_array)),
                                 'frame': frame}
                    list_of_parent_scans.append(scan_dict)
        elif int(acquisitionkey_dict['MsLevel']) == 1:
            mz_array, intensity_array = extract_lcms_baf_spectrum_arrays(baf_data, frames_dict, mode, profile_bins,
                                                                         encoding)

            if mz_array.size != 0 and intensity_array.size != 0 and mz_array.size == intensity_array.size:
                steps_dict = baf_data.steps[baf_data.steps['TargetSpectrum'] == frame].to_dict(orient='records')[0]

                base_peak_index = np.where(intensity_array == np.max(intensity_array))
                isolation_width = float(baf_data.variables[(baf_data.variables['Spectrum'] == frame) &
                                  (baf_data.variables['Variable'] == 8)].to_dict(orient='records')[0]['Value'])

                scan_dict = {'scan_number': None,
                             'scan_type': 'MSn spectrum',
                             'ms_level': 2,
                             'mz_array': mz_array,
                             'intensity_array': intensity_array,
                             'polarity': polarity,
                             'centroided': centroided,
                             'retention_time': float(frames_dict['Rt']) / 60,
                             'total_ion_current': sum(intensity_array),
                             'base_peak_mz': mz_array[base_peak_index][0].astype(float),
                             'base_peak_intensity': intensity_array[base_peak_index][0].astype(float),
                             'high_mz': float(max(mz_array)),
                             'low_mz': float(min(mz_array)),
                             'target_mz': float(baf_data.variables[(baf_data.variables['Spectrum'] == frame) &
                                          (baf_data.variables['Variable'] == 7)].to_dict(orient='records')[0]['Value']),
                             'isolation_lower_offset': isolation_width / 2,
                             'isolation_upper_offset': isolation_width / 2,
                             'selected_ion_mz': float(steps_dict['Mass']),
                             'charge_state': baf_data.variables[(baf_data.variables['Spectrum'] == frame) &
                                                                (baf_data.variables['Variable'] ==
                                                                 6)].to_dict(orient='records')[0]['Value'],
                             'collision_energy': baf_data.variables[(baf_data.variables['Spectrum'] == frame) &
                                                                    (baf_data.variables['Variable'] ==
                                                                     5)].to_dict(orient='records')[0]['Value'],
                             'parent_frame': int(frames_dict['Parent'])}
                list_of_product_scans.append(scan_dict)
    return list_of_parent_scans, list_of_product_scans


# Parse chunks of LC-TIMS-MS(/MS) data from Bruker TDF files.
def parse_lcms_tdf(tdf_data, frame_start, frame_stop, mode, ms2_only, exclude_mobility, profile_bins, encoding):
    if encoding == 32:
        encoding_dtype = np.float32
    elif encoding == 64:
        encoding_dtype = np.float64

    # list_of_frames_dict = tdf_data.frames.to_dict(orient='records')
    # if tdf_data.pasefframemsmsinfo is not None:
    #    list_of_pasefframemsmsinfo_dict = tdf_data.pasefframemsmsinfo.to_dict(orient='records')
    # if tdf_data.precursors is not None:
    #    list_of_precursors_dict = tdf_data.precursors.to_dict(orient='records')
    list_of_parent_scans = []
    list_of_product_scans = []

    if mode == 'profile':
        centroided = False
        exclude_mobility = True
    elif mode == 'centroid' or mode == 'raw':
        centroided = True

    for frame in range(frame_start, frame_stop):
        # frames_dict = [i for i in list_of_frames_dict if int(i['Id']) == frame][0]
        frames_dict = tdf_data.frames[tdf_data.frames['Id'] == frame].to_dict(orient='records')[0]

        if int(frames_dict['MsMsType']) in MSMS_TYPE_CATEGORY['ms1']:
            if ms2_only == False:
                if exclude_mobility == False:
                    frame_mz_arrays = []
                    frame_intensity_arrays = []
                    frame_mobility_arrays = []
                    for scan_num in range(0, int(frames_dict['NumScans'])):
                        mz_array, intensity_array = extract_lcms_tdf_spectrum_arrays(tdf_data,
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
                                     'polarity': frames_dict['Polarity'],
                                     'centroided': centroided,
                                     'retention_time': float(frames_dict['Time']) / 60,
                                     'total_ion_current': sum(frames_array[:, 1]),
                                     'base_peak_mz': frames_array[:, 0][base_peak_index][0].astype(float),
                                     'base_peak_intensity': frames_array[:, 1][base_peak_index][0].astype(float),
                                     'high_mz': float(max(frames_array[:, 0])),
                                     'low_mz': float(min(frames_array[:, 0])),
                                     'frame': frame}
                        list_of_parent_scans.append(scan_dict)
                elif exclude_mobility == True:
                    mz_array, intensity_array = extract_lcms_tdf_spectrum_arrays(tdf_data,
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
                                     'polarity': frames_dict['Polarity'],
                                     'centroided': centroided,
                                     'retention_time': float(frames_dict['Time']) / 60,
                                     'total_ion_current': sum(intensity_array),
                                     'base_peak_mz': mz_array[base_peak_index][0].astype(float),
                                     'base_peak_intensity': intensity_array[base_peak_index][0].astype(float),
                                     'high_mz': float(max(mz_array)),
                                     'low_mz': float(min(mz_array)),
                                     'frame': frame}
                        list_of_parent_scans.append(scan_dict)
            if frame_stop - frame_start > 1:
                # precursor_dicts = [i for i in list_of_precursors_dict if int(i['Parent']) == frame]
                precursor_dicts = tdf_data.precursors[tdf_data.precursors['Parent'] ==
                                                      frame].to_dict(orient='records')
                for precursor_dict in precursor_dicts:
                    # pasefframemsmsinfo_dicts = [i for i in list_of_pasefframemsmsinfo_dict
                    #                            if int(i['Precursor']) == int(precursor_dict['Id'])]
                    pasefframemsmsinfo_dicts = tdf_data.pasefframemsmsinfo[tdf_data.pasefframemsmsinfo['Precursor'] ==
                                                                           precursor_dict['Id']].to_dict(
                        orient='records')
                    pasef_mz_arrays = []
                    pasef_intensity_arrays = []
                    for pasef_dict in pasefframemsmsinfo_dicts:
                        scan_begin = int(pasef_dict['ScanNumBegin'])
                        scan_end = int(pasef_dict['ScanNumEnd'])
                        mz_array, intensity_array = extract_lcms_tdf_spectrum_arrays(tdf_data,
                                                                                     mode,
                                                                                     True,
                                                                                     int(pasef_dict['Frame']),
                                                                                     scan_begin,
                                                                                     scan_end,
                                                                                     profile_bins,
                                                                                     encoding)
                        if mz_array.size != 0 and intensity_array.size != 0 and mz_array.size == intensity_array.size:
                            pasef_mz_arrays.append(mz_array)
                            pasef_intensity_arrays.append(intensity_array)
                    if pasef_mz_arrays and pasef_intensity_arrays:
                        pasef_array = np.stack((np.concatenate(pasef_mz_arrays, axis=None),
                                                np.concatenate(pasef_intensity_arrays, axis=None)),
                                               axis=-1)
                        pasef_array = np.unique(pasef_array[np.argsort(pasef_array[:, 0])], axis=0)

                        mz_acq_range_lower = float(tdf_data.meta_data['MzAcqRangeLower'])
                        mz_acq_range_upper = float(tdf_data.meta_data['MzAcqRangeUpper'])
                        bin_size = 0.005
                        bins = np.arange(mz_acq_range_lower, mz_acq_range_upper, bin_size, dtype=encoding_dtype)

                        unique_indices, inverse_indices = np.unique(np.digitize(pasef_array[:, 0], bins),
                                                                    return_inverse=True)
                        bin_counts = np.bincount(inverse_indices)
                        np.place(bin_counts, bin_counts < 1, [1])

                        mz_array = np.bincount(inverse_indices, weights=pasef_array[:, 0]) / bin_counts
                        intensity_array = np.bincount(inverse_indices, weights=pasef_array[:, 1])

                        base_peak_index = np.where(intensity_array == np.max(intensity_array))

                        scan_dict = {'scan_number': None,
                                     'scan_type': 'MSn spectrum',
                                     'ms_level': 2,
                                     'mz_array': mz_array,
                                     'intensity_array': intensity_array,
                                     'mobility': None,
                                     'mobility_array': None,
                                     'polarity': frames_dict['Polarity'],
                                     'centroided': centroided,
                                     'retention_time': float(frames_dict['Time']) / 60,
                                     'total_ion_current': sum(intensity_array),
                                     'base_peak_mz': mz_array[base_peak_index][0].astype(float),
                                     'base_peak_intensity': intensity_array[base_peak_index][0].astype(float),
                                     'high_mz': float(max(mz_array)),
                                     'low_mz': float(min(mz_array)),
                                     'target_mz': float(precursor_dict['AverageMz']),
                                     'isolation_lower_offset': float(pasefframemsmsinfo_dicts[0]['IsolationWidth']) / 2,
                                     'isolation_upper_offset': float(pasefframemsmsinfo_dicts[0]['IsolationWidth']) / 2,
                                     'selected_ion_mz': float(precursor_dict['LargestPeakMz']),
                                     'selected_ion_intensity': float(precursor_dict['Intensity']),
                                     'selected_ion_mobility':
                                         tdf_data.scan_num_to_oneoverk0(int(precursor_dict['Parent']),
                                         np.array([int(precursor_dict['ScanNumber'])]))[0],
                                     'charge_state': precursor_dict['Charge'],
                                     'collision_energy': pasefframemsmsinfo_dicts[0]['CollisionEnergy'],
                                     'parent_frame': int(precursor_dict['Parent']),
                                     'parent_scan': int(precursor_dict['ScanNumber'])}
                        if not np.isnan(precursor_dict['Charge']):
                            scan_dict['selected_ion_ccs'] = one_over_k0_to_ccs(scan_dict['selected_ion_mobility'],
                                                                               int(precursor_dict['Charge']),
                                                                               float(precursor_dict['LargestPeakMz']))
                        list_of_product_scans.append(scan_dict)
    return list_of_parent_scans, list_of_product_scans
