import requests
from client.arguments import *
from client.constants import URL
from client.select_job import *
from timsconvert.timestamp import *


def download_timsconvert_job(job_uuid):
    job_url = URL + '/download_results?uuid=' + job_uuid
    # req = requests.post(status_url)
    req = requests.get(job_url)
    if req.status_code == 200:
        # download file
        pass
    else:
        logging.info(get_timestamp() + ':' + 'TIMSCONVERT results could not be downloaded.')
        req.raise_for_status()


if __name__ == '__main__':
    # Get arguments.
    args = get_args()
    args_check(args)

    # Initialize logger.
    logname = 'log_' + get_timestamp() + '.log'
    for handler in logging.root.handlers[:]:
        logging.root.removeHandler(handler)
    logging.basicConfig(filename=logname, level=logging.INFO)
    logging.getLogger().addHandler(logging.StreamHandler(sys.stdout))

    # Download data.
    if args['uuid'] == '':
        args['uuid'] = select_job()
    download_timsconvert_job(args['uuid'])

    # Shut down logger.
    for hand in logging.getLogger().handlers:
        logging.getLogger().removeHandler(hand)
    logging.shutdown()
