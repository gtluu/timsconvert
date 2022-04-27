from flask import request, send_from_directory
from server.apps import app, executor
from server.util import *
from server.constants import *
from timsconvert.arguments import *
from bin.run import run_timsconvert


@app.route('/upload', methods=['POST'])
def upload():
    if request.method == 'POST':
        # Get tarball.
        uploaded_data = request.files['data']
        # Get UUID for job.
        job_uuid = generate_uuid()
        # Save tarball to server.
        uploaded_data_path = os.path.join(UPLOAD_FOLDER, str(job_uuid) + '.tar.gz')  # replace filename with uuid
        uploaded_data.save(uploaded_data_path)
        # Add job to new row in sqlite3.db
        add_file_to_db(job_uuid)
        # Decompress uploaded data.
        decompress_tarball(os.path.join(UPLOAD_FOLDER, str(job_uuid) + '.tar.gz'))
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
        run_timsconvert(args)
        return 'ok'


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
        # Compress data for download.
        compress_data(job_uuid)
        # Download data.
        return send_from_directory(UPLOAD_FOLDER, job_uuid + '_output.tar.gz')


@app.route('/purge')
# Remove data older than 7 days.
def purge():
    executor.submit(cleanup_server)
    return 'ok'
