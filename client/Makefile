download_test:
	wget -r ftp://massive.ucsd.edu/MSV000084402/raw/SRM1950_20min_88_01_6950.d
	tar -czvf SRM1950_20min_88_01_6950.d.tar.gz -C massive.ucsd.edu/MSV000084402/raw SRM1950_20min_88_01_6950.d

run_test:
	docker-compose exec timsconvert-client python /client/bin/client.py --input SRM1950_20min_88_01_6950.d.tar.gz