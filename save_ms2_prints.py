import alphatims.bruker
import alphatims.utils
import psims.mzml.components
from psims.mzml import MzMLWriter
from psims.xml import CVParam, UserParam
from lxml import etree as et
import pandas as pd
import numpy as np
import os


def save_ms2(data, directory, filename, overwrite=False, centroiding_window=5, keep_n_most_abundant_peaks=-1):

    full_filename = os.path.join(directory, filename)

    if data.acquisition_mode != 'ddaPASEF':
        print(f'File {data.bruker_d_folder_name} is not a ddaPASEF file, nothing to do.')
        return full_filename
    if os.path.exists(full_filename):
        if not overwrite:
            print(f'File {full_filename} already exists, nothing to do.')
            return full_filename

    print(f'Indexing spectra of {data.bruker_d_folder_name}...')
    (spectrum_indptr, spectrum_tof_indcies, spectrum_intensity_values) = data.index_precursors(centroiding_window=centroiding_window, keep_n_most_abundant_peaks=keep_n_most_abundant_peaks)
    print('spectrum indptr')
    print(spectrum_indptr)
    print('spectrum tof indices')
    print(spectrum_tof_indcies)
    print('spectrum intensity values')
    print(spectrum_intensity_values)
    mono_mzs = data.precursors.MonoisotopicMz.values
    print('mono mzs')
    print(mono_mzs)
    average_mzs = data.precursors.AverageMz.values
    print('average mzs')
    print(average_mzs)
    charges = data.precursors.Charge.values
    charges[np.flatnonzero(np.isnan(charges))] = 0
    charges = charges.astype(np.int64)
    print('charges')
    print(charges)
    rtinseconds = data.rt_values[data.precursors.Parent.values]
    print('rt in seconds')
    print(rtinseconds)
    intensities = data.precursors.Intensity.values
    print('intensities')
    print(intensities)
    mobilities = data.mobility_values[data.precursors.ScanNumber.values.astype(np.int64)]
    print('mobilities')
    print(mobilities)
    print('precursor max index')
    print(data.precursor_max_index)
    print(data.precursors.ScanNumber.values)
    print(data.quad_mz_values[data.precursors.ScanNumber.values.astype(np.int64)])

    for index in alphatims.utils.progress_callback(range(1, data.precursor_max_index)):
        start = spectrum_indptr[index]
        end = spectrum_indptr[index + 1]


if __name__ == '__main__':
    data = alphatims.bruker.TimsTOF('F:\\code\\alphatims_test_data\\pen12_ms2_1_36_1_400.d')
    save_ms2(data, '', '')
