from ctypes import (cdll, POINTER, CFUNCTYPE, create_string_buffer,
                    c_char_p, c_void_p, c_double, c_float, c_int, c_int64, c_int32, c_uint64, c_uint32)
from timsconvert.constants import *


def init_baf2sql_dll(baf2sql_file_name: str = BAF2SQL_DLL_FILE_NAME):
    """
    Initialize select functions from Bruker's Baf2sql library using ctypes.

    :param baf2sql_file_name: Path to Baf2sql library, defaults to path automatically detected in timsconvert.constants.
    :type baf2sql_file_name: str
    :return: Handle for Baf2sql library.
    :rtype: CDLL object
    """
    baf2sql_dll = cdll.LoadLibrary(baf2sql_file_name)

    # Functions for .baf files
    # .baf open
    baf2sql_dll.baf2sql_array_open_storage.argtypes = [c_int, c_char_p]
    baf2sql_dll.baf2sql_array_open_storage.restype = c_uint64

    # .baf close
    baf2sql_dll.baf2sql_array_close_storage.argtypes = [c_uint64]
    baf2sql_dll.baf2sql_array_close_storage.restype = None

    # Get SQLite cache filename
    baf2sql_dll.baf2sql_get_sqlite_cache_filename_v2.argtypes = [c_char_p,
                                                                 c_uint32,
                                                                 c_char_p,
                                                                 c_int]
    baf2sql_dll.baf2sql_get_sqlite_cache_filename_v2.restype = c_uint32

    # Get number of elements in array
    baf2sql_dll.baf2sql_array_get_num_elements.argtypes = [c_uint64,
                                                           c_uint64,
                                                           POINTER(c_uint64)]
    baf2sql_dll.baf2sql_array_get_num_elements.restype = c_int

    # Read array as double
    baf2sql_dll.baf2sql_array_read_double.argtypes = [c_uint64,
                                                      c_uint64,
                                                      POINTER(c_double)]
    baf2sql_dll.baf2sql_array_read_double.restype = c_int

    # Get last error as string
    baf2sql_dll.baf2sql_get_last_error_string.argtypes = [c_char_p, c_uint32]
    baf2sql_dll.baf2sql_get_last_error_string.restype = c_uint32

    return baf2sql_dll


# modified from alphatims
def init_tdf_sdk_dll(bruker_dll_file_name: str = TDF_SDK_DLL_FILE_NAME):
    """
    Initialize select functions from Bruker's TDF-SDK library using ctypes.

    :param bruker_dll_file_name: Path to TDF-SDK library, defaults to path automatically detected in
    timsconvert.constants.
    :type bruker_dll_file_name: str
    :return: Handle for TDF-SDK library.
    :rtype: CDLL object
    """
    tdf_sdk_dll = cdll.LoadLibrary(os.path.realpath(bruker_dll_file_name))

    # Functions for .tsf files
    # .tsf Open
    tdf_sdk_dll.tsf_open.argtypes = [c_char_p, c_uint32]
    tdf_sdk_dll.tsf_open.restype = c_uint64

    # .tsf Close
    tdf_sdk_dll.tsf_close.argtypes = [c_uint64]
    tdf_sdk_dll.tsf_close.restype = None

    # Read in profile or line spectra
    tdf_sdk_dll.tsf_read_line_spectrum.argtypes = [c_uint64,
                                                   c_int64,
                                                   POINTER(c_double),
                                                   POINTER(c_float),
                                                   c_uint32]
    tdf_sdk_dll.tsf_read_line_spectrum.restype = c_uint32
    tdf_sdk_dll.tsf_read_profile_spectrum.argtypes = [c_uint64,
                                                      c_int64,
                                                      POINTER(c_uint32),
                                                      c_uint32]
    tdf_sdk_dll.tsf_read_profile_spectrum.restype = c_uint32

    # Get m/z values from indices.
    tdf_sdk_dll.tsf_index_to_mz.argtypes = [c_uint64,
                                            c_int64,
                                            POINTER(c_double),
                                            POINTER(c_double),
                                            c_uint32]
    tdf_sdk_dll.tsf_index_to_mz.restype = c_uint32

    if TDF_SDK_VERSION == 'sdk22104':
        tdf_sdk_dll.tsf_read_line_spectrum_v2.argtypes = [c_uint64,
                                                          c_int64,
                                                          POINTER(c_double),
                                                          POINTER(c_float),
                                                          c_int32]
        tdf_sdk_dll.tsf_read_line_spectrum_v2.restype = c_int32
        tdf_sdk_dll.tsf_read_profile_spectrum_v2.argtypes = [c_uint64,
                                                             c_int64,
                                                             POINTER(c_uint32),
                                                             c_int32]
        tdf_sdk_dll.tsf_read_profile_spectrum_v2.restype = c_int32

    # Functions for .tdf files
    # .tdf Open
    tdf_sdk_dll.tims_open.argtypes = [c_char_p, c_uint32]
    tdf_sdk_dll.tims_open.restype = c_uint64

    # .tdf Close
    tdf_sdk_dll.tims_close.argtypes = [c_uint64]
    tdf_sdk_dll.tims_close.restype = None

    # Read scans from .tdf
    tdf_sdk_dll.tims_read_scans_v2.argtypes = [c_uint64,
                                               c_int64,
                                               c_uint32,
                                               c_uint32,
                                               c_void_p,
                                               c_uint32]
    tdf_sdk_dll.tims_read_scans_v2.restype = c_uint32

    # Read PASEF MSMS
    MSMS_SPECTRUM_FUNCTOR = CFUNCTYPE(None,
                                      c_int64,
                                      c_uint32,
                                      POINTER(c_double),
                                      POINTER(c_float))
    tdf_sdk_dll.tims_read_pasef_msms.argtypes = [c_uint64,
                                                 POINTER(c_int64),
                                                 c_uint32,
                                                 MSMS_SPECTRUM_FUNCTOR]
    tdf_sdk_dll.tims_read_pasef_msms.restype = c_uint32
    tdf_sdk_dll.tims_read_pasef_msms_for_frame.argtypes = [c_uint64,
                                                           c_int64,
                                                           MSMS_SPECTRUM_FUNCTOR]
    tdf_sdk_dll.tims_read_pasef_msms_for_frame.restype = c_uint32
    MSMS_PROFILE_SPECTRUM_FUNCTOR = CFUNCTYPE(None,
                                              c_int64,
                                              c_uint32,
                                              POINTER(c_int32))

    tdf_sdk_dll.tims_read_pasef_profile_msms.argtypes = [c_uint64,
                                                         POINTER(c_int64),
                                                         c_uint32,
                                                         MSMS_PROFILE_SPECTRUM_FUNCTOR]
    tdf_sdk_dll.tims_read_pasef_profile_msms.restype = c_uint32
    tdf_sdk_dll.tims_read_pasef_profile_msms_for_frame.argtypes = [c_uint64,
                                                                   c_int64,
                                                                   MSMS_PROFILE_SPECTRUM_FUNCTOR]
    tdf_sdk_dll.tims_read_pasef_profile_msms_for_frame.restype = c_uint32

    # Extract spectra from frames
    if TDF_SDK_VERSION != 'sdk22104':
        tdf_sdk_dll.tims_extract_centroided_spectrum_for_frame.argtypes = [c_uint64,
                                                                           c_int64,
                                                                           c_uint32,
                                                                           c_uint32,
                                                                           MSMS_SPECTRUM_FUNCTOR,
                                                                           c_void_p]
        tdf_sdk_dll.tims_extract_centroided_spectrum_for_frame.restype = c_uint32
    tdf_sdk_dll.tims_extract_profile_for_frame.argtypes = [c_uint64,
                                                           c_int64,
                                                           c_uint32,
                                                           c_uint32,
                                                           MSMS_PROFILE_SPECTRUM_FUNCTOR,
                                                           c_void_p]
    tdf_sdk_dll.tims_extract_profile_for_frame.restype = c_uint32

    # Get m/z values from indices
    convfunc_argtypes = [c_uint64,
                         c_int64,
                         POINTER(c_double),
                         POINTER(c_double),
                         c_uint32]
    tdf_sdk_dll.tims_index_to_mz.argtypes = convfunc_argtypes
    tdf_sdk_dll.tims_index_to_mz.restype = c_uint32

    # Get 1/k0 values from scan number
    tdf_sdk_dll.tims_scannum_to_oneoverk0.argtypes = convfunc_argtypes
    tdf_sdk_dll.tims_scannum_to_oneoverk0.restype = c_uint32

    # Convert 1/k0 to CCS
    tdf_sdk_dll.tims_oneoverk0_to_ccs_for_mz.argtypes = [c_double,
                                                         c_int32,
                                                         c_double]
    tdf_sdk_dll.tims_oneoverk0_to_ccs_for_mz.restype = c_double

    if TDF_SDK_VERSION == 'sdk22104':
        MSMS_SPECTRUM_FUNCTION = CFUNCTYPE(None,
                                           c_int64,
                                           c_uint32,
                                           POINTER(c_double),
                                           POINTER(c_float),
                                           POINTER(c_void_p))
        MSMS_PROFILE_SPECTRUM_FUNCTION = CFUNCTYPE(None,
                                                   c_int64,
                                                   c_uint32,
                                                   POINTER(c_int32),
                                                   POINTER(c_void_p))
        tdf_sdk_dll.tims_open_v2.argtypes = [c_char_p,
                                             c_uint32,
                                             c_uint32]
        tdf_sdk_dll.tims_open_v2.restype = c_uint64
        tdf_sdk_dll.tims_read_pasef_msms_v2.argtypes = [c_uint64,
                                                        POINTER(c_int64),
                                                        c_uint32,
                                                        MSMS_SPECTRUM_FUNCTION,
                                                        POINTER(c_void_p)]
        tdf_sdk_dll.tims_read_pasef_msms_v2.restype = c_uint32
        tdf_sdk_dll.tims_read_pasef_msms_for_frame_v2.argtypes = [c_uint64,
                                                                  c_int64,
                                                                  MSMS_SPECTRUM_FUNCTION,
                                                                  POINTER(c_void_p)]
        tdf_sdk_dll.tims_read_pasef_msms_for_frame_v2.restype = c_uint32
        tdf_sdk_dll.tims_read_pasef_profile_msms_v2.argtypes = [c_uint64,
                                                                POINTER(c_int64),
                                                                c_uint32,
                                                                MSMS_PROFILE_SPECTRUM_FUNCTION,
                                                                POINTER(c_void_p)]
        tdf_sdk_dll.tims_read_pasef_profile_msms_v2.restype = c_uint32
        tdf_sdk_dll.tims_read_pasef_profile_msms_for_frame_v2.argtypes = [c_uint64,
                                                                          c_int64,
                                                                          MSMS_PROFILE_SPECTRUM_FUNCTION,
                                                                          POINTER(c_void_p)]
        tdf_sdk_dll.tims_read_pasef_profile_msms_for_frame_v2.restype = c_uint32
        tdf_sdk_dll.tims_extract_centroided_spectrum_for_frame_ext.argtypes = [c_uint64,
                                                                               c_int64,
                                                                               c_uint32,
                                                                               c_uint32,
                                                                               c_double,
                                                                               MSMS_SPECTRUM_FUNCTOR,
                                                                               c_void_p]
        tdf_sdk_dll.tims_extract_centroided_spectrum_for_frame_ext.restype = c_uint32
        tdf_sdk_dll.tims_extract_centroided_spectrum_for_frame_v2.argtypes = [c_uint64,
                                                                              c_int64,
                                                                              c_uint32,
                                                                              c_uint32,
                                                                              MSMS_SPECTRUM_FUNCTOR,
                                                                              c_void_p]
        tdf_sdk_dll.tims_extract_centroided_spectrum_for_frame_v2.restype = c_uint32

    return tdf_sdk_dll


# from tsfdata.py
def throw_last_tsf_error(bruker_dll):
    """
    Error handling for Bruker raw data originating from TSF files. Modified from tsfdata.py example API.

    :param bruker_dll: Handle for TDF-SDK library.
    :type bruker_dll: CDLL object
    """
    err_len = bruker_dll.tsf_get_last_error_string(None, 0)
    buf = create_string_buffer(err_len)
    bruker_dll.tsf_get_last_error_string(buf, err_len)
    raise RuntimeError(buf.value)


# from baf2sql.py
# Throw last baf2sql error string as exception.
def throw_last_baf2sql_error(baf2sql_dll):
    """
    Error handling for Bruker raw data originating from BAF files. Modified from baf2sql.py example API.

    :param baf2sql_dll: Handle for Baf2sql library.
    :type baf2sql_dll: CDLL object
    """
    err_len = baf2sql_dll.baf2sql_get_last_error_string(None, 0)
    buf = create_string_buffer(err_len)
    baf2sql_dll.baf2sql_get_last_error_string(buf, err_len)
    raise RuntimeError(buf.value)


# from tsfdata.py
def decode_array_of_strings(blob):
    """
    Decode method provided by tsfdata.py example API to properly encode strings for TDF-SDK.

    :param blob: String to decode.
    :type blob: str
    :return: Decoded string in utf-8 format.
    :rtype: str
    """
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
    """
    Convert 1/K0 values to CCS values based on a feature's m/z value and charge.

    :param ook0: 1/K0 value of the feature.
    :type ook0: float
    :param charge: Charge of the feature.
    :type charge: int
    :param mz: m/z value of the feature.
    :type mz: float
    :return: CCS value calculated from the provided feature.
    :rtype: float
    """
    bruker_dll = init_tdf_sdk_dll()
    return bruker_dll.tims_oneoverk0_to_ccs_for_mz(ook0, charge, mz)
