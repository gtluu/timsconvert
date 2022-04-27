from flask import render_template, request, url_for, redirect, send_from_directory
from server.apps import app, executor
from server.util import *
from server.constants import *
from bin.run import run_timsconvert


@app.route('/', methods=['GET'])
def index():
    # Hard code filename for now
    filename = 'C:\\Users\\gordon\\Data\\data.tar.gz'
    job_uuid = upload_data(filename)
    return redirect(url_for('job', job_uuid=str(job_uuid)))


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
        return job_uuid


@app.route('/job/<job_uuid>', methods=['GET', 'POST'])
def job(job_uuid):
    # Build URL.
    url = 'http://localhost:5000/run_timsconvert_job?uuid=' + job_uuid
    # Add job to new row in sqlite3.db
    add_job_to_db(job_uuid)
    # Run job.
    requests.post(url)
    return redirect(url_for('status', job_uuid=job_uuid))


@app.route('/run_timsconvert_job', methods=['POST'])
def run_timsconvert_job():
    if request.method == 'POST':
        # Get UUID from POST request.
        job_uuid = request.args.get('uuid')
        # Get default TIMSCONVERT args.
        args = get_default_args(job_uuid)  # replace with args from prooteosafe? or replace entire endpoint w/ nextflow
        # async job needed for rendering the status page immediately
        #run_timsconvert(args)  <- synchronous
        executor.submit_stored(job_uuid, run_timsconvert, args)  # <- asynchronous
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
    compress_output(os.path.join(UPLOAD_FOLDER, str(job_uuid)), job_uuid)
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
