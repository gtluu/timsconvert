#!/bin/bash

# change to parent directory
parent_path=$( cd "$(dirname "${BASH_SOURCE[0]}")" ; pwd -P )
cd "$parent_path"
cd ../../

# save various paths to variables
MSV000084402=test/data/massive.ucsd.edu/raw/SRM1950_20min_88_01_6950.d
lcms=test/data/massive.ucsd.edu/raw/timsconvert_raw_data/lcms/rs17e_1mgml_1_10_1_1206.d
lcms2=test/data/massive.ucsd.edu/updates/2022-02-28_gbass_dc6ca7c3/raw/timsconvert_raw_data_3/bhi_ms2_1_32_1_552.d
dd1=test/data/massive.ucsd.edu/raw/timsconvert_raw_data/dd
dd2=test/data/massive.ucsd.edu/updates/2022-02-24_gbass_3339138d/raw/timsconvert_raw_data_2
ims=test/data/massive.ucsd.edu/raw/timsconvert_raw_data/ims
plate_map=test/data/massive.ucsd.edu/updates/2022-02-24_gbass_3339138d/raw/timsconvert_raw_data_2/plate_map.csv

out75=test/data/output/75
out76=test/data/output/76
out77=test/data/output/77
out78=test/data/output/78
out79=test/data/output/79
out80=test/data/output/80
out81=test/data/output/81
out82=test/data/output/82
out83=test/data/output/83
out84=test/data/output/84
out85=test/data/output/85

python bin/run.py --input "$lcms" --outdir "$out75" --mode raw --lcms_backend tdf2mzml --verbose
python bin/run.py --input "$lcms" --outdir "$out76" --mode centroid --lcms_backend tdf2mzml --verbose
python bin/run.py --input "$lcms" --outdir "$out77" --mode raw --ms2_only --lcms_backend tdf2mzml --verbose
python bin/run.py --input "$lcms" --outdir "$out78" --mode centroid --ms2_only --lcms_backend tdf2mzml --verbose
python bin/run.py --input "$lcms" --outdir "$out79" --mode profile --ms2_only --lcms_backend tdf2mzml --verbose
python bin/run.py --input "$lcms" --outdir "$out80" --mode raw --exclude_mobility --lcms_backend tdf2mzml --verbose
python bin/run.py --input "$lcms" --outdir "$out81" --mode centroid --exclude_mobility --lcms_backend tdf2mzml --verbose
python bin/run.py --input "$lcms" --outdir "$out82" --mode profile --exclude_mobility --lcms_backend tdf2mzml --verbose
python bin/run.py --input "$lcms" --outdir "$out83" --mode raw --exclude_mobility --ms2_only --lcms_backend tdf2mzml --verbose
python bin/run.py --input "$lcms" --outdir "$out84" --mode centroid --exclude_mobility --ms2_only --lcms_backend tdf2mzml --verbose
python bin/run.py --input "$lcms" --outdir "$out85" --mode profile --exclude_mobility --ms2_only --lcms_backend tdf2mzml --verbose