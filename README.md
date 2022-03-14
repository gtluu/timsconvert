# TIMSCONVERT

## About

TIMSCONVERT is a workflow designed for mass spectrometrists that allows for the conversion of raw data from Bruker timsTOF Pro, fleX, and SCP mass 
spectrometers (i.e. .d directory containing BAF, TDF, and TSF files) to open source data formats (i.e. mzML and imzML)
that:
1. are compatible with downstream open source data analysis platorms.
2. incorporate trapped ion mobility spectrometry (TIMS) data into these open source formats.
3. possess manageable file sizes.
4. do not require any programming experience.

#### Examples for file conversion:
- LC-MS(/MS) (BAF) &#8594; mzML
- LC-TIMS-MS(/MS) (TDF) &#8594; mzML
- MALDI-MS(/MS) Dried Droplet (TSF) &#8594; mzML
- MALDI-MS Imaging Mass Spectrometry (TSF) &#8594; imzML
- MALDI-TIMS-MS(/MS) Dried Droplet (TDF) &#8594; mzML
- MALDI-TIMS-MS Imaging Mass Spectrometry (TDF) &#8594; imzML (does not incorporate ion mobility data)
<br>

#### Examples of data analysis platforms include and are not limited to:
- [Global Natural Products Social (GNPS)](https://gnps.ucsd.edu/)
- [Cardinal MSI](https://cardinalmsi.org/)

Please note that TIMSCONVERT is still actively under development and new changes are being pushed regularly. For the 
version of TIMSCONVERT found in our [bioRxiv preprint](https://www.biorxiv.org/content/10.1101/2021.12.09.472024v1), 
please see the [v1.0.0 branch here on Github](https://github.com/gtluu/timsconvert/tree/manuscript_v1.0.0).

## Installation and Usage

### GNPS Online Workflow

The web version of TIMSCONVERT currently only supports LC-TIMS-MS(/MS) data and can be found here. No installation is 
necessary. All that's required is a GNPS account.

1. Upload your data to GNPS ([instructions](https://ccms-ucsd.github.io/GNPSDocumentation/fileupload/)).
2. Go to the [TIMSCONVERT workflow page](https://proteomics2.ucsd.edu/ProteoSAFe/index.jsp?params=%7b%22workflow%22%3A%20%22TIMSCONVERT%22%7d).
3. Select your dataset and parameters.
4. Submit your run.
5. You will receive an email when your job has completed.

### Setting Up Your Local Environment

If you prefer to run TIMSCONVERT locally via Nextflow or the CLI, you can set up an environment to do so. Please note
that TIMSCONVERT should be run under Linux or Windows Subsystem for Linux (WSL) if using Windows 10.

1. Download and install Anaconda. Follow the prompts to complete installation. Anaconda3-2021.11 is used as an example 
here.
```
wget https://repo.anaconda.com/archive/Anaconda3-2021.11-Linux-x86_64.sh
bash /path/to/Anaconda3-2021.11-Linux-x86_64.sh
```
2. Add ```anaconda3/bin``` to PATH.
```
export PATH=$PATH:/path/to/anaconda3/bin
```
3. Create a conda instance. You must be using Python 3.7. Newer versions of Python are not guaranteed to be compatible 
with Bruker's API in Linux.
```
conda create -n timsconvert python=3.7
```
4. Activate conda environment.
```
conda activate timsconvert
```
5. (Optional, for Nextflow workflow only) Install Nextflow.
```
conda install -c bioconda nextflow
```
6. Download TIMSCONVERT by cloning the Github repo.
```
git clone https://www.github.com/gtluu/timsconvert
```
7. Install dependencies.
```
pip install -r /path/to/timsconvert/requirements.txt
```

### Nextflow Workflow

1. Run the ```nextflow.nf``` script provided in this repo and specify your input directory and experiment type. Unless 
specified, all other default parameters for all other values will be used. See below for an explanation of all 
parameters.
```
nextflow run /path/to/timsconvert/nextflow.nf --input /path/to/your/data
```
2. Depending on the size of your data/number of files, TIMSCONVERT may take some time to finish conversion.


### Command Line Interface

The CLI version of TIMSCONVERT supports conversion of all experimental data types specified above.

1. Use ```bin/run.py``` to run TIMSCONVERT. The input directory and experiment type. Unless specified, all other 
default parameters for all other values will be used. See below for an explanation of all parameters.
```
python3 /path/to/timsconvert/bin/run.py --input /path/to/data
```
2. Depending on the size of your data/number of files, TIMSCONVERT may take some time to finish conversion.

## Parameters
```
Required
--input                   Bruker .d file containing TSF/TDF or directory containing multiple Bruker .d files.

Optional
--outdir                  Path to folder in which to write output file(s). Defaults to .d source folder.
--outfile                 User defined filename for output if converting a single file. If input is a folder
                          with msdultiple .d files, this parameter should not be used as it results in each file
                          overwriting the previous due to having the same filename.
--mode                    Choose whether to export spectra in "raw", "centroid", or "profile" formats. Deafults to
                          "centroid".
--ms2_only                Boolean flag that specifies only MS2 spectra should be converted.
--exclude_mobility        Boolean flag used to exclude trapped ion mobility spectrometry data from exported data. 
                          Precursor ion mobility information is still exported. Recommended when exporting in profile 
                          mode due to file size.
--profile_bins            Number of bins used to bin data when converting in profile mode. A value of 0 indicates no 
                          binning is performed. Defaults to 0.
--encoding                Choose encoding for binary arrays. 32-bit ("32") or 64-bit ("64"). Defaults to 64-bit.
--maldi_output_file       For MALDI dried droplet data, whether individual scans should be placed in
                          individual files ("individual") or all into a single file ("combined").
                          Defaults to combined.
--maldi_plate_map         Plate map to be used for parsing spots if --maldi_output_file == "individual".
                          Should be a .csv file with no header/index.
--imzml_mode              Whether imzML files should be written in "processed" or "continuous" mode. Defaults
                          to "processed".

System
--chunk_size              Relative size of chunks of spectral data that are parsed and subsequently written at
                          once. 
--verbose                 Boolean flag to determine whether to print logging output.
```

## Testing

Get test data
```
cd test/data
sh ./get_data.sh
```

Run workflow
```
sh ./run_validation.sh
```

## Changelog
v 1.0.0
- Initial release.
- Compatibility for ESI and MALDI based experiments.
