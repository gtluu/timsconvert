from timsconvert.parse_lcms import *
import os
import logging
from lxml.etree import parse, XMLParser


def write_mzml_metadata(data, writer, infile, mode, ms2_only, barebones_metadata):
    # Basic file descriptions.
    file_description = []
    # Add spectra level and centroid/profile status.
    if ms2_only == False:
        file_description.append('MS1 spectrum')
        file_description.append('MSn spectrum')
    elif ms2_only == True:
        file_description.append('MSn spectrum')
    if mode == 'raw' or mode == 'centroid':
        file_description.append('centroid spectrum')
    elif mode == 'profile':
        file_description.append('profile spectrum')
    writer.file_description(file_description)

    # Source file
    sf = writer.SourceFile(os.path.split(infile)[0],
                           os.path.split(infile)[1],
                           id=os.path.splitext(os.path.split(infile)[1])[0])

    # Add list of software.
    if not barebones_metadata:
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
    inst_config = writer.InstrumentConfiguration(id='instrument', component_list=[source, analyzer, detector])
    writer.instrument_configuration_list([inst_config])

    # Data processing element.
    if not barebones_metadata:
        proc_methods = []
        proc_methods.append(writer.ProcessingMethod(order=1, software_reference='psims-writer',
                                                    params=['Conversion to mzML']))
        processing = writer.DataProcessing(proc_methods, id='exportation')
        writer.data_processing_list([processing])


# Calculate the number of spectra to be written.
# Basically an abridged version of parse_lcms_tdf to account for empty spectra that don't end up getting written.
def get_spectra_count(data):
    if data.meta_data['SchemaType'] == 'TDF':
        ms1_count = data.frames[data.frames['MsMsType'] == 0]['MsMsType'].values.size
        ms2_count = len(list(filter(None, data.precursors['MonoisotopicMz'].values)))
    elif data.meta_data['SchemaType'] == 'Baf2Sql':
        ms1_count = data.frames[data.frames['AcquisitionKey'] == 1]['AcquisitionKey'].values.size
        ms2_count = data.frames[data.frames['AcquisitionKey'] == 2]['AcquisitionKey'].values.size
    return ms1_count + ms2_count


def update_spectra_count(outdir, outfile, num_of_spectra, scan_count):
    with open(os.path.splitext(os.path.join(outdir, outfile))[0] + '_tmp.mzML', 'r') as in_stream, \
            open(os.path.join(outdir, outfile), 'w') as out_stream:
        for line in in_stream:
            out_stream.write(line.replace('      <spectrumList count="' + str(num_of_spectra) + '" defaultDataProcessingRef="exportation">',
                                          '      <spectrumList count="' + str(scan_count) + '" defaultDataProcessingRef="exportation">'))
    os.remove(os.path.splitext(os.path.join(outdir, outfile))[0] + '_tmp.mzML')
