import os
import shutil
import tarfile
import requests
import argparse

URL = 'http://localhost:5000'


def submit_timsconvert_job(filename, url):
    # tar data
    if not filename.endswith('.tar.gz'):
        new_tarball = filename + '.tar.gz'
        with tarfile.open(new_tarball, 'w:gz') as newtar:
            if filename.endswith('.d'):
                shutil.copytree(filename, os.path.join('tmp', os.path.split(filename)[-1]))
                newtar.add('tmp', 'data')
                shutil.rmtree(os.path.join('tmp', os.path.split(filename)[-1]))
                os.rmdir('tmp')
            else:
                newtar.add(filename, 'data')

    # Upload data
    data_obj = open(filename + '.tar.gz', 'rb')
    files = {'data': ('data.tar.gz', data_obj)}
    req = requests.post(url + '/convert', files=files)
    data_obj.close()

    # Download data
    with open(os.path.join('timsconvert_job.tar.gz'), 'wb') as dl_tarball:
        dl_tarball.write(req.content)

    if req.status_code == 200:
        return 'ok'
    else:
        req.raise_for_status()


if __name__ == '__main__':
    # Initialize parser.
    parser = argparse.ArgumentParser()
    parser.add_argument('--input', help='Input tarball.', required=True, type=str)
    arguments = vars(parser.parse_args())

    submit_timsconvert_job(arguments['input'], URL)
