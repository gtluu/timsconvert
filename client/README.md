This is the client to interact with the server to send over a file to be converted. 

To test this

```
make download_test
```

Install requirements if needed
```
pip install -r requirements.txt
```


```
make run_test
```


If nextflow is not already installed, an environment should be created and nextflow should be installed.
```
conda create --prefix ./conda/env/client python=3.7

conda activate ./conda/env/client

pip install requests pandas

conda install -c bioconda nextflow

nextflow
```

To test nextflow workflow

```
make run_nextflow_test
```