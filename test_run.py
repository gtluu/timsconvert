from tims_converter.arguments import *
from tims_converter.data_input import *
from tims_converter.data_parsing import *
from tims_converter.write_mzml import *


# Read in example .d file and convert to dataframe.
pen12_file = 'F:\\code\\alphatims_test_data\\pen12_ms2_1_36_1_400.d'
pen12_df = bruker_to_df(pen12_file)
write_mzml(pen12_df, 'frame', pen12_file, 'F:\\code\\alphatims_test_data\\test1_frame.mzML')
write_mzml(pen12_df, 'scan', pen12_file, 'F:\\code\\alphatims_test_data\\test1_scan.mzML')
#bhi_file = 'F:\\code\\alphatims_test_data\\bhi_ms2_1_32_1_396.d'
#bhi_df = bruker_to_df(bhi_file)
#write_mzml(bhi_df, bhi_file, 'F:\\code\\alphatims_test_data\\bhi_ms2_1_32_1_396_ms1prof_ms2line.mzML')
