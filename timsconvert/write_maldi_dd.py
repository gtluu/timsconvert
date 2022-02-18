from timsconvert.constants import *
import numpy as np
import pandas as pd
import logging


def parse_maldi_plate_map(plate_map_filename):
    plate_map = pd.read_csv(plate_map_filename, header=None)
    plate_dict = {}
    for index, row in plate_map.itterrows():
        for count, value in enumerate(row, start=1):
            plate_dict[chr(index + 65) + str(count)] = value
    return plate_dict


def parse_maldi_tsf(tsf_data, frame_start, frame_end, mode, encoding):
    if encoding == 32:
        encoding_dtype = np.float32
    elif encoding == 64:
        encoding_dtype = np.float64

    logging.info(get_timestamp() + ':' + 'Parsing MALDI spectra')
    list_of_frames_dict = tsf_data.frames.to_dict(orient='records')
    if tsf_data.framemsmsinfo_dict is not None:
        list_of_framemsmsinfo_dict = tsf_data.framemsmsinfo.to_dict(orient='records')
    list_of_scan_dicts = []

    if mode == 'profile':
        centroided = False
    elif mode == 'centroid' or mode == 'raw':
        centroided = True

    for frame in range(frame_start, frame_end):
        frames_dict = [i for i in list_of_frames_dict if int(i['Id']) == frame][0]
