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
    mono_mzs = data.precursors.MonoisotopicMz.values
    average_mzs = data.precursors.AverageMz.values
    charges = data.precursors.Charge.values
    charges[np.flatnonzero(np.isnan(charges))] = 0
    charges = charges.astype(np.int64)
    rtinseconds = data.rt_values[data.precursors.Parent.values]
    intensities = data.precursors.Intensity.values
    mobilities = data.mobility_values[data.precursors.ScanNumber.values.astype(np.int64)]
    quad_mz_values = data.quad_mz_values[data.precursors.ScanNumber.values.astype(np.int64)]

    list_of_scan_dicts = []
    for index in alphatims.utils.progress_callback(range(1, data.precursor_max_index)):
        start = spectrum_indptr[index]
        end = spectrum_indptr[index + 1]
        base_peak_index = spectrum_intensity_values.index(max(spectrum_intensity_values))

        scan_dict = {'scan_number': 0,
                     'mz_array': data.mz_values[spectrum_tof_indcies[start:end]],
                     'intensity_array': spectrum_intensity_values[start:end],
                     #'mobility_array': scan['mobility_values'].values.tolist(),
                     'scan_type': 'MSn spectrum',
                     #'polarity': method_params['polarity'],
                     'polarity': 'positive scan',
                     'centroided': False,
                     'retention_time': float(rtinseconds[index - 1]),  # in min
                     'total_ion_current': sum(spectrum_intensity_values[start:end]),
                     'base_peak_mz': float(data.mz_values[spectrum_tof_indcies[start:end]][base_peak_index]),
                     'base_peak_intensity': float(spectrum_intensity_values[base_peak_index]),
                     'ms_level': 2,
                     'high_mz': float(max(data.mz_values[spectrum_tof_indcies[start:end]])),
                     'low_mz': float(min(data.mz_values[spectrum_tof_indcies[start:end]])),
                     'target_mz': average_mzs[index - 1],
                     'isolation_lower_offset': float(quad_mz_values[index - 1][0]),
                     'isolation_upper_offset': float(quad_mz_values[index - 1][1]),
                     'selected_ion_mz': float(mono_mzs[index - 1]),
                     'selected_ion_intensity': float(intensities[index - 1]),
                     'selected_ion_mobility': float(mobilities[index - 1]),
                     'charge_state': int(charges[index - 1]),
                     'collision_energy': 20  # hard coded for now
                     }
        list_of_scan_dicts.append(scan_dict)
    return list_of_scan_dicts


if __name__ == '__main__':
    data = alphatims.bruker.TimsTOF('F:\\code\\alphatims_test_data\\pen12_ms2_1_36_1_400.d')
    save_ms2(data, '', '')
