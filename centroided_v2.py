import alphatims.bruker
import psims.mzml.components
from psims.mzml import MzMLWriter
from psims.xml import CVParam, UserParam
from lxml import etree as et
import pandas as pd
import numpy as np
import os
from collections.abc import Iterable, Mapping


# Read in bruker .d/.tdf files into dataframe using AlphaTIMS.
def bruker_to_df(filename):
    return alphatims.bruker.TimsTOF(filename)


def centroid(data):
    precursor_order = np.argsort(data.precursor_indices)
    print('precursor order', precursor_order)

    precursor_offsets = np.empty(data.precursor_max_index + 1, dtype=np.int64)
    print('precursor offsets', precursor_offsets)
    precursor_offsets[0] = 0
    print('precursor offsets', precursor_offsets)
    precursor_offsets[1:-1] = np.flatnonzero(np.diff(data.precursor_indices[precursor_order]) > 0) + 1
    print('precursor offsets', precursor_offsets)
    precursor_offsets[-1] = len(precursor_order)
    print('precursor offsets', precursor_offsets)
    print('len precursor offsets', len(precursor_offsets))

    offset = precursor_offsets[1]
    print('offset', offset)
    offsets = precursor_order[offset:]
    print('offsets', offsets)

    counts = np.empty(len(offsets) + 1, dtype=np.int)
    print('counts', counts)
    counts[0] = 0
    print('counts', counts)
    counts[1:] = np.cumsum(data.quad_indptr[offsets + 1] - data.quad_indptr[offsets])
    print('counts', counts)

    spectrum_indptr = np.empty(data.precursor_max_index + 1, dtype=np.int64)
    print('spectrum_indptr', spectrum_indptr)
    spectrum_indptr[1:] = counts[precursor_offsets[1:] - precursor_offsets[1]]
    print('spectrum_indptr', spectrum_indptr)
    spectrum_indptr[0] = 0
    print('spectrum_indptr', spectrum_indptr)

    spectrum_counts = np.zeros_like(spectrum_indptr)
    print('spectrum_counts', spectrum_counts)
    spectrum_tof_indices = np.empty(spectrum_indptr[-1], dtype=np.uint32)
    print('spectrum tof indices', spectrum_tof_indices)
    spectrum_intensity_values = np.empty(len(spectrum_tof_indices), dtype=np.float64)
    print('spectrum_intensity_values', spectrum_intensity_values)

    # set_precursor()
    # centroid_spectra()
    # filter_spectra_by_abundant_peaks()




if __name__ == '__main__':
    # Read in example .d file and convert to dataframe.
    tdf_file = 'F:\\code\\alphatims_test_data\\pen12_ms2_1_36_1_400.d'
    data = bruker_to_df(tdf_file)

    #print(type(data))
    #print(type(data[:, :, :, :, :]['push_indices']))
    #iter(data[:, :, :, :, :])
    #print(isinstance(data[:, :, :, :, :], Iterable))
    #print(isinstance(data[:, :, :, :, :], Mapping))

    # Testing centroiding.
    #alphatims.bruker.centroid_spectra(data[:, :, :, :, :])
    '''print(alphatims.bruker.centroid_spectra(index=1,
                                            #spectrum_indptr=data[],
                                            #spectrum_counts=,
                                            spectrum_tof_indices=data[:, :, :, :, :]['tof_indices'],
                                            spectrum_intensity_values=data[:, :, :, :, :]['intensity_values'],
                                            window_size=5))'''

    # check out index_precursors prints
    #print(np.argsort(data.precursor_indices))
    centroid(data)