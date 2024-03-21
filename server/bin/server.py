import os
import shutil
import tarfile
import uuid
import subprocess
import json
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


@app.route('/heartbeat', methods=['GET'])
def render_heartbeat():
    return json.dumps({'status': 'success'})


@app.route('/convert', methods=['POST'])
def convert():
    if request.method == 'POST':
        # Generate UUID.
        job_uuid = str(uuid.uuid4().hex)

        # Get tarball and save to server.
        uploaded_data = request.files['data']
        uploaded_data_path = os.path.join(UPLOAD_FOLDER, job_uuid + '.tar.gz')
        uploaded_data.save(uploaded_data_path)

        # Decompress uploaded data.
        with tarfile.open(uploaded_data_path) as tarball:
            tarball_dirname = os.path.join(UPLOAD_FOLDER, job_uuid)
            def is_within_directory(directory, target):
                
                abs_directory = os.path.abspath(directory)
                abs_target = os.path.abspath(target)
            
                prefix = os.path.commonprefix([abs_directory, abs_target])
                
                return prefix == abs_directory
            
            def safe_extract(tar, path=".", members=None, *, numeric_owner=False):
            
                for member in tar.getmembers():
                    member_path = os.path.join(path, member.name)
                    if not is_within_directory(path, member_path):
                        raise Exception("Attempted Path Traversal in Tar File")
            
                tar.extractall(path, members, numeric_owner=numeric_owner) 
                
            
            safe_extract(tarball, tarball_dirname)

        # Build TIMSCONVERT command.
        run_path = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))), 'run.py')
        outdir_path = os.path.join(UPLOAD_FOLDER, job_uuid, 'output')
        cmd = 'python ' + run_path + ' --input ' + tarball_dirname + ' --outdir ' + outdir_path + ' --verbose'

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
