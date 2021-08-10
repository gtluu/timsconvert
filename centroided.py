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


if __name__ == '__main__':
    # Read in example .d file and convert to dataframe.
    tdf_file = 'F:\\code\\alphatims_test_data\\pen12_ms2_1_36_1_400.d'
    data = bruker_to_df(tdf_file)

    #print(type(data))
    #print(type(data[:, :, :, :, :]['push_indices']))
    iter(data[:, :, :, :, :])
    print(isinstance(data[:, :, :, :, :], Iterable))
    print(isinstance(data[:, :, :, :, :], Mapping))

    # Testing centroiding.
    #alphatims.bruker.centroid_spectra(data[:, :, :, :, :])
    print(alphatims.bruker.centroid_spectra(index=1,
                                            #spectrum_indptr=data[],
                                            #spectrum_counts=,
                                            spectrum_tof_indices=data[:, :, :, :, :]['tof_indices'],
                                            spectrum_intensity_values=data[:, :, :, :, :]['intensity_values'],
                                            window_size=5))
