from timsconvert.constants import *
from timsconvert.timestamp import *
from timsconvert.parse_lcms import *
import os
import sys
import logging
import numpy as np
import pandas as pd
from psims.mzml import MzMLWriter


def write_mzml_metadata(data, writer, infile, mode, ms2_only):
    # Basic file descriptions.
    file_description = []
    # Add spectra level and centroid/profile status.
    if ms2_only == False:
        file_description.append('MS1 spectrum')
        file_description.append('MSn spectrum')
    elif ms2_only == True:
        file_description.append('MSn spectrum')
    if mode == 'raw' or mode == 'centroid':
        file_description.append('centroid spectrum')
    elif mode == 'profile':
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


# Write out parent spectrum.
def write_lcms_ms1_spectrum(writer, parent_scan, encoding, groupby):
    # Build params
    params = [parent_scan['scan_type'],
              {'ms level': parent_scan['ms_level']},
              {'total ion current': parent_scan['total_ion_current']},
              {'base peak m/z': parent_scan['base_peak_mz']},
              {'base peak intensity': parent_scan['base_peak_intensity']},
              {'highest observed m/z': parent_scan['high_mz']},
              {'lowest observed m/z': parent_scan['low_mz']}]

    if groupby == 'scan':
        params.append({'inverse reduced ion mobility': parent_scan['mobility']})
    other_arrays = [('ion mobility array', parent_scan['mobility_array'])]

    if encoding == 32:
        encoding_dtype = np.float32
    elif encoding == 64:
        encoding_dtype = np.float64

    # Write MS1 spectrum.
    writer.write_spectrum(parent_scan['mz_array'],
                          parent_scan['intensity_array'],
                          id='scan=' + str(parent_scan['scan_number']),
                          polarity=parent_scan['polarity'],
                          centroided=parent_scan['centroided'],
                          scan_start_time=parent_scan['retention_time'],
                          other_arrays=other_arrays,
                          params=params,
                          encoding={'m/z array': encoding_dtype,
                                    'intensity array': encoding_dtype,
                                    'ion mobility array': encoding_dtype})


# Write out product spectrum.
def write_lcms_ms2_spectrum(writer, parent_scan, encoding, product_scan):
    # Build params list for spectrum.
    spectrum_params = [product_scan['scan_type'],
                       {'ms level': product_scan['ms_level']},
                       {'total ion current': product_scan['total_ion_current']}]
    if 'base_peak_mz' in product_scan.keys() and 'base_peak_intensity' in product_scan.keys():
        spectrum_params.append({'base peak m/z': product_scan['base_peak_mz']})
        spectrum_params.append({'base peak intensity': product_scan['base_peak_intensity']})
    if 'high_mz' in product_scan.keys() and 'low_mz' in product_scan.keys():
        spectrum_params.append({'highest observed m/z': product_scan['high_mz']})
        spectrum_params.append({'lowest observed m/z': product_scan['low_mz']})
    other_arrays = None

    # Build precursor information dict.
    precursor_info = {'mz': product_scan['selected_ion_mz'],
                      'intensity': product_scan['selected_ion_intensity'],
                      #'activation': [product_scan['activation'],
                      #               {'collision energy': product_scan['collision_energy']}],
                      'activation': [{'collision energy': product_scan['collision_energy']}],
                      'isolation_window_args': {'target': product_scan['target_mz'],
                                                'upper': product_scan['isolation_upper_offset'],
                                                'lower': product_scan['isolation_lower_offset']},
                      'params': {'inverse reduced ion mobility': product_scan['selected_ion_mobility']}}
    if not np.isnan(product_scan['charge_state']):
        precursor_info['charge'] = product_scan['charge_state']

    if parent_scan != None:
        precursor_info['spectrum_reference'] = 'scan=' + str(parent_scan['scan_number'])

    if encoding == 32:
        encoding_dtype = np.float32
    elif encoding == 64:
        encoding_dtype = np.float64

    # Write MS2 spectrum.
    writer.write_spectrum(product_scan['mz_array'],
                          product_scan['intensity_array'],
                          id='scan=' + str(product_scan['scan_number']),
                          polarity=product_scan['polarity'],
                          centroided=product_scan['centroided'],
                          scan_start_time=product_scan['retention_time'],
                          other_arrays=other_arrays,
                          params=spectrum_params,
                          precursor_information=precursor_info,
                          encoding={'m/z array': encoding_dtype,
                                    'intensity array': encoding_dtype})


def write_chunk_to_mzml(data, writer, i, j, scan_count, ms1_groupby, mode, ms2_only, encoding):
    # Parse TDF data
    logging.info(get_timestamp() + ':' + 'Parsing Frames ' + str(i) + ' - ' + str(j) + '...')
    if data.meta_data['SchemaType'] == 'TDF':
        parent_scans, product_scans = parse_lcms_tdf(data, i, j, ms1_groupby, mode, ms2_only, encoding)
    # add code latter for elif baf -> use baf2sql
    # Write MS1 parent scans.
    logging.info(get_timestamp() + ':' + 'Writing Frames ' + str(i) + ' - ' + str(j) + '...')
    if ms2_only == False:
        for parent in parent_scans:
            if ms1_groupby == 'scan':
                products = [i for i in product_scans if i['parent_frame'] == parent['frame'] and
                            i['parent_scan'] == parent['scan_number']]
            elif ms1_groupby == 'frame':
                products = [i for i in product_scans if i['parent_frame'] == parent['frame']]
            # Set params for scan.
            scan_count += 1
            parent['scan_number'] = scan_count
            write_lcms_ms1_spectrum(writer, parent, encoding, ms1_groupby)
            # Write MS2 Product Scans
            for product in products:
                scan_count += 1
                product['scan_number'] = scan_count
                write_lcms_ms2_spectrum(writer, parent, encoding, product)
    elif ms2_only == True or parent_scans == []:
        for product in product_scans:
            scan_count += 1
            product['scan_number'] = scan_count
            write_lcms_ms2_spectrum(writer, None, encoding, product)
    return scan_count


# Parse out LC-MS(/MS) data and write out mzML file using psims.
def write_lcms_mzml(data, infile, outdir, outfile, mode, ms2_only, ms1_groupby, encoding, chunk_size):
    # Initialize mzML writer using psims.
    writer = MzMLWriter(os.path.join(outdir, outfile))

    with writer:
        # Begin mzML with controlled vocabularies (CV).
        writer.controlled_vocabularies()

        # Start write acquisition, instrument config, processing, etc. to mzML.
        write_mzml_metadata(data, writer, infile, mode, ms2_only)

        logging.info(get_timestamp() + ':' + 'Writing to .mzML file ' + os.path.join(outdir, outfile) + '...')
        # Parse chunks of data and write to spectrum elements.
        with writer.run(id='run', instrument_configuration='instrument'):
            scan_count = 0
            num_of_spectra = get_spectra_count()
            with writer.spectrum_list(count=num_of_spectra):
                chunk = 0
                while chunk + chunk_size + 1 <= len(data.ms1_frames):
                    chunk_list = []
                    for i, j in zip(data.ms1_frames[chunk: chunk + chunk_size],
                                    data.ms1_frames[chunk + 1: chunk + chunk_size + 1]):
                        chunk_list.append((int(i), int(j)))
                    for i, j in chunk_list:
                        scan_count = write_chunk_to_mzml(data, writer, i, j, scan_count, ms1_groupby, mode, ms2_only,
                                                         encoding)
                    chunk += chunk_size
                else:
                    chunk_list = []
                    for i, j in zip(data.ms1_frames[chunk:-1], data.ms1_frames[chunk + 1:]):
                        chunk_list.append((int(i), int(j)))
                    chunk_list.append((chunk_list[len(chunk_list) - 1][1], data.frames.shape[0]))
                    for i, j in chunk_list:
                        scan_count = write_chunk_to_mzml(data, writer, i, j, scan_count, ms1_groupby, mode, ms2_only,
                                                         encoding)
