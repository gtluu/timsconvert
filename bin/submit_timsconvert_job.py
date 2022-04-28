import sqlite3
import shutil
import tarfile
import requests
from client.constants import LOCAL_JOBS_DB
from timsconvert.arguments import *
from timsconvert.timestamp import *


def upload_data(filename, url):
    # Upload data.
    data_obj = open(filename, 'rb')
    files = {'data': ('data.tar.gz', data_obj)}
    req = requests.post(url + '/upload', files=files)
    data_obj.close()
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
        tarball = args['input'] + '.tar.gz'
        with tarfile.open(tarball, 'w:gz') as newtar:
            if args['input'].endswith('.d'):
                shutil.copytree(args['input'], os.path.join('tmp', os.path.split(args['input'])[-1]))
                newtar.add('tmp', 'data')
                shutil.rmtree(os.path.join('tmp', os.path.split(args['input'])[-1]))
                os.rmdir('tmp')
            else:
                newtar.add(args['input'], 'data')
    else:
        tarball = args['input']

    # Upload data.
    job_uuid = upload_data(tarball, args['url'])

    # Delete tmp tarball.
    os.remove(tarball)

    # Start job on server.
    run_url = args['url'] + '/run_timsconvert_job?uuid=' + job_uuid
    req = requests.post(run_url, json=args)

    # Check for errors and add to local sqlite3 db.
    if req.status_code == 200:
        with sqlite3.connect(LOCAL_JOBS_DB) as conn:
            cur = conn.cursor()
            cur.execute('INSERT INTO local_jobs (id,start_time) VALUES (?,?)',
                        (job_uuid, datetime.datetime.now()))
            conn.commit()
        logging.info(get_timestamp() + ': JOB ID: ' + job_uuid)
        logging.info(get_timestamp() +
                     ':' +
                     'TIMSCONVERT job has been submitted to GNPS. Use "python client_check_status.py" to check on job '
                     'status.')
        return job_uuid
    else:
        logging.info(get_timestamp() + ':' + 'TIMSCONVERT job was not submitted. Please try again.')
        req.raise_for_status()


if __name__ == '__main__':
    # Initialize local_jobs.db if not already done.
    # Directory to create sqlite3 database file in.
    db_folder = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'db')

    # Create db folder if not already made.
    if not os.path.exists(db_folder):
        os.mkdir(db_folder)

    # Make the table.
    conn = sqlite3.connect(os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
                                        os.path.join('db', 'local_jobs.db')))
    create_table = 'CREATE TABLE IF NOT EXISTS local_jobs' \
                   '("id" varchar(36) NOT NULL UNIQUE,' \
                   '"start_time" timestamp,' \
                   'PRIMARY KEY (id))'
    conn.execute(create_table)

    conn.close()

    # Get arguments.
    args = get_args(server=True)
    args = args_check(args)

    # Initialize logger if not running on server.
    logname = 'log_' + get_timestamp() + '.log'
    if args['outdir'] == '':
        logfile = os.path.join(os.path.dirname(os.path.abspath(__file__)), logname)
    else:
        logfile = os.path.join(args['outdir'], logname)
    for handler in logging.root.handlers[:]:
        logging.root.removeHandler(handler)
    logging.basicConfig(filename=logfile, level=logging.INFO)
    logging.getLogger().addHandler(logging.StreamHandler(sys.stdout))

    # Submit job.
    submit_timsconvert_job(args)

    # Shut down logger.
    for hand in logging.getLogger().handlers:
        logging.getLogger().removeHandler(hand)
    logging.shutdown()
