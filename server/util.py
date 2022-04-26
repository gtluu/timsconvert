import sys
import os
import shutil
import sqlite3
import tarfile
#import subprocess
import requests
from server.constants import UPLOAD_FOLDER, JOBS_DB


def upload_data(filename):
    url = 'http://localhost:5000/upload'
    files = {'data': ('data.tar.gz', open(filename, 'rb'))}
    req = requests.post(url, files=files)
    return req.text  # uploaded_data_path


def decompress_tarball(uploaded_data_path):
    if uploaded_data_path.endswith('.tar.gz'):
        with tarfile.open(uploaded_data_path) as tarball:
            tarball_dirname = uploaded_data_path[:-7]
            tarball.extractall(tarball_dirname)
        os.remove(uploaded_data_path)
        return tarball_dirname


def get_default_args(job_uuid):
    args = {'uuid': job_uuid,
            'input': decompress_tarball(os.path.join(UPLOAD_FOLDER, str(job_uuid) + '.tar.gz')),
            'outdir': os.path.join(UPLOAD_FOLDER, str(job_uuid), 'output'),
            'outfile': '',
            'mode': 'centroid',
            'compression': 'zlib',
            'ms2_only': True,
            'exclude_mobility': True,
            'encoding': 64,
            'profile_bins': 0,
            'maldi_output_file': 'combined',
            'maldi_plate_map': '',  # check if exists in tarball and if not make it blank
            'imzml_mode': 'processed',
            'lcms_backend': 'timsconvert',
            'chunk_size': 10,
            'verbose': True,
            'start_frame': -1,
            'end_frame': -1,
            'precision': 10.0,
            'ms1_threshold': 100.0,
            'ms2_threshold': 10.0,
            'ms2_nlargest': -1}
    return args


def add_job_to_db(job_uuid):
    with sqlite3.connect(JOBS_DB) as conn:
        cur = conn.cursor()
        cur.execute('INSERT INTO jobs (id,status) VALUES (?,?)', (job_uuid, 'PENDING'))
        conn.commit()


def compress_output(output_directory_path, job_uuid):
    with tarfile.open(os.path.join(UPLOAD_FOLDER, job_uuid + '_output.tar.gz'), 'w:gz') as newtar:
        newtar.add(os.path.join(output_directory_path, 'output'), 'spectra')
    return


def rebirth():
    shutil.rmtree(UPLOAD_FOLDER)
    os.mkdir(UPLOAD_FOLDER)
