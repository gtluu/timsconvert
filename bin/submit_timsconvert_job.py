import tarfile
import requests
from client.constants import URL, LOCAL_JOBS_DB
from client.init_client_db import *
from timsconvert.arguments import *
from timsconvert.timestamp import *


def upload_data(filename):
    # Upload data.
    files = {'data': ('data.tar.gz', open(filename, 'rb'))}
    req = requests.post(URL + '/upload', files=files)
    if req.status_code == 200:
        job_uuid = req.text
        logging.info(get_timestamp() + ':' + 'Data uploaded.')
        return job_uuid
    else:
        logging.info(get_timestamp() + ':' + 'Data not uploaded.')
        req.raise_for_status()


def submit_timsconvert_job(args):
    # tar data.
    if not args['input'].endswith('.tar.gz'):
        tarball = 'tmp.tar.gz'
        with tarfile.open(tarball, 'w:gz') as newtar:
            newtar.add(args['input'])
    else:
        tarball = args['input']

    # Upload data.
    job_uuid = upload_data(tarball)

    # Start job on server.
    run_url = URL + '/run_timsconvert_job?uuid=' + job_uuid
    req = requests.post(run_url, json=args)

    # Delete tmp tarball.
    if tarball == 'tmp.tar.gz':
        os.remove(tarball)

    # Check for errors and add to local sqlite3 db.
    if req.status_code == 200:
        if not os.path.exists(LOCAL_JOBS_DB):
            init_client_db()
        with sqlite3.connect(LOCAL_JOBS_DB) as conn:
            cur = conn.cursor()
            cur.execute('INSERT INTO jobs (id,start_time) VALUES (?,?)',
                        (job_uuid, datetime.datetime.now()))
            conn.commit()
        logging.info(get_timestamp() +
                     ':' +
                     'TIMSCONVERT job has been submitted to GNPS. Use "python client_check_status.py" to check on job '
                     'status.')
        return 'ok'
    else:
        logging.info(get_timestamp() + ':' + 'TIMSCONVERT job was not submitted. Please try again.')
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

    # Submit job.
    submit_timsconvert_job(args)

    # Shut down logger.
    for hand in logging.getLogger().handlers:
        logging.getLogger().removeHandler(hand)
    logging.shutdown()
