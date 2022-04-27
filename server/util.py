import os
import datetime
import shutil
import sqlite3
import tarfile
import requests
import uuid
import pandas as pd
from server.constants import UPLOAD_FOLDER, JOBS_DB


def upload_data(filename):
    url = 'http://localhost:5000/upload'
    files = {'data': ('data.tar.gz', open(filename, 'rb'))}
    req = requests.post(url, files=files)
    return req.text  # uploaded_data_path


def get_jobs_table():
    with sqlite3.connect(JOBS_DB) as conn:
        query = 'SELECT * FROM jobs'
        jobs_table = pd.read_sql_query(query, conn)
    return jobs_table


def generate_uuid():
    jobs_table = get_jobs_table()
    job_uuid_list = jobs_table['id'].values.tolist()
    while True:
        job_uuid = str(uuid.uuid4().hex)
        if job_uuid not in job_uuid_list:
            return job_uuid


def decompress_tarball(uploaded_data_path):
    if uploaded_data_path.endswith('.tar.gz'):
        with tarfile.open(uploaded_data_path) as tarball:
            tarball_dirname = uploaded_data_path[:-7]
            tarball.extractall(tarball_dirname)
        return tarball_dirname


def get_default_args(job_uuid):
    args = {'uuid': job_uuid,
            'input': decompress_tarball(os.path.join(UPLOAD_FOLDER, str(job_uuid) + '.tar.gz')),
            'outdir': os.path.join(UPLOAD_FOLDER, str(job_uuid), 'output'),
            'outfile': '',
            'mode': 'centroid',
            'compression': 'zlib',
            'ms2_only': False,
            'exclude_mobility': False,
            'encoding': 64,
            'profile_bins': 0,
            'maldi_output_file': 'combined',
            'maldi_plate_map': '',  # check if exists in tarball and if not make it blank
            'imzml_mode': 'processed',
            'lcms_backend': 'timsconvert',
            'chunk_size': 10,
            'verbose': False,
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
        cur.execute('INSERT INTO jobs (id,status,start_time,data) VALUES (?,?,?,?)',
                    (job_uuid, 'PENDING', datetime.datetime.now(), 'ON_SERVER'))
        conn.commit()


def compress_output(output_directory_path, job_uuid):
    with tarfile.open(os.path.join(UPLOAD_FOLDER, job_uuid + '_output.tar.gz'), 'w:gz') as newtar:
        newtar.add(os.path.join(output_directory_path, 'output'), 'spectra')
    return


# Delete data more than 7 days old.
def cleanup_server():
    jobs_table = get_jobs_table()
    done_jobs_table = jobs_table[jobs_table.status == 'DONE']
    done_jobs_table = done_jobs_table[done_jobs_table.data == 'ON_SERVER']
    with sqlite3.connect(JOBS_DB) as conn:
        cur = conn.cursor()
        for index, row in done_jobs_table.iterrows():
            seconds_passed = datetime.datetime.now() - datetime.datetime.fromisoformat(row['start_time'])
            seconds_passed = seconds_passed.total_seconds()
            if seconds_passed >= 604800:
            #if seconds_passed >= 1:
                # Delete uploaded tarball.
                os.remove(os.path.join(UPLOAD_FOLDER, str(row['id']) + '.tar.gz'))
                # Delete untared raw and converted data.
                shutil.rmtree(os.path.join(UPLOAD_FOLDER, str(row['id'])))
                # Delete converted tarball.
                os.remove(os.path.join(UPLOAD_FOLDER, str(row['id']) + '_output.tar.gz'))
                cur.execute('UPDATE jobs SET data=? WHERE id=?', ('DELETED', row['id']))
                conn.commit()
    return
