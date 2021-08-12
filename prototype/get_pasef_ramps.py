import alphatims.bruker
import os
from lxml import etree as et


# Check method for PASEF NumRampsPerCycle.
# From microTOFQImpacTemAcquisition.method XML file.
def get_pasef_ramps(input_filename):
    # Get method file path.
    for dirpath, dirnames, filenames in os.walk(input_filename):
        for dirname in dirnames:
            if os.path.splitext(dirname)[1].lower() == '.m':
                method_file = os.path.join(dirpath, dirname, 'microTOFQImpacTemAcquisition.method')

    # Open XML file and get number of ramps per cycle.
    method_data = et.parse(method_file).getroot()
    num_ramps_per_cycle = method_data.xpath('//para_int[@permname="MSMS_Pasef_NumRampsPerCycle"]')[0].attrib['value']
    return num_ramps_per_cycle


if __name__ == '__main__':
    filename = 'F:\\alphatims_test\\pen12_ms2_1_36_1_400.d'
    get_pasef_ramps(filename)
