import os
import argparse
from client.select_job import *
from timsconvert.timestamp import *


def get_args():
    parser = argparse.ArgumentParser()
    parser.add_argument('-u', '--uuid', help='UUID for TIMSCONVERT job.', default='', nargs='+', type=str)
    parser.add_argument('-o', '--output', help='Directory to download converted data to.', default='', type=str)
    arguments = parser.parse_args()
    return vars(arguments)


def args_check(args):
    print(args)
    with sqlite3.connect(LOCAL_JOBS_DB) as conn:
        query = 'SELECT * FROM local_jobs'
        jobs_table = pd.read_sql_query(query, conn)
    id_list = jobs_table['id'].values.tolist()
    if args['uuid'] not in id_list:
        print(get_timestamp() + ':' + 'UUID not found. Select from the following UUIDs.')
        args['uuid'] = select_job()
    if not os.path.isdir(args['output']) and args['output'] != '':
        os.makedirs(args['output'])
    return args
