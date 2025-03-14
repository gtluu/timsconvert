import os
import logging
from timsconvert.timestamp import get_iso8601_timestamp


def line_scan_metadata_detection(input_directory):
    """
    Search the input directory and any subdirectories for .d directory paths.

    :param input_directory: Path to the directory to be searched.
    :type: str
    :return: List of absolute paths for each .csv file found.
    :rtype: list
    """
    if not os.path.exists(input_directory):
        logging.info(get_iso8601_timestamp() + ':' + f'{input_directory} does not exist...')
        logging.info(get_iso8601_timestamp() + ':' + 'Skipping...')
    else:
        return [os.path.join(dirpath, filename) for dirpath, dirnames, filenames in os.walk(input_directory)
                for filename in filenames if filename.endswith('.csv')]
