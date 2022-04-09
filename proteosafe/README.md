## ProteoSAFe Environment Setup

On the GNPS side, to get everything set up for this template workflow, need a few steps:

Installing Conda Enviornment

```
conda create -n timsconvert python=3.7
```

Installing dependencies

```
conda install -n timsconvert -c bioconda nextflow
conda activate timsconvert 
pip install -r requirements.txt
pip install xmltodict requests
```