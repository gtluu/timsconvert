import alphatims.bruker
import alphatims.utils
import psims.mzml.components
from psims.mzml import MzMLWriter
from psims.xml import CVParam, UserParam
from lxml import etree as et
import pandas as pd
import numpy as np
import os
import itertools


# Read in Bruker .d/.tdf files into dataframe using AlphaTIMS.
def bruker_to_df(filename):
    return alphatims.bruker.TimsTOF(filename)


# Function for itertools.groupby() to sort dictionaries based on key.
def key_func(k):
    return k['parent_frame']


# Check method for PASEF NumRampsPerCycle
# From microTOFQImpacTemAcquisition.method XML file.
def get_method_info(input_filename):
    # Get method file path.
    for dirpath, dirnames, filenames in os.walk(input_filename):
        for dirname in dirnames:
            if os.path.splitext(dirname)[1].lower() == '.m':
                method_file = os.path.join(dirpath, dirname, 'microTOFQImpacTemAcquisition.method')

    # Open XML file.
    method_data = et.parse(method_file).getroot()
    method_params = {}
    # Get get number of ramps per cycle.
    method_params['num_ramps_per_cycle'] = int(method_data.xpath('//para_int[@permname="MSMS_Pasef_NumRampsPerCycle"]')[0].attrib['value'])
    # polarity is hardcoded for now, need to find where to get that parameter
    method_params['polarity'] = 'positive scan'
    return method_params


# will need to figure out how to centroid data later; only outputs profile for now
def parse_ms1_scan(scan, method_params, centroided=False):
    base_peak_row = scan.sort_values(by='intensity_values', ascending=False).iloc[0]
    scan_dict = {'scan_number': 0,
                 'mz_array': scan['mz_values'].values.tolist(),
                 'intensity_array': scan['intensity_values'].values.tolist(),
                 'mobility_array': scan['mobility_values'].values.tolist(),
                 'scan_type': 'MS1 spectrum',
                 'polarity': method_params['polarity'],
                 'centroided': centroided,
                 'retention_time': float(list(set(scan['rt_values_min'].values.tolist()))[0]),
                 'total_ion_current': sum(scan['intensity_values'].values.tolist()),
                 'base_peak_mz': float(base_peak_row['mz_values']),
                 'base_peak_intensity': float(base_peak_row['intensity_values']),
                 'ms_level': 1,
                 'high_mz': float(max(scan['mz_values'].values.tolist())),
                 'low_mz': float(min(scan['mz_values'].values.tolist())),
                 'parent_frame': 0}
    return scan_dict


# Get all MS2 scans.
def parse_ms2_scan(raw_data, method_params, overwrite=False, centroided=True,
                   centroiding_window=5, keep_n_most_abundant_peaks=-1):
    # Check to make sure timsTOF object is valid.
    if raw_data.acquisition_mode != 'ddaPASEF':
        return None

    (spectrum_indptr,
     spectrum_tof_indices,
     spectrum_intensity_values) = raw_data.index_precursors(centroiding_window=centroiding_window,
                                                            keep_n_most_abundant_peaks=keep_n_most_abundant_peaks)
    mono_mzs = raw_data.precursors.MonoisotopicMz.values
    average_mzs = raw_data.precursors.AverageMz.values
    charges = raw_data.precursors.Charge.values
    charges[np.flatnonzero(np.isnan(charges))] = 0
    charges = charges.astype(np.int64)
    rtinseconds = raw_data.rt_values[raw_data.precursors.Parent.values]
    intensities = raw_data.precursors.Intensity.values
    mobilities = raw_data.mobility_values[raw_data.precursors.ScanNumber.values.astype(np.int64)]
    quad_mz_values = raw_data.quad_mz_values[raw_data.precursors.ScanNumber.values.astype(np.int64)]
    parent_frames = raw_data.precursors.Parent.values

    list_of_scan_dicts = []
    for index in alphatims.utils.progress_callback(range(1, raw_data.precursor_max_index)):
        start = spectrum_indptr[index]
        end = spectrum_indptr[index + 1]

        # Remove MS2 scan if empty.
        if raw_data.mz_values[spectrum_tof_indices[start:end]].size != 0 or spectrum_intensity_values[start:end] != 0:
            if not np.isnan(mono_mzs[index - 1]):
                scan_dict = {'scan_number': 0,
                             'mz_array': raw_data.mz_values[spectrum_tof_indices[start:end]],
                             'intensity_array': spectrum_intensity_values[start:end],
                             # 'mobility_array': scan['mobility_values'].values.tolist(),  # no mobility array in MS2
                             'scan_type': 'MSn spectrum',
                             'polarity': method_params['polarity'],
                             'centroided': centroided,
                             'retention_time': float(rtinseconds[index - 1] / 60),  # in min
                             'total_ion_current': sum(spectrum_intensity_values[start:end]),
                             'ms_level': 2,
                             'target_mz': average_mzs[index - 1],
                             'isolation_lower_offset': float(quad_mz_values[index - 1][0]),
                             'isolation_upper_offset': float(quad_mz_values[index - 1][1]),
                             'selected_ion_mz': float(mono_mzs[index - 1]),
                             'selected_ion_intensity': float(intensities[index - 1]),
                             'selected_ion_mobility': float(mobilities[index - 1]),
                             'charge_state': int(charges[index - 1]),
                             'collision_energy': 20,  # hard coded for now
                             'parent_frame': parent_frames[index - 1]}

                if spectrum_intensity_values[start:end].size != 0:
                    base_peak_index = spectrum_intensity_values[start:end].argmax()
                    scan_dict['base_peak_mz'] = float(raw_data.mz_values[spectrum_tof_indices[start:end]][base_peak_index])
                    scan_dict['base_peak_intensity'] = float(spectrum_intensity_values[base_peak_index])

                if raw_data.mz_values[spectrum_tof_indices[start:end]].size != 0:
                    scan_dict['high_mz'] = float(max(raw_data.mz_values[spectrum_tof_indices[start:end]]))
                    scan_dict['low_mz'] = float(min(raw_data.mz_values[spectrum_tof_indices[start:end]]))

                list_of_scan_dicts.append(scan_dict)

    ms2_scans_dict = {}
    for key, value in itertools.groupby(list_of_scan_dicts, key_func):
        ms2_scans_dict[key] = list(value)

    return ms2_scans_dict


# Extract all scan information including acquisition parameters, m/z, intensity, and mobility arrays/values
# from dataframes for each scan.
def parse_raw_data(raw_data, ms1_frames, input_filename, output_filename):
    # Get method parameters.
    method_params = get_method_info(input_filename)

    # Get all MS2 scans into dictionary.
    # keys == parent scan
    # values == list of scan dicts containing all the MS2 product scans for a given parent scan
    ms2_scans = parse_ms2_scan(raw_data, method_params, centroiding_window=1)

    ms1_scans = {}
    for frame_num in ms1_frames:
        parent_scan = raw_data[frame_num].sort_values(by='mz_values')
        ms1_scans[frame_num] = parse_ms1_scan(parent_scan, method_params)

    return ms1_scans, ms2_scans


# Count total number of parent and product scans.
def count_scans(parent_scans, product_scans):
    num_parent_scans = 0
    for key, value in parent_scans.items():
        num_parent_scans += 1

    num_product_scans = 0
    for key, value in product_scans.items():
        num_product_scans += len(value)

    return num_parent_scans + num_product_scans


# Write out mzML file using psims.
def write_mzml(raw_data, input_filename, output_filename):
    # Create mzML writer using psims.
    writer = MzMLWriter(output_filename)

    with writer:
        # Begin mzML with controlled vocabularies (CV).
        writer.controlled_vocabularies()

        # Write file description
        writer.file_description(['MS1 spectrum', 'MSn spectrum', 'centroid spectrum'])

        # Add .d folder as source file.
        sf = writer.SourceFile(os.path.split(input_filename)[0],
                               os.path.split(input_filename)[1],
                               id=os.path.splitext(os.path.split(input_filename)[1])[0])  # add params?
        # Checksum source file.
        # skipping, checksum errors out
        #sf.params.append(sf.checksum('sha-1'))

        # Add list of software.
        # will hardcoded bruker software for now
        # look at .d param files and check to see if processed with dataanlysis; add dataanlysis to list if yes
        writer.software_list([{'id': 'psims-writer',
                               'version': '0.1.2',
                               'params': ['python-psims', ]}
                              ])

        # Add instrument configuration information.
        # hardcoded instrument for now
        # not sure if Bruker metadata contains specific instrument prarameters (i.e. ionization type, analyzer, etc.)
        source = writer.Source(1, ['ionization type'])
        analyzer = writer.Analyzer(2, ['mass analyzer type'])
        detector = writer.Detector(3, ['electron multiplier'])
        inst_config = writer.InstrumentConfiguration(id='instrument', component_list=[source, analyzer, detector],
                                                     params=['microOTOF-Q'])
        writer.instrument_configuration_list([inst_config])

        # Add data processing information.
        proc_methods = []
        proc_methods.append(writer.ProcessingMethod(order=1, software_reference='psims-writer',
                                                    params=['Conversion to mzML']))
        processing = writer.DataProcessing(proc_methods, id='exportation')
        writer.data_processing_list([processing])

        # Get MS1 frames.
        ms1_frames = sorted(list(set(raw_data[:, :, 0]['frame_indices'])))
        # Parse raw data to get scans.
        parent_scans, product_scans = parse_raw_data(raw_data, ms1_frames, input_filename, output_filename)
        # Get total number of spectra to write to mzML file.
        num_of_spectra = count_scans(parent_scans, product_scans)

        # Writing data to spectrum list.
        with writer.run(id='run', instrument_configuration='instrument'):
            scan_count = 0
            with writer.spectrum_list(count=num_of_spectra):
                for frame_num in ms1_frames:
                    # Write MS1 parent scan.
                    '''scan_count += 1
                    parent_scans[frame_num]['scan_number'] = scan_count
                    writer.write_spectrum(parent_scans[frame_num]['mz_array'],
                                          parent_scans[frame_num]['intensity_array'],
                                          id='scan=' + str(parent_scans[frame_num]['scan_number']),
                                          polarity=parent_scans[frame_num]['polarity'],
                                          centroided=parent_scans[frame_num]['centroided'],
                                          scan_start_time=parent_scans[frame_num]['retention_time'],
                                          # mobility array goes here once i figure out how to get the mobility array in
                                          # other_arrays: ,
                                          params=[parent_scans[frame_num]['scan_type'],
                                                  {'ms level': parent_scans[frame_num]['ms_level']},
                                                  {'total ion current': parent_scans[frame_num]['total_ion_current']},
                                                  {'base peak m/z': parent_scans[frame_num]['base_peak_mz']},
                                                  {'base peak intensity': parent_scans[frame_num]['base_peak_intensity']},
                                                  {'highest observed m/z': parent_scans[frame_num]['high_mz']},
                                                  {'lowest observed m/z': parent_scans[frame_num]['low_mz']}],
                                          encoding={'ion mobility array': np.float32})'''

                    for product_scan in product_scans[frame_num]:
                        scan_count += 1
                        product_scan['scan_number'] = scan_count

                        # Build params list for spectrum.
                        spectrum_params = [product_scan['scan_type'],
                                           {'ms level': product_scan['ms_level']},
                                           {'total ion current': product_scan['total_ion_current']}]
                        if 'base_peak_mz' in product_scan.keys() and 'base_peak_intensity' in product_scan.keys():
                            spectrum_params.append({'base peak m/z': product_scan['base_peak_mz']})
                            spectrum_params.append({'base peak intensity': product_scan['base_peak_intensity']})
                        if 'high_mz' in product_scan.keys() and 'low_mz' in product_scan.keys():
                            spectrum_params.append({'highest observed m/z': product_scan['high_mz']})
                            spectrum_params.append({'lowest observed m/z': product_scan['low_mz']})

                        # Build precursor information dict.
                        precursor_info = {'mz': product_scan['selected_ion_mz'],
                                          'intensity': product_scan['selected_ion_intensity'],
                                          'charge': product_scan['charge_state'],
                                          'spectrum_reference': 'scan=' + str(parent_scans[frame_num]['scan_number']),
                                          # activation type hard coded for now
                                          'activation': ['low-energy collision-induced dissociation',
                                                         {'collision energy': product_scan['collision_energy']}],
                                          # not able to write correct isolation window right now
                                          #'isolation_window_args': {'target': product_scan['target_mz'],
                                          #                          'upper': product_scan['isolation_upper_offset'],
                                          #                          'lower': product_scan['isolation_lower_offset']},
                                          'isolation_window_args': {'target': product_scan['target_mz']},
                                          'params': {'mobility': product_scan['selected_ion_mobility']}}

                        writer.write_spectrum(product_scan['mz_array'],
                                              product_scan['intensity_array'],
                                              id='scan=' + str(product_scan['scan_number']),
                                              polarity=product_scan['polarity'],
                                              centroided=product_scan['centroided'],
                                              scan_start_time=product_scan['retention_time'],
                                              params=spectrum_params,
                                              precursor_information=precursor_info)


if __name__ == "__main__":
    # Read in example .d file and convert to dataframe.
    pen12_file = 'F:\\code\\alphatims_test_data\\pen12_ms2_1_36_1_400.d'
    pen12_df = bruker_to_df(pen12_file)
    write_mzml(pen12_df, pen12_file, 'F:\\code\\alphatims_test_data\\pen12_ms2_1_36_1_400_noms1_2.mzML')
    bhi_file = 'F:\\code\\alphatims_test_data\\bhi_ms2_1_32_1_396.d'
    bhi_df = bruker_to_df(bhi_file)
    write_mzml(bhi_df, bhi_file, 'F:\\code\\alphatims_test_data\\bhi_ms2_1_32_1_396_noms1_2.mzML')
