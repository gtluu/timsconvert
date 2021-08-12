import alphatims.bruker
import alphatims.utils
import psims.mzml.components
from psims.mzml import MzMLWriter
from psims.xml import CVParam, UserParam
from lxml import etree as et
import pandas as pd
import numpy as np
import os


# need set_precursor, centroid_spectra, filter_spectra_by_abundant_peaks
@alphatims.utils.pjit(signature_or_function="void(i8,i8[:],i8[:],i8[:],u4[:],u2[:],u4[:],f8[:],i8[:],i8[:])")
def set_precursor(precursor_index: int, offset_order: np.ndarray, precursor_offsets: np.ndarray,
                  quad_indptr: np.ndarray, tof_indices: np.ndarray, intensities: np.ndarray,
                  spectrum_tof_indices: np.ndarray, spectrum_intensity_values: np.ndarray, spectrum_indptr: np.ndarray,
                  spectrum_counts: np.ndarray,) -> None:
    offset = spectrum_indptr[precursor_index]
    precursor_offset_lower = precursor_offsets[precursor_index]
    precursor_offset_upper = precursor_offsets[precursor_index + 1]
    selected_offsets = offset_order[precursor_offset_lower: precursor_offset_upper]
    starts = quad_indptr[selected_offsets]
    ends = quad_indptr[selected_offsets + 1]
    offset_index = offset
    for start, end in zip(starts, ends):
        spectrum_tof_indices[offset_index: offset_index + end - start] = tof_indices[start: end]
        spectrum_intensity_values[offset_index: offset_index + end - start] = intensities[start: end]
        offset_index += end - start
    offset_end = spectrum_indptr[precursor_index + 1]
    order = np.argsort(spectrum_tof_indices[offset: offset_end])
    current_index = offset - 1
    previous_tof_index = -1
    for tof_index, intensity in zip(spectrum_tof_indices[offset: offset_end][order], spectrum_intensity_values[offset: offset_end][order],):
        if tof_index != previous_tof_index:
            current_index += 1
            spectrum_tof_indices[current_index] = tof_index
            spectrum_intensity_values[current_index] = intensity
            previous_tof_index = tof_index
        else:
            spectrum_intensity_values[current_index] += intensity
    spectrum_tof_indices[current_index + 1: offset_end] = 0
    spectrum_intensity_values[current_index + 1: offset_end] = 0
    spectrum_counts[precursor_index] = current_index + 1 - offset


@alphatims.utils.pjit
def centroid_spectra(index: int, spectrum_indptr: np.ndarray, spectrum_counts: np.ndarray,
                     spectrum_tof_indices: np.ndarray, spectrum_intensity_values: np.ndarray, window_size: int,):
    start = spectrum_indptr[index]
    end = start + spectrum_counts[index]
    if start == end:
        return
    mzs = spectrum_tof_indices[start: end]
    ints = spectrum_intensity_values[start: end]
    smooth_ints = ints.copy()
    for i, self_mz in enumerate(mzs[:-1]):
        for j in range(i + 1, len(mzs)):
            other_mz = mzs[j]
            diff = other_mz - self_mz + 1
            if diff >= window_size:
                break
            smooth_ints[i] += ints[j] / diff
            smooth_ints[j] += ints[i] / diff
    pre_apex = True
    maxima = [mzs[0]]
    intensities = [ints[0]]
    for i, self_mz in enumerate(mzs[1:], 1):
        if self_mz > mzs[i - 1] + window_size:
            maxima.append(mzs[i])
            intensities.append(0)
            pre_apex = True
        elif pre_apex:
            if smooth_ints[i] < smooth_ints[i - 1]:
                pre_apex = False
                maxima[-1] = mzs[i - 1]
        elif smooth_ints[i] > smooth_ints[i - 1]:
            maxima.append(mzs[i])
            intensities.append(0)
            pre_apex = True
        intensities[-1] += ints[i]
    spectrum_tof_indices[start: start + len(maxima)] = np.array(maxima,dtype=spectrum_tof_indices.dtype)
    spectrum_intensity_values[start: start + len(maxima)] = np.array(intensities,dtype=spectrum_intensity_values.dtype)
    spectrum_counts[index] = len(maxima)





def index_precursors(data, centroiding_window: int = 0, keep_n_most_abundant_peaks: int = -1,) -> tuple:
    precursor_order = np.argsort(data.precursor_indices)
    precursor_offsets = np.empty(data.precursor_max_index + 1, dtype=np.int64)
    precursor_offsets[0] = 0
    precursor_offsets[1:-1] = np.flatnonzero(np.diff(data.precursor_indices[precursor_order]) > 0) + 1
    precursor_offsets[-1] = len(precursor_order)
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

    set_precursor(range(1, data.precursor_max_index),
                  precursor_order,
                  offsets,
                  data.quad_indptr,
                  data.tof_indices,
                  data.intensity_values,
                  spectrum_tof_indices,
                  spectrum_intensity_values,
                  spectrum_indptr,
                  spectrum_counts,)

    if centroiding_window > 0:
        centroid_spectra(range(1, data.precursor_max_index),
                         spectrum_indptr,
                         spectrum_counts,
                         spectrum_tof_indices,
                         spectrum_intensity_values,
                         centroiding_window,)

    '''if keep_n_most_abundant_peaks > -1:
        filter_spectra_by_abundant_peaks(range(1, data.precursor_max_index),
                                         spectrum_indptr,
                                         spectrum_counts,
                                         spectrum_tof_indices,
                                         spectrum_intensity_values,
                                         keep_n_most_abundant_peaks,)'''

    new_spectrum_indptr = np.empty_like(spectrum_counts)
    new_spectrum_indptr[1:] = np.cumsum(spectrum_counts[:-1])
    new_spectrum_indptr[0] = 0

    trimmed_spectrum_tof_indices = np.empty(new_spectrum_indptr[-1], dtype=np.uint32)
    trimmed_spectrum_intensity_values = np.empty(len(trimmed_spectrum_tof_indices), dtype=np.float64)
    spectrum_intensity_values

    '''trim_spectra(range(1, data.precursor_max_index),
                 spectrum_tof_indices,
                 spectrum_intensity_values,
                 spectrum_indptr,
                 trimmed_spectrum_tof_indices,
                 trimmed_spectrum_intensity_values,
                 new_spectrum_indptr,)'''

    return (new_spectrum_indptr, trimmed_spectrum_tof_indices, trimmed_spectrum_intensity_values)


if __name__ == '__main__':
    data = alphatims.bruker.TimsTOF('F:\\code\\alphatims_test_data\\pen12_ms2_1_36_1_400.d')
    index_precursors(data)
