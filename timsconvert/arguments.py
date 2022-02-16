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
    parser.add_argument('--input', help='Filepath for Bruker .d file containing TSF or TDF file or directory containing'
                                        'multiple Bruker .d files.', required=True, type=str)

    # Optional Arguments
    parser.add_argument('--experiment', help='Experiment performed to generate data. Should be lc-tims-ms, maldi-dd,'
                                             'maldi-tims-dd, maldi-ims, or maldi-tims-ims.', default='lc-tims-ms',
                        type=str)
    parser.add_argument('--outdir', help='Path to folder in which to write output file(s). Default = none', default='',
                        type=str)
    parser.add_argument('--outfile', help='User defined filename for output if converting a single file, otherwise'
                                          'files will have same filename and overwrite each other. Default is'
                                          'none. Empty string.', default='', type=str)
    parser.add_argument('--mode', help='Choose whether export spectra in "raw", "centroid", or "profile" formats. '
                                       'Defaults to "raw".', default='raw', type=str)
    parser.add_argument('--ms2_only', help='Boolean flag that specifies only MS2 spectra should be converted.',
                        action='store_true')
    parser.add_argument('--ms1_groupby', help='Define whether an individual MS1 spectrum contains one frame (and'
                                              'multiple scans; "frame") or one scan ("scan"). Defaults to "scan".',
                        default='scan', type=str)
    parser.add_argument('--encoding', help='Choose encoding for binary arrays: 32-bit ("32") or 64-bit ("64"). Defaults'
                                           ' to 64-bit.', default=64, type=int)
    parser.add_argument('--maldi_output_file', help='For MALDI dried droplet data, whether individual scans should be '
                                                    'placed in individual files ("individual") or all into a single '
                                                    'file ("combined"). Defaults to "combined".', default='combined',
                        type=str)
    parser.add_argument('--maldi_plate_map', help='Plate map to be used for parsing spots if --maldi_output_file == '
                                                  '"individual". Should be a .csv file with no header/index.',
                        default='', type=str)
    parser.add_argument('--imzml_mode', help='Whether .imzML files should be written in "processed" or "continuous" '
                                             'mode. Defaults to "processed".', default='processed', type=str)

    # System Arguments
    parser.add_argument('--chunk_size', help='Relative size of chunks of spectral data that are parsed and '
                                             'subsequently at once. Increasing parses and write more spectra at once '
                                             'but increases RAM usage. Default = 10.', default=10, type=int)
    parser.add_argument('--verbose', help='Boolean flag to detemrine whether to print logging output.',
                        action='store_true')

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
    # Check to make sure experiment type is correct.
    experiments = ['lc-tims-ms', 'maldi-dd', 'maldi-tims-dd', 'maldi-ims', 'maldi-tims-ims']
    if args['experiment'] not in experiments:
        logging.info(get_timestamp() + ':' + 'Experiment not valid. Use one of the following: "lc-tims-ms", "maldi-dd",'
                                             ' "maldi-tims-dd", "maldi-ims", or "maldi-tims-ims"...')
        logging.info(get_timestamp() + ':' + 'Exiting...')
        sys.exit(1)
    mode = ['raw', 'centroid', 'profile']
    if args['mode']  not in mode:
        logging.info(get_timestamp() + ':' + 'Mode not valid. Use one of the following: "raw", "centroid", or '
                                             '"profile"...')
        logging.info(get_timestamp() + ':' + 'Exiting...')
        sys.exit(1)
    # Check if output directory exists and create it if it does not.
    if not os.path.isdir(args['outdir']) and args['outdir'] != '':
        os.mkdir(args['outdir'])
    # Check to make sure output filename ends in .mzML extension.
    if os.path.splitext(args['outfile']) != '.mzML' and args['outfile'] != '':
        args['outfile'] = args['outfile'] + '.mzML'
    # Check to make sure --ms1_groupby is either 'frame' or 'scan'.
    if args['ms1_groupby'] not in ['frame', 'scan']:
        logging.info(get_timestamp() + ':' + '--ms1_groupby should be set to "frame" or "scan"...')
        logging.info(get_timestamp() + ':' + 'Exiting...')
        sys.exit(1)
    # Check to make sure --encoding is either 32 or 64.
    if args['encoding'] not in [32, 64]:
        logging.info(get_timestamp() + ':' + '--encoding should be set to "32" or "64"...')
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


if __name__ == '__main__':
    logger = logging.getLogger(__name__)
