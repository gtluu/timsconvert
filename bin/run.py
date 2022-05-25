from timsconvert import *
from tdf2mzml import *


def run_timsconvert(args):
    # Args check.
    args_check(args)
    # Check arguments.
    args['version'] = '1.1.0'
    args['profile_bins'] = 0  # remove hard coded profile_bins after getting profile mode working

    # Initialize logger if not running on server.
    logname = 'log_' + get_timestamp() + '.log'
    if args['outdir'] == '':
        if os.path.isdir(args['input']):
            logfile = os.path.join(args['input'], logname)
        else:
            logfile = os.path.split(args['input'])[0]
            logfile = os.path.join(logfile, logname)
    else:
        logfile = os.path.join(args['outdir'], logname)
    for handler in logging.root.handlers[:]:
        logging.root.removeHandler(handler)
    logging.basicConfig(filename=logfile, level=logging.INFO)
    if args['verbose']:
        logging.getLogger().addHandler(logging.StreamHandler(sys.stdout))

    # Check to make sure using Python 3.7.
    if not sys.version_info.major == 3 and sys.version_info.minor == 7:
        logging.warning(get_timestamp() + 'Must be using Python 3.7 to run TIMSCONVERT.')
        sys.exit(1)

    # Initialize Bruker DLL.
    logging.info(get_timestamp() + ':' + 'Initialize Bruker .dll file...')
    tdf_sdk_dll = init_tdf_sdk_dll(TDF_SDK_DLL_FILE_NAME)
    baf2sql_dll = init_baf2sql_dll(BAF2SQL_DLL_FILE_NAME)

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
            data = tsf_data(infile, tdf_sdk_dll)
        elif schema == 'TDF':
            data = tdf_data(infile, tdf_sdk_dll)
        elif schema == 'BAF':
            data = baf_data(infile, baf2sql_dll)

        # Log arguments.
        for key, value in run_args.items():
            logging.info(get_timestamp() + ':' + str(key) + ': ' + str(value))

        if schema == 'TSF':
            logging.info(get_timestamp() + ':' + '.tsf file detected...')
            if data.meta_data['MaldiApplicationType'] == 'SingleSpectra':
                if run_args['outfile'] == '':
                    run_args['outfile'] = os.path.splitext(os.path.split(infile)[-1])[0] + '.mzML'
                logging.info(get_timestamp() + ':' + 'Processing MALDI dried droplet data...')
                write_maldi_dd_mzml(data, run_args['infile'], run_args['outdir'], run_args['outfile'], run_args['mode'],
                                    run_args['ms2_only'], run_args['exclude_mobility'], run_args['profile_bins'],
                                    run_args['encoding'], run_args['compression'], run_args['maldi_output_file'],
                                    run_args['maldi_plate_map'], run_args['barebones_metadata'], run_args['chunk_size'])
            elif data.meta_data['MaldiApplicationType'] == 'Imaging':
                if run_args['outfile'] == '':
                    run_args['outfile'] = os.path.splitext(os.path.split(infile)[-1])[0] + '.imzML'
                logging.info(get_timestamp() + ':' + 'Processing MALDI imaging mass spectrometry data...')
                write_maldi_ims_imzml(data, run_args['outdir'], run_args['outfile'], run_args['mode'],
                                      run_args['exclude_mobility'], run_args['profile_bins'], run_args['imzml_mode'],
                                      run_args['encoding'], run_args['compression'], run_args['chunk_size'])
        elif schema == 'TDF':
            logging.info(get_timestamp() + ':' + '.tdf file detected...')
            if 'MaldiApplicationType' in data.meta_data.keys():
                if data.meta_data['MaldiApplicationType'] == 'SingleSpectra':
                    if run_args['outfile'] == '':
                        run_args['outfile'] = os.path.splitext(os.path.split(infile)[-1])[0] + '.mzML'
                    logging.info(get_timestamp() + ':' + 'Processing MALDI-TIMS dried droplet data...')
                    write_maldi_dd_mzml(data, run_args['infile'], run_args['outdir'], run_args['outfile'],
                                        run_args['mode'], run_args['ms2_only'], run_args['exclude_mobility'],
                                        run_args['profile_bins'], run_args['encoding'], run_args['compression'],
                                        run_args['maldi_output_file'], run_args['maldi_plate_map'],
                                        run_args['barebones_metadata'], run_args['chunk_size'])
                elif data.meta_data['MaldiApplicationType'] == 'Imaging':
                    if run_args['outfile'] == '':
                        run_args['outfile'] = os.path.splitext(os.path.split(infile)[-1])[0] + '.imzML'
                    logging.info(get_timestamp() + ':' + 'Processing MALDI-TIMS imaging mass spectrometry data...')
                    write_maldi_ims_imzml(data, run_args['outdir'], run_args['outfile'], run_args['mode'],
                                          run_args['exclude_mobility'], run_args['profile_bins'],
                                          run_args['imzml_mode'], run_args['encoding'], run_args['compression'],
                                          run_args['chunk_size'])
            elif 'MaldiApplicationType' not in data.meta_data.keys():
                if run_args['outfile'] == '':
                    run_args['outfile'] = os.path.splitext(os.path.split(infile)[-1])[0] + '.mzML'
                logging.info(get_timestamp() + ':' + 'Processing LC-TIMS-MS data...')
                if run_args['lcms_backend'] == 'timsconvert':
                    write_lcms_mzml(data, infile, run_args['outdir'], run_args['outfile'], run_args['mode'],
                                    run_args['ms2_only'], run_args['exclude_mobility'], run_args['profile_bins'],
                                    run_args['encoding'], run_args['compression'], run_args['barebones_metadata'],
                                    run_args['chunk_size'])
                elif run_args['lcms_backend'] == 'tdf2mzml':
                    tdf2mzml_write_mzml(run_args)
        elif schema == 'BAF':
            logging.info(get_timestamp() + ':' + '.baf file detected...')
            if run_args['outfile'] == '':
                run_args['outfile'] = os.path.splitext(os.path.split(infile)[-1])[0] + '.mzML'
            logging.info(get_timestamp() + ':' + 'Processing LC-MS data...')
            write_lcms_mzml(data, infile, run_args['outdir'], run_args['outfile'], run_args['mode'],
                            run_args['ms2_only'], run_args['exclude_mobility'], run_args['profile_bins'],
                            run_args['encoding'], run_args['compression'], run_args['barebones_metadata'],
                            run_args['chunk_size'])

    for hand in logging.getLogger().handlers:
        logging.getLogger().removeHandler(hand)
    logging.shutdown()


if __name__ == '__main__':
    # Parse arguments.
    args = get_args()

    # Run.
    run_timsconvert(args)
