import sys
import argparse
from client.select_job import *
from timsconvert.timestamp import *


def get_args():
    parser = argparse.ArgumentParser()
    parser.add_argument('-u', '--uuid', help='UUID for TIMSCONVERT job.', default='', type=str)
    arguments = parser.parse_args()
    return vars(arguments)


def args_check(args):
    with sqlite3.connect(LOCAL_JOBS_DB) as conn:
        query = 'SELECT * FROM jobs'
        jobs_table = pd.read_sql_query(query, conn)
    id_list = jobs_table['id'].values.tolist()
    if args['uuid'] not in id_list:
        logging.info(get_timestamp() + ':' + 'UUID not found. Select from the following UUIDs.')
        sys.exit(1)
