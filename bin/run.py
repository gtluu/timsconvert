import copy
from timsconvert import *


def run_timsconvert(args):
    # Initialize Bruker DLL.
    logging.info(get_timestamp() + ':' + 'Initialize Bruker .dll file...')
    bruker_dll = init_bruker_dll(BRUKER_DLL_FILE_NAME)

    # Load in input data.
    logging.info(get_timestamp() + ':' + 'Loading input data...')
    if not args['input'].endswith('.d'):
        input_files = dot_d_detection(args['input'])
    elif args['input'].endswith('.d'):
        input_files = [args['input']]

    # Convert each sample.
    for infile in input_files:
        # Reset args.
        run_args = copy.deepcopy(args)

        # Set input file.
        run_args['infile'] = infile
        # Set output directory to default if not specified.
        if run_args['outdir'] == '':
            run_args['outdir'] = os.path.split(infile)[0]

        # Read in input file (infile).
        logging.info(get_timestamp() + ':' + 'Reading file: ' + infile)
        schema = schema_detection(infile)
        if schema == 'TSF':
            data = tsf_data(infile, bruker_dll)
        elif schema == 'TDF':
            data = tdf_data(infile, bruker_dll)

        # Log arguments.
        for key, value in run_args.items():
            logging.info(get_timestamp() + ':' + str(key) + ': ' + str(value))

        if schema == 'TSF':
            logging.info(get_timestamp() + ':' + '.tsf file detected...')
            if data.meta_data['MaldiApplicationType'] == 'SingleSpectra':
                logging.info(get_timestamp() + ':' + 'Processing MALDI dried droplet data...')
                write_maldi_dd_mzml(data, run_args['infile'], run_args['outdir'], run_args['outfile'], run_args['mode'],
                                    run_args['ms2_only'], run_args['encoding'],
                                    run_args['maldi_output_file'], run_args['maldi_plate_map'], run_args['chunk_size'])
            elif data.meta_data['MaldiApplicationType'] == 'Imaging':
                logging.info(get_timestamp() + ':' + 'Processing MALDI imaging mass spectrometry data...')
                write_maldi_ims_imzml(data, run_args['outdir'], run_args['outfile'], run_args['mode'],
                                      run_args['imzml_mode'], run_args['encoding'], run_args['chunk_size'])
        elif schema == 'TDF':
            logging.info(get_timestamp() + ':' + '.tdf file detected...')
            if 'MaldiApplicationType' in data.meta_data.keys():
                if data.meta_data['MaldiApplicationType'] == 'SingleSpectra':
                    logging.info(get_timestamp() + ':' + 'Processing MALDI-TIMS dried droplet data...')
                    write_maldi_dd_mzml(data, run_args['infile'], run_args['outdir'], run_args['outfile'],
                                        run_args['mode'],
                                        run_args['ms2_only'], run_args['encoding'],
                                        run_args['maldi_output_file'], run_args['maldi_plate_map'],
                                        run_args['chunk_size'])
                elif data.meta_data['MaldiApplicationType'] == 'Imaging':
                    logging.info(get_timestamp() + ':' + 'Processing MALDI-TIMS imaging mass spectrometry data...')
                    write_maldi_ims_imzml(data, run_args['outdir'], run_args['outfile'], run_args['mode'],
                                          run_args['imzml_mode'], run_args['encoding'], run_args['chunk_size'])
            elif 'MaldiApplicationType' not in data.meta_data.keys():
                logging.info(get_timestamp() + ':' + 'Processing LC-TIMS-MS data...')
                write_lcms_mzml(data, infile, run_args['outdir'], run_args['outfile'], run_args['mode'],
                                run_args['ms2_only'], run_args['encoding'], run_args['chunk_size'])


if __name__ == '__main__':
    # Parse arguments.
    arguments = get_args()

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

    # Check to make sure using Python 3.7.
    if not sys.version_info.major == 3 and sys.version_info.minor == 7:
        logging.warning(get_timestamp() + 'Must be using Python 3.7 to run TIMSCONVERT.')
        sys.exit(1)

    # Run.
    run_timsconvert(arguments)
