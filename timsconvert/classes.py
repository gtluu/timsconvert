import sqlite3
import numpy as np
import pandas as pd
from psims.mzml.components import ParameterContainer, NullMap
from timsconvert.init_bruker_dll import *


MSMS_SPECTRUM_FUNCTOR = ctypes.CFUNCTYPE(None,
                                         ctypes.c_int64,
                                         ctypes.c_uint32,
                                         ctypes.POINTER(ctypes.c_double),
                                         ctypes.POINTER(ctypes.c_float))

MSMS_PROFILE_SPECTRUM_FUNCTOR = ctypes.CFUNCTYPE(None,
                                                 ctypes.c_int64,
                                                 ctypes.c_uint32,
                                                 ctypes.POINTER(ctypes.c_int32))


# currently nonfunctional class for adding TIMS to instrument configuration
# may not be supported with current CV dictionary
class IMMS(ParameterContainer):
    def __init(self, order, params=None, context=NullMap, **kwargs):
        params = self.prepare_params(params, **kwargs)
        super(IMMS, self).__init__('ion mobility mass spectrometer',
                                   params,
                                   dict(order=order),
                                   context=context)
        try:
            self.order = int(order)
        except (ValueError, TypeError):
            self.order = order


# modified from baf2sql.py
class baf_data(object):
    def __init__(self, bruker_d_folder_name: str, baf2sql_dll, raw_calibration=False, all_variables=False):
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
        self.dll.baf2sql_array_close_storage(self.handle)

    # modified from baf2sql.py
    # Find out the file name of the SQLite cache corresponding to the specified BAF file.
    # Will be created if it doesn't exist yet.
    def get_sqlite_cache_filename(self):
        u8path = os.path.join(self.source_file, 'analysis.baf').encode('utf-8')

        baf_len = self.dll.baf2sql_get_sqlite_cache_filename_v2(None, 0, u8path, self.all_variables)
        if baf_len == 0:
            throw_last_baf2sql_error(self.dll)

        buf = ctypes.create_string_buffer(baf_len)
        self.dll.baf2sql_get_sqlite_cache_filename_v2(buf, baf_len, u8path, self.all_variables)
        return buf.value

    # Returns number of elements in array with specified ID.
    def get_array_num_elements(self, identity):
        n = ctypes.c_uint64(0)
        if not self.dll.baf2sql_array_get_num_elements(self.handle, identity, n):
            throw_last_baf2sql_error(self.dll)
        return n.value

    # Returns the requested array as a double np.array.
    def read_array_double(self, identity):
        buf = np.empty(shape=self.get_array_num_elements(identity), dtype=np.float64)
        if not self.dll.baf2sql_array_read_double(self.handle,
                                                  identity,
                                                  buf.ctypes.data_as(ctypes.POINTER(ctypes.c_double))):
            throw_last_baf2sql_error(self.dll)
        return buf

    # Gets properties table as a dictionary.
    def get_properties(self):
        properties_query = 'SELECT * FROM Properties'
        properties_df = pd.read_sql_query(properties_query, self.conn)
        properties_dict = {}
        for index, row in properties_df.iterrows():
            properties_dict[row['Key']] = row['Value']
        self.meta_data = properties_dict

    # Gets AcquisitionKeys table from analysis.sqlite SQL database.
    def get_acquisitionkeys_table(self):
        acquisitionkeys_query = 'SELECT * FROM AcquisitionKeys'
        self.acquisitionkeys = pd.read_sql_query(acquisitionkeys_query, self.conn)

    # Get Spectra table from analysis.sqlite SQL database.
    def get_spectra_table(self):
        spectra_query = 'SELECT * FROM Spectra'
        self.frames = pd.read_sql_query(spectra_query, self.conn)

    # Get Steps table from analysis.sqlite SQL database; contains MS/MS metadata.
    # May be redundant with variables table.
    def get_steps_table(self):
        steps_query = 'SELECT * FROM Steps'
        self.steps = pd.read_sql_query(steps_query, self.conn)

    def get_variables_table(self):
        variables_query = 'SELECT * FROM Variables'
        self.variables = pd.read_sql_query(variables_query, self.conn)

    # Subset Frames table to only include MS1 rows. Used for chunking during data parsing/writing.
    def subset_ms1_frames(self):
        self.ms1_frames = list(self.frames[self.frames['AcquisitionKey'] == 1]['Id'].values)

    def close_sql_connection(self):
        self.conn.close()


# modified from tsfdata.py
class tsf_data(object):
    def __init__(self, bruker_d_folder_name: str, tdf_sdk_dll, use_recalibrated_state=True):
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
        self.maldiframeinfo = None
        self.framemsmsinfo = None
        self.source_file = bruker_d_folder_name

        self.get_global_metadata()

        self.get_frames_table()
        self.get_maldiframeinfo_table()
        self.get_framemsmsinfo_table()

        self.close_sql_connection()

    # from Bruker tsfdata.py
    def __del__(self):
        if hasattr(self, 'handle'):
            self.dll.tsf_close(self.handle)

    # from Bruker tsfdata.py
    def __call_conversion_func(self, frame_id, input_data, func):
        if type(input_data) is np.ndarray and input_data.dtype == np.float64:
            in_array = input_data
        else:
            in_array = np.array(input_data, dtype=np.float64)

        cnt = len(in_array)
        out = np.empty(shape=cnt, dtype=np.float64)
        success = func(self.handle,
                       frame_id,
                       in_array.ctypes.data_as(ctypes.POINTER(ctypes.c_double)),
                       out.ctypes.data_as(ctypes.POINTER(ctypes.c_double)),
                       cnt)

        if success == 0:
            throw_last_tsf_error(self.dll)

        return out

    # from Bruker tsfdata.py
    def index_to_mz(self, frame_id, indices):
        return self.__call_conversion_func(frame_id, indices, self.dll.tsf_index_to_mz)

    # modified from Bruker tsfdata.py
    def read_line_spectrum(self, frame_id):
        while True:
            cnt = int(self.profile_buffer_size)
            index_buf = np.empty(shape=cnt, dtype=np.float64)
            intensity_buf = np.empty(shape=cnt, dtype=np.float32)

            required_len = self.dll.tsf_read_line_spectrum(self.handle,
                                                           frame_id,
                                                           index_buf.ctypes.data_as(ctypes.POINTER(ctypes.c_double)),
                                                           intensity_buf.ctypes.data_as(ctypes.POINTER(ctypes.c_float)),
                                                           self.profile_buffer_size)

            if required_len > self.profile_buffer_size:
                if required_len > 16777216:
                    raise RuntimeError('Maximum expected frame size exceeded.')
                self.profile_buffer_size = required_len
            else:
                break

        return (index_buf[0:required_len], intensity_buf[0:required_len])

    # modified from Bruker tsfdata.py
    def read_profile_spectrum(self, frame_id):
        while True:
            cnt = int(self.profile_buffer_size)
            intensity_buf = np.empty(shape=cnt, dtype=np.uint32)

            required_len = self.dll.tsf_read_profile_spectrum(self.handle,
                                                              frame_id,
                                                              intensity_buf.ctypes.data_as(ctypes.POINTER(ctypes.c_uint32)),
                                                              self.profile_buffer_size)

            if required_len > self.profile_buffer_size:
                if required_len > 16777216:
                    raise RuntimeError('Maximum expected frame size exceeded.')
                self.profile_buffer_size = required_len
            else:
                break

        index_buf = np.arange(0, intensity_buf.size, dtype=np.float64)

        return (index_buf[0:required_len], intensity_buf[0:required_len])

    # Gets global metadata table as a dictionary.
    def get_global_metadata(self):
        metadata_query = 'SELECT * FROM GlobalMetadata'
        metadata_df = pd.read_sql_query(metadata_query, self.conn)
        metadata_dict = {}
        for index, row in metadata_df.iterrows():
            metadata_dict[row['Key']] = row['Value']
        self.meta_data = metadata_dict

    # Get Frames table from analysis.tsf SQL database.
    def get_frames_table(self):
        frames_query = 'SELECT * FROM Frames'
        self.frames = pd.read_sql_query(frames_query, self.conn)

    # Get MaldiFramesInfo table from analysis.tsf SQL database.
    def get_maldiframeinfo_table(self):
        maldiframeinfo_query = 'SELECT * FROM MaldiFrameInfo'
        self.maldiframeinfo = pd.read_sql_query(maldiframeinfo_query, self.conn)

    # Get FrameMsMsInfo table from analysis.tsf SQL database.
    def get_framemsmsinfo_table(self):
        framemsmsinfo_query = 'SELECT * FROM FrameMsMsInfo'
        self.framemsmsinfo = pd.read_sql_query(framemsmsinfo_query, self.conn)

    def close_sql_connection(self):
        self.conn.close()


class tdf_data(object):
    def __init__(self, bruker_d_folder_name: str, tdf_sdk_dll, use_recalibrated_state=True):
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
        self.source_file = bruker_d_folder_name

        self.get_global_metadata()
        self.get_frames_table()

        if 'MaldiApplicationType' in self.meta_data.keys():
            self.get_maldiframeinfo_table()
            self.get_framemsmsinfo_table()
        else:
            self.get_pasefframemsmsinfo_table()
            self.get_precursors_table()
            self.subset_ms1_frames()

        self.close_sql_connection()

    def __del__(self):
        if hasattr(self, 'handle'):
            self.dll.tims_close(self.handle)

    def __call_conversion_func(self, frame_id, input_data, func):
        if type(input_data) is np.ndarray and input_data.dtype == np.float64:
            in_array = input_data
        else:
            in_array = np.array(input_data, dtype=np.float64)

        cnt = len(in_array)
        out = np.empty(shape=cnt, dtype=np.float64)
        success = func(self.handle,
                       frame_id,
                       in_array.ctypes.data_as(ctypes.POINTER(ctypes.c_double)),
                       out.ctypes.data_as(ctypes.POINTER(ctypes.c_double)),
                       cnt)

        if success == 0:
            throw_last_tsf_error(self.dll)

        return out

    # following conversion functions from Bruker timsdata.py
    def index_to_mz(self, frame_id, indices):
        return self.__call_conversion_func(frame_id, indices, self.dll.tims_index_to_mz)

    def scan_num_to_oneoverk0(self, frame_id, scan_nums):
        return self.__call_conversion_func(frame_id, scan_nums, self.dll.tims_scannum_to_oneoverk0)

    # modified from Bruker timsdata.py
    def read_scans(self, frame_id, scan_begin, scan_end):
        while True:
            cnt = int(self.initial_frame_buffer_size)
            buf = np.empty(shape=cnt, dtype=np.uint32)
            length = 4 * cnt

            required_len = self.dll.tims_read_scans_v2(self.handle,
                                                       frame_id,
                                                       scan_begin,
                                                       scan_end,
                                                       buf.ctypes.data_as(ctypes.POINTER(ctypes.c_uint32)),
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
        precursors_for_dll = np.array(precursor_list, dtype=np.int64)

        result = {}

        @MSMS_SPECTRUM_FUNCTOR
        def callback_for_dll(precursor_id, num_peaks, mz_values, area_values):
            result[precursor_id] = (mz_values[0:num_peaks], area_values[0:num_peaks])

        rc = self.dll.tims_read_pasef_msms(self.handle,
                                           precursors_for_dll.ctypes.data_as(ctypes.POINTER(ctypes.c_int64)),
                                           len(precursor_list),
                                           callback_for_dll)

        return result

    # Only define if using SDK 2.8.7.1 or SDK 2.7.0.
    if TDF_SDK_VERSION == 'sdk2871' or TDF_SDK_VERSION == 'sdk270':
        def read_pasef_profile_msms(self, precursor_list):
            precursors_for_dll = np.array(precursor_list, dtype=np.int64)

            result = {}

            @MSMS_PROFILE_SPECTRUM_FUNCTOR
            def callback_for_dll(precursor_id, num_points, intensity_values):
                result[precursor_id] = intensity_values[0:num_points]

            rc = self.dll.tims_read_pasef_profile_msms(self.handle,
                                                       precursors_for_dll.ctypes.data_as(ctypes.POINTER(ctypes.c_int64)),
                                                       len(precursor_list),
                                                       callback_for_dll)

            return result

    def read_pasef_centroid_msms_for_frame(self, frame_id):
        result = {}

        @MSMS_SPECTRUM_FUNCTOR
        def callback_for_dll(precursor_id, num_peaks, mz_values, area_values):
            result[precursor_id] = (mz_values[0:num_peaks], area_values[0:num_peaks])

        rc = self.dll.tims_read_pasef_msms_for_frame(self.handle, frame_id, callback_for_dll)

        return result

    # Only define if using SDK 2.8.7.1 or SDK 2.7.0.
    if TDF_SDK_VERSION == 'sdk2871' or TDF_SDK_VERSION == 'sdk270':
        def read_pasef_profile_msms_for_frame(self, frame_id):
            result = {}

            @MSMS_PROFILE_SPECTRUM_FUNCTOR
            def callback_for_dll(precursor_id, num_points, intensity_values):
                result[precursor_id] = intensity_values[0:num_points]

            rc = self.dll.tims_read_pasef_profile_msms_for_frame(self.handle, frame_id, callback_for_dll)

            return result

    # Only define extract_centroided_spectrum_for_frame and extract_profile_spectrum_for_frame if using SDK 2.8.7.1.
    if TDF_SDK_VERSION == 'sdk2871':
        def extract_centroided_spectrum_for_frame(self, frame_id, scan_begin, scan_end):
            result = None

            @MSMS_SPECTRUM_FUNCTOR
            def callback_for_dll(precursor_id, num_peaks, mz_values, area_values):
                nonlocal result
                result = (mz_values[0:num_peaks], area_values[0:num_peaks])

            rc = self.dll.tims_extract_centroided_spectrum_for_frame(self.handle,
                                                                     frame_id,
                                                                     scan_begin,
                                                                     scan_end,
                                                                     callback_for_dll,
                                                                     None)

            return result

        def extract_profile_spectrum_for_frame(self, frame_id, scan_begin, scan_end):
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
        if encoding != 0:
            if encoding == 32:
                encoding_dtype = np.float32
            elif encoding == 64:
                encoding_dtype = np.float64

        list_of_scan_tuples = [i for i in self.read_scans(frame_id, begin_scan, end_scan)
                               if i[0].size != 0 and i[1].size != 0]
        if len(list_of_scan_tuples) == 0:
            return (np.empty(0, dtype=encoding_dtype),
                    np.empty(0, dtype=encoding_dtype))
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

        return (np.array(new_mz_array, dtype=encoding_dtype),
                np.array(new_intensity_array, dtype=encoding_dtype))

    # Gets global metadata table as a dictionary.
    def get_global_metadata(self):
        metadata_query = 'SELECT * FROM GlobalMetadata'
        metadata_df = pd.read_sql_query(metadata_query, self.conn)
        metadata_dict = {}
        for index, row in metadata_df.iterrows():
            metadata_dict[row['Key']] = row['Value']
        self.meta_data = metadata_dict

    # Get Frames table from analysis.tdf SQL database.
    def get_frames_table(self):
        frames_query = 'SELECT * FROM Frames'
        self.frames = pd.read_sql_query(frames_query, self.conn)

    # Get PasefFrameMsMsInfo table from analysis.tdf SQL database.
    def get_pasefframemsmsinfo_table(self):
        pasefframemsmsinfo_query = 'SELECT * FROM PasefFrameMsMsInfo'
        self.pasefframemsmsinfo = pd.read_sql_query(pasefframemsmsinfo_query, self.conn)

    # Get MaldiFramesInfo table from analysis.tdf SQL database.
    def get_maldiframeinfo_table(self):
        maldiframeinfo_query = 'SELECT * FROM MaldiFrameInfo'
        self.maldiframeinfo = pd.read_sql_query(maldiframeinfo_query, self.conn)

    # Get FrameMsMsInfo table from analysis.tdf SQL database.
    def get_framemsmsinfo_table(self):
        framemsmsinfo_query = 'SELECT * FROM FrameMsMsInfo'
        self.framemsmsinfo = pd.read_sql_query(framemsmsinfo_query, self.conn)

    # Get Precursors table from analysis.tdf SQL database.
    def get_precursors_table(self):
        precursors_query = 'SELECT * FROM Precursors'
        self.precursors = pd.read_sql_query(precursors_query, self.conn)
        # Add mobility values to precursor table
        # Get array of mobility values based on number of scans.
        max_num_scans = max(self.frames['NumScans']) + 1
        indices = np.arange(max_num_scans).astype(np.float64)
        mobility_values = np.empty_like(indices)
        self.dll.tims_scannum_to_oneoverk0(self.handle,
                                           1,  # mobility_estimation_from_frame
                                           indices.ctypes.data_as(ctypes.POINTER(ctypes.c_double)),
                                           mobility_values.ctypes.data_as(ctypes.POINTER(ctypes.c_double)),
                                           max_num_scans)
        # Assign mobility values to precursor table.
        precursor_mobility_values = mobility_values[self.precursors['ScanNumber'].astype(np.int64)]
        self.precursors['Mobility'] = precursor_mobility_values

    # Subset Frames table to only include MS1 rows. Used for chunking during data parsing/writing.
    def subset_ms1_frames(self):
        self.ms1_frames = list(self.frames[self.frames['MsMsType'] == 0]['Id'].values)

    def close_sql_connection(self):
        self.conn.close()
