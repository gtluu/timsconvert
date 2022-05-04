import os
import requests
import argparse

URL = 'http://localhost:6521'


def submit_timsconvert_job(filename, url):
    # Upload data
    data_obj = open(filename, 'rb')
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
