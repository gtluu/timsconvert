#!/bin/bash

# change to parent directory
parent_path=$( cd "$(dirname "${BASH_SOURCE[0]}")" ; pwd -P )
cd "$parent_path"
cd ../../

# save various paths to variables
MSV000084402=test/data/massive.ucsd.edu/raw/SRM1950_20min_88_01_6950.d
lcms=test/data/massive.ucsd.edu/raw/timsconvert_raw_data/lcms/rs17e_1mgml_1_10_1_1206.d
dd1=test/data/massive.ucsd.edu/raw/timsconvert_raw_data/dd
dd2=test/data/massive.ucsd.edu/updates/2022-02-24_gbass_3339138d/raw/timsconvert_raw_data_2
ims=test/data/massive.ucsd.edu/raw/timsconvert_raw_data/ims
plate_map=test/data/massive.ucsd.edu/updates/2022-02-24_gbass_3339138d/raw/timsconvert_raw_data_2/plate_map.csv

# output paths
out1=test/data/output/01
out2=test/data/output/02
out3=test/data/output/03
out4=test/data/output/04
out5=test/data/output/05
out6=test/data/output/06
out7=test/data/output/07
out8=test/data/output/08
out9=test/data/output/09
out10=test/data/output/10
out11=test/data/output/11
out12=test/data/output/12
out13=test/data/output/13
out14=test/data/output/14
out15=test/data/output/15
out16=test/data/output/16
out17=test/data/output/17
out18=test/data/output/18
out19=test/data/output/19
out20=test/data/output/20
out21=test/data/output/21
out22=test/data/output/22
out23=test/data/output/23
out24=test/data/output/24
out25=test/data/output/25
out26=test/data/output/26
out27=test/data/output/27
out28=test/data/output/28
out29=test/data/output/29
out30=test/data/output/30
out31=test/data/output/31
out32=test/data/output/32
out33=test/data/output/33
out34=test/data/output/34
out35=test/data/output/35
out36=test/data/output/36
out37=test/data/output/37
out38=test/data/output/38
out39=test/data/output/39
out40=test/data/output/40
out41=test/data/output/41
out42=test/data/output/42
out43=test/data/output/43
out44=test/data/output/44
out45=test/data/output/45
out46=test/data/output/46
out47=test/data/output/47
out48=test/data/output/48
out49=test/data/output/49
out50=test/data/output/50
out51=test/data/output/51
out52=test/data/output/52
out53=test/data/output/53
out54=test/data/output/54
out55=test/data/output/55
out56=test/data/output/56
out57=test/data/output/57
out58=test/data/output/58
out59=test/data/output/59
out60=test/data/output/60
out61=test/data/output/61
out62=test/data/output/62
out63=test/data/output/63
out64=test/data/output/64
out65=test/data/output/65
out66=test/data/output/66
out67=test/data/output/67

python bin/run.py --input "$lcms" --outdir "$out17" --mode raw --exclude_mobility --verbose
python bin/run.py --input "$lcms" --outdir "$out18" --mode centroid --exclude_mobility --verbose
python bin/run.py --input "$lcms" --outdir "$out19" --mode profile --exclude_mobility --verbose

python bin/run.py --input "$dd1" --outdir "$out25" --mode profile --maldi_output_file combined --verbose
