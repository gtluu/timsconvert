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


# Gets global metadata table from .tsf or .tdf as a dictionary.
def get_metadata(bruker_d_folder_name, schema):
    if schema == 'TSF':
        analysis = 'analysis.tsf'
    elif schema == 'TDF':
        analysis = 'analysis.tdf'
    conn = sqlite3.connect(os.path.join(bruker_d_folder_name, analysis))
    metadata_query = 'SELECT * FROM GlobalMetadata'
    metadata_df = pd.read_sql_query(metadata_query, conn)
    metadata_dict = {}
    for index, row in metadata_df.iterrows():
        metadata_dict[row['Key']] = row['Value']
    return metadata_dict


# Read in Bruker .d/.tdf files into dataframe using AlphaTims.
def bruker_to_df(filename):
    return alphatims.bruker.TimsTOF(filename)


if __name__ == '__main__':
    logger = logging.getLogger(__name__)
