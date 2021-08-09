import alphatims.bruker
import psims.mzml.components
from psims.mzml import MzMLWriter
from psims.xml import CVParam, UserParam
from lxml import etree as et
import pandas as pd
import numpy as np
import os


# Read in Bruker .d/.tdf files into dataframe using AlphaTIMS.
def bruker_to_df(filename):
    return alphatims.bruker.TimsTOF(filename)


# Check method for PASEF NumRampsPerCycle, polarity.
# From microTOFQImpacTemAcquisition.method XML file.
def get_method_info(input_filename):
    # Get method file path.
    for dirpath, dirnames, filenames in os.walk(input_filename):
        for dirname in dirnames:
            if os.path.splitext(dirname)[1].lower() == '.m':
                method_file = os.path.join(dirpath, dirname, 'microTOFQImpacTemAcquisition.method')

    # Open XML file and get number of ramps per cycle.
    method_data = et.parse(method_file).getroot()
    method_params = {}
    method_params['num_ramps_per_cycle'] = int(method_data.xpath('//para_int[@permname="MSMS_Pasef_NumRampsPerCycle"]')[0].attrib['value'])
    # polarity is hardcoded for now, need to find where to get that parameter
    method_params['polarity'] = 'positive scan'
    return method_params


# will need to figure out how to centroid data later; only outputs profile for now
def parse_parent_scan(scan, method_params, centroided=False):
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
                 'low_mz': float(min(scan['mz_values'].values.tolist()))}
    return scan_dict


def parse_product_scans(scan, raw_data, frame_num, method_params, centroided=False):
    low_mz_values = scan['quad_low_mz_values'].unique().tolist()
    high_mz_values = scan['quad_high_mz_values'].unique().tolist()

    quad_mz_values = zip(low_mz_values, high_mz_values)

    list_of_scan_dicts = []
    for precursor_low_mz, precursor_high_mz in quad_mz_values:
        # Set scan to subset containing only the detector events in the quad m/z range.
        scan = raw_data[frame_num:frame_num + 1, :, precursor_low_mz:precursor_high_mz + 0.005]

        # Build scan_dict.
        base_peak_row = scan.sort_values(by='intensity_values', ascneding=False).iloc[0]
        scan_dict = {'scan_number': 0,
                     'mz_array': scan['mz_values'].values.tolist(),
                     'intensity_array': scan['intensity_values'].values.tolist(),
                     'mobility_array': scan['mobility_values'].values.tolist(),
                     'scan_type': 'MSn spectrum',
                     'polarity': method_params['polarity'],
                     'centroided': centroided,
                     'retention_time': float(list(set(scan['rt_values_min'].values.tolist()))[0]),
                     'total_ion_current': sum(scan['intensity_values'].values.tolist()),
                     'base_peak_mz': float(base_peak_row['mz_values']),
                     'base_peak_intensity': float(base_peak_row['intensity_values']),
                     'ms_level': 2,
                     'high_mz': float(max(scan['mz_values'].values.tolist())),
                     'low_mz': float(min(scan['mz_values'].values.tolist())),
                     'isolation_window_mz': np.mean(zip(precursor_low_mz, precursor_high_mz)),
                     'isolation_window_lower_offset': abs(np.mean(zip(precursor_low_mz, precursor_high_mz)) - precursor_low_mz),
                     'isolation_window_upper_offset': abs(np.mean(zip(precursor_low_mz, precursor_high_mz)) - precursor_high_mz),
                     'selected_ion_mz': '',
                     'charge_state': '',
                     'collision_energy': '',
                     }
        list_of_scan_dicts.append(scan_dict)
    return list_of_scan_dicts


# Extract m/z, intensity, and mobility arrays from dataframe for each scan.
def parse_raw_data(raw_data, input_filename, output_filename):
    method_params = get_method_info(input_filename)
    num_of_frames = len(set(raw_data[:, :, :, :, :]['frame_indices']))

    # ms1_quad_mz is a list containing only the value -1.
    # quad_low_mz_values and quad_high_mz_values will be a Pandas series containing only the value -1 if scan is MS1.
    ms1_quad_mz = pd.Series(-1).unique()

    parent_scan_dict = {}
    product_scan_dicts = []
    for frame_num in range(1, num_of_frames):
        low_mz_series = raw_data[frame_num:frame_num + 1]['quad_low_mz_values'].unique()
        high_mz_series = raw_data[frame_num:frame_num + 1]['quad_high_mz_values'].unique()
        # If both True, scan/frame is MS1.
        if low_mz_series.size == 1 and high_mz_series.size == 1:
            if ms1_quad_mz == low_mz_series and ms1_quad_mz == high_mz_series:
                parent_scan = raw_data[frame_num:frame_num + 1].sort_values(by='mz_values')
                parent_scan_dict = parse_parent_scan(parent_scan, method_params)
            else:
                product_scans = raw_data[frame_num:frame_num + 1].sort_values(by='quad_low_mz_values')
                product_scan_dicts = parse_product_scans(product_scans, raw_data, frame_num, method_params)

    return (parent_scan_dict, product_scan_dicts)


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

        # Writing data to spectrum list.
        with writer.run(id='run', instrument_configuration='instrument'):
            with writer.spectrum_list(count=len(set(raw_data[:,:,:,:,:]['frame_indices']))):  # count = num of frames
            #with writer.spectrum_list(count=10):
                parent_scan_dict, product_scan_dicts = parse_raw_data(raw_data, input_filename, output_filename)
                # cannot write mobility data; don't know what to pass through to this param, data unpacks incorrectly
                writer.write_spectrum(parent_scan_dict['mz_array'],
                                      parent_scan_dict['intensity_array'],
                                      id='scan=' + str(parent_scan_dict['scan_number']),
                                      polarity=parent_scan_dict['polarity'],
                                      centroided=parent_scan_dict['centroided'],
                                      scan_start_time=parent_scan_dict['retention_time'],
                                      #other_arrays=[{'name': 'ion mobility array',
                                      #               'unit_name': 'ion mobility drift time'},
                                      #              parent_scan_dict['mobility_array']],
                                      #other_arrays=['ion mobility array', parent_scan_dict['mobility_array']],
                                      #other_arrays=UserParam(name=str('ion mobility array'), accession='',
                                      #                     value=parent_scan_dict['mobility_array']),
                                      #other_arrays=[CVParam(name='ion mobility array')],
                                      params=[parent_scan_dict['scan_type'],
                                              {'ms level': parent_scan_dict['ms_level']},
                                              {'total ion current': parent_scan_dict['total_ion_current']},
                                              {'base peak m/z': parent_scan_dict['base_peak_mz']},
                                              {'base peak intensity': parent_scan_dict['base_peak_intensity']},
                                              {'highest observed m/z': parent_scan_dict['high_mz']},
                                              {'lowest observed m/z': parent_scan_dict['low_mz']}],
                                      encoding={'ion mobility array': np.float32})



if __name__ == "__main__":
    # Read in example .d file and convert to dataframe.
    tdf_file = 'F:\\alphatims_test\\pen12_ms2_1_36_1_400.d'
    tdf_df = bruker_to_df(tdf_file)
    parent_scan_dict, product_scan_dicts = parse_raw_data(tdf_df, tdf_file, 'test.mzML')
    #write_mzml(tdf_df, tdf_file, 'test.mzML')
