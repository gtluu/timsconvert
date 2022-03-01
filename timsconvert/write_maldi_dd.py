from timsconvert.parse_maldi import *
from timsconvert.write_mzml import *
import os
import logging
import numpy as np
from psims.mzml import MzMLWriter


def write_maldi_dd_spectrum(writer, data, scan, encoding):
    # Build params
    params = [scan['scan_type'],
              {'ms level': scan['ms_level']},
              {'total ion current': scan['total_ion_current']},
              {'base peak m/z': scan['base_peak_mz']},
              {'base peak intensity': scan['base_peak_intensity']},
              {'highest observed m/z': scan['high_mz']},
              {'lowest observed m/z': scan['low_mz']},
              {'maldi spot identifier': scan['coord']}]

    if data.meta_data['SchemaType'] == 'TDF' and scan['ms_level'] == 1 and scan['mobility_array'] is not None:
        other_arrays = [('ion mobility array', scan['mobility_array'])]
    else:
        other_arrays = None

    if encoding == 32:
        encoding_dtype = np.float32
    elif encoding == 64:
        encoding_dtype = np.float64

    encoding_dict = {'m/z array': encoding_dtype,
                     'intensity array': encoding_dtype}
    if other_arrays is not None:
        encoding_dict['ion mobility array'] = encoding_dtype

    # Write out spectrum.
    writer.write_spectrum(scan['mz_array'],
                          scan['intensity_array'],
                          id='scan=' + str(scan['scan_number']),
                          polarity=scan['polarity'],
                          centroided=scan['centroided'],
                          scan_start_time=scan['retention_time'],
                          other_arrays=other_arrays,
                          params=params,
                          encoding=encoding_dict)


# Parse out MALDI DD data and write out mzML file using psims.
def write_maldi_dd_mzml(data, infile, outdir, outfile, mode, ms2_only, exclude_mobility, encoding, single_file,
                        plate_map, chunk_size):
    if single_file == 'combined':
        # Initialize mzML writer using psims.
        logging.info(get_timestamp() + ':' + 'Initializing mzML Writer...')
        writer = MzMLWriter(os.path.join(outdir, outfile), close=True)

        with writer:
            # Begin mzML with controlled vocabularies (CV).
            logging.info(get_timestamp() + ':' + 'Initializing controlled vocabularies...')
            writer.controlled_vocabularies()

            # Start write acquisition, instrument config, processing, etc. to mzML.
            logging.info(get_timestamp() + ':' + 'Writing mzML metadata...')
            write_mzml_metadata(data, writer, infile, mode, ms2_only)

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
                        list_of_scan_dicts = parse_maldi_tsf(data, 1, num_frames, mode, ms2_only, encoding)
                    # Parse TDF data.
                    elif data.meta_data['SchemaType'] == 'TDF':
                        list_of_scan_dicts = parse_maldi_tdf(data, 1, num_frames, mode, ms2_only, exclude_mobility,
                                                             encoding)
                    # Write MS1 parent scans.
                    for scan_dict in list_of_scan_dicts:
                        if ms2_only == True and scan_dict['ms_level'] == 1:
                            pass
                        else:
                            scan_count += 1
                            scan_dict['scan_number'] = scan_count
                            write_maldi_dd_spectrum(writer, data, scan_dict, encoding)

        logging.info(get_timestamp() + ':' + 'Updating scan count...')
        update_spectra_count(outdir, outfile, scan_count)
        logging.info(get_timestamp() + ':' + 'Finished writing to .mzML file ' + os.path.join(outdir, outfile) + '...')
    elif single_file == 'individual' and plate_map != '':
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
                list_of_scan_dicts = parse_maldi_tsf(data, 1, num_frames, mode, ms2_only, encoding)
            # Parse TDF data.
            elif data.meta_data['SchemaType'] == 'TDF':
                list_of_scan_dicts = parse_maldi_tdf(data, 1, num_frames, mode, ms2_only, exclude_mobility, encoding)

            # Use plate map to determine filename.
            # Names things as sample_position.mzML
            plate_map_dict = parse_maldi_plate_map(plate_map)

            for scan_dict in list_of_scan_dicts:
                output_filename = os.path.join(outdir, plate_map_dict[scan_dict['coord']] + '_' + scan_dict['coord'] +
                                               '.mzML')

                writer = MzMLWriter(output_filename, close=True)

                with writer:
                    writer.controlled_vocabularies()

                    write_mzml_metadata(data, writer, infile, mode, ms2_only)

                    with writer.run(id='run', instrument_configuration='instrument'):
                        scan_count = 1
                        scan_dict['scan_number'] = scan_count
                        with writer.spectrum_list(count=scan_count):
                            if ms2_only == True and scan_dict['ms_level'] == 1:
                                pass
                            else:
                                write_maldi_dd_spectrum(writer, data, scan_dict, encoding)
                logging.info(get_timestamp() + ':' + 'Finished writing to .mzML file ' +
                             os.path.join(outdir, output_filename) + '...')


if __name__ == '__main__':
    logger = logging.getLogger(__name__)
