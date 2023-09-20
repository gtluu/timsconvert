import sqlite3
import numpy as np
import pandas as pd
from timsconvert.parse import get_encoding_dtype, get_centroid_status


MSMS_SPECTRUM_FUNCTOR = CFUNCTYPE(None,
                                  c_int64,
                                  c_uint32,
                                  POINTER(c_double),
                                  POINTER(c_float))

MSMS_PROFILE_SPECTRUM_FUNCTOR = CFUNCTYPE(None,
                                          c_int64,
                                          c_uint32,
                                          POINTER(c_int32))

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


# modified from baf2sql.py
class BafData(object):
    """
    Class containing metadata from BAF files and methods from Baf2sql library to work with BAF format data.

    :param bruker_d_folder_name: Path to a Bruker .d file containing analysis.baf.
    :type bruker_d_folder_name: str
    :param baf2sql_dll: Library initialized by timsconvert.init_bruker_dll.init_baf2sql_dll().
    :type baf2sql_dll: ctypes.CDLL
    :param raw_calibration: Whether to use recalibrated data (False) or not (True), defaults to False.
    :type raw_calibration: bool
    :param all_variables: Whether to load all variables from analysis.sqlite database, defaults to False.
    :type all_variables: bool
    """
    def __init__(self, bruker_d_folder_name: str, baf2sql_dll, raw_calibration=False, all_variables=False):
        """
        Constructor Method
        """
        self.dll = baf2sql_dll
        self.handle = self.dll.baf2sql_array_open_storage(1 if raw_calibration else 0,
                                                          os.path.join(bruker_d_folder_name,
                                                                       'analysis.baf').encode('utf-8'))

        if self.handle == 0:
            throw_last_baf2sql_error(self.dll)

        self.all_variables = all_variables

        self.meta_data = None
        self.acquisitionkeys = None
        self.frames = None
        self.ms1_frames = None
        self.steps = None
        self.variables = None
        self.source_file = bruker_d_folder_name

        self.get_sqlite_cache_filename()
        self.conn = sqlite3.connect(os.path.join(bruker_d_folder_name, 'analysis.sqlite'))

        self.get_properties()
        self.get_acquisitionkeys_table()

        self.get_spectra_table()
        self.get_steps_table()
        self.get_variables_table()
        self.subset_ms1_frames()

        self.close_sql_connection()

    # from Bruker baf2sql.py
    def __del__(self):
        """
        Close connection to raw data handle.
        """
        self.dll.baf2sql_array_close_storage(self.handle)

    # modified from baf2sql.py
    def get_sqlite_cache_filename(self):
        """
        Find out the filename of the SQLite cache corresponding to the specified BAF file. The SQLite cache will be
        created with the filename "analysis.sqlite" if it does not exist yet.

        :return: SQLite filename.
        :rtype: str
        """
        u8path = os.path.join(self.source_file, 'analysis.baf').encode('utf-8')

        baf_len = self.dll.baf2sql_get_sqlite_cache_filename_v2(None, 0, u8path, self.all_variables)
        if baf_len == 0:
            throw_last_baf2sql_error(self.dll)

        buf = create_string_buffer(baf_len)
        self.dll.baf2sql_get_sqlite_cache_filename_v2(buf, baf_len, u8path, self.all_variables)
        return buf.value

    def get_array_num_elements(self, identity):
        """
        Returns the number of elements in the array with the specified ID.

        :param identity: ID of the desired array.
        :type identity: str | int
        :return: Number of elements in the array of the specified ID.
        :rtype: int
        """
        n = c_uint64(0)
        if not self.dll.baf2sql_array_get_num_elements(self.handle, identity, n):
            throw_last_baf2sql_error(self.dll)
        return n.value

    def read_array_double(self, identity):
        """
        Returns the requested array as a numpy.array of doubles.

        :param identity: ID of the desired array.
        :type identity: str | int
        :return: Array from the specified ID.
        :rtype: numpy.array
        """
        buf = np.empty(shape=self.get_array_num_elements(identity), dtype=np.float64)
        if not self.dll.baf2sql_array_read_double(self.handle,
                                                  identity,
                                                  buf.ctypes.data_as(POINTER(c_double))):
            throw_last_baf2sql_error(self.dll)
        return buf

    def get_properties(self):
        """
        Get the Properties table from analysis.sqlite as a dictionary stored in timsconvert.classes.BafData.meta_data.
        """
        properties_query = 'SELECT * FROM Properties'
        properties_df = pd.read_sql_query(properties_query, self.conn)
        properties_dict = {}
        for index, row in properties_df.iterrows():
            properties_dict[row['Key']] = row['Value']
        self.meta_data = properties_dict

    def get_acquisitionkeys_table(self):
        """
        Get the AcquisitionKeys table from analysis.sqlite as a pandas.DataFrame stored in
        timsconvert.classes.BafData.acquisitionkeys.
        """
        acquisitionkeys_query = 'SELECT * FROM AcquisitionKeys'
        self.acquisitionkeys = pd.read_sql_query(acquisitionkeys_query, self.conn)

    def get_spectra_table(self):
        """
        Get the Spectra table from analysis.sqlite as a pandas.DataFrame stored in
        timsconvert.classes.BafData.frames.
        """
        spectra_query = 'SELECT * FROM Spectra'
        self.frames = pd.read_sql_query(spectra_query, self.conn)

    def get_steps_table(self):
        """
        Get the Steps table from analysis.sqlite as a pandas.DataFrame stored in
        timsconvert.classes.BafData.steps. Data may be redundant with that found in the Variables table of
        analysis.sqlite.
        """
        steps_query = 'SELECT * FROM Steps'
        self.steps = pd.read_sql_query(steps_query, self.conn)

    def get_variables_table(self):
        """
        Get the Variables table from analysis.sqlite as a pandas.DataFrame stored in
        timsconvert.classes.BafData.variables. Data may be redundant with that found in the Steps table of
        analysis.sqlite.
        """
        variables_query = 'SELECT * FROM Variables'
        self.variables = pd.read_sql_query(variables_query, self.conn)

    def subset_ms1_frames(self):
        """
        Subset timsconvert.classes.BafData.frames table (Spectra table from analysis.sqlite) to only include MS1 rows.
        Used during the subsetting process during data parsing/writing for memory efficiency. The subsetted
        pandas.DataFrame is stored in timsconvert.classes.BafData.ms1_frames.
        """
        self.ms1_frames = self.frames[self.frames['AcquisitionKey'] == 1]['Id'].values.tolist()

    def close_sql_connection(self):
        """
        Close the connection to analysis.sqlite.
        """
        self.conn.close()


# modified from tsfdata.py
class TsfData(object):
    """
    Class containing metadata from TSF files and methods from TDF-SDK library to work with TSF format data.

    :param bruker_d_folder_name: Path to a Bruker .d file containing analysis.tsf.
    :type bruker_d_folder_name: str
    :param tdf_sdk_dll: Library initialized by timsconvert.init_bruker_dll.init_tdf_sdk_dll().
    :type tdf_sdk_dll: ctypes.CDLL
    :param use_recalibrated_state: Whether to use recalibrated data (True) or not (False), defaults to True.
    :type use_recalibrated_state: bool
    """
    def __init__(self, bruker_d_folder_name: str, tdf_sdk_dll, use_recalibrated_state=True):
        """
        Constructor Method
        """
        self.dll = tdf_sdk_dll
        self.handle = self.dll.tsf_open(bruker_d_folder_name.encode('utf-8'), 1 if use_recalibrated_state else 0)
        if self.handle == 0:
            throw_last_tsf_error(self.dll)

        self.conn = sqlite3.connect(os.path.join(bruker_d_folder_name, 'analysis.tsf'))

        # arbitrary size, from Bruker tsfdata.py
        self.line_buffer_size = 1024
        self.profile_buffer_size = 1024

        self.meta_data = None
        self.frames = None
        self.ms1_frames = None
        self.maldiframeinfo = None
        self.framemsmsinfo = None
        self.source_file = bruker_d_folder_name

        self.get_global_metadata()
        self.get_frames_table()

        if 'MaldiApplicationType' in self.meta_data.keys():
            self.get_maldiframeinfo_table()
            self.get_framemsmsinfo_table()
        else:
            self.get_framemsmsinfo_table()
            self.subset_ms1_frames()

        self.close_sql_connection()

    # from Bruker tsfdata.py
    def __del__(self):
        """
        Close connection to raw data handle.
        """
        if hasattr(self, 'handle'):
            self.dll.tsf_close(self.handle)

    # from Bruker tsfdata.py
    def __call_conversion_func(self, frame_id, input_data, func):
        """
        Convenience method to call conversion functions from TDF-SDK library.

        :param frame_id: ID of the frame containing the raw data of interest.
        :type frame_id: int
        :param input_data: Array of values to be converted.
        :type input_data: numpy.array
        :param func: Function from TDF-SDK to be applied to the input_data.
        :type func: ctypes._FuncPtr
        :return: Output array containing converted values.
        :rtype: numpy.array
        """
        if type(input_data) is np.ndarray and input_data.dtype == np.float64:
            in_array = input_data
        else:
            in_array = np.array(input_data, dtype=np.float64)

        cnt = len(in_array)
        out = np.empty(shape=cnt, dtype=np.float64)
        success = func(self.handle,
                       frame_id,
                       in_array.ctypes.data_as(POINTER(c_double)),
                       out.ctypes.data_as(POINTER(c_double)),
                       cnt)

        if success == 0:
            throw_last_tsf_error(self.dll)

        return out

    # from Bruker tsfdata.py
    def index_to_mz(self, frame_id, indices):
        """
        Convert array of indices for a given frame to m/z values.

        :param frame_id: ID of the frame containing the raw data of interest.
        :type frame_id: int
        :param indices: Array of indices to be converted.
        :type indices: numpy.array
        :return: Array of m/z values.
        :rtype: numpy.array
        """
        return self.__call_conversion_func(frame_id, indices, self.dll.tsf_index_to_mz)

    # modified from Bruker tsfdata.py
    def read_line_spectrum(self, frame_id):
        """
        Read in centroid spectrum for a given frame.

        :param frame_id: ID of the frame containing the raw data of interest.
        :type frame_id: int
        :return: Tuple containing an array of indices for the mass dimension and array of detector acounts.
        :rtype: tuple[numpy.array]
        """
        while True:
            cnt = int(self.profile_buffer_size)
            index_buf = np.empty(shape=cnt, dtype=np.float64)
            intensity_buf = np.empty(shape=cnt, dtype=np.float32)

            required_len = self.dll.tsf_read_line_spectrum_v2(self.handle,
                                                              frame_id,
                                                              index_buf.ctypes.data_as(POINTER(c_double)),
                                                              intensity_buf.ctypes.data_as(POINTER(c_float)),
                                                              self.profile_buffer_size)

            if required_len > self.profile_buffer_size:
                if required_len > 16777216:
                    raise RuntimeError('Maximum expected frame size exceeded.')
                self.profile_buffer_size = required_len
            else:
                break

        return index_buf[0:required_len], intensity_buf[0:required_len]

    # modified from Bruker tsfdata.py
    def read_profile_spectrum(self, frame_id):
        """
        Read in profile spectrum for a given frame.

        :param frame_id: ID of the frame containing the raw data of interest.
        :type frame_id: int
        :return: Tuple containing an array of indices for the mass dimension that is inferred from the length of the
            intensity array and array of detector acounts.
        :rtype: tuple[numpy.array]
        """
        while True:
            cnt = int(self.profile_buffer_size)
            intensity_buf = np.empty(shape=cnt, dtype=np.uint32)

            required_len = self.dll.tsf_read_profile_spectrum_v2(self.handle,
                                                                 frame_id,
                                                                 intensity_buf.ctypes.data_as(POINTER(c_uint32)),
                                                                 self.profile_buffer_size)

            if required_len > self.profile_buffer_size:
                if required_len > 16777216:
                    raise RuntimeError('Maximum expected frame size exceeded.')
                self.profile_buffer_size = required_len
            else:
                break

        index_buf = np.arange(0, intensity_buf.size, dtype=np.float64)

        return index_buf[0:required_len], intensity_buf[0:required_len]

    def get_global_metadata(self):
        """
        Get the GlobalMetadata table from analysis.tsf as a dictionary stored in
        timsconvert.classes.TsfData.meta_data.
        """
        metadata_query = 'SELECT * FROM GlobalMetadata'
        metadata_df = pd.read_sql_query(metadata_query, self.conn)
        metadata_dict = {}
        for index, row in metadata_df.iterrows():
            metadata_dict[row['Key']] = row['Value']
        self.meta_data = metadata_dict

    def get_frames_table(self):
        """
        Get the Frames table from analysis.tsf as a pandas.DataFrame stored in
        timsconvert.classes.TsfData.frames.
        """
        frames_query = 'SELECT * FROM Frames'
        self.frames = pd.read_sql_query(frames_query, self.conn)

    def get_maldiframeinfo_table(self):
        """
        Get the MaldiFrameInfo table from analysis.tsf as a pandas.DataFrame stored in
        timsconvert.classes.TsfData.maldiframeinfo.
        """
        maldiframeinfo_query = 'SELECT * FROM MaldiFrameInfo'
        self.maldiframeinfo = pd.read_sql_query(maldiframeinfo_query, self.conn)

    # Get FrameMsMsInfo table from analysis.tsf SQL database.
    def get_framemsmsinfo_table(self):
        """
        Get the FrameMsMsInfo table from analysis.tsf as a pandas.DataFrame stored in
        timsconvert.classes.TsfData.framemsmsinfo.
        """
        framemsmsinfo_query = 'SELECT * FROM FrameMsMsInfo'
        self.framemsmsinfo = pd.read_sql_query(framemsmsinfo_query, self.conn)

    # Subset Frames table to only include MS1 rows. Used for chunking during data parsing/writing.
    def subset_ms1_frames(self):
        """
        Subset timsconvert.classes.TsfData.frames table (Frames table from analysis.tsf) to only include MS1 rows.
        Used during the subsetting process during data parsing/writing for memory efficiency. The subsetted
        pandas.DataFrame is stored in timsconvert.classes.TsfData.ms1_frames.
        """
        self.ms1_frames = self.frames[self.frames['MsMsType'] == 0]['Id'].values.tolist()

    def close_sql_connection(self):
        """
        Close the connection to analysis.tsf.
        """
        self.conn.close()


class TdfData(object):
    """
    Class containing metadata from TDF files and methods from TDF-SDK library to work with TDF format data.

    :param bruker_d_folder_name: Path to a Bruker .d file containing analysis.tdf.
    :type bruker_d_folder_name: str
    :param tdf_sdk_dll: Library initialized by timsconvert.init_bruker_dll.init_tdf_sdk_dll().
    :type tdf_sdk_dll: ctypes.CDLL
    :param use_recalibrated_state: Whether to use recalibrated data (True) or not (False), defaults to True.
    :type use_recalibrated_state: bool
    """
    def __init__(self, bruker_d_folder_name: str, tdf_sdk_dll, use_recalibrated_state=True):
        """
        Constructor Method
        """
        self.dll = tdf_sdk_dll
        self.handle = self.dll.tims_open(bruker_d_folder_name.encode('utf-8'),
                                         1 if use_recalibrated_state else 0)

        if self.handle == 0:
            throw_last_tsf_error(self.dll)

        self.conn = sqlite3.connect(os.path.join(bruker_d_folder_name, 'analysis.tdf'))

        # arbitrary size, from Bruker timsdata.py
        self.initial_frame_buffer_size = 128

        self.meta_data = None
        self.frames = None
        self.ms1_frames = None
        self.maldiframeinfo = None
        self.pasefframemsmsinfo = None
        self.framemsmsinfo = None
        self.precursors = None
        self.diaframemsmsinfo = None
        self.diaframemsmswindowgroups = None
        self.diaframemsmswindows = None
        self.prmframemsmsinfo = None
        self.prmtargets = None
        self.source_file = bruker_d_folder_name

        self.get_global_metadata()
        self.get_frames_table()

        if 'MaldiApplicationType' in self.meta_data.keys():
            self.get_maldiframeinfo_table()
            self.get_framemsmsinfo_table()
        else:
            # Only parse these tables if data acquired in ddaPASEF mode (MsMsType == 8).
            if 8 in list(set(self.frames['MsMsType'].values.tolist())):
                self.get_pasefframemsmsinfo_table()
                self.get_precursors_table()
            # Only parse these tables if data acquired in diaPASEF mode (MsMsType == 9).
            if 9 in list(set(self.frames['MsMsType'].values.tolist())):
                self.get_diaframemsmsinfo_table()
                self.get_diaframemsmswindows_table()
            # Only parse these tables if data acquired in bbCID mode (ScanMode == 4) or MRM mode (ScanMode == 2).
            if 4 in list(set(self.frames['ScanMode'].values.tolist())) \
                    or 2 in list(set(self.frames['ScanMode'].values.tolist())):
                self.get_framemsmsinfo_table()
            # Only parse these tables if data acquired in prm-PASEF mode (ScanMode == 10).
            if 10 in list(set(self.frames['ScanMode'].values.tolist())):
                self.get_prmframemsmsinfo_table()
                self.get_prmtargets_table()
            self.subset_ms1_frames()

        self.close_sql_connection()

    def __del__(self):
        """
        Close connection to raw data handle.
        """
        if hasattr(self, 'handle'):
            self.dll.tims_close(self.handle)

    def __call_conversion_func(self, frame_id, input_data, func):
        """
        Convenience method to call conversion functions from TDF-SDK library.

        :param frame_id: ID of the frame containing the raw data of interest.
        :type frame_id: int
        :param input_data: Array of values to be converted.
        :type input_data: numpy.array
        :param func: Function from TDF-SDK to be applied to the input_data.
        :type func: ctypes._FuncPtr
        :return: Output array containing converted values.
        :rtype: numpy.array
        """
        if type(input_data) is np.ndarray and input_data.dtype == np.float64:
            in_array = input_data
        else:
            in_array = np.array(input_data, dtype=np.float64)

        cnt = len(in_array)
        out = np.empty(shape=cnt, dtype=np.float64)
        success = func(self.handle,
                       frame_id,
                       in_array.ctypes.data_as(POINTER(c_double)),
                       out.ctypes.data_as(POINTER(c_double)),
                       cnt)

        if success == 0:
            throw_last_tsf_error(self.dll)

        return out

    # following conversion functions from Bruker timsdata.py
    def index_to_mz(self, frame_id, indices):
        """
        Convert array of indices for a given frame to m/z values.

        :param frame_id: ID of the frame containing the raw data of interest.
        :type frame_id: int
        :param indices: Array of indices to be converted.
        :type indices: numpy.array
        :return: Array of m/z values.
        :rtype: numpy.array
        """
        return self.__call_conversion_func(frame_id, indices, self.dll.tims_index_to_mz)

    def scan_num_to_oneoverk0(self, frame_id, scan_nums):
        """
        Convert array of scan numbers for a given frame to 1/K0 values.

        :param frame_id: ID of the frame containing the raw data of interest.
        :type frame_id: int
        :param scan_nums: Array of scan numbers to be converted.
        :type scan_nums: numpy.array.
        :return: Array of 1/K0 values.
        :rtype: numpy.array
        """
        return self.__call_conversion_func(frame_id, scan_nums, self.dll.tims_scannum_to_oneoverk0)

    # modified from Bruker timsdata.py
    def read_scans(self, frame_id, scan_begin, scan_end):
        """
        Read centroid spectra for a given frame (i.e. retention time) and scan (i.e. ion mobility) or range of scans.
        Results slightly differ from methods made for specifically reading centroid spectra. Therefore, the "mode" for
        this method is "raw", which can be interchangeable with "centroid".

        :param frame_id: ID of the frame containing the raw data of interest.
        :type frame_id: int
        :param scan_begin: Beginning scan number (corresponding to 1/K0 value) within frame.
        :type scan_begin: int
        :param scan_end: Ending scan number (corresponding to 1/K0 value) within frame (non-inclusive).
        :type scan_end: int
        :return: List of tuples where each tuple contains an array of mass indices and array of detector counts.
        :rtype: list[tuple[numpy.array]]
        """
        while True:
            cnt = int(self.initial_frame_buffer_size)
            buf = np.empty(shape=cnt, dtype=np.uint32)
            length = 4 * cnt

            required_len = self.dll.tims_read_scans_v2(self.handle,
                                                       frame_id,
                                                       scan_begin,
                                                       scan_end,
                                                       buf.ctypes.data_as(POINTER(c_uint32)),
                                                       length)

            if required_len > length:
                if required_len > 16777216:
                    raise RuntimeError('Maximum expected frame size exceeded.')
                self.initial_frame_buffer_size = required_len / 4 + 1
            else:
                break

        result = []
        d = scan_end - scan_begin
        for i in range(scan_begin, scan_end):
            npeaks = buf[i-scan_begin]
            indices = buf[d:d+npeaks]
            d += npeaks
            intensities = buf[d:d+npeaks]
            d += npeaks
            result.append((indices, intensities))

        return result

    def read_pasef_centroid_msms(self, precursor_list):
        """
        Read in centroid MS/MS spectra from PASEF MS/MS data for precursor(s).

        :param precursor_list: Array or list of precursor IDs to obtain spectra for.
        :type precursor_list: numpy.array | list
        :return: Dictionary in which keys correspond to the precursor ID and values correspond to a tuple containing
            an array of m/z values and an array of detector counts.
        :rtype: dict
        """
        precursors_for_dll = np.array(precursor_list, dtype=np.int64)

        result = {}

        @MSMS_SPECTRUM_FUNCTOR
        def callback_for_dll(precursor_id, num_peaks, mz_values, area_values):
            result[precursor_id] = (mz_values[0:num_peaks], area_values[0:num_peaks])

        # TODO: update this function to v2
        rc = self.dll.tims_read_pasef_msms(self.handle,
                                           precursors_for_dll.ctypes.data_as(POINTER(c_int64)),
                                           len(precursor_list),
                                           callback_for_dll)

        return result

    def read_pasef_profile_msms(self, precursor_list):
        """
        Read in quasi-profile MS/MS spectra from PASEF MS/MS data for precursor(s).

        :param precursor_list: Array or list of precursor IDs to obtain spectra for.
        :type precursor_list: numpy.array | list
        :return: Dictionary in which keys correspond to the precursor ID and values correspond to an array of detector
            counts.
        :rtype: dict
        """
        precursors_for_dll = np.array(precursor_list, dtype=np.int64)

        result = {}

        @MSMS_PROFILE_SPECTRUM_FUNCTOR
        def callback_for_dll(precursor_id, num_points, intensity_values):
            result[precursor_id] = intensity_values[0:num_points]

        # TODO: update this function to v2
        rc = self.dll.tims_read_pasef_profile_msms(self.handle,
                                                   precursors_for_dll.ctypes.data_as(POINTER(c_int64)),
                                                   len(precursor_list),
                                                   callback_for_dll)

        return result

    def read_pasef_centroid_msms_for_frame(self, frame_id):
        """
        Read in centroid MS/MS spectra from PASEF MS/MS data for a given frame.

        :param frame_id: ID of the frame containing the raw data of interest.
        :type frame_id: int
        :return: Dictionary in which keys correspond to the precursor ID and values correspond to a tuple containing
            an array of m/z values and an array of detector counts.
        :rtype: dict
        """
        result = {}

        @MSMS_SPECTRUM_FUNCTOR
        def callback_for_dll(precursor_id, num_peaks, mz_values, area_values):
            result[precursor_id] = (mz_values[0:num_peaks], area_values[0:num_peaks])

        # TODO: update this function to v2
        rc = self.dll.tims_read_pasef_msms_for_frame(self.handle, frame_id, callback_for_dll)

        return result

    def read_pasef_profile_msms_for_frame(self, frame_id):
        """
        Read in quasi-profile MS/MS spectra from PASEF MS/MS data for a given frame.

        :param frame_id: ID of the frame containing the raw data of interest.
        :type frame_id: int
        :return: Dictionary in which keys correspond to the precursor ID and values correspond to a tuple containing
            an array of m/z values and an array of detector counts.
        :rtype: dict
        """
        result = {}

        @MSMS_PROFILE_SPECTRUM_FUNCTOR
        def callback_for_dll(precursor_id, num_points, intensity_values):
            result[precursor_id] = intensity_values[0:num_points]

        # TODO: update this function to v2
        rc = self.dll.tims_read_pasef_profile_msms_for_frame(self.handle, frame_id, callback_for_dll)

        return result

    # Only define extract_centroided_spectrum_for_frame and extract_profile_spectrum_for_frame if using SDK 2.8.7.1 or
    # newer.
    if TDF_SDK_VERSION == 'sdk22104':
        def extract_centroided_spectrum_for_frame(self, frame_id, scan_begin, scan_end):
            """
            Read in centroid spectrum for a given frame.

            :param frame_id: ID of the frame containing the raw data of interest.
            :type frame_id: int
            :param scan_begin: Beginning scan number (corresponding to 1/K0 value) within frame.
            :type scan_begin: int
            :param scan_end: Ending scan number (corresponding to 1/K0 value) within frame (non-inclusive).
            :type scan_end: int
            :return: Tuple containing an array of m/z values and an array of detector counts.
            :rtype: tuple[numpy.array]
            """
            result = None

            @MSMS_SPECTRUM_FUNCTOR
            def callback_for_dll(precursor_id, num_peaks, mz_values, area_values):
                nonlocal result
                result = (mz_values[0:num_peaks], area_values[0:num_peaks])

            rc = self.dll.tims_extract_centroided_spectrum_for_frame_v2(self.handle,
                                                                        frame_id,
                                                                        scan_begin,
                                                                        scan_end,
                                                                        callback_for_dll,
                                                                        None)

            return result

        def extract_profile_spectrum_for_frame(self, frame_id, scan_begin, scan_end):
            """
            Read in quasi-profile spectrum for a given frame.

            :param frame_id: ID of the frame containing the raw data of interest.
            :type frame_id: int
            :param scan_begin: Beginning scan number (corresponding to 1/K0 value) within frame.
            :type scan_begin: int
            :param scan_end: Ending scan number (corresponding to 1/K0 value) within frame (non-inclusive).
            :type scan_end: int
            :return: Tuple containing an array of m/z values that is inferred from the length of the intensity array
                and array of detector acounts.
            :rtype: tuple[numpy.array]
            """
            result = None

            @MSMS_PROFILE_SPECTRUM_FUNCTOR
            def callback_for_dll(precursor_id, num_points, intensity_values):
                nonlocal result
                result = intensity_values[0:num_points]

            rc = self.dll.tims_extract_profile_for_frame(self.handle,
                                                         frame_id,
                                                         scan_begin,
                                                         scan_end,
                                                         callback_for_dll,
                                                         None)

            index_buf = np.arange(0, len(result), dtype=np.float64)

            return (index_buf, result)

    # In house code for getting spectrum for a frame.
    def extract_spectrum_for_frame_v2(self, frame_id, begin_scan, end_scan, encoding, tol=0.01):
        """
        Depracated, use timsconvert.classes.TdfData.extract_centroided_spectrum_for_frame().
        """
        list_of_scan_tuples = [i for i in self.read_scans(frame_id, begin_scan, end_scan)
                               if i[0].size != 0 and i[1].size != 0]
        if len(list_of_scan_tuples) == 0:
            return (np.empty(0, dtype=get_encoding_dtype(encoding)),
                    np.empty(0, dtype=get_encoding_dtype(encoding)))
        list_of_dfs = []
        for scan_tuple in list_of_scan_tuples:
            list_of_dfs.append(pd.DataFrame({'mz': self.index_to_mz(frame_id, scan_tuple[0]),
                                             'intensity': scan_tuple[1]}))
        frame_df = pd.concat(list_of_dfs).groupby(by='mz', as_index=False).sum().sort_values(by='mz')

        def get_mz_generator(mz_array, tol=tol):
            result = []
            prev_mz = mz_array[0]
            for i in mz_array:
                if i - prev_mz > tol:
                    yield result
                    result = []
                result.append(i)
                prev_mz = i
            yield result

        def get_indices_generator(mz_array, tol=tol):
            result = []
            prev_mz = mz_array[0]
            for i in mz_array:
                if i - prev_mz > tol:
                    yield result
                    result = []
                result.append(mz_array.index(i))
                prev_mz = i
            yield result

        new_mz_array = [np.mean(list_of_mz_values)
                        for list_of_mz_values in list(get_mz_generator(frame_df['mz'].values.tolist(), tol))]

        new_intensity_array = []
        for list_of_indices in list(get_indices_generator(frame_df['mz'].values.tolist(), tol)):
            tmp_list = []
            for index in list_of_indices:
                tmp_list.append(frame_df['intensity'].values.tolist()[index])
            new_intensity_array.append(sum(tmp_list))

        return (np.array(new_mz_array, dtype=get_encoding_dtype(encoding)),
                np.array(new_intensity_array, dtype=get_encoding_dtype(encoding)))

    def get_global_metadata(self):
        """
        Get the GlobalMetadata table from analysis.tdf as a dictionary stored in
        timsconvert.classes.TdfData.meta_data.
        """
        metadata_query = 'SELECT * FROM GlobalMetadata'
        metadata_df = pd.read_sql_query(metadata_query, self.conn)
        metadata_dict = {}
        for index, row in metadata_df.iterrows():
            metadata_dict[row['Key']] = row['Value']
        self.meta_data = metadata_dict

    def get_frames_table(self):
        """
        Get the Frames table from analysis.tdf as a pandas.DataFrame stored in
        timsconvert.classes.TdfData.frames.
        """
        frames_query = 'SELECT * FROM Frames'
        self.frames = pd.read_sql_query(frames_query, self.conn)

    def get_pasefframemsmsinfo_table(self):
        """
        Get the PasefFrameMsMsInfo table from analysis.tdf as a pandas.DataFrame stored in
        timsconvert.classes.TdfData.pasefframemsmsinfo.
        """
        pasefframemsmsinfo_query = 'SELECT * FROM PasefFrameMsMsInfo'
        self.pasefframemsmsinfo = pd.read_sql_query(pasefframemsmsinfo_query, self.conn)

    def get_maldiframeinfo_table(self):
        """
        Get the MaldiFramesInfo table from analysis.tdf as a pandas.DataFrame stored in
        timsconvert.classes.TdfData.maldiframeinfo.
        """
        maldiframeinfo_query = 'SELECT * FROM MaldiFrameInfo'
        self.maldiframeinfo = pd.read_sql_query(maldiframeinfo_query, self.conn)

    def get_framemsmsinfo_table(self):
        """
        Get the FrameMsMsInfo table from analysis.tdf as a pandas.DataFrame stored in
        timsconvert.classes.TdfData.framemsmsinfo.
        """
        framemsmsinfo_query = 'SELECT * FROM FrameMsMsInfo'
        self.framemsmsinfo = pd.read_sql_query(framemsmsinfo_query, self.conn)

    def get_precursors_table(self):
        """
        Get the Precursors table from analysis.tdf as a pandas.DataFrame stored in
        timsconvert.classes.TdfData.precursors.
        """
        precursors_query = 'SELECT * FROM Precursors'
        self.precursors = pd.read_sql_query(precursors_query, self.conn)
        # Add mobility values to precursor table
        # Get array of mobility values based on number of scans.
        max_num_scans = max(self.frames['NumScans']) + 1
        indices = np.arange(max_num_scans).astype(np.float64)
        mobility_values = np.empty_like(indices)
        self.dll.tims_scannum_to_oneoverk0(self.handle,
                                           1,  # mobility_estimation_from_frame
                                           indices.ctypes.data_as(POINTER(c_double)),
                                           mobility_values.ctypes.data_as(POINTER(c_double)),
                                           max_num_scans)
        # Assign mobility values to precursor table.
        precursor_mobility_values = mobility_values[self.precursors['ScanNumber'].astype(np.int64)]
        self.precursors['Mobility'] = precursor_mobility_values

    def get_diaframemsmsinfo_table(self):
        """
        Get the DiaFrameMsMsInfo table from analysis.tdf as a pandas.DataFrame stored in
        timsconvert.classes.TdfData.diaframemsmsinfo.
        """
        diaframemsmsinfo_query = 'SELECT * FROM DiaFrameMsMsInfo'
        self.diaframemsmsinfo = pd.read_sql_query(diaframemsmsinfo_query, self.conn)

    def get_diaframemsmswindows_table(self):
        """
        Get the DiaFrameMsMsWindows table from analysis.tdf as a pandas.DataFrame stored in
        timsconvert.classes.TdfData.diaframemsmswindows.
        """
        diaframemsmswindows_query = 'SELECT * FROM DiaFrameMsMsWindows'
        self.diaframemsmswindows = pd.read_sql_query(diaframemsmswindows_query, self.conn)

    def get_prmframemsmsinfo_table(self):
        """
        Get the PrmFrameMsMsInfo table from analysis.tdf as a pandas.DataFrame stored in
        timsconvert.classes.TdfData.prmframemsmsinfo.
        """
        prmframemsmsinfo_query = 'SELECT * FROM PrmFrameMsMsInfo'
        self.prmframemsmsinfo = pd.read_sql_query(prmframemsmsinfo_query, self.conn)

    def get_prmtargets_table(self):
        """
        Get the PrmTargets table from analysis.tdf as a pandas.DataFrame stored in
        timsconvert.classes.TdfData.prmtargets.
        """
        prmtargets_query = 'SELECT * FROM PrmTargets'
        self.prmtargets = pd.read_sql_query(prmtargets_query, self.conn)

    # Subset Frames table to only include MS1 rows. Used for chunking during data parsing/writing.
    def subset_ms1_frames(self):
        """
        Subset timsconvert.classes.TdfData.frames table (Frames table from analysis.tdf) to only include MS1 rows.
        Used during the subsetting process during data parsing/writing for memory efficiency. The subsetted
        pandas.DataFrame is stored in timsconvert.classes.TdfData.ms1_frames.
        """
        self.ms1_frames = self.frames[self.frames['MsMsType'] == 0]['Id'].values.tolist()
        if len(self.ms1_frames) > 0 and self.ms1_frames[0] != 1:
            self.ms1_frames.insert(0, 1)

    def close_sql_connection(self):
        """
        Close the connection to analysis.tdf.
        """
        self.conn.close()
