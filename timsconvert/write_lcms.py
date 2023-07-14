from timsconvert.write_mzml import *
import os
import logging
import numpy as np
from psims.mzml import MzMLWriter


# Write out parent spectrum.
def write_lcms_ms1_spectrum(writer, parent_scan, encoding, compression):
    # Build params
    params = [parent_scan['scan_type'],
              {'ms level': parent_scan['ms_level']},
              {'total ion current': parent_scan['total_ion_current']},
              {'base peak m/z': parent_scan['base_peak_mz']},
              {'base peak intensity': parent_scan['base_peak_intensity']},
              {'highest observed m/z': parent_scan['high_mz']},
              {'lowest observed m/z': parent_scan['low_mz']}]

    if 'mobility_array' in parent_scan.keys() and parent_scan['mobility_array'] is not None:
        # This version only works with newer versions of psims.
        # Currently unusable due to boost::interprocess error on Linux.
        # other_arrays = [({'name': 'mean inverse reduced ion mobility array',
        #                  'unit_name': 'volt-second per square centimeter'},
        #                 parent_scan['mobility_array'])]
        # Need to use older notation with a tuple (name, array) due to using psims 0.1.34.
        other_arrays = [('mean inverse reduced ion mobility array', parent_scan['mobility_array'])]
    else:
        other_arrays = None

    if encoding == 32:
        encoding_dtype = np.float32
    elif encoding == 64:
        encoding_dtype = np.float64

    encoding_dict = {'m/z array': encoding_dtype,
                     'intensity array': encoding_dtype}
    if other_arrays is not None:
        encoding_dict['mean inverse reduced ion mobility array'] = encoding_dtype

    # Write MS1 spectrum.
    writer.write_spectrum(parent_scan['mz_array'],
                          parent_scan['intensity_array'],
                          id='scan=' + str(parent_scan['scan_number']),
                          polarity=parent_scan['polarity'],
                          centroided=parent_scan['centroided'],
                          scan_start_time=parent_scan['retention_time'],
                          other_arrays=other_arrays,
                          params=params,
                          encoding=encoding_dict,
                          compression=compression)


# Write out product spectrum.
def write_lcms_ms2_spectrum(writer, parent_scan, encoding, product_scan, compression):
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

    # Build precursor information dict.
    precursor_info = {'mz': product_scan['selected_ion_mz'],
                      #'activation': [product_scan['activation'],
                      #               {'collision energy': product_scan['collision_energy']}],
                      'activation': [{'collision energy': product_scan['collision_energy']}],
                      'isolation_window_args': {'target': product_scan['target_mz'],
                                                'upper': product_scan['isolation_upper_offset'],
                                                'lower': product_scan['isolation_lower_offset']},
                      'params': []}
    if 'selected_ion_intensity' in product_scan.keys():
        precursor_info['intensity'] = product_scan['selected_ion_intensity']
    if 'selected_ion_mobility' in product_scan.keys():
        precursor_info['params'].append({'inverse reduced ion mobility': product_scan['selected_ion_mobility']})
    if 'selected_ion_ccs' in product_scan.keys():
        precursor_info['params'].append({'collisional cross sectional area': product_scan['selected_ion_ccs']})
    if not np.isnan(product_scan['charge_state']) and int(product_scan['charge_state']) != 0:
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
                          params=spectrum_params,
                          precursor_information=precursor_info,
                          encoding={'m/z array': encoding_dtype,
                                    'intensity array': encoding_dtype},
                          compression=compression)


def write_lcms_chunk_to_mzml(data, writer, frame_start, frame_stop, scan_count, mode, ms2_only, exclude_mobility,
                             profile_bins, encoding, compression):
    # Parse TDF data
    if data.meta_data['SchemaType'] == 'TDF':
        parent_scans, product_scans = parse_lcms_tdf(data, frame_start, frame_stop, mode, ms2_only, exclude_mobility,
                                                     profile_bins, encoding)
    # Parse BAF data
    elif data.meta_data['SchemaType'] == 'Baf2Sql':
        parent_scans, product_scans = parse_lcms_baf(data, frame_start, frame_stop, mode, ms2_only, profile_bins,
                                                     encoding)

    # Write MS1 parent scans.
    if ms2_only == False:
        for parent in parent_scans:
            products = [i for i in product_scans if i['parent_frame'] == parent['frame']]
            # Set params for scan.
            scan_count += 1
            parent['scan_number'] = scan_count
            write_lcms_ms1_spectrum(writer, parent, encoding, compression)
            # Write MS2 Product Scans
            for product in products:
                scan_count += 1
                product['scan_number'] = scan_count
                write_lcms_ms2_spectrum(writer, parent, encoding, product, compression)
    elif ms2_only == True or parent_scans == []:
        for product in product_scans:
            scan_count += 1
            product['scan_number'] = scan_count
            write_lcms_ms2_spectrum(writer, None, encoding, product, compression)
    return scan_count


# Parse out LC-MS(/MS) data and write out mzML file using psims.
def write_lcms_mzml(data, infile, outdir, outfile, mode, ms2_only, exclude_mobility, profile_bins, encoding,
                    compression, barebones_metadata, chunk_size):
    # Initialize mzML writer using psims.
    logging.info(get_timestamp() + ':' + 'Initializing mzML Writer...')
    #writer = MzMLWriter(os.path.join(outdir, outfile), close=True)
    writer = MzMLWriter(os.path.splitext(os.path.join(outdir, outfile))[0] + '_tmp.mzML', close=True)

    with writer:
        # Begin mzML with controlled vocabularies (CV).
        logging.info(get_timestamp() + ':' + 'Initializing controlled vocabularies...')
        writer.controlled_vocabularies()

        # Start write acquisition, instrument config, processing, etc. to mzML.
        logging.info(get_timestamp() + ':' + 'Writing mzML metadata...')
        write_mzml_metadata(data, writer, infile, mode, ms2_only, barebones_metadata)

        logging.info(get_timestamp() + ':' + 'Writing data to .mzML file ' + os.path.join(outdir, outfile) + '...')
        # Parse chunks of data and write to spectrum elements.
        with writer.run(id='run', instrument_configuration='instrument'):
            scan_count = 0
            # Count number of spectra in run.
            logging.info(get_timestamp() + ':' + 'Calculating number of spectra...')
            num_of_spectra = get_spectra_count(data)
            with writer.spectrum_list(count=num_of_spectra):
                chunk = 0
                while chunk + chunk_size + 1 <= len(data.ms1_frames):
                    chunk_list = []
                    for i, j in zip(data.ms1_frames[chunk: chunk + chunk_size],
                                    data.ms1_frames[chunk + 1: chunk + chunk_size + 1]):
                        chunk_list.append((int(i), int(j)))
                    logging.info(get_timestamp() + ':' + 'Parsing and writing Frame ' + str(chunk_list[0][0]) + '...')
                    for frame_start, frame_stop in chunk_list:
                        scan_count = write_lcms_chunk_to_mzml(data, writer, frame_start, frame_stop, scan_count, mode,
                                                              ms2_only, exclude_mobility, profile_bins, encoding,
                                                              compression)
                    chunk += chunk_size
                else:
                    chunk_list = []
                    for i, j in zip(data.ms1_frames[chunk:-1], data.ms1_frames[chunk + 1:]):
                        chunk_list.append((int(i), int(j)))
                    chunk_list.append((j, data.frames.shape[0] + 1))
                    logging.info(get_timestamp() + ':' + 'Parsing and writing Frame ' + str(chunk_list[0][0]) + '...')
                    for frame_start, frame_stop in chunk_list:
                        scan_count = write_lcms_chunk_to_mzml(data, writer, frame_start, frame_stop, scan_count, mode,
                                                              ms2_only, exclude_mobility, profile_bins, encoding,
                                                              compression)

    if num_of_spectra != scan_count:
        logging.info(get_timestamp() + ':' + 'Updating scan count...')
        update_spectra_count(outdir, outfile, num_of_spectra, scan_count)
    logging.info(get_timestamp() + ':' + 'Finished writing to .mzML file ' +
                 os.path.join(outdir, outfile) + '...')
