#!/bin/bash

parent_path=$( cd "$(dirname "${BASH_SOURCE[0]}")" ; pwd -P )
cd "$parent_path"
cd ../../

# test lcms data
python bin/run.py --input test/data/lcms --outdir test/data/output/lcms1 --mode raw --verbose
python bin/run.py --input test/data/lcms --outdir test/data/output/lcms2 --mode centroid --verbose
#python bin/run.py --input test/data/lcms --outdir test/data/output/lcms3 --mode profile --verbose
python bin/run.py --input test/data/lcms --outdir test/data/output/lcms4 --mode raw --ms2_only --verbose
python bin/run.py --input test/data/lcms --outdir test/data/output/lcms5 --mode centroid --ms2_only --verbose
#python bin/run.py --input test/data/lcms --outdir test/data/output/lcms6 --mode profile --ms2_only --verbose

# test maldi dd data
python bin/run.py --input test/data/dd1 --outdir test/data/output/dd11 --mode raw --maldi_output_file combined --verbose
python bin/run.py --input test/data/dd1 --outdir test/data/output/dd12 --mode centroid --maldi_output_file combined --verbose
python bin/run.py --input test/data/dd1 --outdir test/data/output/dd13 --mode profile --maldi_output_file combined --verbose
python bin/run.py --input test/data/dd1 --outdir test/data/output/dd14 --mode raw --ms2_only --maldi_output_file combined --verbose
python bin/run.py --input test/data/dd1 --outdir test/data/output/dd15 --mode centroid --ms2_only --maldi_output_file combined --verbose
python bin/run.py --input test/data/dd1 --outdir test/data/output/dd16 --mode profile --ms2_only --maldi_output_file combined --verbose
python bin/run.py --input test/data/dd2 --outdir test/data/output/dd21 --mode raw --maldi_output_file combined --verbose
python bin/run.py --input test/data/dd2 --outdir test/data/output/dd22 --mode centroid --maldi_output_file combined --verbose
python bin/run.py --input test/data/dd2 --outdir test/data/output/dd23 --mode profile --maldi_output_file combined --verbose
python bin/run.py --input test/data/dd2 --outdir test/data/output/dd24 --mode raw --ms2_only --maldi_output_file combined --verbose
python bin/run.py --input test/data/dd2 --outdir test/data/output/dd25 --mode centroid --ms2_only --maldi_output_file combined --verbose
python bin/run.py --input test/data/dd2 --outdir test/data/output/dd26 --mode profile --ms2_only --maldi_output_file combined --verbose
python bin/run.py --input test/data/dd2 --outdir test/data/output/dd27 --mode raw --maldi_output_file individual --maldi_plate_map test/data/dd2/plate_map_1.csv --verbose
python bin/run.py --input test/data/dd2 --outdir test/data/output/dd28 --mode centroid --maldi_output_file individual --maldi_plate_map test/data/dd2/plate_map_1.csv --verbose
python bin/run.py --input test/data/dd2 --outdir test/data/output/dd29 --mode profile --maldi_output_file individual --maldi_plate_map test/data/dd2/plate_map_1.csv --verbose
python bin/run.py --input test/data/dd2 --outdir test/data/output/dd210 --mode raw --ms2_only --maldi_output_file individual --maldi_plate_map test/data/dd2/plate_map_1.csv --verbose
python bin/run.py --input test/data/dd2 --outdir test/data/output/dd211 --mode centroid --ms2_only --maldi_output_file individual --maldi_plate_map test/data/dd2/plate_map_1.csv --verbose
python bin/run.py --input test/data/dd2 --outdir test/data/output/dd212 --mode profile --ms2_only --maldi_output_file individual --maldi_plate_map test/data/dd2/plate_map_1.csv --verbose

# test maldi ims data
python bin/run.py --input test/data/ims --outdir test/data/output/ims1 --mode raw --imzml_mode processed --verbose
python bin/run.py --input test/data/ims --outdir test/data/output/ims2 --mode centroid --imzml_mode processed --verbose
python bin/run.py --input test/data/ims --outdir test/data/output/ims3 --mode profile --imzml_mode processed --verbose
python bin/run.py --input test/data/ims --outdir test/data/output/ims4 --mode raw --imzml_mode continuous --verbose
python bin/run.py --input test/data/ims --outdir test/data/output/ims5 --mode centroid --imzml_mode continuous --verbose
python bin/run.py --input test/data/ims --outdir test/data/output/ims6 --mode profile --imzml_mode continuous --verbose
