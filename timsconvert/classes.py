import sqlite3
import numpy as np
import pandas as pd
from pyBaf2Sql.classes import BafData
from pyTDFSDK.classes import TsfData, TdfData
from pyTDFSDK.ctypes_data_structures import PressureCompensationStrategy
from timsconvert.parse import get_encoding_dtype, get_centroid_status


class TimsconvertBafData(BafData):
    """
    Child class of pyBaf2Sql.classes.BafData containing metadata from BAF files and methods from Baf2sql library to
    work with BAF format data.

    :param bruker_d_folder_name: Path to Bruker .d directory containing analysis.baf and analysis.sqlite.
    :type bruker_d_folder_name: str
    :param baf2sql: Library initialized by pyBaf2Sql.init_baf2sql.init_baf2sql_api().
    :type baf2sql: ctypes.CDLL
    :param raw_calibration: Whether to use recalibrated data (False) or not (True), defaults to False.
    :type raw_calibration: bool
    :param all_variables: Whether to load all variables from analysis.sqlite database, defaults to False.
    :type all_variables: bool
    """
    def __init__(self, bruker_d_folder_name: str, baf2sql, raw_calibration=False, all_variables=False):
        # Initialize attributes and methods of the parent class.
        super().__init__(bruker_d_folder_name, baf2sql, raw_calibration, all_variables)
        self.ms1_frames = None
        self.subset_ms1_frames()

    def subset_ms1_frames(self):
        """
        Subset timsconvert.classes.BafData.frames table (Spectra table from analysis.sqlite) to only include MS1 rows.
        Used during the subsetting process during data parsing/writing for memory efficiency. The subsetted
        pandas.DataFrame is stored in timsconvert.classes.BafData.ms1_frames.
        """
        self.ms1_frames = self.analysis['Spectra'][self.analysis['Spectra']['AcquisitionKey'] == 1]['Id'].values.tolist()


class TimsconvertTsfData(TsfData):
    """
    Child class of pyTDFSDK.classes.TsfData containing metadata from TSF files and methods from TDF-SDK library to work
    with TSF format data.

    :param bruker_d_folder_name: Path to a Bruker .d directory containing analysis.tsf.
    :type bruker_d_folder_name: str
    :param tdf_sdk: Library initialized by pyTDFSDK.init_tdf_sdk.init_tdf_sdk_api().
    :type tdf_sdk: ctypes.CDLL
    :param use_recalibrated_state: Whether to use recalibrated data (True) or not (False), defaults to True.
    :type use_recalibrated_state: bool
    """
    def __init__(self, bruker_d_folder_name: str, tdf_sdk, use_recalibrated_state=True):
        # Initialize attributes and methods of the parent class.
        super().__init__(bruker_d_folder_name, tdf_sdk, use_recalibrated_state)
        self.ms1_frames = None
        self.subset_ms1_frames()

    def subset_ms1_frames(self):
        """
        Subset timsconvert.classes.TsfData.frames table (Frames table from analysis.tsf) to only include MS1 rows.
        Used during the subsetting process during data parsing/writing for memory efficiency. The subsetted
        pandas.DataFrame is stored in timsconvert.classes.TsfData.ms1_frames.
        """
        self.ms1_frames = self.analysis['Frames'][self.analysis['Frames']['MsMsType'] == 0]['Id'].values.tolist()


class TimsconvertTdfData(TdfData):
    """
    Child class of pyTDFSDK.classes.TdfData containing metadata from TDF files and methods from TDF-SDK library to work
    with TDF format data.

    :param bruker_d_folder_name: Path to a Bruker .d directory containing analysis.tdf.
    :type bruker_d_folder_name: str
    :param tdf_sdk: Library initialized by pyTDFSDK.init_tdf_sdk.init_tdf_sdk_api().
    :type tdf_sdk: ctypes.CDLL
    :param use_recalibrated_state: Whether to use recalibrated data (True) or not (False), defaults to True.
    :type use_recalibrated_state: bool
    :param pressure_compensation_strategy: Pressure compensation when opening TDF data
        (pyTDFSDK.ctypes_data_structures.PressureCompensationStrategy.NoPressureCompensation = None,
        pyTDFSDK.ctypes_data_structures.PressureCompensationStrategy.AnalyisGlobalPressureCompensation = analysis
        global pressure compensation,
        pyTDFSDK.ctypes_data_structures.PressureCompensationStrategy.PerFramePressureCompensation = per frame pressure
        compensation), defaults to No Pressure Compensation.
    :type pressure_compensation_strategy: enum.Enum
    """
    def __init__(self, bruker_d_folder_name: str, tdf_sdk, use_recalibrated_state=True,
                 pressure_compensation_strategy=PressureCompensationStrategy.NoPressureCompensation):
        # Initialize attributes and methods of the parent class.
        super().__init__(bruker_d_folder_name, tdf_sdk, use_recalibrated_state, pressure_compensation_strategy)
        self.ms1_frames = None
        self.subset_ms1_frames()

    def subset_ms1_frames(self):
        """
        Subset timsconvert.classes.TdfData.frames table (Frames table from analysis.tdf) to only include MS1 rows.
        Used during the subsetting process during data parsing/writing for memory efficiency. The subsetted
        pandas.DataFrame is stored in timsconvert.classes.TdfData.ms1_frames.
        """
        self.ms1_frames = self.analysis['Frames'][self.analysis['Frames']['MsMsType'] == 0]['Id'].values.tolist()
        if len(self.ms1_frames) > 0 and self.ms1_frames[0] != 1:
            self.ms1_frames.insert(0, 1)
