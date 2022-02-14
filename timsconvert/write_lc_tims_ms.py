from timsconvert.constants import *
from timsconvert.timestamp import *
from timsconvert.parse_lcms import *
import os
import sys
import logging
import numpy as np
from psims.mzml import MzMLWriter


def write_mzml_metadata(data, writer, infile, centroid, ms2_only):
    # Basic file descriptions.
    file_description = []
    # Add spectra level and centroid/profile status.
    if ms2_only == False:
        file_description.append('MS1 spectrum')
        file_description.append('MSn spectrum')
    elif ms2_only == True:
        file_description.append('MSn spectrum')
    if centroid:
        file_description.append('centroid spectrum')
    elif not centroid:
        file_description.append('profile spectrum')
    writer.file_description(file_description)

    # Source file
    sf = writer.SourceFile(os.path.split(infile)[0],
                           os.path.split(infile)[1],
                           id=os.path.splitext(os.path.split(infile)[1])[0])

    # Add list of software.
    acquisition_software_id = data.meta_data['AcquisitionSoftware']
    acquisition_software_version = data.meta_data['AcquisitionSoftwareVersion']
    if acquisition_software_id == 'Bruker otofControl':
        acquisition_software_params = ['micrOTOFcontrol', ]
    else:
        acquisition_software_params = []
    psims_software = {'id': 'psims-writer',
                      'version': '0.1.2',
                      'params': ['python-psims', ]}
    writer.software_list([{'id': acquisition_software_id,
                           'version': acquisition_software_version,
                           'params': acquisition_software_params},
                          psims_software])

    # Instrument configuration.
    inst_count = 0
    if data.meta_data['InstrumentSourceType'] in INSTRUMENT_SOURCE_TYPE.keys():
        inst_count += 1
        source = writer.Source(inst_count, [INSTRUMENT_SOURCE_TYPE[data.meta_data['InstrumentSourceType']]])
    # If source isn't found in the GlobalMetadata SQL table, hard code source to ESI
    else:
        inst_count += 1
        source = writer.Source(inst_count, [INSTRUMENT_SOURCE_TYPE['1']])

    # Analyzer and detector hard coded for timsTOF fleX
    inst_count += 1
    analyzer = writer.Analyzer(inst_count, ['quadrupole', 'time-of-flight'])
    inst_count += 1
    detector = writer.Detector(inst_count, ['electron multiplier'])
    inst_config = writer.InstrumentConfiguration(id='instrument', component_list=[source, analyzer, detector],
                                                 params=[INSTRUMENT_FAMILY[data.meta_data['InstrumentFamily']]])
    writer.instrument_configuration_list([inst_config])

    # Data processing element.
    proc_methods = []
    proc_methods.append(writer.ProcessingMethod(order=1, software_reference='psims-writer',
                                                params=['Conversion to mzML']))
    processing = writer.DataProcessing(proc_methods, id='exportation')
    writer.data_processing_list([processing])


# Calculate the number of spectra to be written.
def get_spectra_count(data, ms1_groupby, encoding):
    if ms1_groupby == 'scan':



# Parse out LC-MS(/MS) data and write out mzML file using psims.
def write_lcms_mzml(data, infile, outdir, outfile, centroid, ms2_only, ms1_groupby, encoding, chunk_size):
    # Initialize mzML writer using psims.
    writer = MzMLWriter(os.path.join(outdir, outfile))

    with writer:
        # Begin mzML with controlled vocabularies (CV).
        writer.controlled_vocabularies()

        # Start write acquisition, instrument config, processing, etc. to mzML.
        write_mzml_metadata(data, writer, infile, centroid, ms2_only)

        logging.info(get_timestamp() + ':' + 'Writing to .mzML file ' + os.path.join(outdir, outfile) + '...')
        # Parse chunks of data and write to spectrum elements.
        with writer.run(id='run', instrument_configuration='instrument'):
            scan_count = 0
            num_of_spectra = get_spectra_count()







        # Begin parsing and writing out data.
        # add code later for elif baf -> use baf2sql
        if data.meta_data['SchemaType'] == 'TDF':




            chunk = 0
            while chunk + chunk_size + 1 <= len(data.ms1_frames):
                chunk_list = []
                print(chunk, chunk + chunk_size, chunk + 1, chunk + chunk_size + 1)
                for i, j in zip(data.ms1_frames[chunk:chunk + chunk_size],
                                data.ms1_frames[chunk + 1:chunk + chunk_size + 1]):
                    chunk_list.append((int(i), int(j)))
                chunk += chunk_size
                print(chunk_list)
                print(len(chunk_list))
            else:
                chunk_list = []
                for i, j in zip(data.ms1_frames[chunk:-1], data.ms1_frames[chunk + 1:]):
                    chunk_list.append((int(i), int(j)))
                print(chunk_list)
                print(len(chunk_list))