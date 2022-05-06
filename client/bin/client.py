import os
import shutil
import tarfile
import requests
import argparse

URL = 'http://localhost:6521'


def submit_timsconvert_job(filename, output_dir, url):
    # tar data
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
    data_obj = open(new_tarball, 'rb')
    files = {'data': ('data.tar.gz', data_obj)}
    req = requests.post(url + '/convert', files=files)
    data_obj.close()

    # Download data
    with open(os.path.join(output_dir, 'timsconvert_job.tar.gz'), 'wb') as dl_tarball:
        dl_tarball.write(req.content)

    # Decompress uploaded data.
    with tarfile.open(os.path.join(output_dir, 'timsconvert_job.tar.gz')) as tarball:
        tarball.extractall(os.path.join(output_dir, 'timsconvert_job'))

    if req.status_code == 200:
        return 'ok'
    else:
        req.raise_for_status()


if __name__ == '__main__':
    # Initialize parser.
    parser = argparse.ArgumentParser()
    parser.add_argument('--input', help='Input tarball.', required=True, type=str)
    parser.add_argument('--outdir', help='Output directory', default="spectra", type=str)
    args = parser.parse_args()

    submit_timsconvert_job(args.input, args.outdir, URL)
