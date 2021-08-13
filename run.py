from tims_converter import *


def run_tims_converter(args):
    # Load in input data.
    if not args['input'].endswith('.d'):
        input_files = dot_d_detection(args['input'])
    elif args['input'].endswith('.d'):
        input_files = [args['input']]

    # Convert each sample
    for infile in input_files:
        data = bruker_to_df(infile)
        write_mzml(data, args['ms1_groupby'], infile, os.path.join(args['outdir'], args['outfile']))


if __name__ == '__main__':
    # Parse arguments.
    arguments = get_args()

    # Check arguments.
    args_check(arguments)
    arguments['version'] = '0.0.1'

    # Run.
    run_tims_converter(arguments)
