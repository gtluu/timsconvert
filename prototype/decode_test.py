import base64
import struct
import pandas as pd


def decode_peaks(peaks):
    peak_list = base64.b64decode(peaks)
    peak_list = struct.unpack('>' + str(len(peak_list) // 4) + 'L', peak_list)
    mz_list = [struct.unpack('f', struct.pack('I', i))[0] for i in peak_list[::2]]
    int_list = [struct.unpack('f', struct.pack('I', i))[0] for i in peak_list[1::2]]
    return pd.DataFrame(list(zip(mz_list, int_list)), columns=['mz', 'intensity'])


if __name__ == '__main__':
    decode_peaks('eJwDAAAAAAE')