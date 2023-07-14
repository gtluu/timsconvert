#!/usr/bin/env python3
# 
# # Project: OpenMS Compatible MzML generators
# Developer: Michael A. Freitas
#
# Description: generate OpenMS compatible MzML from TDF using SDK
# Copyright (c) 2020, Michael A. Freitas, The Ohio State University
#
# # All rights reserved.
#
# This source code is licensed under the BSD-style license found in the
# LICENSE file in the root directory of this source tree. 

import collections 
import hashlib
from psims.mzml import MzMLWriter
import time
import tdf2mzml.timsdata as timsdata
from timsconvert.write_mzml import *

NAME = 'tdf2mzml'
MAJOR_VERSION = '0.3'
MINOR_VERSION = '20200211.1'
DEBUG = True

# precursor column information
precursor_columns = [
    "Id",
    "LargestPeakMz",
    "AverageMz",
    "MonoisotopicMz",
    "ScanNumber",
    "Charge",
    "Intensity",
    "Parent"
]


def timing(f):
    """
    Helper function for timing other functions

    Parameters
    ----------
    arg1 : function

    Returns
    -------
    funciton
        new function wrap with timer and logging
    """

    def wrap(*args):
        time1 = time.time()
        ret = f(*args)
        time2 = time.time()
        logging.info('{:s} function took {:.3f} s'.format(f.__name__, (time2 - time1)))
        return ret

    return wrap


def scan_progress(mzml_data_struct, interval=1000):
    """
    Progress logger

    Loggs progress for writing mzml spectra.  Defaults to output a log message
    every 1000 scans.

    Parameters
    ----------
    mzml_data_struct : dict
        structure of the mzml data
    interval " int
        loggin interval, defaults to 1000
    Returns
    -------
    None
    """
    if mzml_data_struct['scan_index'] % int(interval) == 0:
        end_time = time.time()
        logging.info("Processed {} of {} scans in {:.3f} s".format(
            mzml_data_struct['scan_index'],
            mzml_data_struct['data_dict']['total_spectra'],
            end_time - mzml_data_struct['scan_loop_time1']
        ))

        mzml_data_struct['scan_loop_time1'] = end_time

    return


@timing
def sha1_checksum(path_name):
    """
    Determine and return SHA1 checsum for file

    Parameters
    ----------
    path_name : str
        file path

    Returns
    -------
    sha1 hash
    """
    BLOCKSIZE = 65536
    hasher = hashlib.sha1()
    with open(path_name, 'rb') as afile:
        buf = afile.read(BLOCKSIZE)
        while len(buf) > 0:
            hasher.update(buf)
            buf = afile.read(BLOCKSIZE)

    return hasher.hexdigest()


def centroid_precursor_frame(mzml_data_struct):
    """
    Read and returns a centroid spectrum for a precursor frame

    This function uses the SDK to get and return an MS1 centroid spectrum for
    the requested frame.

    Parameters
    ----------
    mzml_data_struct : dict
        structure of the mzml data

    Returns
    -------
    list of lists
        list of mz and i lists [[mz,[i]]
    """
    precursor_frame_id = mzml_data_struct['current_precursor']['id']
    num_scans = mzml_data_struct['td'].conn.execute(
        "SELECT NumScans FROM Frames WHERE Id={0}".format(precursor_frame_id)).fetchone()[0]
    # print(mzml_data_struct['td'].conn.execute("SELECT NumScans FROM Frames WHERE Id={}".format(precursor_frame_id)).fetchone())
    data_list = mzml_data_struct['td'].extractCentroidedSpectrumForFrame(precursor_frame_id, 0, num_scans)
    # print(np.array(data_list))
    return np.array(data_list)


def profile_precursor_frame(mzml_data_struct):
    """
    Read and return a profile spectrum for a precursor frame

    This function uses the SDK to get and return an MS1 profile spectrum for
    the requested frame.

    Parameters
    ----------
    mzml_data_struct : dict
        structure of the mzml data

    Returns
    -------
    list of lists
        list of mz and i lists [[mz,[i]]
    """
    precursor_frame_id = mzml_data_struct['current_precursor']['id']
    num_scans = mzml_data_struct['td'].conn.execute(
        "SELECT NumScans FROM Frames WHERE Id={}".format(precursor_frame_id)).fetchone()[0]

    # SDK takes 0-num_scans as input.
    i_array = mzml_data_struct['td'].extractProfileForFrame(precursor_frame_id, 0, num_scans)

    # ******
    # TODO Get size of i_array and then set range from 0,sizeof(i_array)-1
    # Implemented fix needs testing
    m_array = mzml_data_struct['td'].indexToMz(precursor_frame_id,
                                               list(range(0, len(i_array))))

    return np.array([m_array, i_array])


def raw_precursor_frame(mzml_data_struct):
    """
    Read and return a raw spectrum for a precursor frame

    This function simply adds together the ms1 spectra to create a raw MS1 spectrum
    for the requested frame.

    Parameters
    ----------
    mzml_data_struct : dict
        structure of the mzml data

    Returns
    -------
    list of lists
        list of mz and i lists [[mz,[i]]
    """
    precursor_frame_id = mzml_data_struct['current_precursor']['id']
    # build merged array of m/z and intensities
    num_scans = mzml_data_struct['td'].conn.execute(
        "SELECT NumScans FROM Frames WHERE Id={0}".format(precursor_frame_id)).fetchone()[0]
    raw_position_dict = collections.defaultdict(int)
    scans = mzml_data_struct['td'].readScans(precursor_frame_id, 0, num_scans)

    for scan in scans:
        index_array = scan[0]
        # TODO Move index to mz operation to end for speedup
        mz_array = mzml_data_struct['td'].indexToMz(precursor_frame_id, index_array)
        i_array = scan[1]
        for idx_001 in range(0, len(mz_array)):
            mz = mz_array[idx_001]
            i = i_array[idx_001]

            if i >= mzml_data_struct['ms1_threshold']:
                raw_position_dict[mz] += i

    return list(zip(*raw_position_dict.items()))


def get_spectrum_dict(mzml_data_struct):
    """
    Get mzml spectrum information

    Function scans the raw data file and build the data file dictionary

    Parameters
    ----------
    mzml_data_struct : dict
        structure of the mzml data

    Returns
    -------
    dict:
        spectrum dictionary
    """
    spectrum_dict = collections.OrderedDict()

    pasef_frame_columns = ['Frame', 'IsolationMz', 'CollisionEnergy', 'IsolationWidth']

    # TODO add capability to request scan times in addition to frame range

    spectrum_dict['acq_softare'] = mzml_data_struct['td'].conn.execute(
        "Select Value from GlobalMetadata where key=\"AcquisitionSoftware\""
    ).fetchone()[0]

    spectrum_dict['acq_softare_version'] = mzml_data_struct['td'].conn.execute(
        "Select Value from GlobalMetadata where key=\"AcquisitionSoftwareVersion\""
    ).fetchone()[0]

    spectrum_dict['acq_date_time'] = mzml_data_struct['td'].conn.execute(
        "Select Value from GlobalMetadata where key=\"AcquisitionDateTime\""
    ).fetchone()[0]

    spectrum_dict['instrument_serial_number'] = mzml_data_struct['td'].conn.execute(
        "Select Value from GlobalMetadata where key=\"InstrumentSerialNumber\""
    ).fetchone()[0]

    spectrum_dict['mz_acq_range_lower'] = mzml_data_struct['td'].conn.execute(
        "Select Value from GlobalMetadata where key=\"MzAcqRangeLower\""
    ).fetchone()[0]

    spectrum_dict['mz_acq_range_upper'] = mzml_data_struct['td'].conn.execute(
        "Select Value from GlobalMetadata where key=\"MzAcqRangeUpper\""
    ).fetchone()[0]

    spectrum_dict['frame_count'] = mzml_data_struct['td'].conn.execute("SELECT COUNT(*) FROM Frames").fetchone()[0]

    MSMS_frame_list = list()
    total_spectrum_count = 0

    # Get MS1 MMsMsType0 Frames from TDF
    MMsMsType0_frames = len(
        mzml_data_struct['td'].conn.execute("SELECT Id , Time From Frames where MsMsType=0").fetchall())
    logging.debug("number of type 0 frames: {}".format(MMsMsType0_frames))

    MMsMsType0_spectra = MMsMsType0_frames

    # Get MS1 MMsMsType0 Frames from TDF
    MMsMsType8_frames = len(
        mzml_data_struct['td'].conn.execute("SELECT Id , Time From Frames where MsMsType=8").fetchall())
    logging.debug("number of type 8 frames: {}".format(MMsMsType8_frames))

    if MMsMsType8_frames > 0:
        MMsMsType8_spectra = mzml_data_struct['td'].conn.execute("SELECT COUNT(*) FROM Precursors").fetchone()[0]
        logging.debug("number of type 8 spectra: {}".format(MMsMsType8_spectra))

        spectrum_dict['PASEFMSMS_type8'] = 1
        # for MMsMsType0_frame in MMsMsType0_frames:

        #     precursor_frame_id = MMsMsType0_frame[0]
        #     #precursor_frame_rt = MMsMsType0_frame[1]

        #     precursor_list = mzml_data_struct['td'].conn.execute(
        #         "Select Id From Precursors where Parent={}".format(
        #             precursor_frame_id)
        #         ).fetchall()
        #     total_spectrum_count += len(precursor_list) +1
        # logging.debug("number spectra: {}".format(total_spectrum_count))
    else:
        MMsMsType8_spectra = 0
        spectrum_dict['PASEFMSMS_type8'] = 0

    # Get MS9 MMsMsType9 Frames from TDF
    MMsMsType9_frames = len(
        mzml_data_struct['td'].conn.execute("SELECT Id , Time From Frames where MsMsType=9").fetchall())
    logging.debug("number of type 9 frames: {}".format(MMsMsType9_frames))

    if MMsMsType9_frames > 0:
        MMsMsType9_spectra = MMsMsType9_frames
        spectrum_dict['PASEFMSMS_type9'] = 1
    else:
        MMsMsType9_spectra = 0
        spectrum_dict['PASEFMSMS_type9'] = 0

    # spectrum_dict['total_spectra'] = total_spectrum_count
    spectrum_dict['total_spectra'] = MMsMsType0_spectra + MMsMsType8_spectra + MMsMsType9_frames
    spectrum_dict['ms1_spectra_count'] = MMsMsType0_spectra
    spectrum_dict['ms2_spectra_count'] = MMsMsType8_spectra
    spectrum_dict['dia_spectra_count'] = MMsMsType9_spectra

    return spectrum_dict


# def get_num_spectra(mzml_data_struct):
#     """
#     Get the number of spectra for the conversion

#     Helper function to determine number of spectra.  This function rescans the
#     data file in order to account for the start and end frames.

#     Parameters
#     ----------
#     mzml_data_struct : dict
#         structure of the mzml data

#     Returns
#     -------
#     int:
#         spectrum count
#     """
#     total_spectrum_count = 0

#     #Get Frames from TDF
#     frames = mzml_data_struct['td'].conn.execute("SELECT * From Frames where MsMsType=0").fetchall()

#     for frame in frames:
#         frame_id = frame[0]

#         #Skip Frames outside the requested Frame range
#         #TODO add capability to request scan times in addition to frame range
#         if mzml_data_struct['start_frame'] != -1 and frame_id < mzml_data_struct['start_frame']:
#             continue

#         if mzml_data_struct['end_frame'] != -1 and frame_id > mzml_data_struct['end_frame']:
#             break

#         total_spectrum_count +=1

#         #Get number of MS2 Spectra for each precuros in a give Frame
#         ms2_spectra = mzml_data_struct['td'].conn.execute(
#                             "Select * From Precursors where Parent={}"
#                             .format(frame_id)
#                             ).fetchall()

#         if len(ms2_spectra) >= 1:
#             total_spectrum_count += len(ms2_spectra)

#     return total_spectrum_count


def write_sourcefile_list(mzml_data_struct):
    """
    Writes the source file list

    takes data from the mzml_data_struct to format and write mzml information

    Parameters
    ----------
    mzml_data_struct : dict
        structure of the mzml data

    Returns
    -------
    None
    """
    sf_list = list()

    # SourceFile 'analysis.tdf'
    tdf_file_name = 'analysis.tdf'
    tdf_path = os.path.join(mzml_data_struct['input'], tdf_file_name)
    tdf_id = tdf_path.replace('/', "__")
    sf1 = mzml_data_struct['writer'].SourceFile(
        tdf_path,
        tdf_file_name,
        id=tdf_id,
        params=[
            {"Bruker TDF nativeID format": ""},
            {"Bruker TDF format": ""},
            {"SHA-1": sha1_checksum(tdf_path)},
        ]
    )
    sf_list.append(sf1)

    # SourceFile 'analysis.tdf_bin'
    tdf_file_name = 'analysis.tdf_bin'
    tdf_path = os.path.join(mzml_data_struct['input'], tdf_file_name)
    tdf_id = tdf_path.replace('/', "__")
    sf2 = mzml_data_struct['writer'].SourceFile(
        tdf_path,
        tdf_file_name,
        id=tdf_id,
        params=[
            {"Bruker TDF nativeID format": ""},
            {"Bruker TDF format": ""},
            {"SHA-1": sha1_checksum(tdf_path)},
        ]
    )
    sf_list.append(sf2)

    mzml_data_struct['writer'].file_description(["MS1 spectrum", "MSn spectrum"], sf_list)
    return


def write_reference_param_group_list(mzml_data_struct):
    """
    Writes the referenceable param group list

    takes data from the mzml_data_struct to format and write mzml information

    Parameters
    ----------
    mzml_data_struct : dict
        structure of the mzml data

    Returns
    -------
    None
    """
    # TODO Figure out how to add reference to Run section as in PWiz
    rpgl_list = list()

    rpgl_list.append(
        mzml_data_struct['writer'].ReferenceableParamGroup(
            id="CommonInstrumentParams",
            params=[
                {"Bruker Daltonics instrument model": ""},
            ]
        )
    )

    mzml_data_struct['writer'].reference_param_group_list(rpgl_list)
    return


def write_software_list(mzml_data_struct):
    """
    Writes the software list

    takes data from the mzml_data_struct to format and write mzml information

    Parameters
    ----------
    mzml_data_struct : dict
        structure of the mzml data

    Returns
    -------
    None
    """
    # TODO: build up the software list
    # TODO: Automate collecting Sofware names and versions
    software_list = list()

    acq_softare = mzml_data_struct['td'].conn.execute(
        "Select Value from GlobalMetadata where key=\"AcquisitionSoftware\""
    ).fetchone()[0]
    acq_softare_version = mzml_data_struct['td'].conn.execute(
        "Select Value from GlobalMetadata where key=\"AcquisitionSoftwareVersion\""
    ).fetchone()[0]
    mz_acq_range_lower = mzml_data_struct['td'].conn.execute(
        "Select Value from GlobalMetadata where key=\"MzAcqRangeLower\""
    ).fetchone()[0]
    mz_acq_range_upper = mzml_data_struct['td'].conn.execute(
        "Select Value from GlobalMetadata where key=\"MzAcqRangeUpper\""
    ).fetchone()[0]

    ### SDK Description
    software_list.append({
        "id": "TIMS_SDK",
        "version": "2.8.7",
        "params": [
            {"Bruker software": ""},
            {"software name": "TIMS SDK"}
        ]
    })

    ### micrOTOFcontrol Description
    software_list.append({
        "id": acq_softare,
        "version": acq_softare_version,
        "params": [
            {"micrOTOFcontrol": ""}
        ]
    })

    ### python Description
    software_list.append({
        "id": NAME,
        "version": MAJOR_VERSION + "-" + MINOR_VERSION,
        "params": [
            {"python": "3.8.0"}
        ]
    })

    mzml_data_struct['writer'].software_list(software_list)
    return


def write_instrument_configuration_list(mzml_data_struct):
    """
    Writes the instrument configuration list

    takes data from the mzml_data_struct to format and write mzml information

    Parameters
    ----------
    mzml_data_struct : dict
        structure of the mzml data

    Returns
    -------
    None
    """
    # TODO FIX DESCRIPTION
    instrument_configurations = list()
    source = mzml_data_struct['writer'].Source(1, ["nanospray inlet", "quadrupole"])
    analyzer = mzml_data_struct['writer'].Analyzer(2, ["time-of-flight"])
    detector = mzml_data_struct['writer'].Detector(3, ["microchannel plate detector", "photomultiplier"])
    serial_number = mzml_data_struct['data_dict']['instrument_serial_number']

    instparams = [
        {"instrument serial number": serial_number}
    ]

    if mzml_data_struct['data_dict']['PASEFMSMS_type9'] == 1:

        windows = mzml_data_struct['td'].conn.execute("SELECT * From DiaFrameMsMsWindows").fetchall()
        for window in windows:
            instparams.append(
                {"dia_window": {
                    'Group': window[0],
                    'mz_center': window[3],
                    'width': window[4],
                    'energy': window[5]
                }
                }
            )

    instrument_configurations.append(
        mzml_data_struct['writer'].InstrumentConfiguration(
            id="IC1",
            component_list=[
                source,
                analyzer,
                detector
            ],
            params=instparams
        )
    )

    mzml_data_struct['writer'].instrument_configuration_list(instrument_configurations)
    return


def write_data_processing_list(mzml_data_struct):
    """
    Writes the data processing list

    takes data from the mzml_data_struct to format and write mzml information

    Parameters
    ----------
    mzml_data_struct : dict
        structure of the mzml data

    Returns
    -------
    None
    """
    data_processing = list()
    methods = list()

    methods.append(
        mzml_data_struct['writer'].ProcessingMethod(
            order=0,
            software_reference="tdf2mzml",
            params=[
                "Conversion to mzML"
            ]
        )
    )

    data_processing.append(mzml_data_struct['writer'].DataProcessing(methods, id='tdf2mzml_Bruker_conversion'))
    mzml_data_struct['writer'].data_processing_list(data_processing)

    return


def write_header(mzml_data_struct):
    """
    Writes the data file information

    takes data from the mzml_data_struct to format and write the mzml information
    * Load controlled vocabularies
    * write source filel list
    * write reference_param group list
    * write software list
    * write instrument_configuration list
    * write data processing list

    Parameters
    ----------
    mzml_data_struct : dict
        structure of the mzml data

    Returns
    -------
    None
    """
    mzml_data_struct['writer'].controlled_vocabularies()
    write_sourcefile_list(mzml_data_struct)
    write_reference_param_group_list(mzml_data_struct)
    write_software_list(mzml_data_struct)
    write_instrument_configuration_list(mzml_data_struct)
    write_data_processing_list(mzml_data_struct)

    return


def write_precursor_frame(mzml_data_struct):
    """
    Writes a Precursor MS spectrum

    takes data from the mzml_data_struct to format and write the precursor MS1
    spectrum

    Parameters
    ----------
    mzml_data_struct : dict
        structure of the mzml data

    Returns
    -------
    None
    """
    precursor_frame_id = mzml_data_struct['current_precursor']['id']
    scan_start_time = mzml_data_struct['current_precursor']['start_time']
    # Process only frames in frame range

    # build merged array of m/z and intensities
    if mzml_data_struct['ms1_type'] == 'raw':
        ms1_data = raw_precursor_frame(mzml_data_struct)
        centroided_flag = True
    elif mzml_data_struct['ms1_type'] == 'profile':
        ms1_data = profile_precursor_frame(mzml_data_struct)
        centroided_flag = False
    elif mzml_data_struct['ms1_type'] == 'centroid':
        ms1_data = centroid_precursor_frame(mzml_data_struct)
        centroided_flag = True

    ms1_mz_array = np.asarray(ms1_data[0])
    ms1_i_array = np.asarray(ms1_data[1])

    # Write MS1 Spectrum

    mzml_data_struct['current_precursor']['spectrum_id'] = "index={}".format(mzml_data_struct['scan_index'])

    # Only write if not empty.
    if ms1_mz_array.size != 0 and ms1_i_array.size != 0 and ms1_mz_array.size == ms1_i_array.size:
        if len(ms1_mz_array) > 1:
            # base_peak_intensity = np.max(ms1_i_array)
            total_ion_intensity = ms1_i_array.sum()
            bp_index = np.argmax(ms1_i_array)
            base_peak_intensity = ms1_i_array[bp_index]
            base_peak_mz = ms1_mz_array[bp_index]

        else:
            # TODO fix handling for sparce MS1/MS2 data the following is a crude fixe
            base_peak_intensity = total_ion_intensity = 0.0
            base_peak_mz = 0.0

        mzml_data_struct['writer'].write_spectrum(
            ms1_mz_array,
            ms1_i_array,
            id=mzml_data_struct['current_precursor']['spectrum_id'],
            centroided=centroided_flag,
            scan_start_time=scan_start_time,
            scan_window_list=[(mzml_data_struct['data_dict']['mz_acq_range_lower'],
                               mzml_data_struct['data_dict']['mz_acq_range_upper'])],
            compression=mzml_data_struct['compression'],
            params=[
                {"ms level": 1},
                {"total ion current": total_ion_intensity},
                {"base peak intensity": base_peak_intensity, 'unit_accession': 'MS:1000131'},
                {"base peak m/z": base_peak_mz, 'unit_name': 'm/z'}
            ]
        )

    mzml_data_struct['scan_index'] += 1

    return


def get_precursor_list(mzml_data_struct):
    """
    Get list of precursors in the current precursor frame

    takes data from the mzml_data_struct to get list of precursors in the
    contained in the current_precursor frame

    Parameters
    ----------
    mzml_data_struct : dict
        structure of the mzml data

    Returns
    -------
    list
        list of precursor values
    """
    # get MS2 spetrum for each precursor
    precursor_frame_id = mzml_data_struct['current_precursor']['id']

    precursor_list = mzml_data_struct['td'].conn.execute(
        "Select {} From Precursors where Parent={}".format(
            ",".join(precursor_columns),
            precursor_frame_id)
    ).fetchall()

    return precursor_list


def write_pasef_msms_spectrum(mzml_data_struct):
    """
    Writes a PASEF MSMS spectrum

    takes data from the mzml_data_struct to format and write the spectrum

    Parameters
    ----------
    mzml_data_struct : dict
        structure of the mzml data

    Returns
    -------
    None
    """
    precursor = {precursor_columns[i]: mzml_data_struct['current_precursor']['data'][i] for i in
                 range(len(precursor_columns))}

    # Get MS2 Arrays
    result = mzml_data_struct['td'].readPasefMsMs([precursor["Id"]])[precursor["Id"]]
    ms2_mz_array = np.asarray(result[0])
    ms2_i_array = np.asarray(result[1])

    if ms2_mz_array.size != 0 and ms2_i_array.size != 0 and ms2_mz_array.size == ms2_i_array.size:
        # Set Precuror metadata
        # TODO add additional metada
        # TODO clarify correct m/z for precursor to use for Isolation Width

        msn_spectrum_id = "index={}".format(mzml_data_struct['scan_index'])

        parent_frame_list = mzml_data_struct['td'].conn.execute(
            "SELECT Frame From PasefFrameMsMsInfo where Precursor={}".format(precursor['Id'])).fetchall()
        parent_frame_string = " ".join([str(item[0]) for item in parent_frame_list])

        pasef_frame_columns = ['IsolationMz', 'CollisionEnergy', 'IsolationWidth']
        pasef_frame_info_list = mzml_data_struct['td'].conn.execute(
            "SELECT {} From PasefFrameMsMsInfo where Precursor={}".format(
                ",".join(pasef_frame_columns),
                precursor['Id']
            )
        ).fetchone()

        pasef_frame = {pasef_frame_columns[i]: pasef_frame_info_list[i] for i in range(len(pasef_frame_columns))}

        precursor_info = dict()

        ion_mobilitiy = mzml_data_struct['td'].scanNumToOneOverK0(precursor['Parent'], [precursor['ScanNumber']])[0]
        precursor_info['params'] = [
            {"inverse reduced ion mobility": ion_mobilitiy, 'unit_accession': 'MS:1002814'}
        ]

        precursor_info["spectrum_reference"] = mzml_data_struct['current_precursor']['spectrum_id']

        # TODO find the correct metadata and apply it here properly
        precursor_info["activation"] = [
            "CID",
            {"collision energy": pasef_frame["CollisionEnergy"]}
        ]

        precursor_info["isolation_window_args"] = dict()

        if precursor['Charge'] != None:
            precursor_mz = precursor['MonoisotopicMz']
            precursor_info["mz"] = precursor_mz
            precursor_info["isolation_window_args"]["target"] = precursor_mz

            isolation_offset = pasef_frame["IsolationMz"] - precursor_mz
            isolation_width = pasef_frame["IsolationWidth"] / 2.0

            precursor_info["isolation_window_args"]["lower"] = isolation_width - isolation_offset
            precursor_info["isolation_window_args"]["upper"] = isolation_width + isolation_offset

            precursor_info["charge"] = precursor['Charge']
        else:
            precursor_mz = precursor['LargestPeakMz']
            precursor_info["mz"] = precursor_mz
            precursor_info["isolation_window_args"]["target"] = precursor_mz

            isolation_offset = pasef_frame["IsolationMz"] - precursor_mz
            isolation_width = pasef_frame["IsolationWidth"] / 2.0

            precursor_info["isolation_window_args"]["lower"] = isolation_width - isolation_offset
            precursor_info["isolation_window_args"]["upper"] = isolation_width + isolation_offset

            precursor_info["charge"] = 2

        mzml_data_struct['writer'].write_spectrum(
            ms2_mz_array,
            ms2_i_array,
            id=msn_spectrum_id,
            centroided=True,
            scan_start_time=mzml_data_struct['current_precursor']['start_time'],
            scan_window_list=[(
                mzml_data_struct['data_dict']['mz_acq_range_lower'],
                mzml_data_struct['data_dict']['mz_acq_range_upper']
            )],
            compression=mzml_data_struct['compression'],
            precursor_information=precursor_info,
            params=[
                {"ms level": 2},
                {"total ion current": ms2_i_array.sum()}
            ]
        )

    mzml_data_struct['scan_index'] += 1

    return


def write_pasef_dia_spectrum(mzml_data_struct):
    """
    Writes a PASEF MSMS spectrum

    takes data from the mzml_data_struct to format and write the spectrum

    Parameters
    ----------
    mzml_data_struct : dict
        structure of the mzml data

    Returns
    -------
    None
    """
    logging.debug("precursor \n{}".format(mzml_data_struct['current_precursor']))
    logging.debug("dia\n{}".format(mzml_data_struct['current_dia_frame']))

    frame_id = mzml_data_struct['current_dia_frame']['id']
    start_scan = mzml_data_struct['current_dia_frame']['current_window'][1]
    end_scan = mzml_data_struct['current_dia_frame']['current_window'][2]
    mz_center = mzml_data_struct['current_dia_frame']['current_window'][3]
    mz_width = mzml_data_struct['current_dia_frame']['current_window'][4]
    collision_energy = mzml_data_struct['current_dia_frame']['current_window'][5]
    # logging.debug(frame_id, start_scan, end_scan)

    result = mzml_data_struct['td'].extractCentroidedSpectrumForFrame(frame_id, start_scan, end_scan)

    ms2_mz_array = np.asarray(result[0])
    ms2_i_array = np.asarray(result[1])

    logging.debug("{}\n{}".format(ms2_mz_array, ms2_i_array))
    logging.debug(mzml_data_struct['scan_index'])
    msn_spectrum_id = "index={}".format(mzml_data_struct['scan_index'])
    logging.debug(mzml_data_struct['scan_index'])

    precursor_info = dict()
    precursor_info["mz"] = mz_center
    precursor_info["spectrum_reference"] = mzml_data_struct['current_precursor']['spectrum_id']

    # # TODO find the correct metadata and apply it here properly
    precursor_info["activation"] = [
        "CID",
        {"collision energy": collision_energy}
    ]

    precursor_info["isolation_window_args"] = dict()

    precursor_info["isolation_window_args"]["target"] = mz_center

    isolation_width = mz_width / 2.0

    precursor_info["isolation_window_args"]["lower"] = isolation_width
    precursor_info["isolation_window_args"]["upper"] = isolation_width

    mzml_data_struct['writer'].write_spectrum(
        ms2_mz_array,
        ms2_i_array,
        id=msn_spectrum_id,
        centroided=True,
        scan_start_time=mzml_data_struct['current_dia_frame']['frame'][1] / 60,
        scan_window_list=[(
            mzml_data_struct['data_dict']['mz_acq_range_lower'],
            mzml_data_struct['data_dict']['mz_acq_range_upper']
        )],
        compression=mzml_data_struct['compression'],
        precursor_information=precursor_info,
        params=[
            {"ms level": 2},
            {"total ion current": ms2_i_array.sum()}
        ]
    )

    mzml_data_struct['scan_index'] += 1

    return


def process_arg(args):
    """
    Convert namespace args objet to dictionary.

    Helper function. conversion of the args from namespace to dictionary
    allows for easier passing and modification.

    Parameters
    ----------
    args :

        args manespace object from argspars

    Returns
    -------
    dict :
        dictionary of arguments
    """
    return vars(args)


@timing
def tdf2mzml_write_mzml(args):
    """
    Write mzml file

    Read command line arguments and use psims package to format and write mzml

    Parameters
    ----------
    args : args manespace object from argspars

    Returns
    -------
    None
    """
    #mzml_data_struct = process_arg(args)
    mzml_data_struct = args
    mzml_data_struct['output'] = os.path.join(args['outdir'], args['outfile'])
    mzml_data_struct['ms1_type'] = args['mode']

    ### Connect to TDF DB
    logging.info("transforming TDF to mzML file: {}".format(mzml_data_struct['input']))

    mzml_data_struct['td'] = timsdata.TimsData(mzml_data_struct['input'])
    mzml_data_struct['data_dict'] = get_spectrum_dict(mzml_data_struct)

    logging.info("{} Total Frames.".format(mzml_data_struct['data_dict']['frame_count']))
    logging.info("{} Total Spectra.".format(mzml_data_struct['data_dict']['total_spectra']))
    logging.info("{} MS1 Spectra.".format(mzml_data_struct['data_dict']['ms1_spectra_count']))
    logging.info("{} MS2 DDA Scans.".format(mzml_data_struct['data_dict']['ms2_spectra_count']))
    logging.info("{} MS2 DIA Scans.".format(mzml_data_struct['data_dict']['dia_spectra_count']))

    logging.info("writting to mzML file: {}".format(mzml_data_struct['output']))
    mzml_data_struct['writer'] = MzMLWriter(mzml_data_struct['output'])

    with mzml_data_struct['writer']:
        write_header(mzml_data_struct)

        # Get Spectra number in specified range
        # total_spectra_count = get_num_spectra(mzml_data_struct)
        total_spectra_count = mzml_data_struct['data_dict']['total_spectra']
        logging.info("Processing {} Spectra.".format(total_spectra_count))
        logging.info("Reading, Merging and Formating Frames for mzML")

        with mzml_data_struct['writer'].run(id=1, instrument_configuration='IC1',
                                            start_time=mzml_data_struct['data_dict']['acq_date_time']):
            with mzml_data_struct['writer'].spectrum_list(count=total_spectra_count):
                # Process Frames
                mzml_data_struct['scan_loop_time1'] = time.time()
                mzml_data_struct['scan_index'] = 1

                if mzml_data_struct['data_dict']['PASEFMSMS_type8'] == 1:

                    mzml_data_struct['precursor_frames'] = mzml_data_struct['td'].conn.execute(
                        "SELECT * From Frames where MsMsType=0").fetchall()
                    # Check upper frame range
                    if mzml_data_struct['end_frame'] == -1 or mzml_data_struct['end_frame'] > \
                            mzml_data_struct['data_dict']['frame_count']:
                        mzml_data_struct['end_frame'] = mzml_data_struct['data_dict']['frame_count']

                    for precursor_frame in mzml_data_struct['precursor_frames']:
                        # Get Precursor Frame ID
                        mzml_data_struct['current_precursor'] = {}
                        mzml_data_struct['current_precursor']['id'] = precursor_frame[0]
                        mzml_data_struct['current_precursor']['start_time'] = precursor_frame[1] / 60

                        if mzml_data_struct['current_precursor']['id'] < mzml_data_struct['start_frame'] or \
                                mzml_data_struct['current_precursor']['id'] > mzml_data_struct['end_frame']:
                            continue

                        write_precursor_frame(mzml_data_struct)

                        # logging.debug(mzml_data_struct['scan_index'])
                        scan_progress(mzml_data_struct)

                        for precursor_data in get_precursor_list(mzml_data_struct):
                            mzml_data_struct['current_precursor']['data'] = precursor_data
                            write_pasef_msms_spectrum(mzml_data_struct)

                            scan_progress(mzml_data_struct)

                elif mzml_data_struct['data_dict']['PASEFMSMS_type9'] == 1:

                    mzml_data_struct['precursor_frames'] = mzml_data_struct['td'].conn.execute(
                        "SELECT * From Frames where MsMsType=0").fetchall()
                    mzml_data_struct['dia_frames'] = mzml_data_struct['td'].conn.execute(
                        "SELECT * From Frames where MsMsType=9").fetchall()
                    mzml_frames = mzml_data_struct['td'].conn.execute("SELECT * From Frames").fetchall()
                    # Check upper frame range
                    if mzml_data_struct['end_frame'] == -1 or mzml_data_struct['end_frame'] > \
                            mzml_data_struct['data_dict']['frame_count']:
                        mzml_data_struct['end_frame'] = mzml_data_struct['data_dict']['frame_count']

                    for frame in mzml_frames:
                        # for precursor_frame in mzml_data_struct['precursor_frames']:
                        # Get Precursor Frame ID

                        if frame[4] == 0:

                            # if mzml_data_struct['current_precursor']['id'] < mzml_data_struct['start_frame'] or mzml_data_struct['current_precursor']['id'] > mzml_data_struct['end_frame']:
                            #     continue

                            mzml_data_struct['current_precursor'] = {}
                            mzml_data_struct['current_precursor']['id'] = frame[0]
                            mzml_data_struct['current_precursor']['start_time'] = frame[1] / 60

                            write_precursor_frame(mzml_data_struct)

                            # logging.debug(mzml_data_struct['scan_index'])
                            scan_progress(mzml_data_struct)

                        elif frame[4] == 9:
                            window_group = mzml_data_struct['td'].conn.execute(
                                "SELECT WindowGroup From DiaFrameMsMsInfo where Frame={}".format(frame[0])).fetchone()[
                                0]
                            logging.debug(window_group)
                            windows = mzml_data_struct['td'].conn.execute(
                                "SELECT * From DiaFrameMsMsWindows where WindowGroup={}".format(
                                    window_group)).fetchall()
                            logging.debug(windows)

                            mzml_data_struct['current_dia_frame'] = {}
                            mzml_data_struct['current_dia_frame']['frame'] = frame
                            mzml_data_struct['current_dia_frame']['id'] = frame[0]
                            mzml_data_struct['current_dia_frame']['start_time'] = frame[1] / 60
                            mzml_data_struct['current_dia_frame']['window_group'] = window_group
                            mzml_data_struct['current_dia_frame']['windows'] = windows

                            for window in windows:
                                mzml_data_struct['current_dia_frame']['current_window'] = window

                                write_pasef_dia_spectrum(mzml_data_struct)
                                scan_progress(mzml_data_struct)

                    #            logging.debug(window)
                    #             #print(frame[0], window[1], window[2])
                    #             # print(frame[0], list(range(window[1], window[2])))
                    #             # result = mzml_data_struct['td'].extractProfileForFrame( frame[0], window[1], window[2])
                    #             # ms2_mz_array = np.asarray(result[0])
                    #             # ms2_i_array = np.asarray(result[1])
                    #             # m_array = np.asarray(
                    #             #     mzml_data_struct['td'].indexToMz(frame[0], list(range(window[1], window[2])))
                    #             # )

                    #             # result2 = np.asarray(result)
                    #             # print(  result2[np.argsort(result2)[-5:]])
                    #             # print( m_array )

                    #             result = mzml_data_struct['td'].extractCentroidedSpectrumForFrame( frame[0], window[1], window[2])
                    #             #print(result)
                    #             ms2_mz_array = np.asarray(result[0])
                    #             ms2_i_array = np.asarray(result[1])

                    #             msn_spectrum_id = "index={}".format(mzml_data_struct['scan_index'])

                    #             # parent_frame_string = "mz={}_width={} ".format(window[3],window[4])

                    #             # precursor_info["spectrum_reference"] = mzml_data_struct['current_precursor']['spectrum_id']

                    #             # # TODO find the correct metadata and apply it here properly
                    #             # precursor_info["activation"] = [
                    #             #         "CID",
                    #             #         {"collision energy": pasef_frame["CollisionEnergy"]}
                    #             #         ]

                    #             # precursor_info["isolation_window_args"] = dict()

                    #             # if precursor['Charge'] != None:
                    #             #     precursor_mz = precursor['MonoisotopicMz']
                    #             #     precursor_info["mz"] = precursor_mz
                    #             #     precursor_info["isolation_window_args"]["target"] = precursor_mz

                    #             #     isolation_offset = pasef_frame["IsolationMz"] - precursor_mz
                    #             #     isolation_width = pasef_frame["IsolationWidth"]/2.0

                    #             #     precursor_info["isolation_window_args"]["lower"] = isolation_width - isolation_offset
                    #             #     precursor_info["isolation_window_args"]["upper"] = isolation_width + isolation_offset

                    #             #     precursor_info["charge"]  = precursor['Charge']
                    #             # else:
                    #             #     precursor_mz = precursor['LargestPeakMz']
                    #             #     precursor_info["mz"] = precursor_mz
                    #             #     precursor_info["isolation_window_args"]["target"] = precursor_mz

                    #             #     isolation_offset = pasef_frame["IsolationMz"] - precursor_mz
                    #             #     isolation_width = pasef_frame["IsolationWidth"]/2.0

                    #             #     precursor_info["isolation_window_args"]["lower"] = isolation_width - isolation_offset
                    #             #     precursor_info["isolation_window_args"]["upper"] = isolation_width + isolation_offset

                    #             #     precursor_info["charge"]  = 2

                    #             mzml_data_struct['writer'].write_spectrum(
                    #                 ms2_mz_array,
                    #                 ms2_i_array,
                    #                 id=msn_spectrum_id,
                    #                 centroided=True,
                    #                 scan_start_time=mzml_data_struct['current_precursor']['start_time'],
                    #                 params=[
                    #                     {"ms level": 2},
                    #                     {"total ion current": ms2_i_array.sum()}
                    #                 ]
                    #             )

                    #             mzml_data_struct['scan_index'] += 1

                    # logging.debug(mzml_data_struct['scan_index'])
                    # scan_progress(mzml_data_struct)

                    # for precursor_data in get_precursor_list(mzml_data_struct):
                    #     mzml_data_struct['current_precursor']['data'] = precursor_data
                    #     write_pasef_msms_spectrum(mzml_data_struct)

                    #     scan_progress(mzml_data_struct)

    if total_spectra_count != mzml_data_struct['scan_index']-1:
        logging.info('Updating scan count...')
        update_spectra_count(
            args['outdir'], args['outfile'], total_spectra_count, mzml_data_struct['scan_index'] - 1)
    logging.info('Finished writing to .mzML file ' +
                 os.path.join(args['outdir'], args['outfile']) + '...')

    return


def main():
    """
    Main Function

    Parse arguments and start writing

    Parameters
    ----------
    None

    Returns
    -------
    None
    """
    # Argument Parser
    parser = argparse.ArgumentParser(description="tdf2mzml")

    parser.add_argument(
        "-i", "--input",
        action="store",
        type=str,
        metavar="input_file",
        required=True
    )

    parser.add_argument(
        "-o", "--output",
        action="store",
        type=str,
        metavar="output_file",
        required=False
    )

    parser.add_argument(
        "--precision",
        action="store",
        type=float,
        metavar="value",
        default=10.0,
    )

    parser.add_argument(
        "--ms1_threshold",
        action="store",
        type=float,
        metavar="value",
        default=100.0,
    )

    parser.add_argument(
        "--ms2_threshold",
        action="store",
        type=float,
        metavar="value",
        default=10,
    )

    parser.add_argument(
        "--ms2_nlargest",
        action="store",
        type=int,
        metavar="value",
        default=-1,
    )

    parser.add_argument(
        '-s',
        "--start_frame",
        action="store",
        type=int,
        metavar="value",
        default=-1,
    )

    parser.add_argument(
        '-e',
        "--end_frame",
        action="store",
        type=int,
        metavar="value",
        default=-1,
    )

    parser.add_argument(
        '--ms1_type',
        action="store",
        choices=['raw', 'profile', 'centroid'],
        metavar="value",
        default='centroid',
    )

    parser.add_argument(
        '--compression',
        action="store",
        choices=['zlib', 'none'],
        metavar="value",
        default='none',
    )

    parser.add_argument(
        "-d",
        "--debug",
        default=False,
        action="store_true",
        help="print verbose debug messages")

    args = parser.parse_args()

    if args.output == None:
        args.output = os.path.normpath(re.sub('d[/]?$', 'mzml', args.input))

    if args.debug:
        logging.basicConfig(level=logging.DEBUG)
    else:
        logging.basicConfig(level=logging.INFO)

    write_mzml(args)


if __name__ == "__main__":
    main()
