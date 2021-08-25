import argparse
import os
import sys
import logging
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
    parser.add_argument('--outfile', help='User defined filename for output if converting a single file, otherwise'
                                          'files will have same filename and overwrite each other. Default is'
                                          'none. Empty string.', default='', type=str)
    parser.add_argument('--centroid', help='Boolean to determine if data should be centroided. Defaults to True.',
                        default=True, type=bool)
    parser.add_argument('--ms2_only', help='Boolean to determine whether to convert only MS2 spectra or all spectra.'
                                           'Defaults to True', default=True, type=bool)
    parser.add_argument('--ms1_groupby', help='Define whether an individual MS1 spectrum contains one frame (and'
                                              'multiple scans; "frame") or one scan ("scan"). Defaults to "scan".',
                        default='scan', type=str)

    # Advanced MS1 Centroiding Arguments: taken from ms_peak_picker.pick_peaks()
    parser.add_argument('--ms1_fit_type', help='Name of the peak model to use: "quadratic", "gaussian", "lorentzian",'
                                               'or "apex". Defaults to "quadratic".', default='gaussian', type=str)
    parser.add_argument('--ms1_peak_mode', help='Whether peaks are in "profile" mode or are pre"centroid"ed.'
                                                'Defaults to "profile".', default='profile', type=str)
    parser.add_argument('--ms1_signal_to_noise_threshold', help='Minimum signal-to-noise measurement to accept a peak.'
                                                                'Defaults to 1.0.', default=1.0, type=float)
    parser.add_argument('--ms1_intensity_threshold', help='Minimum intensity measurement to accept a peak. Defaults to'
                                                          ' 1.0.', default=1.0, type=float)
    parser.add_argument('--ms1_threshold_data', help='Boolean for whether to apply thresholds to the data. Defaults to'
                                                     'False.', default=False, type=bool)
    parser.add_argument('--ms1_target_envelopes', help='Sequence of (start m/z, end m/z) paris, limiting peak picking'
                                                       ' to only those intervals. Defaults to None', default=None,
                        type=list)
    parser.add_argument('--ms1_transforms', help='List of :class:`scan_filter.FilterBase` instances or callable that '
                                                 'accepts (mz_array, intensity_array) and returns (mz_array, '
                                                 'intensity_array) or `str` matching one of the premade names in '
                                                 '`scan_filter.filter_register`. Defaults to None.', default=None,
                        type=list)
    parser.add_argument('--ms1_verbose', help='Boolean for whether to log extra information while picking peaks. '
                                              'Defaults to False.', default=False, type=bool)
    parser.add_argument('--ms1_start_mz', help='A minimum m/z value to start picking peaks from. Defaults to None.',
                        default=None, type=float)
    parser.add_argument('--ms1_stop_mz', help='A maximum m/z value to stop picking peaks after. Defaults to None.',
                        default=None, type=float)
    parser.add_argument('--ms1_integrate', help='Boolean for whether to integrate along each peak to calculate the '
                                                'area. Defaults to True, but the area value for each peak is not '
                                                'usually used by downstream algorithms for consistency, so this '
                                                'expensive operation can be omitted.', default=True, type=bool)

    # Advanced MS2 Centroiding Arguments: taken from alphatims.bruker.centroid_spectrum()
    parser.add_argument('--ms2_centroiding_window', help='Centroiding window to be used for MS2 spectra. Default = 5.',
                        default=5, type=int)
    parser.add_argument('--ms2_keep_n_most_abundant_peaks', help='Keep N most abundant peaks in MS2 spectra. If -1, all'
                                                                 'peaks are kept. Defaults to -1.', default=-1,
                        type=int)

    # System Arguments
    parser.add_argument('--verbose', help='Boolean determining whether to print logging output. Defaults to False.',
                        default=False, type=bool)

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
