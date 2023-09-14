import os
import logging


# Scan directory for Bruker .d files.
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


# Detect whether .d file is .tdf or .tsf.
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
