import os
import shutil
import tarfile
import uuid
import subprocess
from flask import Flask, request, send_from_directory

# Path to data location
UPLOAD_FOLDER = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))), 'data')

# Make Flask instance.
app = Flask(__name__)

# Create and set upload folder.
if not os.path.exists(UPLOAD_FOLDER):
    os.mkdir(UPLOAD_FOLDER)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
# Set max file size.
app.config['MAX_CONTENT_PATH'] = 1000000000


@app.route('/convert', methods=['POST'])
def convert():
    if request.method == 'POST'
        # Generate UUID.
        job_uuid = str(uuid.uuid4().hex)

        # Get tarball and save to server.
        uploaded_data = request.files['data']
        uploaded_data_path = os.path.join(UPLOAD_FOLDER, job_uuid + '.tar.gz')
        uploaded_data.save(uploaded_data_path)

        # Decompress uploaded data.
        with tarfile.open(uploaded_data_path) as tarball:
            tarball_dirname = os.path.join(UPLOAD_FOLDER, job_uuid)
            tarball.extractall(tarball_dirname)

        # Build TIMSCONVERT command.
        run_path = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))), 'run.py')
        outdir_path = os.path.join(UPLOAD_FOLDER, job_uuid, 'output')
        cmd = 'python ' + run_path + ' --input ' + tarball_dirname + ' --outdir ' + outdir_path

        # Run TIMSCONVERT
        subprocess.call(cmd, shell=True)

        # Compress converted data.
        with tarfile.open(os.path.join(UPLOAD_FOLDER, job_uuid + '_output.tar.gz'), 'w:gz') as newtar:
            newtar.add(os.path.join(UPLOAD_FOLDER, job_uuid, 'output'), 'spectra')

        # Clean up files.
        os.remove(os.path.join(UPLOAD_FOLDER, job_uuid + '.tar.gz'))
        shutil.rmtree(os.path.join(UPLOAD_FOLDER, job_uuid))
        os.remove(os.path.join(UPLOAD_FOLDER, job_uuid + '_output.tar.gz'))

        # Send files to client.
        return send_from_directory(UPLOAD_FOLDER, job_uuid + '_output.tar.gz')
