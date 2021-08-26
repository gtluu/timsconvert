from .data_parsing import *
from .timestamp import *
from psims.mzml import MzMLWriter
from psims.xml import CVParam, UserParam
from psims.mzml.components import ParameterContainer, NullMap
import os
import logging
import numpy as np


INSTRUMENT_FAMILY = {'0': 'trap',
                     '1': 'otof',
                     '2': 'otofq',
                     '3': 'biotof',
                     '4': 'biotofq',
                     '5': 'malditof',
                     '6': 'ftms',
                     '7': 'maxis',
                     '9': 'timstof',
                     '90': 'impact',
                     '91': 'compact',
                     '92': 'solarix',
                     '255': 'unknown'}


INSTRUMENT_SOURCE_TYPE = {'1': 'electrospray ionization',
                          '2': 'atmospheric pressure chemical ionization',
                          '3': 'nanoelectrospray',
                          '4': 'nanoelectrospray',
                          '5': 'atmospheric pressure photoionization',
                          '6': 'multimode ionization',
                          '9': 'nanoflow electrospray ionization',
                          '10': 'ionBooster',
                          '11': 'CaptiveSpray',
                          '12': 'GC-APCI'}


class IMMS(ParameterContainer):
    def __init(self, order, params=None, context=NullMap, **kwargs):
        params = self.prepare_params(params, **kwargs)
        super(IMMS, self).__init__('ion mobility mass spectrometer',
                                   params,
                                   dict(order=order),
                                   context=context)
        try:
            self.order = int(order)
        except (ValueError, TypeError):
            self.order = order


# Count total number of parent and product scans.
def count_scans(parent_scans, product_scans):
    num_parent_scans = 0
    for key, value in parent_scans.items():
        num_parent_scans += 1

    num_product_scans = 0
    for key, value in product_scans.items():
        num_product_scans += len(value)

    return num_parent_scans + num_product_scans


# Write out product spectrum.
def write_ms2_spectrum(writer, parent_scan, product_scan):
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
                      'activation': [product_scan['activation'],
                                     {'collision energy': product_scan['collision_energy']}],
                      'isolation_window_args': {'target': product_scan['target_mz'],
                                                'upper': product_scan['isolation_upper_offset'],
                                                'lower': product_scan['isolation_lower_offset']},
                      'params': {'product ion mobility': product_scan['selected_ion_mobility']}}

    if parent_scan != None:
        precursor_info['spectrum_reference'] = 'scan=' + str(parent_scan['scan_number'])

    # Write MS2 spectrum.
    writer.write_spectrum(product_scan['mz_array'],
                          product_scan['intensity_array'],
                          id='scan=' + str(product_scan['scan_number']),
                          polarity=product_scan['polarity'],
                          centroided=product_scan['centroided'],
                          scan_start_time=product_scan['retention_time'],
                          params=spectrum_params,
                          precursor_information=precursor_info)


# Write out parent spectrum.
def write_ms1_spectrum(writer, parent_scan, groupby):
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

    # Write MS1 spectrum.
    writer.write_spectrum(parent_scan['mz_array'],
                          parent_scan['intensity_array'],
                          id='scan=' + str(parent_scan['scan_number']),
                          polarity=parent_scan['polarity'],
                          centroided=parent_scan['centroided'],
                          scan_start_time=parent_scan['retention_time'],
                          other_arrays=other_arrays,
                          params=params,
                          encoding={'ion mobility array': np.float32})


# Write out mzML file using psims.
def write_mzml(raw_data, args):
    # Create mzML writer using psims.
    writer = MzMLWriter(os.path.join(args['outdir'], args['outfile']))

    with writer:
        # Begin mzML with controlled vocabularies (CV).
        writer.controlled_vocabularies()

        # Write file description.
        file_description = []
        if args['ms2_only'] == False:
            file_description.append('MS1 spectrum')
            file_description.append('MSn spectrum')
        elif args['ms2_only'] == True:
            file_description.append('MSn spectrum')
        if args['centroid'] == True:
            file_description.append('centroid spectrum')
        elif args['centroid'] == False:
            file_description.append('profile spectrum')
        writer.file_description(file_description)

        # Add .d folder as source file.
        sf = writer.SourceFile(os.path.split(args['infile'])[0],
                               os.path.split(args['infile'])[1],
                               id=os.path.splitext(os.path.split(args['infile'])[1])[0])

        # Add list of software.
        # check for processed data from dataanalysis
        acquisition_software_id = raw_data.meta_data['AcquisitionSoftware']
        acquisition_software_version = raw_data.meta_data['AcquisitionSoftwareVersion']
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

        # Add instrument configuration information.
        # hardcoded ion mobility, mass analyzers, and detector for timsTOF series for now
        inst_count = 0
        # Source
        if raw_data.meta_data['InstrumentSourceType'] in INSTRUMENT_SOURCE_TYPE.keys():
            inst_count += 1
            source = writer.Source(inst_count, [INSTRUMENT_SOURCE_TYPE[raw_data.meta_data['InstrumentSourceType']]])
        # Ion Mobility Spectrometer
        #inst_count += 1
        #tims = IMMS(inst_count, ['trapped ion mobility spectrometer'])
        # Mass Analyzer(s)
        inst_count += 1
        analyzer = writer.Analyzer(inst_count, ['quadrupole', 'time-of-flight'])
        # Detector
        # detector info not found in .tdf test file.
        detector = writer.Detector(inst_count, ['electron multiplier'])
        # Write instrument configuration.
        #inst_config = writer.InstrumentConfiguration(id='instrument', component_list=[source, tims, analyzer, detector],
        inst_config = writer.InstrumentConfiguration(id='instrument', component_list=[source, analyzer, detector],
                                                     params=[INSTRUMENT_FAMILY[raw_data.meta_data['InstrumentFamily']]])
        writer.instrument_configuration_list([inst_config])

        # Add data processing information.
        proc_methods = []
        proc_methods.append(writer.ProcessingMethod(order=1, software_reference='tims_converter',
                                                    params=['Conversion to mzML']))
        proc_methods.append(writer.ProcessingMethod(order=2, software_reference='psims-writer',
                                                    params=['Conversion to mzML']))
        processing = writer.DataProcessing(proc_methods, id='exportation')
        writer.data_processing_list([processing])

        # Get MS1 frames.
        ms1_frames = sorted(list(set(raw_data[:, :, 0]['frame_indices'])))
        # Parse raw data to get scans.
        parent_scans, product_scans = parse_raw_data(raw_data, ms1_frames, args)
        # Get total number of spectra to write to mzML file.
        num_of_spectra = count_scans(parent_scans, product_scans)

        # Writing data to spectrum list.
        with writer.run(id='run', instrument_configuration='instrument'):
            scan_count = 0
            with writer.spectrum_list(count=num_of_spectra):
                for frame_num in ms1_frames:
                    if args['ms1_groupby'] == 'scan':
                        ms1_scans = sorted(list(set(raw_data[frame_num]['scan_indices'])))
                        for scan_num in ms1_scans:
                            spectrum = parent_scans['f' + str(frame_num) + 's' + str(scan_num)]
                            # Write MS1 parent scan.
                            if args['ms2_only'] == False:
                                scan_count += 1
                                spectrum['scan_number'] = scan_count
                                logging.info(get_timestamp() + ':' + 'Writing Scan ' + str(scan_count))
                                write_ms1_spectrum(writer, spectrum, args['ms1_groupby'])
                            # Write MS2 product scans.
                            if 'f' + str(frame_num) + 's' + str(scan_num) in product_scans.keys():
                                for product_scan in product_scans['f' + str(frame_num) + 's' + str(scan_num)]:
                                    scan_count += 1
                                    product_scan['scan_number'] = scan_count
                                    logging.info(get_timestamp() + ':' + 'Writing Scan ' + str(scan_count))
                                    write_ms2_spectrum(writer, spectrum, product_scan)
                    elif args['ms1_groupby'] == 'frame':
                        spectrum = parent_scans[frame_num]
                        # Write MS1 parent scan.
                        if args['ms2_only'] == False:
                            scan_count += 1
                            spectrum['scan_number'] = scan_count
                            logging.info(get_timestamp() + ':' + 'Writing Scan ' + str(scan_count))
                            write_ms1_spectrum(writer, spectrum, args['ms1_groupby'])
                        # Write MS2 product scans.
                        if frame_num in product_scans.keys():
                            for product_scan in product_scans[frame_num]:
                                scan_count += 1
                                product_scan['scan_number'] = scan_count
                                logging.info(get_timestamp() + ':' + 'Writing Scan ' + str(scan_count))
                                write_ms2_spectrum(writer, spectrum, product_scan)


if __name__ == '__main__':
    logger = logging.getLogger(__name__)
