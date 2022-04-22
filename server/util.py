import os
import tarfile
import subprocess
from server.constants import UPLOAD_FOLDER


def decompress_tarball(uploaded_data_path):
    if uploaded_data_path.endswith('.tar.gz'):
        with tarfile.open(uploaded_data_path) as tarball:
            tarball.extractall(UPLOAD_FOLDER)
        tarball_filename = uploaded_data_path[:-7]
        return tarball_filename


def parse_request_data(request):
    # Save uploaded files.
    uploaded_data = request.files['data']
    uploaded_data_path = os.path.join(UPLOAD_FOLDER, uploaded_data.filename)
    uploaded_data.save(uploaded_data_path)

    if str(request.form['plate_map_present']) == 'True':
        uploaded_plate_map = request.files['plate_map']
        uploaded_plate_map_path = os.path.join(UPLOAD_FOLDER, uploaded_plate_map.filename)
        uploaded_plate_map.save(uploaded_plate_map_path)
    elif str(request.form['plate_map_present']) == 'False':
        uploaded_plate_map_path = ''

    # Get args for TIMSCONVERT.
    args = {'--input': decompress_tarball(uploaded_data_path),
            '--outdir': os.path.join(UPLOAD_FOLDER, 'output'),
            '--maldi_plate_map': uploaded_plate_map_path,
            '--ms2_only': str(request.form['ms2_only']),
            '--exclude_mobility': str(request.form['exclude_mobility']),
            '--maldi_output_file': str(request.form['maldi_output_mode']),
            '--imzml_mode': str(request.form['imzml_mode']),
            '--verbose': 'True'}

    return args


def run_timsconvert_process(args):
    # Build TIMSCONVERT command.
    run_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'run.py')
    cmd = 'python ' + run_path + ' '
    for key, value in args.items():
        if value == 'True':
            cmd += str(key) + ' '
        elif value != '' and value != 'False':
            cmd += str(key) + ' ' + str(value) + ' '

    # Run TIMSCONVERT.
    subprocess.call(cmd, shell=True)

    # Update job status.
    with open(os.path.join(UPLOAD_FOLDER, 'status.txt'), 'w') as status_file:
        status_file.write('done')
    return


def compress_output(output_directory_path):
    with tarfile.open(os.path.join(UPLOAD_FOLDER, 'timsconvert_spectra.tar.gz'), 'w:gz') as newtar:
        newtar.add(output_directory_path, 'spectra')
    return
