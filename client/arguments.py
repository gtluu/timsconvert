import sys
import argparse
from client.select_job import *
from timsconvert.timestamp import *


def get_args():
    parser = argparse.ArgumentParser()
    parser.add_argument('-u', '--uuid', help='UUID for TIMSCONVERT job.', required=True, nargs='+', type=str)
    parser.add_argument('-o', '--output', help='Directory to download converted data to.', default='', type=str)
    arguments = parser.parse_args()
    return vars(arguments)


def args_check(args):
    with sqlite3.connect(LOCAL_JOBS_DB) as conn:
        query = 'SELECT * FROM local_jobs'
        jobs_table = pd.read_sql_query(query, conn)
    id_list = jobs_table['id'].values.tolist()
    if isinstance(args['uuid'], list):
        for ident in args['uuid']:
            if ident not in id_list:
                print(get_timestamp() + ':JOB ' + ident + ' not found.')
                sys.exit(1)
    else:
        if args['uuid'] not in id_list:
            print(get_timestamp() + ':' + 'UUID not found.')
            sys.exit(1)
    return args
