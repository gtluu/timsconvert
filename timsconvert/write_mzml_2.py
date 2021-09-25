import os
import numpy as np
from psims.mzml import MzMLWriter
from timsconvert.constants import *
from timsconvert.parse_tsf import *


def write_mzml_metadata(data, writer, ms2_only, centroid):
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
    sf = writer.SourceFile(os.path.split(data.source_file)[0],
                           os.path.split(data.source_file)[1],
                           id=os.path.splitext(os.path.split(data.source_file)[1])[0])

    # Acquisition software.
    # no acquisition software for now; using generic cv
    writer.software_list([{'id': 'acquisition software',
                           'version': '0',
                           'params': ['acquisition software', ]},
                          {'id': 'psims-writer',
                           'version': '0.1.2',
                           'params': ['python-psims', ]}])

    # Instrument configuration.
    inst_count = 0
    if data.metadata['InstrumentSourceType'] in INSTRUMENT_SOURCE_TYPE.keys():
        inst_count += 1
        source = writer.Source(inst_count, [INSTRUMENT_SOURCE_TYPE[data.metadata['InstrumentSourceType']]])
    # analyzer and detector hard coded for timsTOF flex
    inst_count += 1
    analyzer = writer.Analyzer(inst_count, ['quadrupole', 'time-of-flight'])
    inst_count += 1
    detector = writer.Detector(inst_count, ['electron multiplier'])
    inst_config = writer.InstrumentCOnfiguration(id='instrument', component_list=[source, analyzer, detector],
                                                 params=[
                                                     INSTRUMENT_FAMILY[data.metadata['InstrumentFamily']]])
    writer.instrument_configuration_list([inst_config])

    # Data processing element.
    proc_methods = []
    proc_methods.append(writer.ProcessingMethod(order=1, software_reference='psims-writer',
                                                params=['Conversion to mzML']))
    processing = writer.DataProcessing(proc_methods, id='exportation')
    writer.data_processing_list([processing])
