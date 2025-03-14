import os
import logging
from multiprocessing import Pool, cpu_count
import pandas as pd
from timsconvert.constants import VERSION
from timsconvert.data_input import dot_d_detection
from timsconvert.timestamp import get_iso8601_timestamp
from timsconvert_nanodesi.arguments import get_args, args_check
from timsconvert_nanodesi.data_input import line_scan_metadata_detection
from timsconvert_nanodesi.convert import convert_raw_file, clean_up_logfiles


def main():
    # Parse arguments.
    args = get_args()
    # Args check.
    args_check(args)
    # Check arguments.
    args['version'] = VERSION

    # Load in input data.
    line_scan_dfs = {}
    for input_path in args['input']:
        if os.path.splitext(input_path)[1] == '.csv':
            df = pd.read_csv(input_path)
            if df.columns.values.tolist() == ['x', 'path']:
                line_scan_dfs[input_path] = df
            else:
                logging.warning(
                    get_iso8601_timestamp() + ':' + f'{input_path} can only contain columns "x" and "path"...')
                logging.warning(get_iso8601_timestamp() + ':' + 'Skipping...')
        elif os.path.splitext(input_path)[1] == '':
            for line_scan_metadata_file in line_scan_metadata_detection(input_path):
                df = pd.read_csv(line_scan_metadata_file)
                if df.columns.values.tolist() == ['x', 'path']:
                    line_scan_dfs[line_scan_metadata_file] = df
                else:
                    logging.warning(
                        get_iso8601_timestamp() + ':' + f'{line_scan_metadata_file} can only contain columns "x" and "path"...')
                    logging.warning(get_iso8601_timestamp() + ':' + 'Skipping...')
        else:
            logging.warning(get_iso8601_timestamp() + ':' + f'{input_path} cannot be read...')
            logging.warning(get_iso8601_timestamp() + ':' + 'Skipping...')

    # Convert each sample.
    with Pool(processes=cpu_count() - 1) as pool:
        pool_map_input = [(args, line_scan_metadata_file, line_scan_df)
                          for line_scan_metadata_file, line_scan_df in line_scan_dfs.items()]
        list_of_logfiles = pool.map(convert_raw_file, pool_map_input)
    list_of_logfiles = list(filter(None, list_of_logfiles))

    # Shutdown logger.
    logging.shutdown()

    # Clean up temporary log files.
    clean_up_logfiles(args, list_of_logfiles)


if __name__ == '__main__':
    # Run.
    main()
