from timsconvert.parse import parse_lcms_baf, parse_lcms_tsf, parse_lcms_tdf
from timsconvert.classes import TimsconvertBafData, TimsconvertTsfData, TimsconvertTdfData
from timsconvert.timestamp import get_iso8601_timestamp
import os
import sys
import logging
import numpy as np
from pyimzml.ImzMLWriter import ImzMLWriter
from pyimzml.compression import NoCompression, ZlibCompression
from pyTDFSDK.util import get_encoding_dtype


def write_nanodesi_chunk_to_imzml(data, imzml_file, frame_start, frame_stop, mode, exclude_mobility, profile_bins,
                                  mz_encoding, intensity_encoding, mobility_encoding, x_coord):
    # Parse and write TSF data.
    if isinstance(data, TimsconvertTsfData):
        parent_scans, product_scans = parse_lcms_tsf(data,
                                                     frame_start,
                                                     frame_stop,
                                                     mode,
                                                     False,
                                                     profile_bins,
                                                     mz_encoding,
                                                     intensity_encoding)
        for scan in parent_scans:
            coord = (x_coord, scan.frame)
            imzml_file.addSpectrum(scan.mz_array,
                                   scan.intensity_array,
                                   coord)
    # Parse and write TDF data.
    elif isinstance(data, TimsconvertTdfData):
        parent_scans, product_scans = parse_lcms_tdf(data,
                                                     frame_start,
                                                     frame_stop,
                                                     mode,
                                                     False,
                                                     exclude_mobility,
                                                     profile_bins,
                                                     mz_encoding,
                                                     intensity_encoding,
                                                     mobility_encoding)
        if mode == 'profile':
            exclude_mobility = True
        if not exclude_mobility:
            for scan in parent_scans:
                coord = (x_coord, scan.frame)
                imzml_file.addSpectrum(scan.mz_array,
                                       scan.intensity_array,
                                       coord,
                                       mobilities=scan.mobility_array)
        elif exclude_mobility:
            for scan in parent_scans:
                coord = (x_coord, scan.frame)
                imzml_file.addSpectrum(scan.mz_array,
                                       scan.intensity_array,
                                       coord)
    # Parse and write BAF data.
    elif isinstance(data, TimsconvertBafData):
        parent_scans, product_scans = parse_lcms_baf(data,
                                                     frame_start,
                                                     frame_stop,
                                                     mode,
                                                     False,
                                                     profile_bins,
                                                     mz_encoding,
                                                     intensity_encoding)
        for scan in parent_scans:
            coord = (x_coord, scan.frame)
            imzml_file.addSpectrum(scan.mz_array,
                                   scan.intensity_array,
                                   coord)


def write_nanodesi_imzml(data_dict, outdir, outfile, mode, exclude_mobility, profile_bins, imzml_mode, mz_encoding,
                         intensity_encoding, mobility_encoding, compression, line_scan_mode, scans_per_line,
                         chunk_size=10):
    # Set polarity for run in imzML.
    polarity = []
    for x_coord, data in data_dict.items():
        polarity += list(set(data.analysis['Frames']['Polarity'].values.tolist()))
    polarity = list(set(polarity))
    if len(polarity) == 1 and polarity[0] == '+':
        polarity = 'positive'
    elif len(polarity) == 1 and polarity[0] == '-':
        polarity = 'negative'
    else:
        polarity = None

    # Get compression type object.
    if compression == 'zlib':
        compression_object = ZlibCompression()
    elif compression == 'none':
        compression_object = NoCompression()

    # Determine number of scans per line depending on line scan mode.
    if line_scan_mode == 'mean':
        scans_per_line = []
        for x_coord, data in data_dict.items():
            if isinstance(data, TimsconvertBafData):
                frames_key = 'Spectra'
            elif isinstance(data, TimsconvertTsfData) or isinstance(data, TimsconvertTdfData):
                frames_key = 'Frames'
            scans_per_line.append(data.analysis[frames_key].shape[0])
        scans_per_line = int(np.floor(np.mean(scans_per_line)))
    elif line_scan_mode == 'minimum':
        scans_per_line = []
        for x_coord, data in data_dict.items():
            if isinstance(data, TimsconvertBafData):
                frames_key = 'Spectra'
            elif isinstance(data, TimsconvertTsfData) or isinstance(data, TimsconvertTdfData):
                frames_key = 'Frames'
            scans_per_line.append(data.analysis[frames_key].shape[0])
        scans_per_line = int(np.min(scans_per_line))
    elif line_scan_mode == 'maximum':
        scans_per_line = []
        for x_coord, data in data_dict.items():
            if isinstance(data, TimsconvertBafData):
                frames_key = 'Spectra'
            elif isinstance(data, TimsconvertTsfData) or isinstance(data, TimsconvertTdfData):
                frames_key = 'Frames'
            scans_per_line.append(data.analysis[frames_key].shape[0])
        scans_per_line = int(np.max(scans_per_line))
    # No change if line scan mode is set to "user_defined", user defined value for scans_per_line was already passed as
    # parameter.

    # TODO: Nearest Neighbor Interpolation would go here if it is still needed.

    # Determine schema types of each data file and initialize imzML writer.
    schema_types = []
    for x_coord, data in data_dict.items():
        if isinstance(data, TimsconvertBafData):
            metadata_key = 'Properties'
        elif isinstance(data, TimsconvertTsfData) or isinstance(data, TimsconvertTdfData):
            metadata_key = 'GlobalMetadata'
        schema_types.append(data.analysis[metadata_key]['SchemaType'])
    schema_types = list(set(schema_types))
    if len(schema_types) == 1 and schema_types[0] == 'TDF':
        if mode == 'profile':
            exclude_mobility = True
            logging.info(
                get_iso8601_timestamp() + ':' + 'Export of ion mobility data is not supported for profile mode data...')
            logging.info(get_iso8601_timestamp() + ':' + 'Exporting without ion mobility data...')
        if not exclude_mobility:
            writer = ImzMLWriter(os.path.join(outdir, outfile),
                                 polarity=polarity,
                                 mode=imzml_mode,
                                 spec_type=mode,
                                 mz_dtype=get_encoding_dtype(mz_encoding),
                                 intensity_dtype=get_encoding_dtype(intensity_encoding),
                                 mobility_dtype=get_encoding_dtype(mobility_encoding),
                                 mz_compression=compression_object,
                                 intensity_compression=compression_object,
                                 mobility_compression=compression_object,
                                 include_mobility=True)
        elif exclude_mobility:
            writer = ImzMLWriter(os.path.join(outdir, outfile),
                                 polarity=polarity,
                                 mode=imzml_mode,
                                 spec_type=mode,
                                 mz_dtype=get_encoding_dtype(mz_encoding),
                                 intensity_dtype=get_encoding_dtype(intensity_encoding),
                                 mz_compression=compression_object,
                                 intensity_compression=compression_object,
                                 include_mobility=False)
    # If more than one schema are detected and/or a non-TDF file is included, prevent ion mobility array export.
    else:
        writer = ImzMLWriter(os.path.join(outdir, outfile),
                             polarity=polarity,
                             mode=imzml_mode,
                             spec_type=mode,
                             mz_dtype=get_encoding_dtype(mz_encoding),
                             intensity_dtype=get_encoding_dtype(intensity_encoding),
                             mz_compression=compression_object,
                             intensity_compression=compression_object,
                             include_mobility=False)

    with writer as imzml_file:
        for x_coord, data in data_dict.items():
            chunk = 0
            frames = data.analysis['Frames']['Id'].to_list()[:scans_per_line]
            while chunk + chunk_size + 1 <= len(frames):
                chunk_list = []
                for i, j in zip(frames[chunk:chunk + chunk_size], frames[chunk + 1: chunk + chunk_size + 1]):
                    chunk_list.append((int(i), int(j)))
                logging.info(get_iso8601_timestamp() +
                             ':' +
                             'Parsing and writing Frame ' +
                             str(chunk_list[0][0]) +
                             ' from ' +
                             data.analysis['GlobalMetadata']['SampleName'] +
                             '...')
                for frame_start, frame_stop in chunk_list:
                    write_nanodesi_chunk_to_imzml(data,
                                                  imzml_file,
                                                  frame_start,
                                                  frame_stop,
                                                  mode,
                                                  exclude_mobility,
                                                  profile_bins,
                                                  mz_encoding,
                                                  intensity_encoding,
                                                  mobility_encoding,
                                                  x_coord)
                    sys.stdout.write(get_iso8601_timestamp() +
                                     ':' +
                                     data.source_file.replace('/', '\\') +
                                     ':Progress:' +
                                     str(round((frame_start / data.analysis['Frames'].shape[0]) * 100)) +
                                     '%\n')
                chunk += chunk_size
            else:
                chunk_list = []
                for i, j in zip(frames[chunk:-1], frames[chunk + 1:]):
                    chunk_list.append((int(i), int(j)))
                chunk_list.append((j, len(frames) + 1))
                logging.info(get_iso8601_timestamp() +
                             ':' +
                             'Parsing and writing Frame ' +
                             str(chunk_list[0][0]) +
                             ' from ' +
                             data.analysis['GlobalMetadata']['SampleName'] +
                             '...')
                for frame_start, frame_stop in chunk_list:
                    write_nanodesi_chunk_to_imzml(data,
                                                  imzml_file,
                                                  frame_start,
                                                  frame_stop,
                                                  mode,
                                                  exclude_mobility,
                                                  profile_bins,
                                                  mz_encoding,
                                                  intensity_encoding,
                                                  mobility_encoding,
                                                  x_coord)
                    sys.stdout.write(get_iso8601_timestamp() +
                                     ':' +
                                     data.source_file.replace('/', '\\') +
                                     ':Progress:100%\n')
    logging.info(
        get_iso8601_timestamp() + ':' + 'Finished writing to .imzML file ' + os.path.join(outdir, outfile) + '...')
