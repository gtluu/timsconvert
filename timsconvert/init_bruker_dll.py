import ctypes
from timsconvert.constants import *


# modified from alphatims
def init_bruker_dll(bruker_dll_file_name: str=BRUKER_DLL_FILE_NAME):
    bruker_dll = ctypes.cdll.LoadLibrary(os.path.realpath(bruker_dll_file_name))

    # Functions for .tsf files
    # .tsf Open
    bruker_dll.tsf_open.argtypes = [ctypes.c_char_p, ctypes.c_uint32]
    bruker_dll.tsf_open.restype = ctypes.c_uint64

    # .tsf Close
    bruker_dll.tsf_close.argtypes = [ctypes.c_uint64]
    bruker_dll.tsf_close.restype = None

    # Read in profile or line spectra
    bruker_dll.tsf_read_line_spectrum.argtypes = [ctypes.c_uint64,
                                                  ctypes.c_int64,
                                                  ctypes.POINTER(ctypes.c_double),
                                                  ctypes.POINTER(ctypes.c_float),
                                                  ctypes.c_uint32]
    bruker_dll.tsf_read_line_spectrum.restype = ctypes.c_uint32
    bruker_dll.tsf_read_profile_spectrum.argtypes = [ctypes.c_uint64,
                                                     ctypes.c_int64,
                                                     ctypes.POINTER(ctypes.c_uint32),
                                                     ctypes.c_uint32]
    bruker_dll.tsf_read_profile_spectrum.restype = ctypes.c_uint32

    # Get m/z values from indices.
    bruker_dll.tsf_index_to_mz.argtypes = [ctypes.c_uint64,
                                           ctypes.c_int64,
                                           ctypes.POINTER(ctypes.c_double),
                                           ctypes.POINTER(ctypes.c_double),
                                           ctypes.c_uint32]
    bruker_dll.tsf_index_to_mz.restype = ctypes.c_uint32

    # Functions for .tdf files
    # .tdf Open
    bruker_dll.tims_open.argtypes = [ctypes.c_char_p, ctypes.c_uint32]
    bruker_dll.tims_open.restype = ctypes.c_uint64

    # .tdf Close
    bruker_dll.tims_close.argtypes = [ctypes.c_uint64]
    bruker_dll.tims_close.restype = None

    # Read scans from .tdf
    bruker_dll.tims_read_scans_v2.argtypes = [ctypes.c_uint64,
                                              ctypes.c_int64,
                                              ctypes.c_uint32,
                                              ctypes.c_uint32,
                                              ctypes.c_void_p,
                                              ctypes.c_uint32]
    bruker_dll.tims_read_scans_v2.restype = ctypes.c_uint32

    # Read PASEF MSMS
    MSMS_SPECTRUM_FUNCTOR = ctypes.CFUNCTYPE(None,
                                             ctypes.c_int64,
                                             ctypes.c_uint32,
                                             ctypes.POINTER(ctypes.c_double),
                                             ctypes.POINTER(ctypes.c_float))
    bruker_dll.tims_read_pasef_msms.argtypes = [ctypes.c_uint64,
                                                ctypes.POINTER(ctypes.c_int64),
                                                ctypes.c_uint32,
                                                MSMS_SPECTRUM_FUNCTOR]
    bruker_dll.tims_read_pasef_msms.restype = ctypes.c_uint32
    bruker_dll.tims_read_pasef_msms_for_frame.argtypes = [ctypes.c_uint64,
                                                          ctypes.c_int64,
                                                          MSMS_SPECTRUM_FUNCTOR]
    bruker_dll.tims_read_pasef_msms_for_frame.restype = ctypes.c_uint32
    MSMS_PROFILE_SPECTRUM_FUNCTOR = ctypes.CFUNCTYPE(None,
                                                     ctypes.c_int64,
                                                     ctypes.c_uint32,
                                                     ctypes.POINTER(ctypes.c_int32))
    bruker_dll.tims_read_pasef_profile_msms.argtypes = [ctypes.c_uint64,
                                                        ctypes.POINTER(ctypes.c_int64),
                                                        ctypes.c_uint32,
                                                        MSMS_PROFILE_SPECTRUM_FUNCTOR]
    bruker_dll.tims_read_pasef_profile_msms.restype = ctypes.c_uint32
    bruker_dll.tims_read_pasef_profile_msms_for_frame.argtypes = [ctypes.c_uint64,
                                                                  ctypes.c_int64,
                                                                  MSMS_PROFILE_SPECTRUM_FUNCTOR]
    bruker_dll.tims_read_pasef_profile_msms_for_frame.restype = ctypes.c_uint32

    # Extract spectra from frames
    bruker_dll.tims_extract_centroided_spectrum_for_frame.argtypes = [ctypes.c_uint64,
                                                                      ctypes.c_int64,
                                                                      ctypes.c_uint32,
                                                                      ctypes.c_uint32,
                                                                      MSMS_SPECTRUM_FUNCTOR,
                                                                      ctypes.c_void_p]
    bruker_dll.tims_extract_centroided_spectrum_for_frame.restype = ctypes.c_uint32
    bruker_dll.tims_extract_profile_for_frame.argtypes = [ctypes.c_uint64,
                                                          ctypes.c_int64,
                                                          ctypes.c_uint32,
                                                          ctypes.c_uint32,
                                                          MSMS_PROFILE_SPECTRUM_FUNCTOR,
                                                          ctypes.c_void_p]
    bruker_dll.tims_extract_profile_for_frame.restype = ctypes.c_uint32

    # Get m/z values from indices
    convfunc_argtypes = [ctypes.c_uint64,
                         ctypes.c_int64,
                         ctypes.POINTER(ctypes.c_double),
                         ctypes.POINTER(ctypes.c_double),
                         ctypes.c_uint32]
    bruker_dll.tims_index_to_mz.argtypes = convfunc_argtypes
    bruker_dll.tims_index_to_mz.restype = ctypes.c_uint32

    # Get 1/k0 values from scan number
    bruker_dll.tims_scannum_to_oneoverk0.argtypes = convfunc_argtypes
    bruker_dll.tims_scannum_to_oneoverk0.restype = ctypes.c_uint32

    # Convert 1/k0 to CCS
    bruker_dll.tims_oneoverk0_to_ccs_for_mz.argtypes = [ctypes.c_double,
                                                        ctypes.c_int32,
                                                        ctypes.c_double]
    bruker_dll.tims_oneoverk0_to_ccs_for_mz.restype = ctypes.c_double

    return bruker_dll


# from tsfdata.py
def throw_last_tsf_error(bruker_dll):
    err_len = bruker_dll.tsf_get_last_error_string(None, 0)
    buf = ctypes.create_string_buffer(err_len)
    bruker_dll.tsf_get_last_error_string(buf, err_len)
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
    bruker_dll = init_bruker_dll()
    return bruker_dll.tims_oneoverk0_to_ccs_for_mz(ook0, charge, mz)


if __name__ == '__main__':
    logger = logging.getLogger(__name__)
