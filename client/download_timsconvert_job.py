import os
import requests
import logging
from arguments import *
from select_job import *


def download_timsconvert_job(job_uuid, output, url):
    job_url = url + '/download_results?uuid=' + job_uuid
    # req = requests.post(status_url)
    req = requests.get(job_url)
    if req.status_code == 200:
        if req.text != 'DELETED':
            # Write downloaded data.
            with open(os.path.join(output, job_uuid + '.tar.gz'), 'wb') as tarball:
                tarball.write(req.content)
            logging.info(get_timestamp() + ': Data ' + job_uuid + '.tar.gz has been downloaded to ' + output)
        else:
            logging.info(get_timestamp() + ': Data for job ' + job_uuid + ' has been deleted from servers. '
                                                                          'Please re-run.')
            sys.exit(1)
    else:
        logging.info(get_timestamp() + ':' + 'TIMSCONVERT results could not be downloaded.')
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

    # Download data.
    if isinstance(args['id'], list):
        for ident in args['id']:
            download_timsconvert_job(ident, args['output'], args['url'])
    else:
        download_timsconvert_job(args['id'], args['output'], args['url'])

    # Shut down logger.
    for hand in logging.getLogger().handlers:
        logging.getLogger().removeHandler(hand)
    logging.shutdown()
