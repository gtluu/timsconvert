import argparse
import os
import sys
import logging
import requests
from timsconvert.timestamp import *


def arg_descriptions():
    descriptions = {'input': 'Filepath for Bruker .d file containing TSF or TDF file or directory containing multiple '
                             'Bruker .d files.',
                    'outdir': 'Path to folder in which to write output file(s). Default = none',
                    'outfile': 'User defined filename for output if converting a single file, otherwise files will '
                               'have same filename and overwrite each other. Default is none.',
                    'mode': 'Choose whether export to spectra in "raw" or "centroid" formats. Defaults to "centroid".',
                    'compression': 'Choose between ZLIB compression ("zlib") or no compression ("none"). Defaults to '
                                   '"zlib".',
                    'ms2_only': 'Boolean flag that specifies only MS2 spectra should be converted.',
                    'exclude_mobility': 'Boolean flag used to exclude trapped ion mobility spectrometry data from '
                                        'exported data. Precursor ion mobility information is still exported.',
                    'encoding': 'Choose encoding for binary arrays: 32-bit ("32") or 64-bit ("64"). Defaults to '
                                '64-bit.',
                    'profile_bins': 'Number of bins used to bin data when converting in profile mode. A value of 0 '
                                    'indicates no binning is performed. Defaults to 0.',
                    'barebones_metadata': 'Only use basic mzML metadata. Use if downstream data analysis tools throw '
                                          'errors with descriptive CV terms.',
                    'maldi_output_file': 'For MALDI dried droplet data, whether individual scans should be placed in '
                                         'individual files ("individual"), combined into a single file ("combined"), '
                                         'or combined by sample label ("sample"). Defaults to "combined".',
                    'maldi_plate_map': 'Plate map to be used for parsing spots if --maldi_output_file == "individual" '
                                       'or --maldi_output_file == "sample". Should be a .csv file with no '
                                       'header/index.',
                    'imzml_mode': 'Whether .imzML files should be written in "processed" or "continuous" mode. '
                                  'Defaults to "processed".',
                    'lcms_backend': 'Choose whether to use "timsconvert" or "tdf2mzml" backend for LC-TIMS-MS/MS data '
                                    'conversion.',
                    'chunk_size': 'Relative size of chunks of spectral data that are parsed and subsequently written '
                                  'at once. Increasing parses and write more spectra at once but increases RAM usage. '
                                  'Default = 10.',
                    'verbose': 'Boolean flag to determine whether to print logging output.',
                    'url': 'URL for server to run TIMSCONVERT (if submitting job through API). Default = GNPS server',
                    'start_frame': 'Start frame.',
                    'end_frame': 'End frame.',
                    'precision': 'Precision.',
                    'ms1_threshold': 'Intensity threshold for MS1 data.',
                    'ms2_threshold': 'Intensity threshold for MS2 data.',
                    'ms2_nlargest': 'N Largest MS2.'}
    return descriptions


# Parse arguments for CLI usage
def get_args(server=False):
    desc = arg_descriptions()

    # Initialize parser.
    parser = argparse.ArgumentParser()

    # Require Arguments
    required = parser.add_argument_group('Required Parameters')
    required.add_argument('--input', help=desc['input'], required=True, type=str)

    # Optional Arguments
    optional = parser.add_argument_group('Optional Parameters')
    optional.add_argument('--outdir', help=desc['outdir'], default='', type=str)
    optional.add_argument('--outfile', help=desc['outfile'], default='', type=str)
    optional.add_argument('--mode', help=desc['mode'], default='centroid', type=str, choices=['raw', 'centroid', 'profile'])
    optional.add_argument('--compression', help=desc['compression'], default='zlib', type=str, choices=['zlib', 'none'])

    # TIMSCONVERT Arguments
    timsconvert_args = parser.add_argument_group('TIMSCONVERT Optional Parameters')
    timsconvert_args.add_argument('--ms2_only', help=desc['ms2_only'], action='store_true')
    timsconvert_args.add_argument('--exclude_mobility', help=desc['exclude_mobility'], action='store_true')
    timsconvert_args.add_argument('--encoding', help=desc['encoding'], default=64, type=int, choices=[32, 64])
    timsconvert_args.add_argument('--barebones_metadata', help=desc['barebones_metadata'], action='store_true')
    timsconvert_args.add_argument('--profile_bins', help=desc['profile_bins'], default=0, type=int)
    timsconvert_args.add_argument('--maldi_output_file', help=desc['maldi_output_file'], default='combined', type=str,
                                  choices=['combined', 'individual', 'sample'])
    timsconvert_args.add_argument('--maldi_plate_map', help=desc['maldi_plate_map'], default='', type=str)
    timsconvert_args.add_argument('--imzml_mode', help=desc['imzml_mode'], default='processed', type=str,
                                  choices=['processed', 'continuous'])

    # TIMSCONVERT System Arguments
    system = parser.add_argument_group('TIMSCONVERT System Parameters')
    system.add_argument('--lcms_backend', help=desc['lcms_backend'], default='timsconvert', type=str,
                        choices=['timsconvert', 'tdf2mzml'])
    system.add_argument('--chunk_size', help=desc['chunk_size'], default=10, type=int)
    system.add_argument('--verbose', help=desc['verbose'], action='store_true')
    if server:
        # change to GNPS URL later
        system.add_argument('--url', help=desc['url'], default='http://localhost:5000', type=str)

    # tdf2mzml Arguments
    tdf2mzml_args = parser.add_argument_group('tdf2mzml Optional Parameters')
    tdf2mzml_args.add_argument('--start_frame', help=desc['start_frame'], default=-1, type=int)
    tdf2mzml_args.add_argument('--end_frame', help=desc['end_frame'], default=-1, type=int)
    tdf2mzml_args.add_argument('--precision', help=desc['precision'], default=10.0, type=float)
    tdf2mzml_args.add_argument('--ms1_threshold', help=desc['ms1_threshold'], default=100, type=float)
    tdf2mzml_args.add_argument('--ms2_threshold', help=desc['ms2_threshold'], default=10, type=float)
    tdf2mzml_args.add_argument('--ms2_nlargest', help=desc['ms2_nlargest'], default=-1, type=int)

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
    # Check if output directory exists and create it if it does not.
    if not os.path.isdir(args['outdir']) and args['outdir'] != '':
        os.makedirs(args['outdir'])
    # Check to make sure output filename ends in .mzML extension.
    if os.path.splitext(args['outfile']) != '.mzML' and args['outfile'] != '':
        args['outfile'] = args['outfile'] + '.mzML'
    # Check if plate map path is valid and if plate map is available if --maldi_single_file is True.
    if args['maldi_output_file'] != '' and args['maldi_output_file'] in ['individual', 'sample']:
        if args['maldi_plate_map'] == '':
            logging.info(get_timestamp() + ':' + 'Plate map is required for MALDI dried droplet data...')
            logging.info(get_timestamp() + ':' + 'Exiting...')
            sys.exit(1)
        else:
            if not os.path.exists(args['maldi_plate_map']):
                logging.info(get_timestamp() + ':' + 'Plate map path does not exist...')
                logging.info(get_timestamp() + ':' + 'Exiting...')
                sys.exit(1)
    # Check if server URL is valid.
    if 'url' in args.keys():
        response = requests.get(args['url'])
        if response.status_code != 200:
            logging.info(get_timestamp() + ':' + 'URL is not valid or server is down...')
            logging.info(get_timestamp() + ':' + 'Exiting...')
            response.raise_for_status()
    return args
