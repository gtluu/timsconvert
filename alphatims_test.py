import alphatims.bruker
import alphatims.utils
import pandas as pd
import numpy as np

if __name__ == '__main__':
    data = alphatims.bruker.TimsTOF('F:\\code\\alphatims_test_data\\pen12_ms2_1_36_1_400.d')
    #print(data.index_precursors(centroiding_window=0))
    #print(data.index_precursors(centroiding_window=1))
    #print(data.index_precursors(centroiding_window=1)[0])

    #print(data[:,:,:,:,:])
    #data[:, :, :, :, :].to_csv('pen12_ms2.csv')
    #data[1].to_csv('pen12_ms2_frame1.csv')
    #data[176:186].to_csv('pen12_ms2_frame_176-185.csv')
    print(data.meta_data)
    for key, value in data.meta_data.items():
        print(key, value)

    #print(alphatims.bruker.read_bruker_sql('pen12_ms2_1_36_1_400.d')[1])

    #print(len(set(data[:,:,:,:,:]['frame_indices'])))

    #print(pd.Series(-1).unique() == data[176]['quad_low_mz_values'].unique())
    #print(data.precursors)
    #data.precursors.to_csv('pen12_ms2_precursors.csv')

    '''print(alphatims.bruker.centroid_spectra(index=data[1, :, :, :, :]['push_indices'],
                                            spectrum_indptr=data.index_precursors(centroiding_window=1)[0],
                                            #spectrum_counts=,
                                            spectrum_tof_indices=data.index_precursors(centroiding_window=1)[1],
                                            spectrum_intensity_values=data.index_precursors(centroiding_window=1)[2],
                                            window_size=1))'''

    '''print(alphatims.bruker.centroid_spectra(index=data[1, :, :, :, :]['push_indices'],
                                            spectrum_indptr=data[1, :, :, :, :]['scan_indices'],
                                            spectrum_counts=np.array([1]),
                                            spectrum_tof_indices=data[1, :, :, :, :]['tof_indices'],
                                            spectrum_intensity_values=data[1, :, :, :, :]['intensity_values'],
                                            window_size=1))'''

    #pre_ind = data.index_precursors(centroiding_window=1)
    #print(len(pre_ind[0]), len(pre_ind[1]), len(pre_ind[2]))

    #for i in range(0, len(pre_ind[0] + 1), 100):
    #    print(pre_ind[0][i:i+100])

    '''print('all')
    print(data[pre_ind[0], :, :, pre_ind[1], pre_ind[2]])
    print('spectrum_indptr')
    print(data[pre_ind[0], :, :, :, :])
    print('tof_indices')
    print(data[:, :, :, pre_ind[1], :])
    print('intensity_indices')
    print(data[:, :, :, :, pre_ind[2]])'''

    #print(data[:, :, :, :, :, 'raw'])
    #print(data.rt_values)

    #data.save_as_mgf(directory='F:\\code\\alphatims_test_data', file_name='pen12_2.mgf', centroiding_window=1)

    #alphatims.utils.progress_callback