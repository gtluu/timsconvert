import sys
import argparse
import sqlite3
import pandas as pd
from client.constants import LOCAL_JOBS_DB
from timsconvert.timestamp import *


def get_args():
    parser = argparse.ArgumentParser()
    parser.add_argument('-i', '--id', help='ID for TIMSCONVERT job.', required=True, nargs='+',
                        type=str)
    parser.add_argument('-o', '--output', help='Directory to download converted data to.', default='', type=str)
    parser.add_argument('-u', '--url', help='URL for server to run TIMSCONVERT (if submitting job through API). '
                                            'Default = GNPS server', default='http://localhost:5000', type=str)
    arguments = parser.parse_args()
    return vars(arguments)


def args_check(args):
    with sqlite3.connect(LOCAL_JOBS_DB) as conn:
        query = 'SELECT * FROM local_jobs'
        jobs_table = pd.read_sql_query(query, conn)
    id_list = jobs_table['id'].values.tolist()
    if isinstance(args['id'], list):
        for ident in args['id']:
            if ident not in id_list:
                print(get_timestamp() + ':JOB ' + ident + ' not found.')
                sys.exit(1)
    else:
        if args['id'] not in id_list:
            print(get_timestamp() + ':' + 'ID not found.')
            sys.exit(1)
    return args
