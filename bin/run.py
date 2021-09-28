import copy
from timsconvert import *


def run_tims_converter(args):
    # Initialize Bruker DLL.
    bruker_dll = init_bruker_dll(BRUKER_DLL_FILE_NAME)

    # Load in input data.
    logging.info(get_timestamp() + ':' + 'Loading input data...')
    if not args['input'].endswith('.d'):
        input_files = dot_d_detection(args['input'])
    elif args['input'].endswith('.d'):
        input_files = [args['input']]

    # Convert each sample
    for infile in input_files:
        # Reset args.
        run_args = copy.deepcopy(args)

        # Set input file.
        run_args['infile'] = infile
        # Set output directory to default if not specified.
        if run_args['outdir'] == '':
            run_args['outdir'] = os.path.split(infile)[0]
        # Make output filename the default filename if not specified.
        if run_args['outfile'] == '':
            run_args['outfile'] = os.path.splitext(os.path.split(infile)[-1])[0] + '.mzML'

        logging.info(get_timestamp() + ':' + 'Reading file: ' + infile)
        schema = schema_detection(infile)
        if schema == 'TSF':
            data = tsf_data(infile, bruker_dll)
        elif schema == 'TDF':
            data = bruker_to_df(infile)
            if 'MaldiApplicationType' in data.meta_data.keys():
                data = tdf_data(infile, bruker_dll)
        logging.info(get_timestamp() + ':' + 'Writing to file: ' + os.path.join(run_args['outdir'],
                                                                                run_args['outfile']))
        # Log arguments.
        for key, value in run_args.items():
            logging.info(get_timestamp() + ':' + str(key) + ': ' + str(value))

        if schema == 'TSF':
            if data.meta_data['MaldiApplicationType'] == 'SingleSpectra':
                if args['maldi_plate_map'] == '':
                    logging.info(get_timestamp() + ':' + 'Plate map is required for MALDI dried droplet data...')
                    logging.info(get_timestamp() + ':' + 'Exiting...')
                    sys.exit(1)
                write_maldi_dd_mzml(data, args['outdir'], args['outfile'], args['ms2_only'], args['ms1_groupby'],
                                    args['centroid'], args['encoding'], args['maldi_single_file'],
                                    args['maldi_plate_map'])
            elif data.meta_data['MaldiApplicationType'] == 'Imaging':
                write_maldi_ims_imzml(data, args['outdir'], args['outfile'], 'frame', args['imzml_mode'],
                                      args['centroid'])
        elif schema == 'TDF':
            if 'MaldiApplicationType' in data.meta_data.keys():
                if data.meta_data['MaldiApplicationType'] == 'SingleSpectra':
                    if args['maldi_plate_map'] == '':
                        logging.info(get_timestamp() + ':' + 'Plate map is required for MALDI dried droplet data...')
                        logging.info(get_timestamp() + ':' + 'Exiting...')
                        sys.exit(1)
                    write_maldi_dd_mzml(data, args['outdir'], args['outfile'], args['ms2_only'], args['ms1_groupby'],
                                        args['centroid'], args['encoding'], args['maldi_single_file'],
                                        args['maldi_plate_map'])
                elif data.meta_data['MaldiApplicationType'] == 'Imaging':
                    write_maldi_ims_imzml(data, args['outdir'], args['outfile'], 'frame', args['imzml_mode'],
                                          args['centroid'])
            elif 'MaldiApplicationType' not in data.meta_data.keys():
                write_lcms_mzml(data, args['infile'], args['outdir'], args['outfile'], args['centroid'],
                                args['ms2_only'], args['ms1_groupby'], args['encoding'],
                                args['ms2_keep_n_most_abundant_peaks'])
        run_args.clear()


if __name__ == '__main__':
    # Parse arguments.
    arguments = get_args()
    # Hardcode centroid to True. Current code does not support profile.
    arguments['centroid'] = True

    # Check arguments.
    args_check(arguments)
    arguments['version'] = '0.1.0'

    # Initialize logger.
    logname = 'log_' + get_timestamp() + '.log'
    if arguments['outdir'] == '':
        if os.path.isdir(arguments['input']):
            logfile = os.path.join(arguments['input'], logname)
        else:
            logfile = os.path.split(arguments['input'])[0]
            logfile = os.path.join(logfile, logname)
    else:
        logfile = os.path.join(arguments['outdir'], logname)
    for handler in logging.root.handlers[:]:
        logging.root.removeHandler(handler)
    logging.basicConfig(filename=logfile, level=logging.INFO)
    if arguments['verbose']:
        logging.getLogger().addHandler(logging.StreamHandler(sys.stdout))
    logger = logging.getLogger(__name__)

    # Run.
    run_tims_converter(arguments)
