import sys
import os
import logging
from timsconvert.timestamp import *


logger = logging.getLogger(__name__)
logging.info(get_timestamp() + ':' + 'Initialize constants...')


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


SCAN_MODE = {'0': 'MS',
             '1': 'MS/MS',
             '2': 'MS-MS/MS (isCID)',
             '3': 'MS/MS (MRM)',
             '4': 'MS/MS (Auto)',
             '5': 'MS-MS/MS (bbCID)',
             '6': 'MS/MS (Pasef)',
             '9': 'dia-PASEF',
             '10': 'prm-PASEF'}

SCAN_MODE_CATEGORY = {'ms1': [0],
                      'ms2': [1, 2, 3, 4, 5, 6, 9, 10]}

MSMS_TYPE = {'0': 'MS',
             '2': 'MALDI MS/MS',
             '8': 'dia-PASEF',
             '9': 'dda-PASEF'}

MSMS_TYPE_CATEGORY = {'ms1': [0],
                      'ms2': [2, 8, 9]}

# modified from alphatims
if sys.platform[:5] == 'win32':
    # change filepath later.
    BRUKER_DLL_FILE_NAME = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
                                        os.path.join('lib', 'timsdata.dll'))
elif sys.platform[:5] == 'linux':
    BRUKER_DLL_FILE_NAME = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
                                        os.path.join('lib', 'timsdata.so'))
else:
    # Add logging warning here.
    BRUKER_DLL_FILE_NAME = ''
