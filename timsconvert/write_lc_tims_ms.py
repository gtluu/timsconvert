from timsconvert.constants import *
from timsconvert.timestamp import *
from timsconvert.parse_lcms import *
import os
import sys
import logging
import numpy as np
import pandas as pd
from psims.mzml import MzMLWriter


def write_mzml_metadata(data, writer, infile, centroid, ms2_only):
    # Basic file descriptions.
    file_description = []
    # Add spectra level and centroid/profile status.
    if ms2_only == False:
        file_description.append('MS1 spectrum')
        file_description.append('MSn spectrum')
    elif ms2_only == True:
        file_description.append('MSn spectrum')
    if centroid:
        file_description.append('centroid spectrum')
    elif not centroid:
        file_description.append('profile spectrum')
    writer.file_description(file_description)

    # Source file
    sf = writer.SourceFile(os.path.split(infile)[0],
                           os.path.split(infile)[1],
                           id=os.path.splitext(os.path.split(infile)[1])[0])

    # Add list of software.
    acquisition_software_id = data.meta_data['AcquisitionSoftware']
    acquisition_software_version = data.meta_data['AcquisitionSoftwareVersion']
    if acquisition_software_id == 'Bruker otofControl':
        acquisition_software_params = ['micrOTOFcontrol', ]
    else:
        acquisition_software_params = []
    psims_software = {'id': 'psims-writer',
                      'version': '0.1.2',
                      'params': ['python-psims', ]}
    writer.software_list([{'id': acquisition_software_id,
                           'version': acquisition_software_version,
                           'params': acquisition_software_params},
                          psims_software])

    # Instrument configuration.
    inst_count = 0
    if data.meta_data['InstrumentSourceType'] in INSTRUMENT_SOURCE_TYPE.keys():
        inst_count += 1
        source = writer.Source(inst_count, [INSTRUMENT_SOURCE_TYPE[data.meta_data['InstrumentSourceType']]])
    # If source isn't found in the GlobalMetadata SQL table, hard code source to ESI
    else:
        inst_count += 1
        source = writer.Source(inst_count, [INSTRUMENT_SOURCE_TYPE['1']])

    # Analyzer and detector hard coded for timsTOF fleX
    inst_count += 1
    analyzer = writer.Analyzer(inst_count, ['quadrupole', 'time-of-flight'])
    inst_count += 1
    detector = writer.Detector(inst_count, ['electron multiplier'])
    inst_config = writer.InstrumentConfiguration(id='instrument', component_list=[source, analyzer, detector],
                                                 params=[INSTRUMENT_FAMILY[data.meta_data['InstrumentFamily']]])
    writer.instrument_configuration_list([inst_config])

    # Data processing element.
    proc_methods = []
    proc_methods.append(writer.ProcessingMethod(order=1, software_reference='psims-writer',
                                                params=['Conversion to mzML']))
    processing = writer.DataProcessing(proc_methods, id='exportation')
    writer.data_processing_list([processing])


# Calculate the number of spectra to be written.
def get_spectra_count(data, ms1_groupby, encoding):
    if ms1_groupby == 'scan':
        pass


# Get either raw (slightly modified implementation that gets centroid spectrum), quasi-profile, or centroid spectrum.
# Returns an m/z array and intensity array.
def extract_spectrum_arrays(tdf_data, mode, multiscan, frame, scan_begin, scan_end, encoding):
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
        intensity_array = np.array(tdf_data.extract_profile_spectrum_for_frame(frame, scan_begin, scan_end),
                                   dtype=encoding_dtype)
        mz_acq_range_lower = float(tdf_data.meta_data['MzAcqRangeLower'])
        mz_acq_range_upper = float(tdf_data.meta_data['MzAcqRangeUpper'])
        step_size = (mz_acq_range_upper - mz_acq_range_lower) / len(intensity_array)
        mz_array = np.arange(mz_acq_range_lower, mz_acq_range_upper, step_size, dtype=encoding_dtype)
        return mz_array, intensity_array
    elif mode == 'centroid':
        mz_array, intensity_array = tdf_data.extract_centroided_spectrum_for_frame(frame, scan_begin, scan_end)
        mz_array = np.array(mz_array, dtype=encoding_dtype)
        intensity_array = np.array(intensity_array, dtype=encoding_dtype)
        return mz_array, intensity_array


# New version of parse_lcms_tdf?
def parse_lcms_tdf(tdf_data, ms1_groupby, mode, ms2_only, encoding):
    if encoding == 32:
        encoding_dtype = np.float32
    elif encoding == 64:
        encoding_dtype = np.float64

    list_of_frames_dict = tdf_data.frames.to_dict(orient='records')
    if tdf_data.pasefframemsmsinfo is not None:
        list_of_pasefframemsmsinfo_dict = tdf_data.pasefframemsmsinfo.to_dict(orient='records')
    if tdf_data.precursors is not None:
        list_of_precursors_dict = tdf_data.precursors.to_dict(orient='records')
    list_of_parent_scans = []
    list_of_product_scans = []

    if mode == 'profile':
        centroided = False
    elif mode == 'centroid' or mode == 'raw':
        centroided = True

    #for index in range(len(tdf_data.ms1_frames)):
    for index in range(169, 170):
        frame = int(tdf_data.ms1_frames[index])
        frames_dict = [i for i in list_of_frames_dict if int(i['Id']) == frame][0]

        if frames_dict['MsMsType'] in MSMS_TYPE_CATEGORY['ms1']:
            if ms2_only == False:
                if ms1_groupby == 'frame':
                    frame_mz_arrays = []
                    frame_intensity_arrays = []
                    frame_mobility_arrays = []
                for scan_num in range(0, int(frames_dict['NumScans'])):
                    mz_array, intensity_array = extract_spectrum_arrays(tdf_data,
                                                                        mode,
                                                                        True,
                                                                        frame,
                                                                        scan_num,
                                                                        scan_num + 1,
                                                                        encoding)
                    if mz_array.size != 0 and intensity_array.size != 0 and mz_array.size == intensity_array.size:
                        mobility = tdf_data.scan_num_to_oneoverk0(frame, np.array([scan_num]))[0]
                        mobility_array = np.repeat(mobility, mz_array.size)

                        if ms1_groupby == 'frame':
                            frame_mz_arrays.append(mz_array)
                            frame_intensity_arrays.append(intensity_array)
                            frame_mobility_arrays.append(mobility_array)
                        elif ms1_groupby == 'scan':
                            base_peak_index = np.where(intensity_array == np.max(intensity_array))

                            scan_dict = {'scan_number': int(scan_num),
                                         'scan_type': 'MS1 spectrum',
                                         'ms_level': 1,
                                         'mz_array': mz_array,
                                         'intensity_array': intensity_array,
                                         'mobility': mobility,
                                         'mobility_array': mobility_array,
                                         'polarity': frames_dict['Polarity'],
                                         'centroided': centroided,
                                         'retention_time': float(frames_dict['Time']),
                                         'total_ion_current': sum(intensity_array),
                                         'base_peak_mz': mz_array[base_peak_index][0].astype(float),
                                         'base_peak_intensity': intensity_array[base_peak_index][0].astype(float),
                                         'high_mz': float(max(mz_array)),
                                         'low_mz': float(min(mz_array)),
                                         'frame': frame}
                            list_of_parent_scans.append(scan_dict)

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
                                 'retention_time': float(frames_dict['Time']),
                                 'total_ion_current': sum(frames_array[:, 1]),
                                 'base_peak_mz': frames_array[:, 0][base_peak_index][0].astype(float),
                                 'base_peak_intensity': frames_array[:, 1][base_peak_index][0].astype(float),
                                 'high_mz': float(max(frames_array[:, 0])),
                                 'low_mz': float(min(frames_array[:, 0])),
                                 'frame': frame}
                    list_of_parent_scans.append(scan_dict)
            if int(tdf_data.ms1_frames[index + 1]) - int(tdf_data.ms1_frames[index]) > 1:
                precursor_dicts = [i for i in list_of_precursors_dict if int(i['Parent']) == frame]
                for precursor_dict in precursor_dicts:
                    pasefframemsmsinfo_dicts = [i for i in list_of_pasefframemsmsinfo_dict
                                                if int(i['Precursor']) == int(precursor_dict['Id'])]
                    pasef_mz_arrays = []
                    pasef_intensity_arrays = []
                    #pasef_mobility_arrays = []
                    for pasef_dict in pasefframemsmsinfo_dicts:
                        scan_begin = int(pasef_dict['ScanNumBegin'])
                        scan_end = int(pasef_dict['ScanNumEnd'])
                        frame_mz_arrays = []
                        frame_intensity_arrays = []
                        #frame_mobility_arrays = []
                        for scan_num in range(scan_begin, scan_end):
                            mz_array, intensity_array = extract_spectrum_arrays(tdf_data,
                                                                                mode,
                                                                                True,
                                                                                int(pasef_dict['Frame']),
                                                                                scan_begin,
                                                                                scan_end,
                                                                                encoding)
                            if mz_array.size != 0 and intensity_array.size != 0 and mz_array.size == intensity_array.size:
                                #mobility = tdf_data.scan_num_to_oneoverk0(int(pasef_dict['Frame']),
                                #                                          np.array([scan_num]))[0]
                                #mobility_array = np.repeat(mobility, mz_array.size)

                                frame_mz_arrays.append(mz_array)
                                frame_intensity_arrays.append(intensity_array)
                                #frame_mobility_arrays.append(mobility_array)
                        if frame_mz_arrays and frame_intensity_arrays:
                            frames_array = np.stack((np.concatenate(frame_mz_arrays, axis=None),
                                                     np.concatenate(frame_intensity_arrays, axis=None)),
                                                     #np.concatenate(frame_mobility_arrays, axis=None)),
                                                    axis=-1)
                            frames_array = np.unique(frames_array[np.argsort(frames_array[:, 0])], axis=0)
                            pasef_mz_arrays.append(frames_array[:, 0])
                            pasef_intensity_arrays.append(frames_array[:, 1])
                            #pasef_mobility_arrays.append(frames_array[:, 2])
                    if pasef_mz_arrays and pasef_intensity_arrays:
                        pasef_array = np.stack((np.concatenate(pasef_mz_arrays, axis=None),
                                                np.concatenate(pasef_intensity_arrays, axis=None)),
                                                #np.concatenate(pasef_mobility_arrays, axis=None)),
                                               axis=-1)
                        pasef_array = np.unique(pasef_array[np.argsort(pasef_array[:, 0])], axis=0)

                        base_peak_index = np.where(pasef_array[:, 1] == np.max(pasef_array[:, 1]))

                        scan_dict = {'scan_number': None,
                                     'scan_type': 'MSn spectrum',
                                     'ms_level': 2,
                                     'mz_array': pasef_array[:, 0],
                                     'intensity_array': pasef_array[:, 1],
                                     'mobility': None,
                                     'mobility_array': None,
                                     'polarity': frames_dict['Polarity'],
                                     'centroided': centroided,
                                     'retention_time': float(frames_dict['Time']),
                                     'total_ion_current': sum(pasef_array[:, 1]),
                                     'base_peak_mz': pasef_array[:, 0][base_peak_index][0].astype(float),
                                     'base_peak_intensity': pasef_array[:, 1][base_peak_index][0].astype(float),
                                     'high_mz': float(max(pasef_array[:, 0])),
                                     'low_mz': float(min(pasef_array[:, 0])),
                                     'target_mz': float(precursor_dict['AverageMz']),
                                     'isolation_lower_offset': float(pasefframemsmsinfo_dicts[0]['IsolationWidth']) / 2,
                                     'isolation_upper_offset': float(pasefframemsmsinfo_dicts[0]['IsolationWidth']) / 2,
                                     'selected_ion_mz': float(precursor_dict['LargestPeakMz']),
                                     'selected_ion_intensity': float(precursor_dict['Intensity']),
                                     'selected_ion_mobility': tdf_data.scan_num_to_oneoverk0(int(precursor_dict['Parent']),
                                                              np.array([int(precursor_dict['ScanNumber'])]))[0],
                                     'charge_state': precursor_dict['Charge'],
                                     'collision_energy': pasefframemsmsinfo_dicts[0]['CollisionEnergy'],
                                     'parent_frame': int(precursor_dict['Parent']),
                                     'parent_scan': int(precursor_dict['ScanNumber'])}
                        list_of_product_scans.append(scan_dict)
    return list_of_parent_scans, list_of_product_scans


# Parse out LC-MS(/MS) data and write out mzML file using psims.
def write_lcms_mzml(data, infile, outdir, outfile, centroid, ms2_only, ms1_groupby, encoding, chunk_size):
    # Initialize mzML writer using psims.
    writer = MzMLWriter(os.path.join(outdir, outfile))

    with writer:
        # Begin mzML with controlled vocabularies (CV).
        writer.controlled_vocabularies()

        # Start write acquisition, instrument config, processing, etc. to mzML.
        write_mzml_metadata(data, writer, infile, centroid, ms2_only)

        logging.info(get_timestamp() + ':' + 'Writing to .mzML file ' + os.path.join(outdir, outfile) + '...')
        # Parse chunks of data and write to spectrum elements.
        with writer.run(id='run', instrument_configuration='instrument'):
            scan_count = 0
            num_of_spectra = get_spectra_count()







        # Begin parsing and writing out data.
        # add code later for elif baf -> use baf2sql
        if data.meta_data['SchemaType'] == 'TDF':




            chunk = 0
            while chunk + chunk_size + 1 <= len(data.ms1_frames):
                chunk_list = []
                print(chunk, chunk + chunk_size, chunk + 1, chunk + chunk_size + 1)
                for i, j in zip(data.ms1_frames[chunk:chunk + chunk_size],
                                data.ms1_frames[chunk + 1:chunk + chunk_size + 1]):
                    chunk_list.append((int(i), int(j)))
                chunk += chunk_size
                print(chunk_list)
                print(len(chunk_list))
            else:
                chunk_list = []
                for i, j in zip(data.ms1_frames[chunk:-1], data.ms1_frames[chunk + 1:]):
                    chunk_list.append((int(i), int(j)))
                print(chunk_list)
                print(len(chunk_list))