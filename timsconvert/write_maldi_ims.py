from pyimzml.ImzMLWriter import ImzMLWriter
from timsconvert.parse_maldi import *


def write_maldi_ims_chunk_to_imzml(data, imzml_file, i, j, mode, encoding):
    # Parse TSF data.
    if data.meta_data['SchemaType'] == 'TSF':
        list_of_scan_dicts = parse_maldi_tsf(data, i, j, mode, False, encoding)
    # Parse TDF data.
    elif data.meta_data['SchemaType'] == 'TDF':
        list_of_scan_dicts = parse_maldi_tdf(data, i, j, 'frame', mode, False, encoding)
    for scan_dict in list_of_scan_dicts:
        imzml_file.addSpectrum(scan_dict['mz_array'],
                               scan_dict['intensity_array'],
                               scan_dict['coord'])


def write_maldi_ims_imzml(data, outdir, outfile, mode, imzml_mode, encoding, chunk_size):
    # Set polarity for run in imzML.
    polarity = list(set(data.frames['Polarity'].values.toolist()))
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
            for i, j in chunk_list:
                write_maldi_ims_chunk_to_imzml(data, imzml_file, i, j, mode, encoding)
            chunk += chunk_size
        else:
            chunk_list = []
            for i, j in zip(frames[chunk:-1], frames[chunk + 1:]):
                chunk_list.append((int(i), int(j)))
            chunk_list.append((chunk_list[len(chunk_list) - 1][1], len(frames)))
            logging.info(get_timestamp() + ':' + 'Parsing and writing Frame ' + ':' + str(chunk_list[0][0]) + '...')
            for i, j in chunk_list:
                write_maldi_ims_chunk_to_imzml(data, imzml_file, i, j, mode, encoding)


if __name__ == '__main__':
    logger = logging.getLogger(__name__)
