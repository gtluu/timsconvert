from timsconvert.classes import *
from timsconvert.init_bruker_dll import *
import alphatims.bruker


# modified from alphatims
if sys.platform[:5] == 'win32':
    # change filepath later.
    BRUKER_DLL_FILE_NAME = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
                                        'lib\\timsdata.dll')
elif sys.platform[:5] == 'linux':
    BRUKER_DLL_FILE_NAME = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
                                        'lib\\timsdata.so')
else:
    # Add logging warning here.
    BRUKER_DLL_FILE_NAME = ''

dll = init_bruker_dll(BRUKER_DLL_FILE_NAME)

if __name__ == '__main__':
    tdf_dd_file = 'F:\\code\\timsconvert_no\\data\\PenMB-ZoneofInhibition-568-MALDI-TIMS-MS-MS-P1-2.319_0_C7_MSMS568.1313.d'
    tdf = tdf_data(tdf_dd_file, dll)
    print(tdf.meta_data)
    print(tdf.read_scans(1, 702, 703))
    mz_array, intensity_array = tdf.extract_centroided_spectrum_for_frame(1, 1, 865)
    print(mz_array)
    print(intensity_array)
    print(np.array(list(range(1, 866))).size)
    print(tdf.scan_num_to_oneoverk0(1, np.array(list(range(1, 866)))))
    print(tdf.scan_num_to_oneoverk0(1, np.array([651])))
    print(tdf.read_scans(1, 1, 3)[0][0])
    at_tdf = alphatims.bruker.TimsTOF(tdf_dd_file)
    #at_tdf[:, :, :, :, :].to_csv('F:\\code\\alphatims_test_data\\maldi_dd_tdf_ms2.csv')
    print(at_tdf[1]['scan_indices'].values.tolist())
    print(at_tdf[1, 582])
