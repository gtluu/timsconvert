from flask import render_template, request, url_for, redirect, send_from_directory
from server.apps import app, executor
from server.util import *
from server.constants import *
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
        return job_uuid


@app.route('/run_timsconvert_job', methods=['POST'])
def run_timsconvert_job():
    if request.method == 'POST':
        # Get UUID from POST request.
        job_uuid = request.args.get('uuid')
        # Get default TIMSCONVERT args.
        args = get_default_args(job_uuid)  # replace with args from prooteosafe? or replace entire endpoint w/ nextflow
        # get args from json and modify args with args found in json



        run_timsconvert(args)
        return 'ok'


@app.route('/status/<job_uuid>', methods=['GET'])
def status(job_uuid):
    jobs_table = get_jobs_table()
    status = jobs_table.loc[jobs_table['id'] == job_uuid]['status'].values[0]
    if status == 'PENDING' or status == 'RUNNING':
        return render_template('status.html', uuid=job_uuid)
    elif status == 'DONE':
        return redirect(url_for('results', job_uuid=job_uuid))


@app.route('/results/<job_uuid>', methods=['GET'])
def results(job_uuid):
    # Remove job from executor.
    executor.futures.pop(job_uuid)
    # Compress converted data.
    compress_data(os.path.join(UPLOAD_FOLDER, str(job_uuid)), job_uuid)
    return render_template('results.html', uuid=job_uuid)


@app.route('/download_results', methods=['GET'])
def download_results():
    job_uuid = request.args.get('uuid')
    return send_from_directory(UPLOAD_FOLDER, job_uuid + '_output.tar.gz')


@app.route('/purge')
# Remove data older than 7 days.
def purge():
    executor.submit(cleanup_server)
    return 'ok'
