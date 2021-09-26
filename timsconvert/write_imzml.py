from pyimzml.ImzMLWriter import ImzMLWriter
from .data_parsing import *


def write_maldi_ims_imzml(tsf_data, outdir, outfile, mode='processed', centroid=True):
    list_of_scan_dicts = parse_maldi_tsf(tsf_data, centroid)

    polarity = list(set(tsf_data.frames['Polarity'].values.tolist()))
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

    writer = ImzMLWriter(os.path.join(outdir, outfile),
                         polarity=polarity,
                         mode=mode,
                         spec_type=centroid)

    with writer as imzml_file:
        for scan_dict in list_of_scan_dicts:
            imzml_file.addSpectrum(scan_dict['mz_array'],
                                   scan_dict['intensity_array'],
                                   scan_dict['coord'])
