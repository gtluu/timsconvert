import argparse
import os
import sys
from multiprocessing import cpu_count
from .timestamp import *


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
    parser.add_argument('--outfile', help='User defined filename for output if converting a single file. Default is'
                                          'none. Empty string.', default='', type=str)
    parser.add_argument('--centroid', help='Boolean to determine if data should be centroided. Defaults to True.',
                        default=True, type=bool)
    parser.add_argument('--ms2_centroiding_window', help='Centroiding window to be used for MS2 spectra. Default = 5.',
                        default=5, type=int)
    parser.add_argument('--ms2_keep_n_most_abundant_peaks', help='Keep N most abundant peaks in MS2 spectra. If -1, all'
                                                                 'peaks are kept. Defaults to -1.', default=-1,
                        type=int)
    parser.add_argument('--ms2_only', help='Boolean to determine whether to convert only MS2 spectra or all spectra.'
                                           'Defaults to True', default=True, type=bool)
    parser.add_argument('--ms1_groupby', help='Define whether an individual MS1 spectrum contains one frame (and'
                                              'multiple scans; "frame") or one scan ("scan"). Defaults to "scan".',
                        default='scan', type=str)

    # System Arguments
    parser.add_argument('--verbose', help='Boolean determining whether to print logging output. Defaults to False.',
                        default=False, type=bool)
    parser.add_argument('--cpu', help='Number of CPU threads to use. Defaults to number of cpu threads - 1.',
                        default=cpu_count()-1, type=int)

    # Return parser
    arguments = parser.parse_args()
    return vars(arguments)


# Checks to ensure arguments are valid.
def args_check(args):
    # Check if input directory exists.
    if not os.path.exists(args['input']):
        print(get_timestamp() + ':' + 'Input path does not exist...')
        print(get_timestamp() + ':' + 'Exiting...')
        sys.exit(1)
    # Check if output directory exists and create it if it does not.
    if not os.path.isdir(args['outdir']) and args['outdir'] != '':
        os.mkdir(args['outdir'])
    # Check to make sure output filename ends in .mzML extension.
    if os.path.splitext(args['outfile']) != 'mzML' and args['outfile'] != '':
        args['outfile'] = args['outfile'] + '.mzML'
    # Check to make sure --ms1_groupby is either 'frame' or 'scan'.
    if args['ms1_groupby'] not in ['frame', 'scan']:
        print(get_timestamp() + ':' + '--ms1_groupby should be set to "frame" or "scan"...')
        print(get_timestamp() + ':' + 'Exiting...')
        sys.exit(1)
    # Check CPU thread count settings.
    if args['cpu'] > cpu_count():
        print(get_timestamp() + ':' + 'Number of threads specified exceeds number of available threads...')
        print(get_timestamp() + ':' + 'Your computer has ' + str(cpu_count()) + ' usable threads...')
        print(get_timestamp() + ':' + 'Exiting...')
        sys.exit(1)
    return args


# Write parameters used to run BLANKA to text file.
def write_params(args, logfile):
    with open(os.path.join(os.path.split(logfile)[0], 'parameters_' + get_timestamp() + '.txt'), 'a') as params:
        for key, value in args.items():
            params.write('[' + str(key) + ']' + '\n' + str(value) + '\n')
