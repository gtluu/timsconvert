from flask import request, send_from_directory
from rq import Retry
from apps import app, q
from util import *
from constants import *
from timsconvert.arguments import *
from timsconvert.run import run_timsconvert


@app.route('/', methods=['GET'])
def index():
    return 'ok'


@app.route('/upload', methods=['POST'])
def upload():
    if request.method == 'POST':
        # Get tarball.
        uploaded_data = request.files['data']
        if 'plate_map' in request.files.keys():
            uploaded_plate_map = request.files['plate_map']
        # Get UUID for job.
        job_uuid = generate_uuid()
        # Save tarball to server.
        uploaded_data_path = os.path.join(UPLOAD_FOLDER, str(job_uuid) + '.tar.gz')
        uploaded_data.save(uploaded_data_path)
        # Add job to new row in sqlite3.db
        add_file_to_db(job_uuid)
        # Decompress uploaded data.
        decompress_tarball(os.path.join(UPLOAD_FOLDER, str(job_uuid) + '.tar.gz'))
        if 'plate_map' in request.files['plate_map']:
            uploaded_plate_map_path = os.path.join(UPLOAD_FOLDER, str(job_uuid), 'data',
                                                   str(job_uuid) + '_plate_map.csv')
            uploaded_plate_map.save(uploaded_plate_map_path)
        return job_uuid


@app.route('/run_timsconvert_job', methods=['POST'])
def run_timsconvert_job():
    if request.method == 'POST':
        # Get UUID from POST request.
        job_uuid = request.args.get('uuid')
        # Get default TIMSCONVERT args.
        args = get_default_args(job_uuid)
        # Get args from json and modify args with args found in json.
        req_args = request.get_json()
        for key, value in req_args.items():
            if key != 'input' and key != 'outdir' and key != 'outfile':
                args[key] = value
        args_check(args)
        #q.enqueue(run_timsconvert, args, retry=Retry(max=3))
        run_timsconvert(args)
        return job_uuid


@app.route('/status', methods=['GET'])
def status():
    if request.method == 'GET':
        # Get UUID from GET request.
        job_uuid = request.args.get('uuid')
        # Get job status.
        jobs_table = get_jobs_table()
        status = jobs_table.loc[jobs_table['id'] == job_uuid]['status'].values[0]
        return str(job_uuid) + ' Job Status: ' + str(status)


@app.route('/download_results', methods=['GET'])
def download_results():
    if request.method == 'GET':
        # Get UUID from GET request.
        job_uuid = request.args.get('uuid')
        # Check to make sure data not deleted.
        jobs_table = get_jobs_table()
        file_presence = jobs_table.loc[jobs_table['id'] == job_uuid]['data'].values[0]
        if str(file_presence) == 'ON_SERVER':
            # Compress data for download.
            compress_data(job_uuid)
            # Download data.
            return send_from_directory(UPLOAD_FOLDER, job_uuid + '_output.tar.gz')
        elif str(file_presence) == 'DELETED':
            return 'DELETED'


@app.route('/purge', methods=['GET'])
# Remove data older than 7 days.
def purge():
    if request.method == 'GET':
        if 'uuid' in request.args:
            # Get UUID from GET request.
            job_uuid = request.args.get('uuid')
            # Check to make sure data not deleted.
            jobs_table = get_jobs_table()
            file_presence = jobs_table.loc[jobs_table['id'] == job_uuid]['data'].values[0]
            if str(file_presence) == 'ON_SERVER':
                # Delete data.
                q.enqueue(cleanup_server_by_uuid, job_uuid)
                return 'DELETED'
            elif str(file_presence) == 'DELETED':
                return 'DELETED'
        else:
            q.enqueue(cleanup_server)
    return 'ok'
