# views.py
from flask import abort, jsonify, render_template, request, redirect, url_for, make_response, send_from_directory
import uuid

from app import app
import os
import glob
import json
import tarfile
import subprocess


UPLOAD_FOLDER = "./data"

@app.route('/heartbeat', methods=['GET'])
def heartbeat():
    return "{}"

@app.route('/convert', methods=['POST'])
def convert():
    # Generate UUID.
    job_uuid = str(uuid.uuid4().hex)

    # Creating outputing directory
    temp_dir = os.path.join(UPLOAD_FOLDER, job_uuid)
    os.makedirs(temp_dir) # Making sure the folder exists

    # Get tarball and save to server.
    uploaded_data = request.files['data']
    uploaded_data_path = os.path.join(UPLOAD_FOLDER, job_uuid, 'upload.tar.gz')
    uploaded_data.save(uploaded_data_path)

    # Decompress uploaded data.
    with tarfile.open(uploaded_data_path) as tarball:
        tarball.extractall(temp_dir)

    # Build TIMSCONVERT command.
    run_script = "/app/timsconvert/bin/run.py"
    input_file = glob.glob(os.path.join(temp_dir, '*.d'))[0]
    output_file = os.path.join(temp_dir, 'output.mzML')
    cmd = 'python {} --input {} --outfile {}'.format(run_script, input_file, output_file)

    # Run TIMSCONVERT
    #subprocess.call(cmd, shell=True)
    os.system(cmd)

    # Clean up files, we will do this later
    # os.remove(os.path.join(UPLOAD_FOLDER, job_uuid + '.tar.gz'))
    # shutil.rmtree(os.path.join(UPLOAD_FOLDER, job_uuid))
    # os.remove(os.path.join(UPLOAD_FOLDER, job_uuid + '_output.tar.gz'))

    # Send files to client.
    return send_from_directory(UPLOAD_FOLDER, os.path.basename(output_file))
