from timsconvert.parse_maldi import *
from timsconvert.write_mzml import *
import os
import logging
import numpy as np
from psims.mzml import MzMLWriter


def write_maldi_dd_ms1_spectrum(writer, data, scan, encoding, compression, title=None):
    # Build params.
    params = [scan['scan_type'],
              {'ms level': scan['ms_level']},
              {'total ion current': scan['total_ion_current']},
              {'base peak m/z': scan['base_peak_mz']},
              {'base peak intensity': scan['base_peak_intensity']},
              {'highest observed m/z': scan['high_mz']},
              {'lowest observed m/z': scan['low_mz']},
              {'maldi spot identifier': scan['coord']},
              {'spectrum title': title}]

    if data.meta_data['SchemaType'] == 'TDF' and scan['ms_level'] == 1 and scan['mobility_array'] is not None:
        # This version only works with newer versions of psims.
        # Currently unusable due to boost::interprocess error on Linux.
        # other_arrays = [({'name': 'mean inverse reduced ion mobility array',
        #                  'unit_name': 'volt-second per square centimeter'},
        #                 scan['mobility_array'])]
        # Need to use older notation with a tuple (name, array) due to using psims 0.1.34.
        other_arrays = [('mean inverse reduced ion mobility array', scan['mobility_array'])]
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

    # Write out spectrum.
    writer.write_spectrum(scan['mz_array'],
                          scan['intensity_array'],
                          id='scan=' + str(scan['scan_number']),
                          polarity=scan['polarity'],
                          centroided=scan['centroided'],
                          scan_start_time=scan['retention_time'],
                          other_arrays=other_arrays,
                          params=params,
                          encoding=encoding_dict,
                          compression=compression)


def write_maldi_dd_ms2_spectrum(writer, scan, encoding, compression, title=None):
    # Build params.
    params = [scan['scan_type'],
              {'ms level': scan['ms_level']},
              {'total ion current': scan['total_ion_current']},
              {'spectrum title': title}]
    if 'base_peak_mz' in scan.keys() and 'base_peak_intensity' in scan.keys():
        params.append({'base peak m/z': scan['base_peak_mz']})
        params.append({'base peak intensity': scan['base_peak_intensity']})
    if 'high_mz' in scan.keys() and 'low_mz' in scan.keys():
        params.append({'highest observed m/z': scan['high_mz']})
        params.append({'lowest observed m/z': scan['low_mz']})

    # Build precursor information dict.
    precursor_info = {'mz': scan['selected_ion_mz'],
                      'activation': [{'collision energy': scan['collision_energy']}],
                      'isolation_window_args': {'target': scan['target_mz'],
                                                'upper': scan['isolation_upper_offset'],
                                                'lower': scan['isolation_lower_offset']}}

    if scan['charge_state'] is not None:
        precursor_info['charge'] = scan['charge_state']

    if encoding == 32:
        encoding_dtype = np.float32
    elif encoding == 64:
        encoding_dtype = np.float64

    # Write out MS2 spectrum.
    writer.write_spectrum(scan['mz_array'],
                          scan['intensity_array'],
                          id='scan=' + str(scan['scan_number']),
                          polarity=scan['polarity'],
                          centroided=scan['centroided'],
                          scan_start_time=scan['retention_time'],
                          params=params,
                          precursor_information=precursor_info,
                          encoding={'m/z array':encoding_dtype,
                                    'intensity_array': encoding_dtype},
                          compression=compression)


# Parse out MALDI DD data and write out mzML file using psims.
def write_maldi_dd_mzml(data, infile, outdir, outfile, mode, ms2_only, exclude_mobility, profile_bins, encoding,
                        compression, maldi_output_file, plate_map, barebones_metadata, chunk_size):
    if maldi_output_file == 'combined':
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
            # Parse chunks of data and write to spectrum element.
            with writer.run(id='run', instrument_configuration='instrument'):
                scan_count = 0
                # Count number of spectra in run.
                logging.info(get_timestamp() + ':' + 'Calculating number of spectra...')
                num_of_spectra = len(list(data.frames['Id'].values))
                with writer.spectrum_list(count=num_of_spectra):
                    # Parse all MALDI data.
                    num_frames = data.frames.shape[0] + 1
                    # Parse TSF data.
                    if data.meta_data['SchemaType'] == 'TSF':
                        if mode == 'raw':
                            logging.info(get_timestamp() + ':' + 'TSF file detected. Only export in profile or '
                                                                 'centroid mode are supported. Defaulting to centroid '
                                                                 'mode.')
                        list_of_scan_dicts = parse_maldi_tsf(data, 1, num_frames, mode, ms2_only, profile_bins,
                                                             encoding)
                    # Parse TDF data.
                    elif data.meta_data['SchemaType'] == 'TDF':
                        list_of_scan_dicts = parse_maldi_tdf(data, 1, num_frames, mode, ms2_only, exclude_mobility,
                                                             profile_bins, encoding)
                    # Write MS1 parent scans.
                    for scan_dict in list_of_scan_dicts:
                        if ms2_only == True and scan_dict['ms_level'] == 1:
                            pass
                        else:
                            scan_count += 1
                            scan_dict['scan_number'] = scan_count
                            if scan_dict['ms_level'] == 1:
                                write_maldi_dd_ms1_spectrum(writer, data, scan_dict, encoding, compression,
                                                            title=os.path.splitext(outfile)[0])
                            elif scan_dict['ms_level'] == 2:
                                write_maldi_dd_ms2_spectrum(writer, scan_dict, encoding, compression,
                                                            title=os.path.splitext(outfile)[0])

        logging.info(get_timestamp() + ':' + 'Updating scan count...')
        update_spectra_count(outdir, outfile, num_of_spectra, scan_count)
        logging.info(get_timestamp() + ':' + 'Finished writing to .mzML file ' + os.path.join(outdir, outfile) + '...')
    elif maldi_output_file == 'individual' and plate_map != '':
        # Check to make sure plate map is a valid csv file.
        if os.path.exists(plate_map) and os.path.splitext(plate_map)[1] == '.csv':
            # Parse all MALDI data.
            num_frames = data.frames.shape[0] + 1
            # Parse TSF data.
            if data.meta_data['SchemaType'] == 'TSF':
                if mode == 'raw':
                    logging.info(get_timestamp() + ':' + 'TSF file detected. Only export in profile or '
                                                         'centroid mode are supported. Defaulting to centroid '
                                                         'mode.')
                list_of_scan_dicts = parse_maldi_tsf(data, 1, num_frames, mode, ms2_only, profile_bins, encoding)
            # Parse TDF data.
            elif data.meta_data['SchemaType'] == 'TDF':
                list_of_scan_dicts = parse_maldi_tdf(data, 1, num_frames, mode, ms2_only, exclude_mobility,
                                                     profile_bins, encoding)

            # Use plate map to determine filename.
            # Names things as sample_position.mzML
            plate_map_dict = parse_maldi_plate_map(plate_map)

            for scan_dict in list_of_scan_dicts:
                output_filename = os.path.join(outdir, plate_map_dict[scan_dict['coord']] + '_' + scan_dict['coord'] +
                                               '.mzML')

                writer = MzMLWriter(output_filename, close=True)

                with writer:
                    writer.controlled_vocabularies()

                    write_mzml_metadata(data, writer, infile, mode, ms2_only, barebones_metadata)

                    with writer.run(id='run', instrument_configuration='instrument'):
                        scan_count = 1
                        scan_dict['scan_number'] = scan_count
                        with writer.spectrum_list(count=scan_count):
                            if ms2_only == True and scan_dict['ms_level'] == 1:
                                pass
                            else:
                                if scan_dict['ms_level'] == 1:
                                    write_maldi_dd_ms1_spectrum(writer, data, scan_dict, encoding, compression,
                                                                title=plate_map_dict[scan_dict['coord']])
                                elif scan_dict['ms_level'] == 2:
                                    write_maldi_dd_ms2_spectrum(writer, scan_dict, encoding, compression,
                                                                title=plate_map_dict[scan_dict['coord']])
                logging.info(get_timestamp() + ':' + 'Finished writing to .mzML file ' +
                             os.path.join(outdir, output_filename) + '...')
    elif maldi_output_file == 'sample' and plate_map != '':
        # Check to make sure plate map is a valid csv file.
        if os.path.exists(plate_map) and os.path.splitext(plate_map)[1] == '.csv':
            # Parse all MALDI data.
            num_frames = data.frames.shape[0] + 1
            # Parse TSF data.
            if data.meta_data['SchemaType'] == 'TSF':
                if mode == 'raw':
                    logging.info(get_timestamp() + ':' + 'TSF file detected. Only export in profile or '
                                                         'centroid mode are supported. Defaulting to centroid '
                                                         'mode.')
                list_of_scan_dicts = parse_maldi_tsf(data, 1, num_frames, mode, ms2_only, profile_bins, encoding)
            # Parse TDF data.
            elif data.meta_data['SchemaType'] == 'TDF':
                list_of_scan_dicts = parse_maldi_tdf(data, 1, num_frames, mode, ms2_only, exclude_mobility,
                                                     profile_bins, encoding)

            # Parse plate map.
            plate_map_dict = parse_maldi_plate_map(plate_map)

            # Get coordinates for each condition replicate.
            conditions = [str(value) for key, value in plate_map_dict.items()]
            conditions = sorted(list(set(conditions)))

            dict_of_scan_lists = {}
            for i in conditions:
                dict_of_scan_lists[i] = []

            for key, value in plate_map_dict.items():
                try:
                    dict_of_scan_lists[value].append(key)
                except KeyError:
                    pass

            for key, value in dict_of_scan_lists.items():
                if key != 'nan':
                    output_filename = os.path.join(outdir, key + '.mzML')

                    writer = MzMLWriter(output_filename, close=True)

                    with writer:
                        writer.controlled_vocabularies()
                        write_mzml_metadata(data, writer, infile, mode, ms2_only, barebones_metadata)
                        with writer.run(id='run', instrument_configuration='instrument'):
                            scan_count = len(value)
                            with writer.spectrum_list(count=scan_count):
                                condition_scan_dicts = [i for i in list_of_scan_dicts if i['coord'] in value]
                                scan_count = 0
                                for scan_dict in condition_scan_dicts:
                                    if ms2_only == True and scan_dict['ms_level'] == 1:
                                        pass
                                    else:
                                        scan_count += 1
                                        scan_dict['scan_number'] = scan_count
                                        if scan_dict['ms_level'] == 1:
                                            write_maldi_dd_ms1_spectrum(writer, data, scan_dict, encoding, compression,
                                                                        title=key)
                                        elif scan_dict['ms_level'] == 2:
                                            write_maldi_dd_ms2_spectrum(writer, scan_dict, encoding, compression,
                                                                        title=key)

                    logging.info(get_timestamp() + ':' + 'Finished writing to .mzML file ' +
                                 os.path.join(outdir, outfile) + '...')
