#!/bin/bash

parent_path=$( cd "$(dirname "${BASH_SOURCE[0]}")" ; pwd -P )
cd "$parent_path"

#if [ ! -d data]; then
#  bash bin/get_data.sh
#fi

# test lcms data
python bin/run.py --input data --experiment lc-tims-ms --outdir data/output --mode raw --verbose
python bin/run.py --input data --experiment lc-tims-ms --outdir data/output --mode centroid --verbose
python bin/run.py --input data --experiment lc-tims-ms --outdir data/output --mode profile --verbose
python bin/run.py --input data --experiment lc-tims-ms --outdir data/output --mode raw --ms2_only --verbose
python bin/run.py --input data --experiment lc-tims-ms --outdir data/output --mode centroid --ms2_only --verbose
python bin/run.py --input data --experiment lc-tims-ms --outdir data/output --mode profile --ms2_only --verbose

# test maldi dd data
python bin/run.py --input data --experiment maldi-dd --outdir data/output --mode raw --maldi_output_file combined --verbose
python bin/run.py --input data --experiment maldi-dd --outdir data/output --mode centroid --maldi_output_file combined --verbose
python bin/run.py --input data --experiment maldi-dd --outdir data/output --mode profile --maldi_output_file combined --verbose
python bin/run.py --input data --experiment maldi-dd --outdir data/output --mode raw --maldi_output_file individual --maldi_plate_map --verbose
python bin/run.py --input data --experiment maldi-dd --outdir data/output --mode centroid --maldi_output_file individual --maldi_plate_map --verbose
python bin/run.py --input data --experiment maldi-dd --outdir data/output --mode profile --maldi_output_file individual --maldi_plate_map --verbose
python bin/run.py --input data --experiment maldi-tims-dd --outdir data/output --mode raw --maldi_output_file combined --verbose
python bin/run.py --input data --experiment maldi-tims-dd --outdir data/output --mode centroid --maldi_output_file combined --verbose
python bin/run.py --input data --experiment maldi-tims-dd --outdir data/output --mode profile --maldi_output_file combined --verbose
python bin/run.py --input data --experiment maldi-tims-dd --outdir data/output --mode raw --maldi_output_file individual --maldi_plate_map --verbose
python bin/run.py --input data --experiment maldi-tims-dd --outdir data/output --mode centroid --maldi_output_file individual --maldi_plate_map --verbose
python bin/run.py --input data --experiment maldi-tims-dd --outdir data/output --mode profile --maldi_output_file individual --maldi_plate_map --verbose

# test maldi ims data
python bin/run.py --input data --experiment maldi-ims --outdir data/output --mode raw --imzml_mode processed --verbose
python bin/run.py --input data --experiment maldi-ims --outdir data/output --mode centroid --imzml_mode processed --verbose
python bin/run.py --input data --experiment maldi-ims --outdir data/output --mode profile --imzml_mode processed --verbose
python bin/run.py --input data --experiment maldi-ims --outdir data/output --mode raw --imzml_mode continuous --verbose
python bin/run.py --input data --experiment maldi-ims --outdir data/output --mode centroid --imzml_mode continuous --verbose
python bin/run.py --input data --experiment maldi-ims --outdir data/output --mode profile --imzml_mode continuous --verbose
python bin/run.py --input data --experiment maldi-tims-ims --outdir data/output --mode raw --imzml_mode processed --verbose
python bin/run.py --input data --experiment maldi-tims-ims --outdir data/output --mode centroid --imzml_mode processed --verbose
python bin/run.py --input data --experiment maldi-tims-ims --outdir data/output --mode profile --imzml_mode processed --verbose
python bin/run.py --input data --experiment maldi-tims-ims --outdir data/output --mode raw --imzml_mode continuous --verbose
python bin/run.py --input data --experiment maldi-tims-ims --outdir data/output --mode centroid --imzml_mode continuous --verbose
python bin/run.py --input data --experiment maldi-tims-ims --outdir data/output --mode profile --imzml_mode continuous --verbose