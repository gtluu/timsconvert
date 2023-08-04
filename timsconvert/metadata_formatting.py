import numpy as np


def get_encoding_dtype(encoding):
    if encoding == 32:
        return np.float32
    elif encoding == 64:
        return np.float64


def get_centroid_status(mode, exclude_mobility=None):
    if mode == 'profile':
        centroided = False
        exclude_mobility = True
    elif mode == 'centroid' or mode == 'raw':
        centroided = True
    return centroided, exclude_mobility


def get_baf_spectrum_polarity(acquisitionkey_dict):
    # Polarity == 0 -> 'positive'; Polarity == 1 -> 'negative"?
    if int(acquisitionkey_dict['Polarity']) == 0:
        polarity = '+'
    elif int(acquisitionkey_dict['Polarity']) == 1:
        polarity = '-'
    return polarity


def get_maldi_coords(data, maldiframeinfo_dict):
    if data.meta_data['MaldiApplicationType'] == 'SingleSpectra':
        coords = maldiframeinfo_dict['SpotName']
    elif data.meta_data['MaldiApplicationType'] == 'Imaging':
        coords = [int(maldiframeinfo_dict['XIndexPos']), int(maldiframeinfo_dict['YIndexPos'])]
        if 'ZIndexPos' in data.maldiframeinfo.columns:
            coords.append(int(maldiframeinfo_dict['ZIndexPos']))
        coords = tuple(coords)
    return coords
