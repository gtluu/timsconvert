from flask import render_template, request, url_for, redirect, send_from_directory
import uuid
from server.apps import app, executor
from server.util import *
from server.constants import *
#from bin.run import run_timsconvert


@app.route('/', methods=['GET'])
def index():
    # Hard code filename for now
    #filename = 'C:\\Users\\gordon\\Data\\data.tar.gz'
    #job_uuid = upload_data(filename)
    #print(str(job_uuid), file=sys.stdout)
    #return redirect(url_for('job', job_uuid=str(job_uuid)))
    return render_template('timsconvert_old.html')


@app.route('/upload', methods=['POST'])
def upload():
    if request.method == 'POST':
        uploaded_data = request.files['data']
        job_uuid = str(uuid.uuid4())
        uploaded_data_path = os.path.join(UPLOAD_FOLDER, str(job_uuid) + '.tar.gz')  # replace filename with uuid
        uploaded_data.save(uploaded_data_path)
        return job_uuid


@app.route('/job/<job_uuid>', methods=['GET', 'POST'])
def job(job_uuid):
    print(request.method, file=sys.stdout)
    print('1')
    print('1', file=sys.stdout)
    print('2', file=sys.stdout)
    url = 'http://localhost:5000/run_timsconvert_job'
    print(url, file=sys.stdout)
    print('3', file=sys.stdout)
    requests.post(url, params={'uuid': job_uuid})
    print('4', file=sys.stdout)
    return redirect(url_for('status', job_uuid=job_uuid))


@app.route('/run_timsconvert_job', methods=['POST'])
def run_timsconvert_job(job_uuid):
    print('5', file=sys.stdout)
    if request.method == 'POST':
        args = get_default_args(job_uuid)
        executor.submit(run_timsconvert, args)
        return 'ok'


@app.route('/status', methods=['GET'])
def status2():
    # if status done, redirect to results. if not, redirect to status.
    return render_template('status.html')


@app.route('/status/<job_uuid>', methods=['GET'])
def status(job_uuid):
    # if status done, redirect to results. if not, redirect to status.
    return render_template('status.html')


@app.route('/results', methods=['GET'])
def results():
    compress_output(os.path.join(UPLOAD_FOLDER, 'output'))
    return render_template('results.html')


@app.route('/download_results', methods=['GET'])
def download_results():
    return send_from_directory(UPLOAD_FOLDER, 'timsconvert_spectra.tar.gz')
