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
    #print(data.precursor_indices[:100])
    precursor_order = np.argsort(data.precursor_indices)
    print(precursor_order)
    print(len(precursor_order))
    print(type(precursor_order))
    # should use scan indices instead of frame indices
    parent_order = np.argsort(data[:, :, 0]['scan_indices'].to_numpy())
    print(parent_order)
    print(type(parent_order))

    precursor_offsets = np.empty(data.precursor_max_index + 1, dtype=np.int64)
    precursor_offsets[0] = 0
    precursor_offsets[1:-1] = np.flatnonzero(np.diff(data.precursor_indices[precursor_order]) > 0) + 1
    print(len(np.flatnonzero(np.diff(data.precursor_indices[precursor_order]) > 0) + 1))
    print(len(precursor_order))
    precursor_offsets[-1] = len(precursor_order)

    parent_offsets = np.empty(len(list(data[:, :, 0]['scan_indices'])), dtype=np.int64)
    parent_offsets[0] = 0
    parent_offsets[1:-1] = np.flatnonzero(np.diff(data[:, :, 0]['scan_indices'].to_numpy()[parent_order]) > 0) + 1
    print(len(np.flatnonzero(np.diff(data[:, :, 0]['scan_indices'].to_numpy()[parent_order]) > 0) + 1))
    print(len(parent_order))
    parent_offsets[-1] = len(parent_order)

    print(precursor_offsets)
    print(parent_offsets)

    offset = precursor_offsets[1]
    offsets = precursor_order[offset:]

    counts = np.empty(len(offsets) + 1, dtype=np.int)
    counts[0] = 0
    counts[1:] = np.cumsum(data.quad_indptr[offsets + 1] - data.quad_indptr[offsets])

    spectrum_indptr = np.empty(data.precursor_max_index + 1, dtype=np.int64)
    spectrum_indptr[1:] = counts[precursor_offsets[1:] - precursor_offsets[1]]
    spectrum_indptr[0] = 0

    spectrum_counts = np.zeros_like(spectrum_indptr)
    spectrum_tof_indices = np.empty(spectrum_indptr[-1], dtype=np.uint32)
    spectrum_intensity_values = np.empty(len(spectrum_tof_indices), dtype=np.float64)

    # instead of 1, should use frame_num?
    #alphatims.bruker.centroid_spectra(1, spectrum_indptr, spectrum_counts, spectrum_tof_indices, spectrum_intensity_values, centroiding_window=5)

    print(spectrum_indptr)
    print(spectrum_counts)
    print(spectrum_tof_indices)
    print(spectrum_intensity_values)


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