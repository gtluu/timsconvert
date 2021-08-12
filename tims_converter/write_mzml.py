from data_parsing import *
from psims.mzml import MzMLWriter
from psims.xml import CVParam, UserParam
import os
import numpy as np


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
                    scan_count += 1
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
                                          encoding={'ion mobility array': np.float32})

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
                                          'params': {'product ion mobility': product_scan['selected_ion_mobility']}}

                        writer.write_spectrum(product_scan['mz_array'],
                                              product_scan['intensity_array'],
                                              id='scan=' + str(product_scan['scan_number']),
                                              polarity=product_scan['polarity'],
                                              centroided=product_scan['centroided'],
                                              scan_start_time=product_scan['retention_time'],
                                              params=spectrum_params,
                                              precursor_information=precursor_info)
