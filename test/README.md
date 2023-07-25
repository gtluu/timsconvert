Test TIMSCONVERT locally

To test this (from this directory)

Download test data

```
make download_test
```

If a conda env has not already set up

```
conda create -n timsconvert python=3.7

conda activate timsconvert

conda install -c bioconda nextflow

pip install -r ../requirements.txt

pip install git+https://github.com/gtluu/pyimzML
```

To test Python CLI workflow

```
make run_test
```


To test nextflow workflow

```
make run_nextflow_test
```