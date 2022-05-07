import os
import shutil
import tarfile
import requests
import argparse


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
    req.raise_for_status()

    # Download data
    result_tar_filename = os.path.join(output_dir, 'timsconvert_job.tar.gz')
    with open(result_tar_filename, 'wb') as dl_tarball:
        dl_tarball.write(req.content)

    # Decompress uploaded data.
    with tarfile.open(result_tar_filename) as tarball:
        print(tarball.getnames())
        print(filename)
        if "output.mzML" in tarball.getnames():
            output_filename = os.path.join(output_dir, os.path.basename(filename.replace(".d", ".mzML")))
            temp_filename = os.path.join(output_dir, "output.mzML")
            tarball.extract('output.mzML', output_dir)

            # Moving to correct filename
            os.rename(temp_filename, output_filename)
        if "output.imzML" in tarball.getnames():
            output_imzml = os.path.join(output_dir, os.path.basename(filename.replace(".d", ".imzML")))
            output_ibd = os.path.join(output_dir, os.path.basename(filename.replace(".d", ".ibd")))

            temp_imzml = os.path.join(output_dir, "output.imzML")
            tarball.extract('output.imzML', output_dir)

            temp_ibd = os.path.join(output_dir, "output.ibd")
            tarball.extract('output.ibd', output_dir)

            # Moving to correct filename
            os.rename(temp_imzml, output_imzml)
            os.rename(temp_ibd, output_ibd)
            
    # Cleanup
    os.remove(result_tar_filename)

    return 0

if __name__ == '__main__':
    # Initialize parser.
    parser = argparse.ArgumentParser()
    parser.add_argument('--input', help='Input tarball.', required=True, type=str)
    parser.add_argument('--outdir', help='Output directory', default="spectra", type=str)
    parser.add_argument('--host', help='Host for server', default="localhost:6521")
    args = parser.parse_args()

    submit_timsconvert_job(args.input, args.outdir, "http://" + args.host)
