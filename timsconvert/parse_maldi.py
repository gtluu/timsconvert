from .timestamp import *
from .constants import *
import alphatims.bruker
import alphatims.utils
from lxml import etree as et
import sqlite3
import numpy as np
import pandas as pd
import os
import sys
import itertools
import logging


def parse_maldi_plate_map(plate_map_filename):
    plate_map = pd.read_csv(plate_map_filename, header=None)
    plate_dict = {}
    for index, row in plate_map.itterrows():
        for count, value in enumerate(row, start=1):
            plate_dict[chr(index + 65) + str(count)] = value
    return plate_dict


def parse_maldi_tsf(tsf_data, centroid):
    list_of_frames_dict = tsf_data.frames.todict(orient='records')
    list_of_scan_dicts = []
    for index, row in tsf_data.maldiframeinfo.iterrows():
        frames_dict = [i for i in list_of_frames_dict if int(i['Id']) == int(row['Frame'])][0]
        index_buf, intensity_array = tsf_data.read_line_spectrum(int(row['Frame']))
        mz_array = tsf_data.index_to_mz(int(row['Frame']), index_buf)
        if int(frames_dict['MsMsType']) in MSMS_TYPE_CATEGORY['ms1']:
            scan_type = 'MS1 spectrum'
            ms_level = 1
        elif int(frames_dict['MsMsType']) in MSMS_TYPE_CATEGORY['ms2']:
            scan_type = 'MSn spectrum'
            ms_level = 2
        else:
            scan_type = None
            ms_level = None

        if mz_array.size != 0 and intensity_array.size != 0:
            base_peak_index = np.where(intensity_array == np.max(intensity_array))
            if tsf_data.meta_data['MaldiApplicationType'] == 'SingleSpectra':
                list_of_scan_dicts.append({'scan_number': None,
                                           'mz_array': mz_array,
                                           'intensity_array': intensity_array,
                                           'coord': row['SpotName'],
                                           'scan_type': scan_type,
                                           'polarity': frames_dict['Polarity'],
                                           'centroided': centroid,
                                           'retention_time': 0,
                                           'total_ion_current': sum(intensity_array),
                                           'base_peak_mz': float(mz_array[base_peak_index]),
                                           'base_peak_intensity': float(intensity_array[base_peak_index]),
                                           'ms_level': ms_level,
                                           'high_mz': float(max(mz_array)),
                                           'low_mz': float(min(mz_array))})
            elif tsf_data.meta_data['MaldiApplicationType'] == 'Imaging':
                coords = []
                coords.append(int(row['XIndexPos']))
                coords.append(int(row['YIndexPos']))
                if 'ZIndexPos' in tsf_data.maldiframeinfo.columns:
                    coords.append(int(row['ZIndexPos']))
                list_of_scan_dicts.append({'scan_number': None,
                                           'mz_array': mz_array,
                                           'intensity_array': intensity_array,
                                           'coord': tuple(coords),
                                           'scan_type': scan_type,
                                           'polarity': frames_dict['Polarity'],
                                           'centroided': centroid,
                                           'retention_time': 0,
                                           'total_ion_current': sum(intensity_array),
                                           'base_peak_mz': float(mz_array[base_peak_index]),
                                           'base_peak_intensity': float(intensity_array[base_peak_index]),
                                           'ms_level': ms_level,
                                           'high_mz': float(max(mz_array)),
                                           'low_mz': float(min(mz_array))})
    return list_of_scan_dicts


def parse_maldi_tdf(tdf_data, infile, centroid):
    con = sqlite3.connect(os.path.join(infile, 'analysis.tdf'))
    frames_query = 'SELECT * FROM Frames'
    frames_df = pd.read_sql_query(frames_query, con)
    maldiframeinfo_query = 'SELECT * FROM MaldiFrameInfo'
    maldiframeinfo_df = pd.read_sql_query(maldiframeinfo_query, con)

    list_of_frames_dict = frames_df.to_dict(orient='records')
    list_of_scan_dicts = []
    for index, row in maldiframeinfo_df.iterrows():
        frames_dict = [i for i in list_of_frames_dict if int(i['Id']) == int(row['Frame'])][0]


if __name__ == '__main__':
    logger = logging.getLogger(__name__)
