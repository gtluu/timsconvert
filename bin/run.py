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
                if run_args['maldi_output_file'] == 'individual':
                    if run_args['maldi_plate_map'] == '':
                        logging.info(get_timestamp() + ':' + 'Plate map is required for MALDI dried droplet data in '
                                                             'multiple file mode...')
                        logging.info(get_timestamp() + ':' + 'Exiting...')
                        sys.exit(1)
                elif run_args['maldi_output_file'] == '':
                    logging.info(get_timestamp() + ':' + 'MALDI output file mode must be specified ("individual" or '
                                                         '"combined")...')
                    logging.info(get_timestamp() + ':' + 'Exiting...')
                    sys.exit(1)
                write_maldi_dd_mzml(data, run_args['infile'], run_args['outdir'], run_args['outfile'],
                                    run_args['ms2_only'], run_args['ms1_groupby'], run_args['centroid'],
                                    run_args['encoding'], run_args['maldi_output_file'], run_args['maldi_plate_map'])
            elif data.meta_data['MaldiApplicationType'] == 'Imaging':
                write_maldi_ims_imzml(data, run_args['outdir'], run_args['outfile'], 'frame', run_args['encoding'],
                                      run_args['imzml_mode'], run_args['centroid'])
        elif schema == 'TDF':
            if 'MaldiApplicationType' in data.meta_data.keys():
                if data.meta_data['MaldiApplicationType'] == 'SingleSpectra':
                    if run_args['maldi_output_file'] == 'individual':
                        if run_args['maldi_plate_map'] == '':
                            logging.info(
                                get_timestamp() + ':' + 'Plate map is required for MALDI dried droplet data in '
                                                        'multiple file mode...')
                            logging.info(get_timestamp() + ':' + 'Exiting...')
                            sys.exit(1)
                    elif run_args['maldi_output_file'] == '':
                        logging.info(
                            get_timestamp() + ':' + 'MALDI output file mode must be specified ("individual" or '
                                                    '"combined")...')
                        logging.info(get_timestamp() + ':' + 'Exiting...')
                        sys.exit(1)
                    write_maldi_dd_mzml(data, run_args['infile'], run_args['outdir'], run_args['outfile'],
                                        run_args['ms2_only'], run_args['ms1_groupby'], run_args['centroid'],
                                        run_args['encoding'], run_args['maldi_output_file'],
                                        run_args['maldi_plate_map'])
                elif data.meta_data['MaldiApplicationType'] == 'Imaging':
                    write_maldi_ims_imzml(data, run_args['outdir'], run_args['outfile'], 'frame', run_args['encoding'],
                                          run_args['imzml_mode'], run_args['centroid'])
            elif 'MaldiApplicationType' not in data.meta_data.keys():
                write_lcms_mzml(data, infile, run_args['outdir'], run_args['outfile'], run_args['centroid'],
                                run_args['ms2_only'], run_args['ms1_groupby'], run_args['encoding'],
                                run_args['ms2_keep_n_most_abundant_peaks'])
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
