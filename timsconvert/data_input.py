import alphatims.bruker
import os
import logging


# Scan directory for Bruker .d files.
def dot_d_detection(input_directory):
    return [os.path.join(dirpath, directory) for dirpath, dirnames, filenames in os.walk(input_directory)
            for directory in dirnames if directory.endswith('.d')]


# Read in Bruker .d/.tdf files into dataframe using AlphaTims.
def bruker_to_df(filename):
    return alphatims.bruker.TimsTOF(filename)


if __name__ == '__main__':
    logger = logging.getLogger(__name__)
