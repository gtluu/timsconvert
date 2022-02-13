from timsconvert.constants import *
from timsconvert.timestamp import *
import os
import sys
import logging
import numpy as np
from psims.mzml import MzMLWriter


def parse_lcms_tdf(tdf_data, frames_df, ms1_groupby, centroid, encoding, ms2_only):
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


# Parse out LC-MS(/MS) data and write out mzML file using psims.
def write_lcms_mzml(data, infile, outdir, outfile, centroid, ms2_only, ms1_groupby, encoding):
    # Initialize mzML writer using psims.
    writer = MzMLWriter(os.path.join(outdir, outfile))

    with writer:
        # Begin mzML with controlled vocabularies (CV).
        writer.controlled_vocabularies()

        # Start write acquisition, instrument config, processing, etc. to mzML.
        write_mzml_metadata(data, writer, infile, centroid, ms2_only)

        # Begin parsing and writing out data.
        if data.meta_data['SchemaType'] == 'TDF':
