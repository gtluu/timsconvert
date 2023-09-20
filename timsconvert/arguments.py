import argparse
import json
import os
import sys
import logging
import requests
from timsconvert.timestamp import *


# Parse arguments for CLI usage
def get_args(server=False):
    """
    Parse command line parameters, including required, optional, and system parameters.

    :param server: If enabled, allows the user to specify a custom url using the "--url" parameter, defaults to False
    :type server: bool
    :return: Arguments with default or user specified values.
    :rtype: dict
    """
    with open(os.path.join(os.path.realpath(__file__), 'parameter_descriptions.json'), 'r') as json_file:
        arg_descriptions = json.loads(json_file.read())

    # Initialize parser.
    parser = argparse.ArgumentParser()

    # Require Arguments
    required = parser.add_argument_group('Required Parameters')
    required.add_argument('--input',
                          help=arg_descriptions['input'],
                          required=True,
                          type=str)

    # Optional Arguments
    optional = parser.add_argument_group('Optional Parameters')
    optional.add_argument('--outdir',
                          help=arg_descriptions['outdir'],
                          default='',
                          type=str)
    optional.add_argument('--outfile',
                          help=arg_descriptions['outfile'],
                          default='',
                          type=str)
    optional.add_argument('--mode',
                          help=arg_descriptions['mode'],
                          default='centroid',
                          type=str,
                          choices=['raw', 'centroid', 'profile'])
    optional.add_argument('--compression',
                          help=arg_descriptions['compression'],
                          default='zlib',
                          type=str,
                          choices=['zlib', 'none'])
    optional.add_argument('--ms2_only',
                          help=arg_descriptions['ms2_only'],
                          action='store_true')
    optional.add_argument('--exclude_mobility',
                          help=arg_descriptions['exclude_mobility'],
                          action='store_true')
    optional.add_argument('--encoding',
                          help=arg_descriptions['encoding'],
                          default=64,
                          type=int,
                          choices=[32, 64])
    optional.add_argument('--barebones_metadata',
                          help=arg_descriptions['barebones_metadata'],
                          action='store_true')
    optional.add_argument('--profile_bins',
                          help=arg_descriptions['profile_bins'],
                          default=0,
                          type=int)
    optional.add_argument('--maldi_output_file',
                          help=arg_descriptions['maldi_output_file'],
                          default='combined',
                          type=str,
                          choices=['combined', 'individual', 'sample'])
    optional.add_argument('--maldi_plate_map',
                          help=arg_descriptions['maldi_plate_map'],
                          default='',
                          type=str)
    optional.add_argument('--imzml_mode',
                          help=arg_descriptions['imzml_mode'],
                          default='processed',
                          type=str,
                          choices=['processed', 'continuous'])

    # System Arguments
    system = parser.add_argument_group('System Parameters')
    system.add_argument('--chunk_size',
                        help=arg_descriptions['chunk_size'],
                        default=10,
                        type=int)
    system.add_argument('--verbose',
                        help=arg_descriptions['verbose'],
                        action='store_true')
    if server:
        # change to GNPS URL later
        system.add_argument('--url',
                            help=arg_descriptions['url'],
                            default='http://localhost:5000',
                            type=str)

    # Return parser
    arguments = parser.parse_args()
    return vars(arguments)


# Checks to ensure arguments are valid.
def args_check(args):
    """
    Check relevant arguments to ensure user input values are valid.

    :param args: Arguments obtained from timsconvert.arguments.get_args().
    :type args: dict
    """
    # Check if input directory exists.
    if not os.path.exists(args['input']):
        print(get_timestamp() + ':' + 'Input path does not exist...')
        print(get_timestamp() + ':' + 'Exiting...')
        sys.exit(1)
    # Check if output directory exists and create it if it does not.
    if not os.path.isdir(args['outdir']) and args['outdir'] != '':
        os.makedirs(args['outdir'])
    # Check to make sure output filename ends in .mzML extension.
    if os.path.splitext(args['outfile']) != '.mzML' and args['outfile'] != '':
        args['outfile'] = args['outfile'] + '.mzML'
    # Check if plate map path is valid and if plate map is available if --maldi_single_file is True.
    if args['maldi_output_file'] != '' \
            and args['maldi_output_file'] in ['individual', 'sample'] \
            and args['maldi_plate_map'] == '':
        print(get_timestamp() + ':' + 'Plate map is required for MALDI dried droplet data...')
        print(get_timestamp() + ':' + 'Exiting...')
        sys.exit(1)
    elif args['maldi_output_file'] != '' \
            and args['maldi_output_file'] in ['individual', 'sample'] \
            and not os.path.exists(args['maldi_plate_map']):
        print(get_timestamp() + ':' + 'Plate map path does not exist...')
        print(get_timestamp() + ':' + 'Exiting...')
        sys.exit(1)
    # Check if server URL is valid.
    if 'url' in args.keys():
        response = requests.get(args['url'])
        if response.status_code != 200:
            print(get_timestamp() + ':' + 'URL is not valid or server is down...')
            print(get_timestamp() + ':' + 'Exiting...')
            response.raise_for_status()
