from flask import render_template, request, url_for, redirect, send_from_directory
from timsconvert_server.apps import *
from timsconvert_server.util import *
from timsconvert_server.constants import *


@app.route('/', methods=['GET'])
def index():
    return render_template('timsconvert.html')


@app.route('/run', methods=['GET', 'POST'])
def run():
    if request.method == 'POST':
        args = parse_request_data(request)

        executor.submit(run_timsconvert_process, args)

        with open(os.path.join(UPLOAD_FOLDER, 'status.txt'), 'w') as status_file:
            status_file.write('running')

        return redirect(url_for('status'))


@app.route('/status', methods=['GET', 'POST'])
def status():
    with open(os.path.join(UPLOAD_FOLDER, 'status.txt'), 'r') as status_file:
        status = status_file.read()
        if status == 'running':
            return render_template('status.html')
        elif status == 'done':
            return redirect(url_for('results'))


@app.route('/results', methods=['GET'])
def results():
    compress_output(os.path.join(UPLOAD_FOLDER, 'output'))
    return render_template('results.html')


@app.route('/download_results', methods=['GET'])
def download_results():
    return send_from_directory(UPLOAD_FOLDER, 'timsconvert_spectra.tar.gz')
