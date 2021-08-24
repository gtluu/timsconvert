# alphatims_test
package scripts in tims_converter folder, prototype scripts in prototype folder
<br/>
tdf_to_mzml_v4.py was used to convert mzML files in successful classical GNPS runs:
<br/>
[mzML files with no MS1 scans and centroided MS2 scans](https://gnps.ucsd.edu/ProteoSAFe/status.jsp?task=2358c2cbc8e743239fda19073d1340a8)
<br/>
[mzML files with profile MS1 scans and centroided MS2 scans](https://gnps.ucsd.edu/ProteoSAFe/status.jsp?task=6afc839728334b18a713e53876e8df73)


## Requirements

Create a conda instance 

```
conda create -n alphatims python=3.8
```

Install Nextflow
```
conda install -c bioconda nextflow
```


Install dependencies

```
pip install -r requirements.txt
```

## Testing

Get test data

```
cd test/data
sh ./get_data.sh
```

Run workflow

```
make run_test
```