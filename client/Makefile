BIN=./conda/env/client/bin/

download_test:
	wget -r ftp://massive.ucsd.edu/MSV000088438/updates/2022-05-05_gbass_c9522c16/raw/timsconvert_raw_data_4/mini_tdf_1_1_1_1565.d
	wget -r ftp://massive.ucsd.edu/MSV000088438/raw/timsconvert_raw_data/dd/rs17e_1mgml_no_tims_1_0_C2_MS.d
	wget -r ftp://massive.ucsd.edu/MSV000088438/updates/2022-02-24_gbass_3339138d/raw/timsconvert_raw_data_2/brevi_brachy.d
	wget -r ftp://massive.ucsd.edu/MSV000088438/raw/timsconvert_raw_data/dd/rs17e_1mgml_1_0_C2_MS.d
	wget -r ftp://massive.ucsd.edu/MSV000088438/raw/timsconvert_raw_data/ims/20210920_vc_rugose_1mMTCA_gordon/20210920_vc_rugose_1mMTCA_gordon.d
	wget -r ftp://massive.ucsd.edu/MSV000088438/raw/timsconvert_raw_data/ims/20210921_vc_rugose_tims_gordon/20210921_vc_rugose_tims_gordon.d

run_test:
	mkdir -p spectra
	python3 ./bin/client.py --input massive.ucsd.edu/MSV000088438/updates/2022-05-05_gbass_c9522c16/raw/timsconvert_raw_data_4/mini_tdf_1_1_1_1565.d
	python3 ./bin/client.py --input massive.ucsd.edu/MSV000088438/raw/timsconvert_raw_data/dd/rs17e_1mgml_no_tims_1_0_C2_MS.d
	python3 ./bin/client.py --input massive.ucsd.edu/MSV000088438/updates/2022-02-24_gbass_3339138d/raw/timsconvert_raw_data_2/brevi_brachy.d
	python3 ./bin/client.py --input massive.ucsd.edu/MSV000088438/raw/timsconvert_raw_data/dd/rs17e_1mgml_1_0_C2_MS.d
	python3 ./bin/client.py --input massive.ucsd.edu/MSV000088438/raw/timsconvert_raw_data/ims/20210920_vc_rugose_1mMTCA_gordon/20210920_vc_rugose_1mMTCA_gordon.d
	python3 ./bin/client.py --input massive.ucsd.edu/MSV000088438/raw/timsconvert_raw_data/ims/20210921_vc_rugose_tims_gordon/20210921_vc_rugose_tims_gordon.d

run_nextflow_test:
	nextflow run ../nextflow.nf --input massive.ucsd.edu/MSV000088438/updates/2022-05-05_gbass_c9522c16/raw/timsconvert_raw_data_4/mini_tdf_1_1_1_1565.d --location server
	nextflow run ../nextflow.nf --input massive.ucsd.edu/MSV000088438/raw/timsconvert_raw_data/dd/rs17e_1mgml_no_tims_1_0_C2_MS.d --location server
	nextflow run ../nextflow.nf --input massive.ucsd.edu/MSV000088438/updates/2022-02-24_gbass_3339138d/raw/timsconvert_raw_data_2/brevi_brachy.d --location server
	nextflow run ../nextflow.nf --input massive.ucsd.edu/MSV000088438/raw/timsconvert_raw_data/dd/rs17e_1mgml_1_0_C2_MS.d --location server
	nextflow run ../nextflow.nf --input massive.ucsd.edu/MSV000088438/raw/timsconvert_raw_data/ims/20210920_vc_rugose_1mMTCA_gordon/20210920_vc_rugose_1mMTCA_gordon.d --location server
	nextflow run ../nextflow.nf --input massive.ucsd.edu/MSV000088438/raw/timsconvert_raw_data/ims/20210921_vc_rugose_tims_gordon/20210921_vc_rugose_tims_gordon.d --location server