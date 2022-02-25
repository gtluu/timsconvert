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
out68=test/data/output/68
out69=test/data/output/69
out70=test/data/output/70
out71=test/data/output/71
out72=test/data/output/72
out73=test/data/output/73
out74=test/data/output/74
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
out86=test/data/output/86
out87=test/data/output/87
out88=test/data/output/88
out89=test/data/output/89
out90=test/data/output/90
out91=test/data/output/91
out92=test/data/output/92
out93=test/data/output/93
out94=test/data/output/94
out95=test/data/output/95
out96=test/data/output/96
out97=test/data/output/97
out98=test/data/output/98
out99=test/data/output/99
out101=test/data/output/101
out102=test/data/output/102
out103=test/data/output/103
out104=test/data/output/104
out105=test/data/output/105
out106=test/data/output/106
out107=test/data/output/107
out108=test/data/output/108
out109=test/data/output/109
out110=test/data/output/110
out111=test/data/output/111
out112=test/data/output/112
out113=test/data/output/113
out114=test/data/output/114
out115=test/data/output/115
out116=test/data/output/116
out117=test/data/output/117
out118=test/data/output/118
out119=test/data/output/119
out120=test/data/output/120
out121=test/data/output/121
out122=test/data/output/122
out123=test/data/output/123
out124=test/data/output/124
out125=test/data/output/125
out126=test/data/output/126
out127=test/data/output/127
out128=test/data/output/128
out129=test/data/output/129
out130=test/data/output/130
out131=test/data/output/131
out132=test/data/output/132
out133=test/data/output/133
out134=test/data/output/134
out135=test/data/output/135
out136=test/data/output/136

# python
# test lcms
: << 'END'
python bin/run.py --input "$MSV000084402" --outdir "$out1" --mode raw --verbose
python bin/run.py --input "$MSV000084402" --outdir "$out2" --mode centroid --verbose
python bin/run.py --input "$MSV000084402" --outdir "$out3" --mode raw --ms2_only --verbose
python bin/run.py --input "$MSV000084402" --outdir "$out4" --mode centroid --ms2_only --verbose
python bin/run.py --input "$MSV000084402" --outdir "$out5" --mode profile --ms2_only --verbose
python bin/run.py --input "$MSV000084402" --outdir "$out6" --mode raw --exclude_mobility --verbose
python bin/run.py --input "$MSV000084402" --outdir "$out7" --mode centroid --exclude_mobility --verbose
python bin/run.py --input "$MSV000084402" --outdir "$out8" --mode profile --exclude_mobility --verbose
python bin/run.py --input "$MSV000084402" --outdir "$out9" --mode raw --exclude_mobility --ms2_only --verbose
python bin/run.py --input "$MSV000084402" --outdir "$out10" --mode centroid --exclude_mobility --ms2_only --verbose
python bin/run.py --input "$MSV000084402" --outdir "$out11" --mode profile --exclude_mobility --ms2_only --verbose
END

python bin/run.py --input "$lcms" --outdir "$out12" --mode raw --verbose
python bin/run.py --input "$lcms" --outdir "$out13" --mode centroid --verbose
python bin/run.py --input "$lcms" --outdir "$out14" --mode raw --ms2_only --verbose
python bin/run.py --input "$lcms" --outdir "$out15" --mode centroid --ms2_only --verbose
python bin/run.py --input "$lcms" --outdir "$out16" --mode profile --ms2_only --verbose
python bin/run.py --input "$lcms" --outdir "$out17" --mode raw --exclude_mobility --verbose
python bin/run.py --input "$lcms" --outdir "$out18" --mode centroid --exclude_mobility --verbose
python bin/run.py --input "$lcms" --outdir "$out19" --mode profile --exclude_mobility --verbose
python bin/run.py --input "$lcms" --outdir "$out20" --mode raw --exclude_mobility --ms2_only --verbose
python bin/run.py --input "$lcms" --outdir "$out21" --mode centroid --exclude_mobility --ms2_only --verbose
python bin/run.py --input "$lcms" --outdir "$out22" --mode profile --exclude_mobility --ms2_only --verbose

# test maldi dd data
python bin/run.py --input "$dd1" --outdir "$out23" --mode raw --maldi_output_file combined --verbose
python bin/run.py --input "$dd1" --outdir "$out24" --mode centroid --maldi_output_file combined --verbose
python bin/run.py --input "$dd1" --outdir "$out25" --mode profile --maldi_output_file combined --verbose
python bin/run.py --input "$dd1" --outdir "$out26" --mode raw --ms2_only --maldi_output_file combined --verbose
python bin/run.py --input "$dd1" --outdir "$out27" --mode centroid --ms2_only --maldi_output_file combined --verbose
python bin/run.py --input "$dd1" --outdir "$out28" --mode profile --ms2_only --maldi_output_file combined --verbose
python bin/run.py --input "$dd1" --outdir "$out29" --mode raw --exclude_mobility --maldi_output_file combined --verbose
python bin/run.py --input "$dd1" --outdir "$out30" --mode centroid --exclude_mobility --maldi_output_file combined --verbose
python bin/run.py --input "$dd1" --outdir "$out31" --mode profile --exclude_mobility --maldi_output_file combined --verbose
python bin/run.py --input "$dd1" --outdir "$out32" --mode raw --exclude_mobility --ms2_only --maldi_output_file combined --verbose
python bin/run.py --input "$dd1" --outdir "$out33" --mode centroid --exclude_mobility --ms2_only --maldi_output_file combined --verbose
python bin/run.py --input "$dd1" --outdir "$out34" --mode profile --exclude_mobility --ms2_only --maldi_output_file combined --verbose
python bin/run.py --input "$dd2" --outdir "$out35" --mode raw --maldi_output_file combined --verbose
python bin/run.py --input "$dd2" --outdir "$out36" --mode centroid --maldi_output_file combined --verbose
python bin/run.py --input "$dd2" --outdir "$out37" --mode profile --maldi_output_file combined --verbose
python bin/run.py --input "$dd2" --outdir "$out38" --mode raw --ms2_only --maldi_output_file combined --verbose
python bin/run.py --input "$dd2" --outdir "$out39" --mode centroid --ms2_only --maldi_output_file combined --verbose
python bin/run.py --input "$dd2" --outdir "$out40" --mode profile --ms2_only --maldi_output_file combined --verbose
python bin/run.py --input "$dd2" --outdir "$out41" --mode raw --exclude_mobility --maldi_output_file combined --verbose
python bin/run.py --input "$dd2" --outdir "$out42" --mode centroid --exclude_mobility --maldi_output_file combined --verbose
python bin/run.py --input "$dd2" --outdir "$out43" --mode profile --exclude_mobility --maldi_output_file combined --verbose
python bin/run.py --input "$dd2" --outdir "$out44" --mode raw --exclude_mobility --ms2_only --maldi_output_file combined --verbose
python bin/run.py --input "$dd2" --outdir "$out45" --mode centroid --exclude_mobility --ms2_only --maldi_output_file combined --verbose
python bin/run.py --input "$dd2" --outdir "$out46" --mode profile --exclude_mobility --ms2_only --maldi_output_file combined --
python bin/run.py --input "$dd2" --outdir "$out47" --mode raw --maldi_output_file individual --maldi_plate_map "$plate_map" --verbose
python bin/run.py --input "$dd2" --outdir "$out48" --mode centroid --maldi_output_file individual --maldi_plate_map "$plate_map" --verbose
python bin/run.py --input "$dd2" --outdir "$out49" --mode profile --maldi_output_file individual --maldi_plate_map "$plate_map" --verbose
python bin/run.py --input "$dd2" --outdir "$out50" --mode raw --ms2_only --maldi_output_file individual --maldi_plate_map "$plate_map" --verbose
python bin/run.py --input "$dd2" --outdir "$out51" --mode centroid --ms2_only --maldi_output_file individual --maldi_plate_map "$plate_map" --verbose
python bin/run.py --input "$dd2" --outdir "$out52" --mode profile --ms2_only --maldi_output_file individual --maldi_plate_map "$plate_map" --verbose
python bin/run.py --input "$dd2" --outdir "$out53" --mode raw --exclude_mobility --maldi_output_file individual --maldi_plate_map "$plate_map" --verbose
python bin/run.py --input "$dd2" --outdir "$out54" --mode centroid --exclude_mobility --maldi_output_file individual --maldi_plate_map "$plate_map" --verbose
python bin/run.py --input "$dd2" --outdir "$out55" --mode profile --exclude_mobility --maldi_output_file individual --maldi_plate_map "$plate_map" --verbose
python bin/run.py --input "$dd2" --outdir "$out56" --mode raw --exclude_mobility --ms2_only --maldi_output_file individual --maldi_plate_map "$plate_map" --verbose
python bin/run.py --input "$dd2" --outdir "$out57" --mode centroid --exclude_mobility --ms2_only --maldi_output_file individual --maldi_plate_map "$plate_map" --verbose
python bin/run.py --input "$dd2" --outdir "$out58" --mode profile --exclude_mobility --ms2_only --maldi_output_file individual --maldi_plate_map "$plate_map" --verbose

# test maldi ims data
python bin/run.py --input "$ims" --outdir "$out59" --mode raw --imzml_mode processed --verbose
python bin/run.py --input "$ims" --outdir "$out60" --mode centroid --imzml_mode processed --verbose
python bin/run.py --input "$ims" --outdir "$out61" --mode raw --imzml_mode continous --verbose
python bin/run.py --input "$ims" --outdir "$out62" --mode centroid --imzml_mode continuous --verbose
python bin/run.py --input "$ims" --outdir "$out63" --mode raw --exclude_mobility --imzml_mode processed --verbose
python bin/run.py --input "$ims" --outdir "$out64" --mode centroid --exclude_mobility --imzml_mode processed --verbose
python bin/run.py --input "$ims" --outdir "$out65" --mode profile --exclude_mobility --imzml_mode processed --verbose
python bin/run.py --input "$ims" --outdir "$out66" --mode raw --exclude_mobility --imzml_mode continous --verbose
python bin/run.py --input "$ims" --outdir "$out67" --mode centroid --exclude_mobility --imzml_mode continuous --verbose
python bin/run.py --input "$ims" --outdir "$out68" --mode profile --exclude_mobility --imzml_mode continuous --verbose

# nextflow
# test lcms
: << 'END'
nextflow bin/run.py --input "$MSV000084402" --outdir "$out69" --mode raw --verbose
nextflow bin/run.py --input "$MSV000084402" --outdir "$out70" --mode centroid --verbose
nextflow bin/run.py --input "$MSV000084402" --outdir "$out71" --mode raw --ms2_only --verbose
nextflow bin/run.py --input "$MSV000084402" --outdir "$out72" --mode centroid --ms2_only --verbose
nextflow bin/run.py --input "$MSV000084402" --outdir "$out73" --mode profile --ms2_only --verbose
nextflow bin/run.py --input "$MSV000084402" --outdir "$out74" --mode raw --exclude_mobility --verbose
nextflow bin/run.py --input "$MSV000084402" --outdir "$out75" --mode centroid --exclude_mobility --verbose
nextflow bin/run.py --input "$MSV000084402" --outdir "$out76" --mode profile --exclude_mobility --verbose
nextflow bin/run.py --input "$MSV000084402" --outdir "$out77" --mode raw --exclude_mobility --ms2_only --verbose
nextflow bin/run.py --input "$MSV000084402" --outdir "$out78" --mode centroid --exclude_mobility --ms2_only --verbose
nextflow bin/run.py --input "$MSV000084402" --outdir "$out79" --mode profile --exclude_mobility --ms2_only --verbose
END

nextflow bin/run.py --input "$lcms" --outdir "$out80" --mode raw --verbose
nextflow bin/run.py --input "$lcms" --outdir "$out81" --mode centroid --verbose
nextflow bin/run.py --input "$lcms" --outdir "$out82" --mode raw --ms2_only --verbose
nextflow bin/run.py --input "$lcms" --outdir "$out83" --mode centroid --ms2_only --verbose
nextflow bin/run.py --input "$lcms" --outdir "$out84" --mode profile --ms2_only --verbose
nextflow bin/run.py --input "$lcms" --outdir "$out85" --mode raw --exclude_mobility --verbose
nextflow bin/run.py --input "$lcms" --outdir "$out86" --mode centroid --exclude_mobility --verbose
nextflow bin/run.py --input "$lcms" --outdir "$out87" --mode profile --exclude_mobility --verbose
nextflow bin/run.py --input "$lcms" --outdir "$out88" --mode raw --exclude_mobility --ms2_only --verbose
nextflow bin/run.py --input "$lcms" --outdir "$out89" --mode centroid --exclude_mobility --ms2_only --verbose
nextflow bin/run.py --input "$lcms" --outdir "$out90" --mode profile --exclude_mobility --ms2_only --verbose

# test maldi dd data
nextflow bin/run.py --input "$dd1" --outdir "$out91" --mode raw --maldi_output_file combined --verbose
nextflow bin/run.py --input "$dd1" --outdir "$out92" --mode centroid --maldi_output_file combined --verbose
nextflow bin/run.py --input "$dd1" --outdir "$out93" --mode profile --maldi_output_file combined --verbose
nextflow bin/run.py --input "$dd1" --outdir "$out94" --mode raw --ms2_only --maldi_output_file combined --verbose
nextflow bin/run.py --input "$dd1" --outdir "$out95" --mode centroid --ms2_only --maldi_output_file combined --verbose
nextflow bin/run.py --input "$dd1" --outdir "$out96" --mode profile --ms2_only --maldi_output_file combined --verbose
nextflow bin/run.py --input "$dd1" --outdir "$out97" --mode raw --exclude_mobility --maldi_output_file combined --verbose
nextflow bin/run.py --input "$dd1" --outdir "$out98" --mode centroid --exclude_mobility --maldi_output_file combined --verbose
nextflow bin/run.py --input "$dd1" --outdir "$out99" --mode profile --exclude_mobility --maldi_output_file combined --verbose
nextflow bin/run.py --input "$dd1" --outdir "$out100" --mode raw --exclude_mobility --ms2_only --maldi_output_file combined --verbose
nextflow bin/run.py --input "$dd1" --outdir "$out101" --mode centroid --exclude_mobility --ms2_only --maldi_output_file combined --verbose
nextflow bin/run.py --input "$dd1" --outdir "$out102" --mode profile --exclude_mobility --ms2_only --maldi_output_file combined --verbose
nextflow bin/run.py --input "$dd2" --outdir "$out103" --mode raw --maldi_output_file combined --verbose
nextflow bin/run.py --input "$dd2" --outdir "$out104" --mode centroid --maldi_output_file combined --verbose
nextflow bin/run.py --input "$dd2" --outdir "$out105" --mode profile --maldi_output_file combined --verbose
nextflow bin/run.py --input "$dd2" --outdir "$out106" --mode raw --ms2_only --maldi_output_file combined --verbose
nextflow bin/run.py --input "$dd2" --outdir "$out107" --mode centroid --ms2_only --maldi_output_file combined --verbose
nextflow bin/run.py --input "$dd2" --outdir "$out108" --mode profile --ms2_only --maldi_output_file combined --verbose
nextflow bin/run.py --input "$dd2" --outdir "$out109" --mode raw --exclude_mobility --maldi_output_file combined --verbose
nextflow bin/run.py --input "$dd2" --outdir "$out110" --mode centroid --exclude_mobility --maldi_output_file combined --verbose
nextflow bin/run.py --input "$dd2" --outdir "$out111" --mode profile --exclude_mobility --maldi_output_file combined --verbose
nextflow bin/run.py --input "$dd2" --outdir "$out112" --mode raw --exclude_mobility --ms2_only --maldi_output_file combined --verbose
nextflow bin/run.py --input "$dd2" --outdir "$out113" --mode centroid --exclude_mobility --ms2_only --maldi_output_file combined --verbose
nextflow bin/run.py --input "$dd2" --outdir "$out114" --mode profile --exclude_mobility --ms2_only --maldi_output_file combined --
nextflow bin/run.py --input "$dd2" --outdir "$out115" --mode raw --maldi_output_file individual --maldi_plate_map "$plate_map" --verbose
nextflow bin/run.py --input "$dd2" --outdir "$out116" --mode centroid --maldi_output_file individual --maldi_plate_map "$plate_map" --verbose
nextflow bin/run.py --input "$dd2" --outdir "$out117" --mode profile --maldi_output_file individual --maldi_plate_map "$plate_map" --verbose
nextflow bin/run.py --input "$dd2" --outdir "$out118" --mode raw --ms2_only --maldi_output_file individual --maldi_plate_map "$plate_map" --verbose
nextflow bin/run.py --input "$dd2" --outdir "$out119" --mode centroid --ms2_only --maldi_output_file individual --maldi_plate_map "$plate_map" --verbose
nextflow bin/run.py --input "$dd2" --outdir "$out120" --mode profile --ms2_only --maldi_output_file individual --maldi_plate_map "$plate_map" --verbose
nextflow bin/run.py --input "$dd2" --outdir "$out121" --mode raw --exclude_mobility --maldi_output_file individual --maldi_plate_map "$plate_map" --verbose
nextflow bin/run.py --input "$dd2" --outdir "$out122" --mode centroid --exclude_mobility --maldi_output_file individual --maldi_plate_map "$plate_map" --verbose
nextflow bin/run.py --input "$dd2" --outdir "$out123" --mode profile --exclude_mobility --maldi_output_file individual --maldi_plate_map "$plate_map" --verbose
nextflow bin/run.py --input "$dd2" --outdir "$out124" --mode raw --exclude_mobility --ms2_only --maldi_output_file individual --maldi_plate_map "$plate_map" --verbose
nextflow bin/run.py --input "$dd2" --outdir "$out125" --mode centroid --exclude_mobility --ms2_only --maldi_output_file individual --maldi_plate_map "$plate_map" --verbose
nextflow bin/run.py --input "$dd2" --outdir "$out126" --mode profile --exclude_mobility --ms2_only --maldi_output_file individual --maldi_plate_map "$plate_map" --verbose

# test maldi ims data
nextflow bin/run.py --input "$ims" --outdir "$out127" --mode raw --imzml_mode processed --verbose
nextflow bin/run.py --input "$ims" --outdir "$out128" --mode centroid --imzml_mode processed --verbose
nextflow bin/run.py --input "$ims" --outdir "$out129" --mode raw --imzml_mode continous --verbose
nextflow bin/run.py --input "$ims" --outdir "$out130" --mode centroid --imzml_mode continuous --verbose
nextflow bin/run.py --input "$ims" --outdir "$out131" --mode raw --exclude_mobility --imzml_mode processed --verbose
nextflow bin/run.py --input "$ims" --outdir "$out132" --mode centroid --exclude_mobility --imzml_mode processed --verbose
nextflow bin/run.py --input "$ims" --outdir "$out133" --mode profile --exclude_mobility --imzml_mode processed --verbose
nextflow bin/run.py --input "$ims" --outdir "$out134" --mode raw --exclude_mobility --imzml_mode continous --verbose
nextflow bin/run.py --input "$ims" --outdir "$out135" --mode centroid --exclude_mobility --imzml_mode continuous --verbose
nextflow bin/run.py --input "$ims" --outdir "$out136" --mode profile --exclude_mobility --imzml_mode continuous --verbose
