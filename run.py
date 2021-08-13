import logging

from tims_converter import *


def run_tims_converter(args):
    # Load in input data.
    logging.info(get_timestamp() + ':' + 'Loading input data...')
    if not args['input'].endswith('.d'):
        input_files = dot_d_detection(args['input'])
    elif args['input'].endswith('.d'):
        input_files = [args['input']]

    # Convert each sample
    for infile in input_files:
        logging.info(get_timestamp() + ':' + 'Reading file: ' + infile)
        data = bruker_to_df(infile)
        logging.info(get_timestamp() + ':' + 'Writing to file: ' + os.path.join(args['outdir'], args['outfile']))
        write_mzml(data, args['ms1_groupby'], infile, os.path.join(args['outdir'], args['outfile']))


if __name__ == '__main__':
    # Parse arguments.
    arguments = get_args()

    # Check arguments.
    args_check(arguments)
    arguments['version'] = '0.0.1'

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
