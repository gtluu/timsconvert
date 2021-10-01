from timsconvert.classes import *
from timsconvert.init_bruker_dll import *
import alphatims.bruker


# modified from alphatims
if sys.platform[:5] == 'win32':
    # change filepath later.
    BRUKER_DLL_FILE_NAME = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
                                        'lib\\timsdata.dll')
elif sys.platform[:5] == 'linux':
    BRUKER_DLL_FILE_NAME = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
                                        'lib\\timsdata.so')
else:
    # Add logging warning here.
    BRUKER_DLL_FILE_NAME = ''

dll = init_bruker_dll(BRUKER_DLL_FILE_NAME)

if __name__ == '__main__':
    tdf_dd_file = 'F:\\code\\data\\PenMB-ZoneofInhibition-568-TIMS-MSMS.d'
    tdf = tdf_data(tdf_dd_file, dll)
    #print(tdf.meta_data)
    #print(tdf.read_scans(1, 702, 703))
    #print(tdf.extract_centroided_spectrum_for_frame(1, 0, 1))

    #print(tdf.extract_centroided_spectrum_for_frame(1, 0, 865)[0][:100])
    #print(tdf.extract_centroided_spectrum_for_frame(1, 0, 865)[1][:100])
    ecsff = pd.DataFrame({'mz': tdf.extract_centroided_spectrum_for_frame(1, 0, 865)[0],
                          'intensity': tdf.extract_centroided_spectrum_for_frame(1, 0, 865)[1]})
    #ecsff.to_csv('F:\\code\\data\\ecsff.csv')
    #print(tdf.read_scans(1, 0, 865))

    #print(tdf.extract_centroided_spectrum_for_frame(int(1), int(0), int(865)))
    #mz_array, intensity_array = tdf.extract_centroided_spectrum_for_frame(1, 0, 865)
    #print(mz_array)
    #print(intensity_array)
    #print(len(mz_array))
    #print(len(intensity_array))
    #print(tdf.read_scans(1, 0, 865))
    #print(np.array(list(range(1, 866))).size)
    #print(tdf.scan_num_to_oneoverk0(1, np.array(list(range(1, 866)))))
    #print(tdf.scan_num_to_oneoverk0(1, np.array([651])))
    #print(tdf.read_scans(1, 1, 3)[0][0])
    #at_tdf = alphatims.bruker.TimsTOF(tdf_dd_file)
    ##at_tdf[:, :, :, :, :].to_csv('F:\\code\\alphatims_test_data\\maldi_dd_tdf_ms2.csv')
    #print(at_tdf[1]['scan_indices'].values.tolist())
    #print(at_tdf[1, 582])




    # combining individual scans
    list_of_scan_tuples = [i for i in tdf.read_scans(1, 0, 865) if i[0].size != 0 and i[1].size != 0]
    list_of_dfs = []
    for frame in range(1, 2):
        for scan_tuple in list_of_scan_tuples:
            list_of_dfs.append(pd.DataFrame({'mz': tdf.index_to_mz(frame, scan_tuple[0]),
                                             'intensity': scan_tuple[1]}))
    frame_df = pd.concat(list_of_dfs).sort_values(by='mz')
    #frame_df.to_csv('F:\\code\\data\\frame_df_sorted.csv')
    #print(frame_df)
    frame_df = frame_df.groupby(by='mz', as_index=False).sum()
    #print(frame_df)
    frame_df = frame_df.sort_values(by='mz')
    #print(frame_df)
    #frame_df.to_csv('F:\\code\\data\\frame_df_grouped.csv')

    mz_df = pd.DataFrame(data=frame_df['mz'].values, columns=['mz'])
    #print(pd.merge_asof(mz_df, mz_df, on='mz', tolerance=0.01, direction='nearest', allow_exact_matches=False))

    mz = frame_df['mz'].values.tolist()
    intensity = frame_df['intensity'].values.tolist()

    def group_mz(mz_array, tol=0.01):
        result = []
        last = mz_array[0]
        for i in mz_array:
            if i - last > tol:
                yield result
                result = []
            result.append(i)
            last = i
        yield result

    def group_mz_indices(mz_array, tol=0.01):
        result = []
        last = mz_array[0]
        for i in mz_array:
            if i - last > tol:
                yield result
                result = []
            result.append(mz_array.index(i))
            last = i
        yield result


    def group_features(mz_array, intensity_array, encoding, tol=0.01):
        def get_mz_generator(mz_array, tol=tol):
            result = []
            last = mz_array[0]
            for i in mz_array:
                if i - last > tol:
                    yield result
                    result = []
                result.append(i)
                last = i
            yield result

        def get_indices_generator(mz_array, tol=tol):
            result = []
            last = mz_array[0]
            for i in mz_array:
                if i - last > tol:
                    yield result
                    result = []
                result.append(mz_array.index(i))
                last = i
            yield result

        # Set encoding if necessary.
        if encoding != 0:
            if encoding == 32:
                encoding_dtype = np.float32
            elif encoding == 64:
                encoding_dtype = np.float64

        new_mz_array = [np.mean(list_of_mz_values) for list_of_mz_values in list(get_mz_generator(mz_array, tol))]

        new_intensity_array = []
        for list_of_indices in list(get_indices_generator(mz_array, tol)):
            tmp_list = []
            for index in list_of_indices:
                tmp_list.append(intensity_array[index])
            new_intensity_array.append(sum(tmp_list))

        return (np.array(new_mz_array, dtype=encoding_dtype),
                np.array(new_intensity_array, dtype=encoding_dtype))


    #print(list(group_mz(mz)))
    #print(len(list(group_mz(mz))))
    #print(list(group_mz_indices(mz)))
    #print(len(list(group_mz_indices(mz))))

    grouped_mz_values = [np.mean(list_of_mz_values) for list_of_mz_values in list(group_mz(mz))]

    grouped_intensity_values = []
    for list_of_indices in list(group_mz_indices(mz)):
        tmp_list = []
        for index in list_of_indices:
            tmp_list.append(intensity[index])
        grouped_intensity_values.append(tmp_list)
    grouped_intensity_values = [sum(list_of_intensity_values) for list_of_intensity_values in grouped_intensity_values]

    #print(np.array(grouped_mz_values, dtype=np.float64))
    #print(np.array(grouped_intensity_values, dtype=np.float64))
    #print(len(grouped_mz_values))
    #print(len(grouped_intensity_values))

    mz_array, intensity_array = group_features(mz, intensity, encoding=64, tol=0.01)
    print(len(group_features(mz, intensity, encoding=64, tol=0.01)[0]))
    print(len(group_features(mz, intensity, encoding=64, tol=0.01)[1]))
