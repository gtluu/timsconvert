run_test:
	parent_path=$( cd "$(dirname "${BASH_SOURCE[0]}")" ; pwd -P )
	cd "$parent_path"
	cd ../../
	wget -r -l=0 -P "$parent_path" --ftp-user=MSV000084402 --ftp-password=a ftp://massive.ucsd.edu
	MSV000084402=test/data/massive.ucsd.edu/raw/SRM1950_20min_88_01_6950.d
	python submit_timsconvert_job.py --input "$MSV000084402 --verbose