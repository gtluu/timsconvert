from pyimzml.ImzMLWriter import ImzMLWriter
from timsconvert.parse_maldi import *


def write_maldi_ims_chunk_to_imzml(data, imzml_file, frame_start, frame_stop, mode, exclude_mobility, profile_bins,
                                   encoding):
    # Parse TSF data.
    if data.meta_data['SchemaType'] == 'TSF':
        list_of_scan_dicts = parse_maldi_tsf(data, frame_start, frame_stop, mode, False, profile_bins, encoding)
    # Parse TDF data.
    elif data.meta_data['SchemaType'] == 'TDF':
        list_of_scan_dicts = parse_maldi_tdf(data, frame_start, frame_stop, mode, False, exclude_mobility, profile_bins,
                                             encoding)
    for scan_dict in list_of_scan_dicts:
        imzml_file.addSpectrum(scan_dict['mz_array'],
                               scan_dict['intensity_array'],
                               scan_dict['coord'])


def write_maldi_ims_imzml(data, outdir, outfile, mode, exclude_mobility, profile_bins, imzml_mode, encoding,
                          chunk_size):
    # Set polarity for run in imzML.
    polarity = list(set(data.frames['Polarity'].values.tolist()))
    if len(polarity) == 1:
        polarity = polarity[0]
        if polarity == '+':
            polarity = 'positive'
        elif polarity == '-':
            polarity = 'negative'
        else:
            polarity = None
    else:
        polarity = None

    if data.meta_data['SchemaType'] == 'TSF' and mode == 'raw':
        logging.info(get_timestamp() + ':' + 'TSF file detected. Only export in profile or centroid mode are '
                                             'supported. Defaulting to centroid mode.')

    # Set centroided status.
    if mode == 'profile':
        centroided = False
    elif mode == 'centroid' or mode == 'raw':
        centroided = True

    writer = ImzMLWriter(os.path.join(outdir, outfile),
                         polarity=polarity,
                         mode=imzml_mode,
                         spec_type=centroided)

    logging.info(get_timestamp() + ':' + 'Writing to .imzML file ' + os.path.join(outdir, outfile) + '...')
    with writer as imzml_file:
        chunk = 0
        frames = list(data.frames['Id'].values)
        while chunk + chunk_size + 1 <= len(frames):
            chunk_list = []
            for i, j in zip(frames[chunk:chunk + chunk_size], frames[chunk + 1: chunk + chunk_size + 1]):
                chunk_list.append((int(i), int(j)))
            logging.info(get_timestamp() + ':' + 'Parsing and writing Frame ' + ':' + str(chunk_list[0][0]) + '...')
            for frame_start, frame_stop in chunk_list:
                write_maldi_ims_chunk_to_imzml(data, imzml_file, frame_start, frame_stop, mode, exclude_mobility,
                                               profile_bins, encoding)
            chunk += chunk_size
        else:
            chunk_list = []
            for i, j in zip(frames[chunk:-1], frames[chunk + 1:]):
                chunk_list.append((int(i), int(j)))
            chunk_list.append((j, data.frames.shape[0] + 1))
            logging.info(get_timestamp() + ':' + 'Parsing and writing Frame ' + ':' + str(chunk_list[0][0]) + '...')
            for frame_start, frame_stop in chunk_list:
                write_maldi_ims_chunk_to_imzml(data, imzml_file, frame_start, frame_stop, mode, exclude_mobility,
                                               profile_bins, encoding)
    logging.info(get_timestamp() + ':' + 'Finished writing to .mzML file ' + os.path.join(outdir, outfile) + '...')


if __name__ == '__main__':
    logger = logging.getLogger(__name__)
