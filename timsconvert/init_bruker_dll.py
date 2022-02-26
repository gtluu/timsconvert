import ctypes
from timsconvert.constants import *


def init_baf2sql_dll(baf2sql_file_name: str=BAF2SQL_DLL_FILE_NAME):
    baf2sql_dll = ctypes.cdll.LoadLibrary(baf2sql_file_name)

    # Functions for .baf files
    # .baf open
    baf2sql_dll.baf2sql_array_open_storage.argtypes = [ctypes.c_int, ctypes.c_char_p]
    baf2sql_dll.baf2sql_array_open_storage.restype = ctypes.c_uint64

    # .baf close
    baf2sql_dll.baf2sql_array_close_storage.argtypes = [ctypes.c_uint64]
    baf2sql_dll.baf2sql_array_close_storage.restype = None

    # Get SQLite cache filename
    baf2sql_dll.baf2sql_get_sqlite_cache_filename_v2.argtypes = [ctypes.c_char_p,
                                                                 ctypes.c_uint32,
                                                                 ctypes.c_char_p,
                                                                 ctypes.c_int]
    baf2sql_dll.baf2sql_get_sqlite_cache_filename_v2.restype = ctypes.c_uint32

    # Get number of elements in array
    baf2sql_dll.baf2sql_array_get_num_elements.argtypes = [ctypes.c_uint64,
                                                           ctypes.c_uint64,
                                                           ctypes.POINTER(ctypes.c_uint64)]
    baf2sql_dll.baf2sql_array_get_num_elements.restype = ctypes.c_int

    # Read array as double
    baf2sql_dll.baf2sql_array_read_double.argtypes = [ctypes.c_uint64,
                                                      ctypes.c_uint64,
                                                      ctypes.POINTER(ctypes.c_double)]
    baf2sql_dll.baf2sql_array_read_double.restype = ctypes.c_int

    # Get last error as string
    baf2sql_dll.baf2sql_get_last_error_string.argtypes = [ctypes.c_char_p, ctypes.c_uint32]
    baf2sql_dll.baf2sql_get_last_error_string.restype = ctypes.c_uint32

    return baf2sql_dll


# modified from alphatims
def init_tdf_sdk_dll(bruker_dll_file_name: str=TDF_SDK_DLL_FILE_NAME):
    tdf_sdk_dll = ctypes.cdll.LoadLibrary(os.path.realpath(bruker_dll_file_name))

    # Functions for .tsf files
    # Only load .tsf functions if on Windows; newer Linux .so library errors our due to Boost C++ lib in source code.
    if TDF_SDK_VERSION == 'sdk2871' or TDF_SDK_VERSION == 'sdk270':
        # .tsf Open
        tdf_sdk_dll.tsf_open.argtypes = [ctypes.c_char_p, ctypes.c_uint32]
        tdf_sdk_dll.tsf_open.restype = ctypes.c_uint64

        # .tsf Close
        tdf_sdk_dll.tsf_close.argtypes = [ctypes.c_uint64]
        tdf_sdk_dll.tsf_close.restype = None

        # Read in profile or line spectra
        tdf_sdk_dll.tsf_read_line_spectrum.argtypes = [ctypes.c_uint64,
                                                      ctypes.c_int64,
                                                      ctypes.POINTER(ctypes.c_double),
                                                      ctypes.POINTER(ctypes.c_float),
                                                      ctypes.c_uint32]
        tdf_sdk_dll.tsf_read_line_spectrum.restype = ctypes.c_uint32
        tdf_sdk_dll.tsf_read_profile_spectrum.argtypes = [ctypes.c_uint64,
                                                         ctypes.c_int64,
                                                         ctypes.POINTER(ctypes.c_uint32),
                                                         ctypes.c_uint32]
        tdf_sdk_dll.tsf_read_profile_spectrum.restype = ctypes.c_uint32

        # Get m/z values from indices.
        tdf_sdk_dll.tsf_index_to_mz.argtypes = [ctypes.c_uint64,
                                               ctypes.c_int64,
                                               ctypes.POINTER(ctypes.c_double),
                                               ctypes.POINTER(ctypes.c_double),
                                               ctypes.c_uint32]
        tdf_sdk_dll.tsf_index_to_mz.restype = ctypes.c_uint32

    # Functions for .tdf files
    # .tdf Open
    tdf_sdk_dll.tims_open.argtypes = [ctypes.c_char_p, ctypes.c_uint32]
    tdf_sdk_dll.tims_open.restype = ctypes.c_uint64

    # .tdf Close
    tdf_sdk_dll.tims_close.argtypes = [ctypes.c_uint64]
    tdf_sdk_dll.tims_close.restype = None

    # Read scans from .tdf
    tdf_sdk_dll.tims_read_scans_v2.argtypes = [ctypes.c_uint64,
                                              ctypes.c_int64,
                                              ctypes.c_uint32,
                                              ctypes.c_uint32,
                                              ctypes.c_void_p,
                                              ctypes.c_uint32]
    tdf_sdk_dll.tims_read_scans_v2.restype = ctypes.c_uint32

    # Read PASEF MSMS
    MSMS_SPECTRUM_FUNCTOR = ctypes.CFUNCTYPE(None,
                                             ctypes.c_int64,
                                             ctypes.c_uint32,
                                             ctypes.POINTER(ctypes.c_double),
                                             ctypes.POINTER(ctypes.c_float))
    tdf_sdk_dll.tims_read_pasef_msms.argtypes = [ctypes.c_uint64,
                                                ctypes.POINTER(ctypes.c_int64),
                                                ctypes.c_uint32,
                                                MSMS_SPECTRUM_FUNCTOR]
    tdf_sdk_dll.tims_read_pasef_msms.restype = ctypes.c_uint32
    tdf_sdk_dll.tims_read_pasef_msms_for_frame.argtypes = [ctypes.c_uint64,
                                                          ctypes.c_int64,
                                                          MSMS_SPECTRUM_FUNCTOR]
    tdf_sdk_dll.tims_read_pasef_msms_for_frame.restype = ctypes.c_uint32
    MSMS_PROFILE_SPECTRUM_FUNCTOR = ctypes.CFUNCTYPE(None,
                                                     ctypes.c_int64,
                                                     ctypes.c_uint32,
                                                     ctypes.POINTER(ctypes.c_int32))
    # Only available in SDK version 2.8.7.1 or 2.7.0.
    if TDF_SDK_VERSION == 'sdk2871' or TDF_SDK_VERSION == 'sdk270':
        tdf_sdk_dll.tims_read_pasef_profile_msms.argtypes = [ctypes.c_uint64,
                                                            ctypes.POINTER(ctypes.c_int64),
                                                            ctypes.c_uint32,
                                                            MSMS_PROFILE_SPECTRUM_FUNCTOR]
        tdf_sdk_dll.tims_read_pasef_profile_msms.restype = ctypes.c_uint32
        tdf_sdk_dll.tims_read_pasef_profile_msms_for_frame.argtypes = [ctypes.c_uint64,
                                                                      ctypes.c_int64,
                                                                      MSMS_PROFILE_SPECTRUM_FUNCTOR]
        tdf_sdk_dll.tims_read_pasef_profile_msms_for_frame.restype = ctypes.c_uint32

    # Extract spectra from frames
    # Only available in SDK version 2.8.7.1
    if TDF_SDK_VERSION == 'sdk2871':
        tdf_sdk_dll.tims_extract_centroided_spectrum_for_frame.argtypes = [ctypes.c_uint64,
                                                                          ctypes.c_int64,
                                                                          ctypes.c_uint32,
                                                                          ctypes.c_uint32,
                                                                          MSMS_SPECTRUM_FUNCTOR,
                                                                          ctypes.c_void_p]
        tdf_sdk_dll.tims_extract_centroided_spectrum_for_frame.restype = ctypes.c_uint32
        tdf_sdk_dll.tims_extract_profile_for_frame.argtypes = [ctypes.c_uint64,
                                                              ctypes.c_int64,
                                                              ctypes.c_uint32,
                                                              ctypes.c_uint32,
                                                              MSMS_PROFILE_SPECTRUM_FUNCTOR,
                                                              ctypes.c_void_p]
        tdf_sdk_dll.tims_extract_profile_for_frame.restype = ctypes.c_uint32

    # Get m/z values from indices
    convfunc_argtypes = [ctypes.c_uint64,
                         ctypes.c_int64,
                         ctypes.POINTER(ctypes.c_double),
                         ctypes.POINTER(ctypes.c_double),
                         ctypes.c_uint32]
    tdf_sdk_dll.tims_index_to_mz.argtypes = convfunc_argtypes
    tdf_sdk_dll.tims_index_to_mz.restype = ctypes.c_uint32

    # Get 1/k0 values from scan number
    tdf_sdk_dll.tims_scannum_to_oneoverk0.argtypes = convfunc_argtypes
    tdf_sdk_dll.tims_scannum_to_oneoverk0.restype = ctypes.c_uint32

    # Convert 1/k0 to CCS
    # Only available in SDK version 2.8.7.1 or 2.7.0
    if TDF_SDK_VERSION == 'sdk2871' or TDF_SDK_VERSION == 'sdk270':
        tdf_sdk_dll.tims_oneoverk0_to_ccs_for_mz.argtypes = [ctypes.c_double,
                                                            ctypes.c_int32,
                                                            ctypes.c_double]
        tdf_sdk_dll.tims_oneoverk0_to_ccs_for_mz.restype = ctypes.c_double

    return tdf_sdk_dll


# from tsfdata.py
def throw_last_tsf_error(bruker_dll):
    err_len = bruker_dll.tsf_get_last_error_string(None, 0)
    buf = ctypes.create_string_buffer(err_len)
    bruker_dll.tsf_get_last_error_string(buf, err_len)
    raise RuntimeError(buf.value)


# from baf2sql.py
# Throw last baf2sql error string as exception.
def throw_last_baf2sql_error(baf2sql_dll):
    err_len = baf2sql_dll.baf2sql_get_last_error_string(None, 0)
    buf = ctypes.create_string_buffer(err_len)
    baf2sql_dll.baf2sql_get_last_error_string(buf, err_len)
    raise RuntimeError(buf.value)


# from tsfdata.py
def decode_array_of_strings(blob):
    if blob is None:
        return None
    if len(blob) == 0:
        return []
    blob = bytearray(blob)
    if blob[-1] != 0:
        raise ValueError('Illegal BLOB contents.')
    return str(blob, 'utf-8').split('\0')[:-1]


# from timsdata.py
# Convert 1/k0 to CCS for a given charge and mz
def one_over_k0_to_ccs(ook0, charge, mz):
    bruker_dll = init_tdf_sdk_dll()
    return bruker_dll.tims_oneoverk0_to_ccs_for_mz(ook0, charge, mz)


if __name__ == '__main__':
    logger = logging.getLogger(__name__)
