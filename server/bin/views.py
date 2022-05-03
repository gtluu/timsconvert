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

@app.route('/convert', methods=['POST'])
def upload():
    # Get tarball.
    uploaded_data = request.files['data']
    if 'plate_map' in request.files.keys():
        uploaded_plate_map = request.files['plate_map']
    # Get UUID for job.
    job_uuid = generate_uuid()
    # Save tarball to server.
    uploaded_data_path = os.path.join(UPLOAD_FOLDER, str(job_uuid) + '.tar.gz')
    uploaded_data.save(uploaded_data_path)

    # Decompress uploaded data.
    decompress_tarball(os.path.join(UPLOAD_FOLDER, str(job_uuid) + '.tar.gz'))
    if 'plate_map' in request.files['plate_map']:
        uploaded_plate_map_path = os.path.join(UPLOAD_FOLDER, str(job_uuid), 'data',
                                                str(job_uuid) + '_plate_map.csv')
        uploaded_plate_map.save(uploaded_plate_map_path)
    
    # Running conversion
    run_timsconvert(args)

    # Sending back job uuid

    return job_uuid


# TODO: Update this
@app.route('/download_results', methods=['GET'])
def download_results():
    if request.method == 'GET':
        # Get UUID from GET request.
        job_uuid = request.args.get('uuid')
        # Check to make sure data not deleted.
        if str(file_presence) == 'ON_SERVER':
            # Compress data for download.
            compress_data(job_uuid)
            # Download data.
            return send_from_directory(UPLOAD_FOLDER, job_uuid + '_output.tar.gz')
        elif str(file_presence) == 'DELETED':
            return 'DELETED'

        # TODO: Add synchronous cleanup


