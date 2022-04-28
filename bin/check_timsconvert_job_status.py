import os
import requests
import logging
from client.arguments import *
from client.select_job import *
from timsconvert.timestamp import *


def check_timsconvert_job_status(job_uuid, url):
    status_url = url + '/status?uuid=' + job_uuid
    req = requests.get(status_url)
    if req.status_code == 200:
        logging.info(req.text)
    else:
        logging.info(get_timestamp() + ':' + 'Status could not be obtained.')
        req.raise_for_status()


if __name__ == '__main__':
    # Get arguments.
    args = get_args()
    args = args_check(args)

    # Initialize logger if not running on server.
    logname = 'log_' + get_timestamp() + '.log'
    if args['output'] == '':
        logfile = os.path.join(os.path.dirname(os.path.abspath(__file__)), logname)
    else:
        logfile = os.path.join(args['output'], logname)
    for handler in logging.root.handlers[:]:
        logging.root.removeHandler(handler)
    logging.basicConfig(filename=logfile, level=logging.INFO)
    logging.getLogger().addHandler(logging.StreamHandler(sys.stdout))

    # Check job status.
    if isinstance(args['id'], list):
        for ident in args['id']:
            check_timsconvert_job_status(ident, args['url'])
    else:
        check_timsconvert_job_status(args['id'], args['url'])

    # Shut down logger.
    for hand in logging.getLogger().handlers:
        logging.getLogger().removeHandler(hand)
    logging.shutdown()
