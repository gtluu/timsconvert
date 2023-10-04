import logging
from timsconvert.timestamp import *


logging.info(get_iso8601_timestamp() + ':' + 'Initialize constants...')

VERSION = '1.5.1'

INSTRUMENT_FAMILY = {'1': 'otof',
                     '2': 'otofq',
                     '6': 'maxis',
                     '7': 'impact',
                     '8': 'compact',
                     '9': 'timstof',
                     '512': 'ftms',
                     '513': 'solarix'}

# Only type "1" has been tested with the current test dataset.
INSTRUMENT_SOURCE_TYPE = {'0': 'unspecified',
                          '1': 'electrospray ionization',
                          '2': 'atmospheric pressure chemical ionization',
                          '3': 'nanoelectrospray',
                          '4': 'nanoelectrospray',
                          '5': 'atmospheric pressure photoionization',
                          '6': 'multimode ionization',
                          '9': 'nanoflow electrospray ionization',
                          '10': 'ionBooster',
                          '11': 'CaptiveSpray',
                          '12': 'GC-APCI',
                          '13': 'VIP-HESI-APCI'}

BAF_SCAN_MODE = {'0': 'MS',
                 '2': 'MS/MS (Auto) | MS/MS (MRM)',
                 '4': 'MS/MS (isCID)',
                 '5': 'MS/MS (bbCID)'}

TSF_TDF_SCAN_MODE = {'0': 'MS',
                     '1': 'MS/MS (Auto)',
                     '2': 'MS/MS (MRM)',
                     '4': 'MS/MS (bbCID)',
                     '8': 'dda-PASEF',
                     '9': 'dia-PASEF',
                     '10': 'prm-PASEF',
                     '20': 'MS/MS (MALDI)'}

MSMS_TYPE = {'0': 'MS',
             '2': 'MS/MS',
             '8': 'dda-PASEF',
             '9': 'dia-PASEF'}

MSMS_TYPE_CATEGORY = {'ms1': [0],
                      'ms2': [2, 8, 9]}
