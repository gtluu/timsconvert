import alphatims.bruker
import pandas as pd

if __name__ == '__main__':
    data = alphatims.bruker.TimsTOF('pen12_ms2_1_36_1_400.d')
    #print(data.index_precursors(centroiding_window=1))
    #print(data[:,:,:,:,:])
    #data[:, :, :, :, :].to_csv('pen12_ms2.csv')
    #data[1].to_csv('pen12_ms2_frame1.csv')
    #data[176:186].to_csv('pen12_ms2_frame_176-185.csv')
    #print(data.meta_data)

    #print(alphatims.bruker.read_bruker_sql('pen12_ms2_1_36_1_400.d')[1])

    #print(len(set(data[:,:,:,:,:]['frame_indices'])))

    #print(pd.Series(-1).unique() == data[176]['quad_low_mz_values'].unique())
    print(data.precursors)
    data.precursors.to_csv('pen12_ms2_precursors.csv')