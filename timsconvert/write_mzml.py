from timsconvert.parse_lcms import *
from timsconvert.parse_maldi import *
from timsconvert.timestamp import *
from psims.mzml import MzMLWriter
import os
import logging
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


def write_mzml_metadata(data, writer, infile, ms2_only):
    # Basic file descriptions.
    file_description = []
    if ms2_only == False:
        file_description.append('MS1 spectrum')
        file_description.append('MSn spectrum')
    elif ms2_only == True:
        file_description.append('MSn spectrum')
    file_description.append('centroid spectrum')
    writer.file_description(file_description)

    # Source file element.
    sf = writer.SourceFile(os.path.split(infile)[0],
                           os.path.split(infile)[1],
                           id=os.path.splitext(os.path.split(infile)[1])[0])

    # Add list of software.
    # check for processed data from dataanalysis
    acquisition_software_id = data.meta_data['AcquisitionSoftware']
    acquisition_software_version = data.meta_data['AcquisitionSoftwareVersion']
    if acquisition_software_id == 'Bruker otofControl':
        acquisition_software_params = ['micrOTOFcontrol', ]
    else:
        acquisition_software_params = []
    writer.software_list([{'id': acquisition_software_id,
                           'version': acquisition_software_version,
                           'params': acquisition_software_params},
                          {'id': 'psims-writer',
                           'version': '0.1.2',
                           'params': ['python-psims', ]}])

    # Instrument configuration.
    inst_count = 0
    if data.meta_data['InstrumentSourceType'] in INSTRUMENT_SOURCE_TYPE.keys():
        inst_count += 1
        source = writer.Source(inst_count, [INSTRUMENT_SOURCE_TYPE[data.meta_data['InstrumentSourceType']]])
    # analyzer and detector hard coded for timsTOF flex
    inst_count += 1
    analyzer = writer.Analyzer(inst_count, ['quadrupole', 'time-of-flight'])
    inst_count += 1
    detector = writer.Detector(inst_count, ['electron multiplier'])
    inst_config = writer.InstrumentConfiguration(id='instrument', component_list=[source, analyzer, detector],
                                                 params=[
                                                     INSTRUMENT_FAMILY[data.meta_data['InstrumentFamily']]])
    writer.instrument_configuration_list([inst_config])

    # Data processing element.
    proc_methods = []
    proc_methods.append(writer.ProcessingMethod(order=1, software_reference='psims-writer',
                                                params=['Conversion to mzML']))
    processing = writer.DataProcessing(proc_methods, id='exportation')
    writer.data_processing_list([processing])


# Write out product spectrum.
def write_lcms_ms2_spectrum(writer, parent_scan, encoding, product_scan):
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
                      #'activation': [product_scan['activation'],
                      #               {'collision energy': product_scan['collision_energy']}],
                      'activation': [{'collision energy': product_scan['collision_energy']}],
                      'isolation_window_args': {'target': product_scan['target_mz'],
                                                'upper': product_scan['isolation_upper_offset'],
                                                'lower': product_scan['isolation_lower_offset']},
                      'params': {'product ion mobility': product_scan['selected_ion_mobility']}}
    if not np.isnan(product_scan['charge_state']):
        precursor_info['charge'] = product_scan['charge_state']

    if parent_scan != None:
        precursor_info['spectrum_reference'] = 'scan=' + str(parent_scan['scan_number'])

    if encoding == 32:
        encoding_dtype = np.float32
    elif encoding == 64:
        encoding_dtype = np.float64

    # Write MS2 spectrum.
    writer.write_spectrum(product_scan['mz_array'],
                          product_scan['intensity_array'],
                          id='scan=' + str(product_scan['scan_number']),
                          polarity=product_scan['polarity'],
                          centroided=product_scan['centroided'],
                          scan_start_time=product_scan['retention_time'],
                          params=spectrum_params,
                          precursor_information=precursor_info,
                          encoding={'m/z array': encoding_dtype,
                                    'intensity array': encoding_dtype})


# Write out parent spectrum.
def write_lcms_ms1_spectrum(writer, parent_scan, encoding, groupby):
    # Build params
    params = [parent_scan['scan_type'],
              {'ms level': parent_scan['ms_level']},
              {'total ion current': parent_scan['total_ion_current']},
              {'base peak m/z': parent_scan['base_peak_mz']},
              {'base peak intensity': parent_scan['base_peak_intensity']},
              {'highest observed m/z': parent_scan['high_mz']},
              {'lowest observed m/z': parent_scan['low_mz']}]

    if groupby == 'scan':
        params.append({'ion mobility drift time': parent_scan['mobility']})
        other_arrays = None
    elif groupby == 'frame':
        other_arrays = [('ion mobility array', parent_scan['mobility_array'])]

    if encoding == 32:
        encoding_dtype = np.float32
    elif encoding == 64:
        encoding_dtype = np.float64

    # Write MS1 spectrum.
    writer.write_spectrum(parent_scan['mz_array'],
                          parent_scan['intensity_array'],
                          id='scan=' + str(parent_scan['scan_number']),
                          polarity=parent_scan['polarity'],
                          centroided=parent_scan['centroided'],
                          scan_start_time=parent_scan['retention_time'],
                          other_arrays=other_arrays,
                          params=params,
                          encoding={'m/z array': encoding_dtype,
                                    'intensity array': encoding_dtype,
                                    'ion mobility array': encoding_dtype})


# Write out mzML file using psims.
def write_lcms_mzml(data, infile, outdir, outfile, centroid, ms2_only, ms1_groupby, encoding,
                    ms2_keep_n_most_abundant_peaks):
    # Initialize mzML writer using psims.
    writer = MzMLWriter(os.path.join(outdir, outfile))

    with writer:
        # Begin mzML with controlled vocabulatires (CV).
        writer.controlled_vocabularies()

        write_mzml_metadata(data, writer, infile, ms2_only)

        # Begin writing out data.
        if data.meta_data['SchemaType'] == 'TDF':
            parent_scans, product_scans = parse_lcms_tdf(data, ms1_groupby, centroid, encoding, ms2_only)
        # later add code for elif baf -> use baf2sql
        if ms2_only == False:
            num_of_spectra = len(parent_scans) + len(product_scans)
        elif ms2_only == True:
            num_of_spectra = len(product_scans)

        logging.info(get_timestamp() + ':' + 'Writing to .mzML file ' + os.path.join(outdir, outfile) + '...')
        # Writing data to spectrum
        with writer.run(id='run', instrument_configuration='instrument'):
            scan_count = 0
            with writer.spectrum_list(count=num_of_spectra):
                if ms1_groupby == 'scan':
                    # Write MS1 parent scans.
                    if ms2_only == False:
                        for parent in parent_scans:
                            products = [i for i in product_scans
                                        if i['parent_frame'] == parent['frame'] and
                                        i['parent_scan'] == parent['scan_number']]
                            # Set params for scan.
                            scan_count += 1
                            parent['scan_number'] = scan_count
                            logging.info(get_timestamp() + ':' + 'Writing Scan ' + str(scan_count))
                            write_lcms_ms1_spectrum(writer, parent, encoding, ms1_groupby)
                            # Write MS2 product scans.
                            for product in products:
                                scan_count += 1
                                product['scan_number'] = scan_count
                                logging.info(get_timestamp() + ':' + 'Writing Scan ' + str(scan_count))
                                write_lcms_ms2_spectrum(writer, parent, encoding, product)
                    elif ms2_only == True or parent_scans == []:
                        for product in product_scans:
                            scan_count += 1
                            product['scan_number'] = scan_count
                            logging.info(get_timestamp() + ':' + 'Writing Scan ' + str(scan_count))
                            write_lcms_ms2_spectrum(writer, None, encoding, product)
                elif ms1_groupby == 'frame':
                    # Write MS1 parent scans.
                    if ms2_only == False:
                        for parent in parent_scans:
                            products = [i for i in product_scans if i['parent_frame'] == parent['frame']]
                            # Set params for scan.
                            scan_count += 1
                            parent['scan_number'] = scan_count
                            logging.info(get_timestamp() + ':' + 'Writing Scan ' + str(scan_count))
                            write_lcms_ms1_spectrum(writer, parent, encoding, ms1_groupby)
                            for product in products:
                                scan_count += 1
                                product['scan_number'] = scan_count
                                logging.info(get_timestamp() + ':' + 'Writing Scan ' + str(scan_count))
                                write_lcms_ms2_spectrum(writer, parent, encoding, product)
                    if ms2_only == True:
                        for product in product_scans:
                            scan_count += 1
                            product['scan_number'] = scan_count
                            logging.info(get_timestamp() + ':' + 'Writing Scan ' + str(scan_count))
                            write_lcms_ms2_spectrum(writer, None, encoding, product)


def write_maldi_dd_mzml(data, infile, outdir, outfile, ms2_only, groupby, centroid=True, encoding=0,
                        single_file='combined', plate_map=''):
    if single_file == 'combined':
        # Initialize the mzML writer.
        writer = MzMLWriter(os.path.join(outdir, outfile))

        with writer:
            # Begin mzML with controlled vocabulatires (CV).
            writer.controlled_vocabularies()

            write_mzml_metadata(data, writer, infile, ms2_only)

            # Begin writing out data.
            if data.meta_data['SchemaType'] == 'TDF':
                list_of_scan_dicts = parse_maldi_tdf(data, groupby, encoding, centroid)
            elif data.meta_data['SchemaType'] == 'TSF':
                list_of_scan_dicts = parse_maldi_tsf(data, centroid)
            num_of_spectra = len(list_of_scan_dicts)

            logging.info(get_timestamp() + ':' + 'Writing to .mzML file ' + os.path.join(outdir, outfile) + '...')
            # Writing data to spectrum list.
            with writer.run(id='run', instrument_configuration='instrument'):
                scan_count = 0
                with writer.spectrum_list(count=num_of_spectra):
                    for scan_dict in list_of_scan_dicts:
                        # Set params for scan.
                        scan_count += 1
                        scan_dict['scan_number'] = scan_count
                        params = [scan_dict['scan_type'],
                                  {'ms level': scan_dict['ms_level']},
                                  {'total ion current': scan_dict['total_ion_current']},
                                  {'base peak m/z': scan_dict['base_peak_mz']},
                                  {'base peak intensity': scan_dict['base_peak_intensity']},
                                  {'highest observed m/z': scan_dict['high_mz']},
                                  {'lowest observed m/z': scan_dict['low_mz']},
                                  {'maldi spot identifier': scan_dict['coord']}]

                        if data.meta_data['SchemaType'] == 'TDF':
                            if groupby == 'scan':
                                params.append({'ion mobility drift time': scan_dict['mobility']})
                                other_arrays = None
                            elif groupby == 'frame':
                                other_arrays = [('ion mobility array', scan_dict['mobility_array'])]
                        else:
                            other_arrays = None

                        # Set encoding if necessary.
                        if encoding != 0:
                            if encoding == 32:
                                encoding_dtype = np.float32
                            elif encoding == 64:
                                encoding_dtype = np.float64

                        # Write out spectrum
                        writer.write_spectrum(scan_dict['mz_array'],
                                              scan_dict['intensity_array'],
                                              id='scan=' + str(scan_dict['scan_number']),
                                              polarity=scan_dict['polarity'],
                                              centroided=scan_dict['centroided'],
                                              scan_start_time=scan_dict['retention_time'],
                                              other_arrays=other_arrays,
                                              params=params,
                                              encoding={'m/z array': encoding_dtype,
                                                        'intensity array': encoding_dtype,
                                                        'ion mobility array': encoding_dtype})

    elif single_file == 'individual' and plate_map != '':
        # Check to make sure plate map is a valid csv file.
        if os.path.exists(plate_map) and os.path.splitext(plate_map)[1] == 'csv':
            # Parse all MALDI data.
            if data.meta_data['SchemaType'] == 'TDF':
                list_of_scan_dicts = parse_maldi_tdf(data, groupby, encoding, centroid)
            elif data.meta_data['SchemaType'] == 'TSF':
                list_of_scan_dicts = parse_maldi_tsf(data, centroid)

            # Use plate map to determine filename.
            # Names things as 'sample_position.mzML
            plate_map_dict = parse_maldi_plate_map(plate_map)

            for scan_dict in list_of_scan_dicts:
                output_filename = os.path.join(outdir,
                                               plate_map_dict[scan_dict['coord']] + '_' + scan_dict['coord'] + '.mzML')

                writer = MzMLWriter(output_filename)

                with writer:
                    writer.controlled_vocabularies()

                    write_mzml_metadata(data, writer, infile, ms2_only)

                    with writer.run(id='run', instrument_configuration='instrument'):
                        scan_count = 1
                        with writer.spectrum_list(count=1):
                            # Set params for scan.
                            scan_dict['scan_number'] = scan_count
                            params = [scan_dict['scan_type'],
                                      {'ms level': scan_dict['ms_level']},
                                      {'total ion current': scan_dict['total_ion_current']},
                                      {'base peak m/z': scan_dict['base_peak_mz']},
                                      {'base peak intensity': scan_dict['base_peak_intensity']},
                                      {'highest observed m/z': scan_dict['high_mz']},
                                      {'lowest observed m/z': scan_dict['low_mz']},
                                      {'maldi spot identifier': scan_dict['coord']}]

                            if data.meta_data['SchemaType'] == 'TDF':
                                if groupby == 'scan':
                                    params.append({'ion mobility drift time': scan_dict['mobility']})
                                    other_arrays = None
                                elif groupby == 'frame':
                                    other_arrays = [('ion mobility array', scan_dict['mobility_array'])]
                            else:
                                other_arrays = None

                            # Set encoding if necessary.
                            if encoding != 0:
                                if encoding == 32:
                                    encoding_dtype = np.float32
                                elif encoding == 64:
                                    encoding_dtype = np.float64

                            # Write out spectrum
                            writer.write_spectrum(scan_dict['mz_array'],
                                                  scan_dict['intensity_array'],
                                                  id='scan=' + str(scan_dict['scan_number']),
                                                  polarity=scan_dict['polarity'],
                                                  centroided=scan_dict['centroided'],
                                                  scan_start_time=scan_dict['retention_time'],
                                                  other_arrays=other_arrays,
                                                  params=params,
                                                  encoding={'m/z array': encoding_dtype,
                                                            'intensity array': encoding_dtype,
                                                            'ion mobility array': encoding_dtype})


if __name__ == '__main__':
    logger = logging.getLogger(__name__)
