import os
import logging
from timsconvert.timestamp import get_iso8601_timestamp


def dot_d_detection(input_directory):
    """
    Search the input directory and any subdirectories for .d directory paths.

    :param input_directory: Path to the directory to be searched.
    :type: str
    :return: List of absolute paths for each .d directory found.
    :rtype: list
    """
    return [os.path.join(dirpath, directory) for dirpath, dirnames, filenames in os.walk(input_directory)
            for directory in dirnames if directory.endswith('.d')]


def schema_detection(bruker_dot_d_file):
    """
    Detect the schema used by the raw data in the Bruker .d directory.

    :param bruker_dot_d_file: Path to the .d directory of interest.
    :type: str
    :return: Capitalized schema extension (TDF, TSF, or BAF).
    :rtype: str
    """
    exts = [os.path.splitext(fname)[1] for dirpath, dirnames, filenames in os.walk(bruker_dot_d_file)
            for fname in filenames]
    if '.tdf' in exts and '.tsf' not in exts and '.baf' not in exts:
        return 'TDF'
    elif '.tsf' in exts and '.tdf' not in exts and '.baf' not in exts:
        return 'TSF'
    elif '.baf' in exts and '.tdf' not in exts and '.tsf' not in exts:
        return 'BAF'


def check_for_multiple_analysis(bruker_dot_d_file):
    """
    Check to ensure that only a single .baf/.tsf/.tdf and associated .tsf_bin/.tdf_bin exists within the .d directory.

    :param bruker_dot_d_file: Path to the .d directory of interest.
    :type: str
    """
    fnames = [fname for dirpath, dirnames, filenames in os.walk(bruker_dot_d_file) for fname in filenames]
    if len(fnames) != len(set(fnames)):
        logging.warning(get_iso8601_timestamp() + ':' + 'Duplicate analysis file detected within .d directory...')
        logging.warning(get_iso8601_timestamp() + ':' + 'Skipping conversion of ' + bruker_dot_d_file + '...')
        return True
    fnames = [os.path.splitext(fname)[0] for dirpath, dirnames, filenames in os.walk(bruker_dot_d_file)
              for fname in filenames]
    if len(fnames) != len(set(fnames)):
        logging.warning(get_iso8601_timestamp() + ':' + 'Duplicate analysis file detected within .d directory...')
        logging.warning(get_iso8601_timestamp() + ':' + 'Skipping conversion of ' + bruker_dot_d_file + '...')
        return True
    fname_exts = [os.path.splitext(fname)[1] for dirpath, dirnames, filenames in os.walk(bruker_dot_d_file)
                  for fname in filenames]
    fname_exts = [ext for ext in fname_exts if ext in ['.baf', '.tsf', '.tdf', '.tsf_bin', '.tdf_bin']]
    if len(fname_exts) != len(set(fname_exts)):
        logging.warning(get_iso8601_timestamp() + ':' + 'Duplicate analysis file detected within .d directory...')
        logging.warning(get_iso8601_timestamp() + ':' + 'Skipping conversion of ' + bruker_dot_d_file + '...')
        return True
    return False
