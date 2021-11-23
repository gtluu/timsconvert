import alphatims.bruker
import os
import logging
import sqlite3
import pandas as pd


# Scan directory for Bruker .d files.
def dot_d_detection(input_directory):
    return [os.path.join(dirpath, directory) for dirpath, dirnames, filenames in os.walk(input_directory)
            for directory in dirnames if directory.endswith('.d')]


# Detect whether .d file is .tdf or .tsf.
def schema_detection(bruker_dot_d_file):
    exts = [os.path.splitext(fname)[1] for dirpath, dirnames, filenames in os.walk(bruker_dot_d_file)
            for fname in filenames]
    if '.tdf' in exts and '.tsf' not in exts:
        return 'TDF'
    elif '.tsf' in exts and '.tdf' not in exts:
        return 'TSF'


# Read in Bruker .d/.tdf files into dataframe using AlphaTims.
def bruker_to_df(filename):
    return alphatims.bruker.TimsTOF(filename)


if __name__ == '__main__':
    logger = logging.getLogger(__name__)
