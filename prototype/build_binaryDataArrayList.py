import alphatims.bruker
from psims.mzml import MzMLWriter
from lxml import etree as et
import os
import pandas as pd


# Read in Bruker .d/.tdf files into dataframe using AlphaTIMS.
def bruker_to_df(filename):
    return alphatims.bruker.TimsTOF(filename)


# Check method for PASEF NumRampsPerCycle.
# From microTOFQImpacTemAcquisition.method XML file.
def get_pasef_ramps(input_filename):
    # Get method file path.
    for dirpath, dirnames, filenames in os.walk(input_filename):
        for dirname in dirnames:
            if os.path.splitext(dirname)[1].lower() == '.m':
                method_file = os.path.join(dirpath, dirname, 'microTOFQImpacTemAcquisition.method')

    # Open XML file and get number of ramps per cycle.
    method_data = et.parse(method_file).getroot()
    num_ramps_per_cycle = method_data.xpath('//para_int[@permname="MSMS_Pasef_NumRampsPerCycle"]')[0].attrib['value']
    return num_ramps_per_cycle


# Extract retention time, m/z, intensity, and mobility arrays from dataframe for each scan.
def build_binaryDataArrayList(input_filename, raw_data):
    raw_data_df = raw_data[:, :, :, :, :]
    num_ramps_per_cycle = get_pasef_ramps(input_filename)
    num_of_frames = len(set(raw_data_df['frame_indices']))

    scan_dicts = []
    # ms1_quad_mz is a list containing only the value -1.
    # quad_low_mz_values and quad_high_mz_values will be a Pandas series containing only the value -1 if scan is MS1.
    ms1_quad_mz = pd.Series(-1).unique()
    #for frame_num in range(1, num_of_frames+1):
    for frame_num in range(1, 2):
        low_mz_series = raw_data[frame_num:frame_num+1]['quad_low_mz_values'].unique()
        high_mz_series = raw_data[frame_num:frame_num+1]['quad_high_mz_values'].unique()
        # If True, scan/frame is ms1
        if low_mz_series.size == 1 and high_mz_series.size == 1:
            if ms1_quad_mz == low_mz_series and ms1_quad_mz == high_mz_series:
                retention_time = raw_data[frame_num:frame_num+1]['rt_values'].unique()
                sorted_raw_data_df = raw_data[frame_num:frame_num+1].sort_values(by='mz_values')
                print(retention_time)
                print(sorted_raw_data_df)
                print(sorted_raw_data_df['mz_values'])
                print(sorted_raw_data_df['intensity_values'])
        else:
            print('skip')

if __name__ == '__main__':
    tdf_file = 'F:\\alphatims_test\\pen12_ms2_1_36_1_400.d'
    raw_data = bruker_to_df(tdf_file)
    build_binaryDataArrayList(tdf_file, raw_data)
