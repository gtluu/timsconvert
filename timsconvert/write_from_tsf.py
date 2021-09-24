import os
import numpy as np
from psims.mzml import MzMLWriter
from pyimzml.ImzMLWriter import ImzMLWriter
from timsconvert.constants import *
from timsconvert.parse_tsf import *
from timsconvert.write_mzml import *


def write_maldi_dd_mzml(tsf_data, outdir, outfile, ms2_only, centroid=True, encoding=0, single_file=True, plate_map=''):
    if single_file == True:
        # Initialize the mzML writer.
        writer = MzMLWriter(os.path.join(outdir, outfile))

        with writer:
            writer.controlled_vocabularies()

            write_mzml_metadata(tsf_data, writer, ms2_only, centroid)

            # Begin writing out data.
            list_of_scan_dicts = parse_maldi_tsf(tsf_data, centroid)

            for scan_dict in list_of_scan_dicts:
                # Set params for scan.
                params = [scan_dict['scan_type'],
                          {'ms level': scan_dict['ms_level']},
                          {'total ion current': scan_dict['total_ion_current']},
                          {'base peak m/z': scan_dict['base_peak_mz']},
                          {'base peak intensity': scan_dict['base_peak_intensity']},
                          {'highest observed m/z': scan_dict['high_mz']},
                          {'lowest observed m/z': scan_dict['low_mz']},
                          {'maldi spot identifier': scan_dict['coord']}]

                # Set encoding if necessary.
                if encoding != 0:
                    if encoding == 32:
                        encoding_dtype = np.float32
                    elif encoding == 64:
                        encoding_dtype = np.float64

                # Write out spectrum
                writer.write_spectrum(scan_dict['mz_array'],
                                      scan_dict['intensity_array'],
                                      id='scan=' + str(scan_dict['scan_number']),
                                      polarity=scan_dict['polarity'],
                                      centroided=scan_dict['centroided'],
                                      scan_start_time=scan_dict['retention_time'],
                                      params=params,
                                      encoding={'m/z array': encoding_dtype,
                                                'intensity array': encoding_dtype})

    elif single_file == False and plate_map != '':
        # Check to make sure plate map is a valid csv file.
        if os.path.exists(plate_map) and os.path.splitext(plate_map)[1] == 'csv':
            # Parse all MALDI data.
            list_of_scan_dicts = parse_maldi_tsf(tsf_data, centroid)

            # Use plate map to determine filename.
            # Names things as 'sample_position.mzML
            plate_map_dict = parse_maldi_plate_map(plate_map)

            for scan_dict in list_of_scan_dicts:
                output_filename = os.path.join(outdir,
                                               plate_map_dict[scan_dict['coord']] + '_' + scan_dict['coord'] + '.mzML')

                writer = MzMLWriter(output_filename)

                with writer:
                    writer.controlled_vocabularies()

                    write_mzml_metadata(tsf_data, writer, ms2_only, centroid)

                    # Set params for scan.
                    params = [scan_dict['scan_type'],
                              {'ms level': scan_dict['ms_level']},
                              {'total ion current': scan_dict['total_ion_current']},
                              {'base peak m/z': scan_dict['base_peak_mz']},
                              {'base peak intensity': scan_dict['base_peak_intensity']},
                              {'highest observed m/z': scan_dict['high_mz']},
                              {'lowest observed m/z': scan_dict['low_mz']},
                              {'maldi spot identifier': scan_dict['coord']}]

                    # Set encoding if necessary.
                    if encoding != 0:
                        if encoding == 32:
                            encoding_dtype = np.float32
                        elif encoding == 64:
                            encoding_dtype = np.float64

                    # Write out spectrum
                    writer.write_spectrum(scan_dict['mz_array'],
                                          scan_dict['intensity_array'],
                                          id='scan=' + str(scan_dict['scan_number']),
                                          polarity=scan_dict['polarity'],
                                          centroided=scan_dict['centroided'],
                                          scan_start_time=scan_dict['retention_time'],
                                          params=params,
                                          encoding={'m/z array': encoding_dtype,
                                                    'intensity array': encoding_dtype})


def write_maldi_ims_imzml(tsf_data, outdir, outfile, mode='processed', centroid=True):
    list_of_scan_dicts = parse_maldi_tsf(tsf_data, centroid)

    polarity = list(set(tsf_data.frames['Polarity'].values.tolist()))
    if len(polarity) == 1:
        polarity = polarity[0]
        if polarity == '+':
            polarity = 'positive'
        elif polarity == '-':
            polarity = 'negative'
        else:
            polarity = None
    else:
        polarity = None

    writer = ImzMLWriter(os.path.join(outdir, outfile),
                         polarity=polarity,
                         mode=mode,
                         spec_type=centroid)

    with writer as imzml_file:
        for scan_dict in list_of_scan_dicts:
            imzml_file.addSpectrum(scan_dict['mz_array'],
                                   scan_dict['intensity_array'],
                                   scan_dict['coord'])
