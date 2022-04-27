import argparse
import os
import sys
import logging
from timsconvert.timestamp import *


# Parse arguments for CLI usage
def get_args():
    # Initialize parser.
    parser = argparse.ArgumentParser()

    # Require Arguments
    required = parser.add_argument_group('Required Parameters')
    required.add_argument('--input', help='Filepath for Bruker .d file containing TSF or TDF file or directory '
                                          'containing multiple Bruker .d files.', required=True, type=str)

    # Optional Arguments
    optional = parser.add_argument_group('Optional Parameters')
    optional.add_argument('--outdir', help='Path to folder in which to write output file(s). Default = none',
                          default='',type=str)
    optional.add_argument('--outfile', help='User defined filename for output if converting a single file, otherwise '
                                            'files will have same filename and overwrite each other. Default is none. '
                                            'Empty string.', default='', type=str)
    optional.add_argument('--mode', help='Choose whether export to spectra in "raw", "centroid", or "profile" formats. '
                                         'Defaults to "centroid".', default='centroid', type=str)
    optional.add_argument('--compression', help='Choose between ZLIB compression ("zlib") or no compression ("none"). '
                                                'Defaults to "zlib".', default='zlib', type=str)

    # TIMSCONVERT Arguments
    timsconvert_args = parser.add_argument_group('TIMSCONVERT Optional Parameters')
    timsconvert_args.add_argument('--ms2_only', help='Boolean flag that specifies only MS2 spectra should be '
                                                     'converted.', action='store_true')
    timsconvert_args.add_argument('--exclude_mobility', help='Boolean flag used to exclude trapped ion mobility '
                                                             'spectrometry data from exported data. Precursor ion '
                                                             'mobility information is still exported. Recommended when '
                                                             'exporting in profile mode due to file size.',
                                  action='store_true')
    timsconvert_args.add_argument('--encoding', help='Choose encoding for binary arrays: 32-bit ("32") or 64-bit '
                                                     '("64"). Defaults to 64-bit.', default=64, type=int)
    timsconvert_args.add_argument('--profile_bins', help='Number of bins used to bin data when converting in profile '
                                                         'mode. A value of 0 indicates no binning is performed. '
                                                         'Defaults to 0.', default=0, type=int)
    timsconvert_args.add_argument('--maldi_output_file', help='For MALDI dried droplet data, whether individual scans '
                                                              'should be placed in individual files ("individual") or '
                                                              'all into a single file ("combined"). Defaults to '
                                                              '"combined".', default='combined', type=str)
    timsconvert_args.add_argument('--maldi_plate_map', help='Plate map to be used for parsing spots if '
                                                            '--maldi_output_file == "individual". Should be a .csv '
                                                            'file with no header/index.', default='', type=str)
    timsconvert_args.add_argument('--imzml_mode', help='Whether .imzML files should be written in "processed" or '
                                                       '"continuous" mode. Defaults to "processed".',
                                  default='processed', type=str)

    # TIMSCONVERT System Arguments
    system = parser.add_argument_group('TIMSCONVERT System Parameters')
    system.add_argument('--lcms_backend', help='Choose whether to use "timsconvert" or "tdf2mzml" backend for '
                                               'LC-TIMS-MS/MS data conversion.', default='timsconvert', type=str)
    system.add_argument('--chunk_size', help='Relative size of chunks of spectral data that are parsed and '
                                             'subsequently written at once. Increasing parses and write more spectra '
                                             'at once but increases RAM usage. Default = 10.', default=10, type=int)
    system.add_argument('--verbose', help='Boolean flag to detemrine whether to print logging output.',
                        action='store_true')

    # tdf2mzml Arguments
    tdf2mzml_args = parser.add_argument_group('tdf2mzml Optional Parameters')
    tdf2mzml_args.add_argument('--start_frame', help='Start frame.', default=-1, type=int)
    tdf2mzml_args.add_argument('--end_frame', help='End frame.', default=-1, type=int)
    tdf2mzml_args.add_argument('--precision', help='Precision.', default=10.0, type=float)
    tdf2mzml_args.add_argument('--ms1_threshold', help='Intensity threshold for MS1 data.', default=100, type=float)
    tdf2mzml_args.add_argument('--ms2_threshold', help='Intensity threshold for MS2 data.', default=10, type=float)
    tdf2mzml_args.add_argument('--ms2_nlargest', help='N Largest MS2.', default=-1, type=int)

    # Return parser
    arguments = parser.parse_args()
    return vars(arguments)


# Checks to ensure arguments are valid.
def args_check(args):
    # Check if input directory exists.
    if not os.path.exists(args['input']):
        logging.info(get_timestamp() + ':' + 'Input path does not exist...')
        logging.info(get_timestamp() + ':' + 'Exiting...')
        sys.exit(1)
    mode = ['raw', 'centroid', 'profile']
    if args['mode'] not in mode:
        logging.info(get_timestamp() + ':' + 'Mode not valid. Use one of the following: "raw", "centroid", or '
                                             '"profile"...')
        logging.info(get_timestamp() + ':' + 'Exiting...')
        sys.exit(1)
    # Check if output directory exists and create it if it does not.
    if not os.path.isdir(args['outdir']) and args['outdir'] != '':
        os.makedirs(args['outdir'])
    # Check to make sure output filename ends in .mzML extension.
    if os.path.splitext(args['outfile']) != '.mzML' and args['outfile'] != '':
        args['outfile'] = args['outfile'] + '.mzML'
    # Check to make sure --encoding is either 32 or 64.
    if args['encoding'] not in [32, 64]:
        logging.info(get_timestamp() + ':' + '--encoding should be set to "32" or "64"...')
        logging.info(get_timestamp() + ':' + 'Exiting...')
        sys.exit(1)
    # Check to make sure --compression is either zlib or none.
    if args['compression'] not in ['zlib', 'none']:
        logging.info(get_timestamp() + ':' + '--compression should be set to "zlib" or "none"...')
        logging.info(get_timestamp() + ':' + 'Exiting...')
        sys.exit(1)
    # Check if plate map path is valid and if plate map is available if --maldi_single_file is True.
    if args['maldi_output_file'] != '' and args['maldi_output_file'] == 'individual':
        if args['maldi_plate_map'] == '':
            logging.info(get_timestamp() + ':' + 'Plate map is required for MALDI dried droplet data...')
            logging.info(get_timestamp() + ':' + 'Exiting...')
            sys.exit(1)
        else:
            if not os.path.exists(args['maldi_plate_map']):
                logging.info(get_timestamp() + ':' + 'Plate map path does not exist...')
                logging.info(get_timestamp() + ':' + 'Exiting...')
                sys.exit(1)
    if args['imzml_mode'] not in ['processed', 'continuous']:
        logging.info(get_timestamp() + ':' + '--imzml_mode should be set to "processed" or "continuous"...')
        logging.info(get_timestamp() + ':' + 'Exiting...')
        sys.exit(1)
    return args
