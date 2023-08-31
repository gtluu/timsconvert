from timsconvert.constants import *
from timsconvert.init_bruker_dll import *
import numpy as np
import pandas as pd
import sys
import logging


def get_encoding_dtype(encoding):
    if encoding == 32:
        return np.float32
    elif encoding == 64:
        return np.float64


def get_centroid_status(mode, exclude_mobility=None):
    if mode == 'profile':
        centroided = False
        exclude_mobility = True
    elif mode == 'centroid' or mode == 'raw':
        centroided = True
    return centroided, exclude_mobility


def get_baf_spectrum_polarity(acquisitionkey_dict):
    # Polarity == 0 -> 'positive'; Polarity == 1 -> 'negative"?
    if int(acquisitionkey_dict['Polarity']) == 0:
        polarity = '+'
    elif int(acquisitionkey_dict['Polarity']) == 1:
        polarity = '-'
    return polarity


def get_maldi_coords(data, maldiframeinfo_dict):
    if data.meta_data['MaldiApplicationType'] == 'SingleSpectra':
        coords = maldiframeinfo_dict['SpotName']
    elif data.meta_data['MaldiApplicationType'] == 'Imaging':
        coords = [int(maldiframeinfo_dict['XIndexPos']), int(maldiframeinfo_dict['YIndexPos'])]
        if 'ZIndexPos' in data.maldiframeinfo.columns:
            coords.append(int(maldiframeinfo_dict['ZIndexPos']))
        coords = tuple(coords)
    return coords


def init_scan_dict():
    return {'scan_number': None,
            'scan_type': None,
            'ms_level': None,
            'mz_array': None,
            'intensity_array': None,
            'mobility_array': None,
            'polarity': None,
            'centroided': None,
            'retention_time': None,
            'coord': None,
            'total_ion_current': None,
            'base_peak_mz': None,
            'base_peak_intensity': None,
            'high_mz': None,
            'low_mz': None,
            'target_mz': None,
            'isolation_lower_offset': None,
            'isolation_upper_offset': None,
            'selected_ion_mz': None,
            'selected_ion_intensity': None,
            'selected_ion_mobility': None,
            'selected_ion_ccs': None,
            'charge_state': None,
            'collision_energy': None,
            'frame': None,
            'parent_frame': None,
            'parent_scan': None,
            'ms2_no_precursor': False}


def populate_scan_dict_w_baf_metadata(scan_dict, frames_dict, acquisitionkey_dict, mode):
    scan_dict['polarity'] = get_baf_spectrum_polarity(acquisitionkey_dict)
    scan_dict['centroided'] = get_centroid_status(mode)[0]
    scan_dict['retention_time'] = float(frames_dict['Rt']) / 60
    return scan_dict


def populate_scan_dict_w_spectrum_data(scan_dict, mz_array, intensity_array):
    scan_dict['mz_array'] = mz_array
    scan_dict['intensity_array'] = intensity_array
    scan_dict['total_ion_current'] = sum(intensity_array)
    base_peak_index = np.where(intensity_array == np.max(intensity_array))
    scan_dict['base_peak_mz'] = mz_array[base_peak_index][0].astype(float)
    scan_dict['base_peak_intensity'] = intensity_array[base_peak_index][0].astype(float)
    scan_dict['high_mz'] = float(max(mz_array))
    scan_dict['low_mz'] = float(min(mz_array))
    return scan_dict


def populate_scan_dict_w_ms1(scan_dict, frame):
    scan_dict['scan_type'] = 'MS1 spectrum'
    scan_dict['ms_level'] = 1
    scan_dict['frame'] = frame
    return scan_dict


def populate_scan_dict_w_bbcid_iscid_ms2(scan_dict, frame, schema,  baf_data=None, framemsmsinfo_dict=None):
    scan_dict['scan_type'] = 'MSn spectrum'
    scan_dict['ms_level'] = 2
    if schema == 'TSF' or schema == 'TDF':
        scan_dict['collision_energy'] = float(framemsmsinfo_dict['CollisionEnergy'])
    elif schema == 'BAF':
        scan_dict['collision_energy'] = float(baf_data.variables[(baf_data.variables['Spectrum'] == frame) &
                                                                 (baf_data.variables['Variable'] ==
                                                                  5)].to_dict(orient='records')[0]['Value'])
    scan_dict['frame'] = frame
    scan_dict['ms2_no_precursor'] = True
    return scan_dict


def populate_scan_dict_w_baf_ms2(scan_dict, baf_data, frames_dict, frame):
    scan_dict['scan_type'] = 'MSn spectrum'
    scan_dict['ms_level'] = 2
    scan_dict['target_mz'] = float(baf_data.variables[(baf_data.variables['Spectrum'] == frame) &
                                   (baf_data.variables['Variable'] == 7)].to_dict(orient='records')[0]['Value'])
    isolation_width = float(baf_data.variables[(baf_data.variables['Spectrum'] == frame) &
                                               (baf_data.variables['Variable'] == 8)].to_dict(orient='records')[0][
                                'Value'])
    scan_dict['isolation_lower_offset'] = isolation_width / 2
    scan_dict['isolation_upper_offset'] = isolation_width / 2
    steps_dict = baf_data.steps[baf_data.steps['TargetSpectrum'] == frame].to_dict(orient='records')[0]
    scan_dict['selected_ion_mz'] = float(steps_dict['Mass'])
    scan_dict['charge_state'] = baf_data.variables[(baf_data.variables['Spectrum'] == frame) &
                                                   (baf_data.variables['Variable'] ==
                                                    6)].to_dict(orient='records')[0]['Value']
    scan_dict['collision_energy'] = baf_data.variables[(baf_data.variables['Spectrum'] == frame) &
                                                       (baf_data.variables['Variable'] ==
                                                        5)].to_dict(orient='records')[0]['Value']
    scan_dict['parent_frame'] = int(frames_dict['Parent'])
    return scan_dict


def populate_scan_dict_w_lcms_tsf_tdf_metadata(scan_dict, frames_dict, mode, exclude_mobility=None):
    scan_dict['polarity'] = frames_dict['Polarity']
    scan_dict['centroided'] = get_centroid_status(mode, exclude_mobility)[0]
    # For ddaPASEF, parent frame RT is used because a precursor spectrum is collected over multiple scans.
    scan_dict['retention_time'] = float(frames_dict['Time']) / 60
    return scan_dict


def populate_scan_dict_w_ddapasef_ms2(scan_dict, tdf_data, precursor_dict, pasefframemsmsinfo_dicts):
    scan_dict['scan_type'] = 'MSn spectrum'
    scan_dict['ms_level'] = 2
    scan_dict['target_mz'] = float(precursor_dict['AverageMz'])
    scan_dict['isolation_lower_offset'] = float(pasefframemsmsinfo_dicts[0]['IsolationWidth']) / 2
    scan_dict['isolation_upper_offset'] = float(pasefframemsmsinfo_dicts[0]['IsolationWidth']) / 2
    scan_dict['selected_ion_mz'] = float(precursor_dict['LargestPeakMz'])
    scan_dict['selected_ion_intensity'] = float(precursor_dict['Intensity'])
    scan_dict['selected_ion_mobility'] = tdf_data.scan_num_to_oneoverk0(int(precursor_dict['Parent']),
                                         np.array([int(precursor_dict['ScanNumber'])]))[0]
    scan_dict['charge_state'] = precursor_dict['Charge']
    scan_dict['collision_energy'] = pasefframemsmsinfo_dicts[0]['CollisionEnergy']
    scan_dict['parent_frame'] = int(precursor_dict['Parent'])
    scan_dict['parent_scan'] = int(precursor_dict['ScanNumber'])
    if not np.isnan(precursor_dict['Charge']):
        scan_dict['selected_ion_ccs'] = one_over_k0_to_ccs(scan_dict['selected_ion_mobility'],
                                                           int(precursor_dict['Charge']),
                                                           float(precursor_dict['LargestPeakMz']))
    return scan_dict


def populate_scan_dict_w_diapasef_ms2(scan_dict, diaframemsmswindows_dict):
    scan_dict['scan_type'] = 'MSn spectrum'
    scan_dict['ms_level'] = 2
    scan_dict['target_mz'] = float(diaframemsmswindows_dict['IsolationMz'])
    scan_dict['isolation_lower_offset'] = float(diaframemsmswindows_dict['IsolationWidth']) / 2
    scan_dict['isolation_upper_offset'] = float(diaframemsmswindows_dict['IsolationWidth']) / 2
    scan_dict['selected_ion_mz'] = float(diaframemsmswindows_dict['IsolationMz'])
    scan_dict['collision_energy'] = diaframemsmswindows_dict['CollisionEnergy']
    return scan_dict


def populate_scan_dict_w_prmpasef_ms2(scan_dict, prmframemsmsinfo_dict, prmtargets_dict):
    scan_dict['scan_type'] = 'MSn spectrum'
    scan_dict['ms_level'] = 2
    scan_dict['target_mz'] = float(prmframemsmsinfo_dict['IsolationMz'])
    scan_dict['isolation_lower_offset'] = float(prmframemsmsinfo_dict['IsolationWidth']) / 2
    scan_dict['isolation_upper_offset'] = float(prmframemsmsinfo_dict['IsolationWidth']) / 2
    scan_dict['selected_ion_mz'] = float(prmframemsmsinfo_dict['IsolationMz'])
    scan_dict['selected_ion_mobility'] = float(prmtargets_dict['OneOverK0'])
    scan_dict['charge_state'] = prmtargets_dict['Charge']
    scan_dict['collision_energy'] = prmframemsmsinfo_dict['CollisionEnergy']
    if not np.isnan(prmtargets_dict['Charge']):
        scan_dict['selected_ion_ccs'] = one_over_k0_to_ccs(scan_dict['selected_ion_mobility'],
                                                           int(prmtargets_dict['Charge']),
                                                           float(prmframemsmsinfo_dict['IsolationMz']))
    return scan_dict


def populate_scan_dict_w_maldi_metadata(scan_dict, data, frames_dict, maldiframeinfo_dict, frame, mode):
    scan_dict['coord'] = get_maldi_coords(data, maldiframeinfo_dict)
    scan_dict['polarity'] = frames_dict['Polarity']
    scan_dict['centroided'] = get_centroid_status(mode)[0]
    scan_dict['retention_time'] = 0
    scan_dict['frame'] = frame
    return scan_dict


def populate_scan_dict_w_tsf_ms2(scan_dict, framemsmsinfo_dict, lcms=False):
    scan_dict['scan_type'] = 'MSn spectrum'
    scan_dict['ms_level'] = 2
    scan_dict['target_mz'] = float(framemsmsinfo_dict['TriggerMass'])
    scan_dict['isolation_lower_offset'] = float(framemsmsinfo_dict['IsolationWidth']) / 2
    scan_dict['isolation_upper_offset'] = float(framemsmsinfo_dict['IsolationWidth']) / 2
    scan_dict['selected_ion_mz'] = float(framemsmsinfo_dict['TriggerMass'])
    scan_dict['charge_state'] = framemsmsinfo_dict['PrecursorCharge']
    scan_dict['collision_energy'] = framemsmsinfo_dict['CollisionEnergy']
    if lcms:
        scan_dict['parent_frame'] = int(framemsmsinfo_dict['Parent'])
    return scan_dict


def bin_profile_spectrum(mz_array, intensity_array, profile_bins, encoding):
    mz_acq_range_lower = float(mz_array[0])
    mz_acq_range_upper = float(mz_array[-1])
    bins = np.linspace(mz_acq_range_lower, mz_acq_range_upper, profile_bins, dtype=get_encoding_dtype(encoding))
    unique_indices, inverse_indices = np.unique(np.digitize(mz_array, bins), return_inverse=True)
    bin_counts = np.bincount(inverse_indices)
    np.place(bin_counts, bin_counts < 1, [1])
    mz_array = np.bincount(inverse_indices, weights=mz_array) / bin_counts
    intensity_array = np.bincount(inverse_indices, weights=intensity_array)
    return mz_array, intensity_array


# Get either quasi-profile or centroid spectrum.
def extract_baf_spectrum(baf_data, frame_dict, mode, profile_bins, encoding):
    if mode == 'raw' or mode == 'centroid':
        mz_array = np.array(baf_data.read_array_double(frame_dict['LineMzId']), dtype=get_encoding_dtype(encoding))
        intensity_array = np.array(baf_data.read_array_double(frame_dict['LineIntensityId']),
                                   dtype=get_encoding_dtype(encoding))
    elif mode == 'profile':
        mz_array = np.array(baf_data.read_array_double(frame_dict['ProfileMzId']), dtype=get_encoding_dtype(encoding))
        intensity_array = np.array(baf_data.read_array_double(frame_dict['ProfileIntensityId']),
                                   dtype=get_encoding_dtype(encoding))
        if profile_bins != 0:
            mz_array, intensity_array = bin_profile_spectrum(mz_array, intensity_array, profile_bins, encoding)
    return mz_array, intensity_array


# Get either quasi-profile or centroid spectrum.
# Returns an m/z array and intensity array.
def extract_tsf_spectrum(tsf_data, mode, frame, profile_bins, encoding):
    if mode == 'raw' or mode == 'centroid':
        index_buf, intensity_array = tsf_data.read_line_spectrum(frame)
        mz_array = tsf_data.index_to_mz(frame, index_buf)
    elif mode == 'profile':
        index_buf, intensity_array = tsf_data.read_profile_spectrum(frame)
        intensity_array = np.array(intensity_array, dtype=get_encoding_dtype(encoding))
        mz_array = tsf_data.index_to_mz(frame, index_buf)
        if profile_bins != 0:
            mz_array, intensity_array = bin_profile_spectrum(mz_array, intensity_array, profile_bins, encoding)
    return mz_array, intensity_array


# Get either raw (slightly modified implementation that gets centroid spectrum), quasi-profile, or centroid spectrum.
# Returns an m/z array and intensity array.
def extract_2d_tdf_spectrum(tdf_data, mode, frame, scan_begin, scan_end, profile_bins, encoding):
    if mode == 'raw':
        list_of_scans = tdf_data.read_scans(frame, scan_begin, scan_end)  # tuple (index_array, intensity_array)
        frame_mz_arrays = []
        frame_intensity_arrays = []
        for scan_num in range(scan_begin, scan_end):
            if list_of_scans[scan_num][0].size != 0 \
                    and list_of_scans[scan_num][1].size != 0 \
                    and list_of_scans[scan_num][0].size == list_of_scans[scan_num][1].size:
                mz_array = tdf_data.index_to_mz(frame, list_of_scans[scan_num][0])
                intensity_array = list_of_scans[scan_num][1]
                frame_mz_arrays.append(mz_array)
                frame_intensity_arrays.append(intensity_array)
        if frame_mz_arrays and frame_intensity_arrays:
            frames_array = np.stack((np.concatenate(frame_mz_arrays, axis=None),
                                     np.concatenate(frame_intensity_arrays, axis=None)),
                                    axis=-1)
            frames_array = np.unique(frames_array[np.argsort(frames_array[:, 0])], axis=0)
            mz_array = frames_array[:, 0]
            intensity_array = frames_array[:, 1]
            return mz_array, intensity_array
        else:
            return None, None
    elif mode == 'profile':
        index_buf, intensity_array = tdf_data.extract_profile_spectrum_for_frame(frame, scan_begin, scan_end)
        intensity_array = np.array(intensity_array, dtype=get_encoding_dtype(encoding))
        mz_array = tdf_data.index_to_mz(frame, index_buf)
        if profile_bins != 0:
            mz_array, intensity_array = bin_profile_spectrum(mz_array, intensity_array, profile_bins, encoding)
    elif mode == 'centroid':
        mz_array, intensity_array = tdf_data.extract_centroided_spectrum_for_frame(frame, scan_begin, scan_end)
        mz_array = np.array(mz_array, dtype=get_encoding_dtype(encoding))
        intensity_array = np.array(intensity_array, dtype=get_encoding_dtype(encoding))
    return mz_array, intensity_array


def extract_3d_tdf_spectrum(tdf_data, mode, frame, scan_begin, scan_end, profile_bins, encoding):
    list_of_scans = tdf_data.read_scans(frame, scan_begin, scan_end)  # tuple (index_array, intensity_array)
    frame_mz_arrays = []
    frame_intensity_arrays = []
    frame_mobility_arrays = []
    if scan_begin != 0:
        scan_end = scan_end - scan_begin
        scan_begin = 0
    for scan_num in range(scan_begin, scan_end):
        if list_of_scans[scan_num][0].size != 0 \
                and list_of_scans[scan_num][1].size != 0 \
                and list_of_scans[scan_num][0].size == list_of_scans[scan_num][1].size:
            mz_array = tdf_data.index_to_mz(frame, list_of_scans[scan_num][0])
            intensity_array = list_of_scans[scan_num][1]
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
        mz_array = frames_array[:, 0]
        intensity_array = frames_array[:, 1]
        mobility_array = frames_array[:, 2]
        return mz_array, intensity_array, mobility_array
    else:
        return None, None, None


def extract_ddapasef_precursor_spectrum(tdf_data, pasefframemsmsinfo_dicts, mode, profile_bins, encoding):
    pasef_mz_arrays = []
    pasef_intensity_arrays = []
    for pasef_dict in pasefframemsmsinfo_dicts:
        scan_begin = int(pasef_dict['ScanNumBegin'])
        scan_end = int(pasef_dict['ScanNumEnd'])
        mz_array, intensity_array = extract_2d_tdf_spectrum(tdf_data,
                                                            mode,
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
        bins = np.arange(mz_acq_range_lower, mz_acq_range_upper, bin_size,
                         dtype=get_encoding_dtype(encoding))

        unique_indices, inverse_indices = np.unique(np.digitize(pasef_array[:, 0], bins),
                                                    return_inverse=True)
        bin_counts = np.bincount(inverse_indices)
        np.place(bin_counts, bin_counts < 1, [1])

        mz_array = np.bincount(inverse_indices, weights=pasef_array[:, 0]) / bin_counts
        intensity_array = np.bincount(inverse_indices, weights=pasef_array[:, 1])
        return mz_array, intensity_array
    else:
        return None, None


# Parse chunks of LC-MS(/MS) data from Bruker BAF files acquired in Auto MS/MS mode in otofControl.
def parse_lcms_baf(baf_data, frame_start, frame_stop, mode, ms2_only, profile_bins, encoding):
    list_of_parent_scans = []
    list_of_product_scans = []

    for frame in range(frame_start, frame_stop):
        scan_dict = init_scan_dict()
        frames_dict = baf_data.frames[baf_data.frames['Id'] == frame].to_dict(orient='records')[0]
        acquisitionkey_dict = baf_data.acquisitionkeys[baf_data.acquisitionkeys['Id'] ==
                                                       frames_dict['AcquisitionKey']].to_dict(orient='records')[0]
        scan_dict = populate_scan_dict_w_baf_metadata(scan_dict, frames_dict, acquisitionkey_dict, mode)

        mz_array, intensity_array = extract_baf_spectrum(baf_data, frames_dict, mode, profile_bins, encoding)
        if mz_array.size != 0 and intensity_array.size != 0 and mz_array.size == intensity_array.size:
            scan_dict = populate_scan_dict_w_spectrum_data(scan_dict, mz_array, intensity_array)
            # MS1
            if int(acquisitionkey_dict['ScanMode']) == 0 and not ms2_only:
                scan_dict = populate_scan_dict_w_ms1(scan_dict, frame)
                list_of_parent_scans.append(scan_dict)
            # Auto MS/MS and MRM MS/MS
            elif int(acquisitionkey_dict['ScanMode']) == 2:
                scan_dict = populate_scan_dict_w_baf_ms2(scan_dict, baf_data, frames_dict, frame)
                list_of_product_scans.append(scan_dict)
            # isCID MS/MS
            elif int(acquisitionkey_dict['ScanMode']) == 4:
                scan_dict = populate_scan_dict_w_bbcid_iscid_ms2(scan_dict, frame, 'BAF', baf_data=baf_data)
                list_of_parent_scans.append(scan_dict)
            # bbCID MS/MS
            elif int(acquisitionkey_dict['ScanMode']) == 5:
                scan_dict = populate_scan_dict_w_bbcid_iscid_ms2(scan_dict, frame, 'BAF', baf_data=baf_data)
                list_of_parent_scans.append(scan_dict)
    return list_of_parent_scans, list_of_product_scans


# Parse chunks of LC-MS(/MS) data from Bruker TSF files acquired in Auto MS/MS mode in timsControl.
def parse_lcms_tsf(tsf_data, frame_start, frame_stop, mode, ms2_only, profile_bins, encoding):
    list_of_parent_scans = []
    list_of_product_scans = []

    for frame in range(frame_start, frame_stop):
        scan_dict = init_scan_dict()
        frames_dict = tsf_data.frames[tsf_data.frames['Id'] == frame].to_dict(orient='records')[0]
        scan_dict = populate_scan_dict_w_lcms_tsf_tdf_metadata(scan_dict, frames_dict, mode, exclude_mobility=None)

        mz_array, intensity_array = extract_tsf_spectrum(tsf_data, mode, frame, profile_bins, encoding)
        if mz_array.size != 0 and intensity_array.size != 0 and mz_array.size == intensity_array.size:
            scan_dict = populate_scan_dict_w_spectrum_data(scan_dict, mz_array, intensity_array)
            if int(frames_dict['MsMsType']) in MSMS_TYPE_CATEGORY['ms1'] and not ms2_only:
                scan_dict = populate_scan_dict_w_ms1(scan_dict, frame)
                list_of_parent_scans.append(scan_dict)
            elif int(frames_dict['MsMsType']) in MSMS_TYPE_CATEGORY['ms2']:
                framemsmsinfo_dict = tsf_data.framemsmsinfo[tsf_data.framemsmsinfo['Frame'] ==
                                                            frame].to_dict(orient='records')[0]
                if int(frames_dict['ScanMode']) == 1:
                    scan_dict = populate_scan_dict_w_tsf_ms2(scan_dict, framemsmsinfo_dict, lcms=True)
                    list_of_product_scans.append(scan_dict)
                elif int(frames_dict['ScanMode']) == 4:
                    scan_dict = populate_scan_dict_w_bbcid_iscid_ms2(scan_dict,
                                                                     frame,
                                                                     'TSF',
                                                                     framemsmsinfo_dict=framemsmsinfo_dict)
                    list_of_parent_scans.append(scan_dict)
                elif int(frames_dict['ScanMode']) == 2:
                    scan_dict = populate_scan_dict_w_tsf_ms2(scan_dict, framemsmsinfo_dict)
                    list_of_parent_scans.append(scan_dict)
    return list_of_parent_scans, list_of_product_scans


# Parse chunks of LC-TIMS-MS(/MS) data from Bruker TDF files acquired in ddaPASEF mode acquired in timsControl.
def parse_lcms_tdf(tdf_data, frame_start, frame_stop, mode, ms2_only, exclude_mobility, profile_bins, encoding):
    list_of_parent_scans = []
    list_of_product_scans = []
    exclude_mobility = get_centroid_status(mode, exclude_mobility)[1]

    # Frame start and frame stop will only be MS1 frames; MS2 frames cannot be used as frame_start and frame_stop.
    for frame in range(frame_start, frame_stop):
        # Parse MS1 frame(s).
        frames_dict = tdf_data.frames[tdf_data.frames['Id'] == frame].to_dict(orient='records')[0]

        if int(frames_dict['MsMsType']) in MSMS_TYPE_CATEGORY['ms1'] and not ms2_only:
            scan_dict = init_scan_dict()
            scan_dict = populate_scan_dict_w_lcms_tsf_tdf_metadata(scan_dict, frames_dict, mode, exclude_mobility)
            scan_dict = populate_scan_dict_w_ms1(scan_dict, frame)
            if not exclude_mobility:
                mz_array, intensity_array, mobility_array = extract_3d_tdf_spectrum(tdf_data,
                                                                                    mode,
                                                                                    frame,
                                                                                    0,
                                                                                    int(frames_dict['NumScans']),
                                                                                    profile_bins,
                                                                                    encoding)
            elif exclude_mobility:
                mz_array, intensity_array = extract_2d_tdf_spectrum(tdf_data,
                                                                    mode,
                                                                    frame,
                                                                    0,
                                                                    int(frames_dict['NumScans']),
                                                                    profile_bins,
                                                                    encoding)
            if mz_array.size != 0 \
                    and intensity_array.size != 0 \
                    and mz_array.size == intensity_array.size \
                    and mz_array is not None \
                    and intensity_array is not None:
                scan_dict = populate_scan_dict_w_spectrum_data(scan_dict, mz_array, intensity_array)
                if not exclude_mobility and mobility_array.size != 0 and mobility_array is not None:
                    scan_dict['mobility_array'] = mobility_array
                list_of_parent_scans.append(scan_dict)

            # This block only runs if frame_stop - frame_start > 1, meaning MS/MS scans are detected.
            if frame_stop - frame_start > 1:
                # Parse frames with ddaPASEF spectra for precursors.
                if int(frames_dict['ScanMode']) == 8 and int(frames_dict['MsMsType']) == 0:
                    precursor_dicts = tdf_data.precursors[tdf_data.precursors['Parent'] == frame].to_dict(orient='records')
                    for precursor_dict in precursor_dicts:
                        scan_dict = init_scan_dict()
                        scan_dict = populate_scan_dict_w_lcms_tsf_tdf_metadata(scan_dict,
                                                                               frames_dict,
                                                                               mode,
                                                                               exclude_mobility)
                        pasefframemsmsinfo_dicts = tdf_data.pasefframemsmsinfo[tdf_data.pasefframemsmsinfo['Precursor'] ==
                                                                            precursor_dict['Id']].to_dict(orient='records')
                        mz_array, intensity_array = extract_ddapasef_precursor_spectrum(tdf_data,
                                                                                        pasefframemsmsinfo_dicts,
                                                                                        mode,
                                                                                        profile_bins,
                                                                                        encoding)
                        if mz_array is not None and intensity_array is not None:
                            scan_dict = populate_scan_dict_w_ddapasef_ms2(scan_dict,
                                                                          tdf_data,
                                                                          precursor_dict,
                                                                          pasefframemsmsinfo_dicts)
                            scan_dict = populate_scan_dict_w_spectrum_data(scan_dict, mz_array, intensity_array)
                            list_of_product_scans.append(scan_dict)
        # Parse frames with diaPASEF spectra.
        elif int(frames_dict['ScanMode']) == 9 and int(frames_dict['MsMsType']) == 9:
            diaframemsmsinfo_dict = tdf_data.diaframemsmsinfo[tdf_data.diaframemsmsinfo['Frame'] ==
                                                              frame].to_dict(orient='records')[0]
            diaframemsmswindows_dicts = tdf_data.diaframemsmswindows[tdf_data.diaframemsmswindows['WindowGroup'] ==
                                        diaframemsmsinfo_dict['WindowGroup']].to_dict(orient='records')

            for diaframemsmswindows_dict in diaframemsmswindows_dicts:
                scan_dict = init_scan_dict()
                scan_dict = populate_scan_dict_w_lcms_tsf_tdf_metadata(scan_dict,
                                                                       frames_dict,
                                                                       mode,
                                                                       exclude_mobility)

                if not exclude_mobility:
                    mz_array, intensity_array, mobility_array = extract_3d_tdf_spectrum(tdf_data,
                                                                                        mode,
                                                                                        frame,
                                                                                        int(diaframemsmswindows_dict['ScanNumBegin']),
                                                                                        int(diaframemsmswindows_dict['ScanNumEnd']),
                                                                                        profile_bins,
                                                                                        encoding)
                elif exclude_mobility:
                    mz_array, intensity_array = extract_2d_tdf_spectrum(tdf_data,
                                                                        mode,
                                                                        frame,
                                                                        int(diaframemsmswindows_dict['ScanNumBegin']),
                                                                        int(diaframemsmswindows_dict['ScanNumEnd']),
                                                                        profile_bins,
                                                                        encoding)
                if mz_array.size != 0 \
                        and intensity_array.size != 0 \
                        and mz_array.size == intensity_array.size \
                        and mz_array is not None \
                        and intensity_array is not None:
                    scan_dict = populate_scan_dict_w_diapasef_ms2(scan_dict, diaframemsmswindows_dict)
                    scan_dict = populate_scan_dict_w_spectrum_data(scan_dict, mz_array, intensity_array)
                    if not exclude_mobility and mobility_array.size != 0 and mobility_array is not None:
                        scan_dict['mobility_array'] = mobility_array
                    list_of_parent_scans.append(scan_dict)
        # Parse frames with bbCID spectra.
        elif int(frames_dict['ScanMode']) == 4 and int(frames_dict['MsMsType']) == 2:
            scan_dict = init_scan_dict()
            scan_dict = populate_scan_dict_w_lcms_tsf_tdf_metadata(scan_dict, frames_dict, mode, exclude_mobility)
            framemsmsinfo_dict = tdf_data.framemsmsinfo[tdf_data.framemsmsinfo['Frame'] ==
                                                        frame].to_dict(orient='records')[0]
            scan_dict = populate_scan_dict_w_bbcid_iscid_ms2(scan_dict,
                                                             frame,
                                                             'TDF',
                                                             framemsmsinfo_dict=framemsmsinfo_dict)
            if not exclude_mobility:
                mz_array, intensity_array, mobility_array = extract_3d_tdf_spectrum(tdf_data,
                                                                                    mode,
                                                                                    frame,
                                                                                    0,
                                                                                    int(frames_dict['NumScans']),
                                                                                    profile_bins,
                                                                                    encoding)
            elif exclude_mobility:
                mz_array, intensity_array = extract_2d_tdf_spectrum(tdf_data,
                                                                    mode,
                                                                    frame,
                                                                    0,
                                                                    int(frames_dict['NumScans']),
                                                                    profile_bins,
                                                                    encoding)
            if mz_array.size != 0 \
                    and intensity_array.size != 0 \
                    and mz_array.size == intensity_array.size \
                    and mz_array is not None \
                    and intensity_array is not None:
                scan_dict = populate_scan_dict_w_spectrum_data(scan_dict, mz_array, intensity_array)
                if not exclude_mobility and mobility_array.size != 0 and mobility_array is not None:
                    scan_dict['mobility_array'] = mobility_array
                list_of_parent_scans.append(scan_dict)
        # Parse frames with MRM spectra.
        elif int(frames_dict['ScanMode']) == 2 and int(frames_dict['MsMsType']) == 2:
            scan_dict = init_scan_dict()
            scan_dict = populate_scan_dict_w_lcms_tsf_tdf_metadata(scan_dict, frames_dict, mode, exclude_mobility)
            framemsmsinfo_dict = tdf_data.framemsmsinfo[tdf_data.framemsmsinfo['Frame'] ==
                                                        frame].to_dict(orient='records')[0]
            mz_array, intensity_array = extract_2d_tdf_spectrum(tdf_data,
                                                                mode,
                                                                frame,
                                                                0,
                                                                int(frames_dict['NumScans']),
                                                                profile_bins,
                                                                encoding)
            if mz_array.size != 0 \
                    and intensity_array.size != 0 \
                    and mz_array.size == intensity_array.size \
                    and mz_array is not None \
                    and intensity_array is not None:
                # lcms set as False since MRM MS/MS spectra do not have a parent frame.
                scan_dict = populate_scan_dict_w_tsf_ms2(scan_dict, framemsmsinfo_dict, lcms=False)
                scan_dict = populate_scan_dict_w_spectrum_data(scan_dict, mz_array, intensity_array)
                list_of_parent_scans.append(scan_dict)
        # Parse frames with prm-PASEF spectra.
        elif int(frames_dict['ScanMode']) == 10 and int(frames_dict['MsMsType']) == 10:
            scan_dict = init_scan_dict()
            scan_dict = populate_scan_dict_w_lcms_tsf_tdf_metadata(scan_dict, frames_dict, mode, exclude_mobility)
            prmframemsmsinfo_dict = tdf_data.prmframemsmsinfo[tdf_data.prmframemsmsinfo['Frame'] ==
                                                              frame].to_dict(orient='records')[0]
            prmtargets_dict = tdf_data.prmtargets[tdf_data.prmtargets['Id'] ==
                                                  int(prmframemsmsinfo_dict['Target'])].to_dict(orient='records')[0]
            mz_array, intensity_array = extract_2d_tdf_spectrum(tdf_data,
                                                                mode,
                                                                frame,
                                                                int(prmframemsmsinfo_dict['ScanNumBegin']),
                                                                int(prmframemsmsinfo_dict['ScanNumEnd']),
                                                                profile_bins,
                                                                encoding)
            if mz_array.size != 0 \
                    and intensity_array.size != 0 \
                    and mz_array.size == intensity_array.size \
                    and mz_array is not None \
                    and intensity_array is not None:
                scan_dict = populate_scan_dict_w_prmpasef_ms2(scan_dict, prmframemsmsinfo_dict, prmtargets_dict)
                scan_dict = populate_scan_dict_w_spectrum_data(scan_dict, mz_array, intensity_array)
                list_of_parent_scans.append(scan_dict)
    return list_of_parent_scans, list_of_product_scans


# Parse MALDI plate map from CSV file.
def parse_maldi_plate_map(plate_map_filename):
    plate_map = pd.read_csv(plate_map_filename, header=None)
    plate_dict = {}
    for index, row in plate_map.iterrows():
        for count, value in enumerate(row, start=1):
            plate_dict[chr(index + 65) + str(count)] = value
    return plate_dict


def parse_maldi_tsf(tsf_data, frame_start, frame_stop, mode, ms2_only, profile_bins, encoding):
    list_of_scan_dicts = []

    for frame in range(frame_start, frame_stop):
        scan_dict = init_scan_dict()
        frames_dict = tsf_data.frames[tsf_data.frames['Id'] == frame].to_dict(orient='records')[0]
        maldiframeinfo_dict = tsf_data.maldiframeinfo[tsf_data.maldiframeinfo['Frame'] ==
                                                      frame].to_dict(orient='records')[0]
        scan_dict = populate_scan_dict_w_maldi_metadata(scan_dict,
                                                        tsf_data,
                                                        frames_dict,
                                                        maldiframeinfo_dict,
                                                        frame,
                                                        mode)

        mz_array, intensity_array = extract_tsf_spectrum(tsf_data, mode, frame, profile_bins, encoding)
        if mz_array.size != 0 and intensity_array.size != 0 and mz_array.size == intensity_array.size:
            scan_dict = populate_scan_dict_w_spectrum_data(scan_dict, mz_array, intensity_array)
            if int(frames_dict['MsMsType']) in MSMS_TYPE_CATEGORY['ms1'] and not ms2_only:
                scan_dict = populate_scan_dict_w_ms1(scan_dict, frame)
                list_of_scan_dicts.append(scan_dict)
            elif int(frames_dict['MsMsType']) in MSMS_TYPE_CATEGORY['ms2']:
                framemsmsinfo_dict = tsf_data.framemsmsinfo[tsf_data.framemsmsinfo['Frame'] ==
                                                            maldiframeinfo_dict['Frame']].to_dict(orient='records')[0]
                scan_dict = populate_scan_dict_w_tsf_ms2(scan_dict, framemsmsinfo_dict)
                list_of_scan_dicts.append(scan_dict)
    return list_of_scan_dicts


def parse_maldi_tdf(tdf_data, frame_start, frame_stop, mode, ms2_only, exclude_mobility, profile_bins, encoding):
    list_of_scan_dicts = []
    exclude_mobility = get_centroid_status(mode, exclude_mobility)[1]

    for frame in range(frame_start, frame_stop):
        scan_dict = init_scan_dict()
        frames_dict = tdf_data.frames[tdf_data.frames['Id'] == frame].to_dict(orient='records')[0]
        maldiframeinfo_dict = tdf_data.maldiframeinfo[tdf_data.maldiframeinfo['Frame'] ==
                                                      frame].to_dict(orient='records')[0]

        scan_dict = populate_scan_dict_w_maldi_metadata(scan_dict,
                                                        tdf_data,
                                                        frames_dict,
                                                        maldiframeinfo_dict,
                                                        frame,
                                                        mode)

        if int(frames_dict['MsMsType']) in MSMS_TYPE_CATEGORY['ms1'] and not ms2_only:
            scan_dict['scan_type'] = 'MS1 spectrum'
            scan_dict['ms_level'] = 1
            if not exclude_mobility:
                mz_array, intensity_array, mobility_array = extract_3d_tdf_spectrum(tdf_data,
                                                                                    mode,
                                                                                    frame,
                                                                                    0,
                                                                                    int(frames_dict['NumScans']),
                                                                                    profile_bins,
                                                                                    encoding)
            elif exclude_mobility:
                mz_array, intensity_array = extract_2d_tdf_spectrum(tdf_data,
                                                                    mode,
                                                                    frame,
                                                                    0,
                                                                    int(frames_dict['NumScans']),
                                                                    profile_bins,
                                                                    encoding)

            if mz_array.size != 0 \
                    and intensity_array.size != 0 \
                    and mz_array.size == intensity_array.size \
                    and mz_array is not None \
                    and intensity_array is not None:
                scan_dict = populate_scan_dict_w_spectrum_data(scan_dict, mz_array, intensity_array)
                if not exclude_mobility and mobility_array.size != 0 and mobility_array is not None:
                    scan_dict['mobility_array'] = mobility_array
                list_of_scan_dicts.append(scan_dict)
        elif int(frames_dict['MsMsType']) in MSMS_TYPE_CATEGORY['ms2']:
            framemsmsinfo_dict = tdf_data.framemsmsinfo[tdf_data.framemsmsinfo['Frame'] ==
                                                        maldiframeinfo_dict['Frame']].to_dict(orient='records')[0]
            if not exclude_mobility:
                mz_array, intensity_array, mobility_array = extract_3d_tdf_spectrum(tdf_data,
                                                                                    mode,
                                                                                    frame,
                                                                                    0,
                                                                                    int(frames_dict['NumScans']),
                                                                                    profile_bins,
                                                                                    encoding)
            elif exclude_mobility:
                mz_array, intensity_array = extract_2d_tdf_spectrum(tdf_data,
                                                                    mode,
                                                                    frame,
                                                                    0,
                                                                    int(frames_dict['NumScans']),
                                                                    profile_bins,
                                                                    encoding)

            if mz_array.size != 0 \
                    and intensity_array.size != 0 \
                    and mz_array.size == intensity_array.size \
                    and mz_array is not None \
                    and intensity_array is not None:
                scan_dict = populate_scan_dict_w_spectrum_data(scan_dict, mz_array, intensity_array)
                if not exclude_mobility and mobility_array.size != 0 and mobility_array is not None:
                    scan_dict['mobility_array'] = mobility_array
                scan_dict = populate_scan_dict_w_tsf_ms2(scan_dict, framemsmsinfo_dict)
                list_of_scan_dicts.append(scan_dict)
    return list_of_scan_dicts
