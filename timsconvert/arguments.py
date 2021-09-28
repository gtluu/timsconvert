import argparse
import os
import sys
from timsconvert.timestamp import *


# Parse arguments for CLI usage
def get_args():
    # Initialize parser.
    parser = argparse.ArgumentParser()

    # Require Arguments
    parser.add_argument('--input', help='Filepath for Bruker .d file containing TDF file or directory containing'
                                        'multiple Bruker .d files.', required=True, type=str)

    # Optional Arguments
    parser.add_argument('--outdir', help='Path to folder in which to write output file(s). Default = none', default='',
                        type=str)
    parser.add_argument('--outfile', help='User defined filename for output if converting a single file, otherwise'
                                          'files will have same filename and overwrite each other. Default is'
                                          'none. Empty string.', default='', type=str)
    parser.add_argument('--ms2_only', help='Boolean to only use MS2 spectra.', action='store_true')
    parser.add_argument('--ms1_groupby', help='Define whether an individual MS1 spectrum contains one frame (and'
                                              'multiple scans; "frame") or one scan ("scan"). Defaults to "scan".',
                        default='scan', type=str)
    parser.add_argument('--encoding', help='Choose encoding: 32-bit ("32") or 64-bit ("64"). Defaults to 32-bit.',
                        default=32, type=int)

    # Advanced MS2 Centroiding Arguments: taken from alphatims.bruker.centroid_spectrum()
    parser.add_argument('--ms2_keep_n_most_abundant_peaks', help='Keep N most abundant peaks in MS2 spectra. If -1, all'
                                                                 'peaks are kept. Defaults to -1.', default=-1,
                        type=int)

    # System Arguments
    parser.add_argument('--verbose', help='Boolean to print logging output.', action='store_true')

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
        os.mkdir(args['outdir'])
    # Check to make sure output filename ends in .mzML extension.
    if os.path.splitext(args['outfile']) != '.mzML' and args['outfile'] != '':
        args['outfile'] = args['outfile'] + '.mzML'
    # Check to make sure --ms1_groupby is either 'frame' or 'scan'.
    if args['ms1_groupby'] not in ['frame', 'scan']:
        logging.info(get_timestamp() + ':' + '--ms1_groupby should be set to "frame" or "scan"...')
        logging.info(get_timestamp() + ':' + 'Exiting...')
        sys.exit(1)
    return args


if __name__ == '__main__':
    logger = logging.getLogger(__name__)
