download_test:
	wget -r ftp://massive.ucsd.edu/MSV000088438/raw/timsconvert_raw_data/lcms/rs17e_1mgml_1_10_1_1206.d
	tar -czvf lc_tims_msms.d.tar.gz -C massive.ucsd.edu/MSV000088438/raw/timsconvert_raw_data/lcms rs17e_1mgml_1_10_1_1206.d

	wget -r ftp://massive.ucsd.edu/MSV000088438/raw/timsconvert_raw_data/dd/rs17e_1mgml_no_tims_1_0_C2_MS.d
	tar -czvf maldi_qtof_dd.d.tar.gz -C massive.ucsd.edu/MSV000088438/raw/timsconvert_raw_data/dd rs17e_1mgml_no_tims_1_0_C2_MS.d

	wget -r ftp://massive.ucsd.edu/MSV000088438/updates/2022-02-24_gbass_3339138d/raw/timsconvert_raw_data_2/brevi_brachy.d
	tar -czvf maldi_qtof_dd_autox.d.tar.gz -C massive.ucsd.edu/MSV000088438/updates/2022-02-24_gbass_3339138d/raw/timsconvert_raw_data_2 brevi_brachy.d

	wget -r ftp://massive.ucsd.edu/MSV000088438/raw/timsconvert_raw_data/dd/rs17e_1mgml_1_0_C2_MS.d
	tar -czvf maldi_tims_qtof_dd.d.tar.gz -C massive.ucsd.edu/MSV000088438/raw/timsconvert_raw_data/dd rs17e_1mgml_1_0_C2_MS.d

	wget -r ftp://massive.ucsd.edu/MSV000088438/raw/timsconvert_raw_data/ims/20210920_vc_rugose_1mMTCA_gordon/20210920_vc_rugose_1mMTCA_gordon.d
	tar -czvf maldi_qtof_msi.d.tar.gz -C massive.ucsd.edu/MSV000088438/raw/timsconvert_raw_data/ims/20210920_vc_rugose_1mMTCA_gordon 20210920_vc_rugose_1mMTCA_gordon.d

	wget -r ftp://massive.ucsd.edu/MSV000088438/raw/timsconvert_raw_data/ims/20210921_vc_rugose_tims_gordon/20210921_vc_rugose_tims_gordon.d
	tar -czvf maldi_tims_qtof_msi.d.tar.gz -C massive.ucsd.edu/MSV000088438/raw/timsconvert_raw_data/ims/20210921_vc_rugose_tims_gordon 20210921_vc_rugose_tims_gordon.d

run_test:
	python ./bin/client.py --input lc_tims_msms.d.tar.gz
	python ./bin/client.py --input maldi_qtof_dd.d.tar.gz
	python ./bin/client.py --input maldi_qtoof_dd_autox.d.tar.gz
	python ./bin/client.py --input maldi_tims_qtof_dd.d.tar.gz
	python ./bin/client.py --input maldi_qtof_msi.d.tar.gz
	python ./bin/client.py --input maldi_tims_qtof_msi.d.tar.gz