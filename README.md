# TIMSCONVERT

## About

TIMSCONVERT is a workflow designed for mass spectrometrists that allows for the conversion of raw data from Bruker 
timsTOF Pro and fleX mass spectrometers (i.e. .d directory containing BAF, TDF, and TSF files) to open source 
data formats (i.e. mzML and imzML) that:
1. are compatible with downstream open source data analysis platorms.
2. incorporate trapped ion mobility spectrometry (TIMS) data into these open source formats.
3. do not require any programming experience.

If you use TIMSCONVERT, please cite us:

Gordon T. Luu, Michael A. Freitas, Itzel Lizama-Chamu, Catherine S. McCaughey, Laura M. Sanchez, Mingxun Wang. (2022). 
TIMSCONVERT: A workflow to convert trapped ion mobility data to open formats. *Bioinformatics*; btac419. 
DOI: [10.1093/bioinformatics/btac419](https://doi.org/10.1093/bioinformatics/btac419).

#### Examples for file conversion:

- LC-MS(/MS) (BAF or TSF) &#8594; mzML
- LC-TIMS-MS(/MS) (TDF) &#8594; mzML
- MALDI-MS(/MS) Dried Droplet (TSF) &#8594; mzML
- MALDI-MS Imaging Mass Spectrometry (TSF) &#8594; imzML
- MALDI-TIMS-MS(/MS) Dried Droplet (TDF) &#8594; mzML
- MALDI-TIMS-MS Imaging Mass Spectrometry (TDF) &#8594; imzML (does not incorporate ion mobility data)
<br>

#### Examples of data analysis platforms include and are not limited to:

- [Global Natural Products Social (GNPS)](https://gnps.ucsd.edu/)
- [Cardinal MSI](https://cardinalmsi.org/)

Please note that TIMSCONVERT is still actively under development and new changes are being pushed regularly.

## Dimensionality of timsTOF Data

Example of dimensionality of LC-TIMS-MS/MS data and a simplified corresponding mzML schema. Elements in the simplified 
mzML schema are color coded by the corresponding data in the chromatograms/spectra. At a given retention time in the 
chromatogram (indicated in pink), an MS1 spectrum may be visualized in the form of a three dimensional plot generated 
from m/z, intensity, and ion mobility arrays (indicated in orange). Precursor ions of interest found in MS1 spectra 
(indicated in purple) can be further analyzed by plotting m/z and intensity arrays for MS/MS spectra (indicated in 
teal). These spectral identifiers (i.e. retention time, precursor m/z, precursor 1/K0) may be used to locate the 
corresponding MS/MS spectrum from Bruker DataAnalysis or other data visualization software of choice.

![timsTOF Data mzML](imgs/dimensions.png)

## Installation and Usage

### GNPS TIMSCONVERT Workflow

The web version of TIMSCONVERT currently supports various data formats listed below. No installation is necessary. All 
that's required is a GNPS account.

1. Upload your data to GNPS ([instructions](https://ccms-ucsd.github.io/GNPSDocumentation/fileupload/)).
2. Go to the [TIMSCONVERT workflow page](https://proteomics2.ucsd.edu/ProteoSAFe/index.jsp?params=%7b%22workflow%22%3A%20%22TIMSCONVERT%22%7d).
3. Select your dataset.
4. Submit your run.
5. You will receive an email when your job has completed.

#### Compatible file types in GNPS TIMSCONVERT Workflow

| Acquisition Mode                        | Raw File Format | Converted File Format | Compatible?        |
|-----------------------------------------|-----------------|-----------------------|--------------------|
| LC-MS(/MS)                              | .d/BAF          | mzML                  | :x:                |
| LC-MS(/MS)                              | .d/TSF          | mzML                  | :x:                |
| LC-TIMS-MS(/MS)                         | .d/TDF          | mzML                  | :heavy_check_mark: |
| MALDI-MS(/MS) Dried Droplet             | .d/TSF          | mzML                  | :heavy_check_mark: |
| MALDI-MS Imaging Mass Spectrometry      | .d/TSF          | imzML                 | :heavy_check_mark: |
| MALDI-TIMS-MS(/MS) Dried Droplet        | .d/TDF          | mzML                  | :heavy_check_mark: |
| MALDI-TIMS-MS Imaging Mass Spectrometry | .d/TDF          | imzML                 | :heavy_check_mark: |

### Setting Up Your Local Environment

If you prefer to run TIMSCONVERT locally via Nextflow or the CLI, you can set up an environment to do so. Please note
that TIMSCONVERT should be run under Linux or Windows. macOS is not supported.

#### Install Anaconda on Linux

1. Download and install Anaconda for [Linux](https://repo.anaconda.com/archive/Anaconda3-2021.11-Linux-x86_64.sh). 
Follow the prompts to complete installation. Anaconda3-2021.11 for Linux is used as an example here.
```
wget https://repo.anaconda.com/archive/Anaconda3-2021.11-Linux-x86_64.sh
bash /path/to/Anaconda3-2021.11-Linux-x86_64.sh
```
2. Add ```anaconda3/bin``` to PATH.
```
export PATH=$PATH:/path/to/anaconda3/bin
```

#### Install Anaconda on Windows.

1. Download and install Anaconda for [Windows](https://repo.anaconda.com/archive/Anaconda3-2021.11-Windows-x86_64.exe). 
Follow the prompts to complete installation.
2. Run ```Anaconda Prompt (R-MINI~1)``` as Administrator.

#### Set Up ```conda env```

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

#### Install TIMSCONVERT

6. Download TIMSCONVERT by cloning the Github repo (you will need to have [Git](https://git-scm.com/downloads) and 
ensure that the option to enable symbolic links was checked during installation). It may be necessary to explicitly
allow for the use of symbolic links by adding the ```-c core.symlinks=true``` parameter on Windows.
```
git clone https://www.github.com/gtluu/timsconvert
or
git clone -c core.symlinks=true https://www.github.com/gtluu/timsconvert
```
7. Install dependencies.
```
# TIMSCONVERT dependencies
pip install -r /path/to/timsconvert/requirements.txt
```
8. You will also need to install our forked version of pyimzML, which has added support for ion mobility arrays in imzML
 data from imaging mass spectrometry experiments.
```
pip install git+https://github.com/gtluu/pyimzML
```

### Nextflow Workflow

A Nextflow workflow has been provided to run TIMSCONVERT.

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
python /path/to/timsconvert/bin/run.py --input /path/to/data
or
python3 /path/to/timsconvert/bin/run.py --input /path/to/data
```
2. Depending on the size of your data/number of files, TIMSCONVERT may take some time to finish conversion.

### Docker

A Dockerfile has also been provided to run TIMSCONVERT inside a Docker container.

1. Build the Docker image.
```
docker build --tag timsconvert -f /path/to/timsconvert/Dockerfile .
```
2. Run the Docker image in a container.
```
docker run --rm -it -v /path/to/data:/data timsconvert --input /data --outdir /data
```

## Parameters

```
Required Parameters
--input                   Filepath for Bruker .d file containing TSF or TDF file or directory containing multiple 
                          Bruker .d files.

Optional Parameters
--outdir                  Path to folder in which to write output file(s). Default = none.
--outfile                 User defined filename for output if converting a single file, otherwise files will have same 
                          filename and overwrite each other. Default is none.
--mode                    Choose whether export to spectra in "raw" or "centroid" formats. Defaults to "centroid".
--compression             Choose between ZLIB compression ("zlib") or no compression ("none"). Defaults to "zlib".

TIMSCONVERT Optional Parameters
--ms2_only                Boolean flag that specifies only MS2 spectra should be converted.
--exclude_mobility        Boolean flag used to exclude trapped ion mobility spectrometry data from exported data. 
                          Precursor ion mobility information is still exported.
--encoding                Choose encoding for binary arrays: 32-bit ("32") or 64-bit ("64"). Defaults to 64-bit.
--profile_bins            Number of bins used to bin data when converting in profile mode. A value of 0 indicates no 
                          binning is performed. Defaults to 0.
--barebones_metadata      Only use basic mzML metadata. Use if downstream data analysis tools throw errors with 
                          descriptive CV terms.
--maldi_output_file       For MALDI dried droplet data, whether individual scans should be placed in individual files 
                          ("individual"), combined into a single file ("combined"), or combined by sample label 
                          ("sample"). Defaults to "combined".
--maldi_plate_map         Plate map to be used for parsing spots if --maldi_output_file == "individual" or 
                          --maldi_output_file == "sample". Should be a .csv file with no header/index.
--imzml_mode              Whether .imzML files should be written in "processed" or "continuous" mode. Defaults to 
                          "processed".

TIMSCONVERT System Parameters
--lcms_backend            Choose whether to use "timsconvert" or "tdf2mzml" backend for LC-TIMS-MS/MS data conversion.
--chunk_size              Relative size of chunks of spectral data that are parsed and subsequently written at once. 
                          Increasing parses and write more spectra at once but increases RAM usage. Default = 10.
--verbose                 Boolean flag to determine whether to print logging output.

tdf2mzml Optional Parameters
--start_frame             Start frame.
--end_frame               End frame.
--precision               Precision.
--ms1_threshold           Intensity threshold for MS1 data.
--ms2_threshold           Intensity threshold for MS2 data.
--ms2_nlargest            N Largest MS2.
```

## Testing

To test TIMSCONVERT locally:

Download test data
```
cd test
make download_test
```

To test Python CLI workflow
```
cd test
make run_test
```

To test nextflow workflow
```
cd test
make run_nextflow_test
```

## Changelog
v 1.0.0
- Initial release.
- Compatibility for ESI and MALDI based experiments.
