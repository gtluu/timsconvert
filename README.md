# TIMSCONVERT

## About

TIMSCONVERT is a workflow that allows for the conversion of raw data from Bruker timsTOF Pro, fleX, and SCP mass 
spectrometers (i.e. .d directory containing TDF and TSF files) to open source data formats (i.e. mzML and imzML).
Examples for file conversion include:
<br>
- LC-TIMS-MS(/MS) (TDF) &#8594; mzML
- MALDI-MS(/MS) Dried Droplet (TSF) &#8594; mzML
- MALDI-MS Imaging Mass Spectrometry (TSF) &#8594; imzML
- MALDI-TIMS-MS(/MS) Dried Droplet (TDF) &#8594; mzML
- MALDI-TIMS-MS Imaging Mass Spectrometry (TDF) &#8594; imzML (does not incorporate ion mobility data)

## Installation and Usage

### GNPS Online Workflow

The web version of TIMSCONVERT currently only supports LC-TIMS-MS(/MS) data and can be found here. No installation is 
necessary. All that's required is a GNPS account.

1. Upload your data to GNPS ([instructions](https://ccms-ucsd.github.io/GNPSDocumentation/fileupload/)).
2. Go to the [TIMSCONVERT workflow page]().
3. Select your dataset and parameters.
4. Submit your run.

### Nextflow Workflow

Similar to the web version, the Nextflow workflow for TIMSCONVERT only supports LC-TIMS-MS(/MS) data currently.

1. Create a conda instance.
```
conda create -n timsconvert python=3.8
```
2. Install Nextflow.
```
conda install -c bioconda nextflow
```
3. Install dependencies.
```
pip install -r requirements.txt
```
4. Run the ```nextflow.nf``` script provided in this repo and specify your input directory. Unless specified, all other 
default parameters for all other values will be used.
```
nextflow run nextflow.nf --input /path/to/your/data
```
5. Depending on the size of your data/number of files, TIMSCONVERT may take some time to finish conversion.

### Command Line Interface

The CLI version of TIMSCONVERT supports conversion of all experimental data types specified above.

1. Download and unzip the [CLI version](https://github.com/gtluu/timsconvert/archive/refs/heads/main.zip) of TIMSCONVERT.
2. Install dependencies.
```
pip install -r requirements.txt
```
3. Use ```bin/run.py``` to run TIMSCONVERT and pass through required/desired parameters.
```
python3 /path/to/timsconvert_folder/bin/run.py --input /path/to/data
```

## Parameters
```
Required
--input : Bruker .d file containing TSF/TDF or directory containing multiple Bruker .d files.

Optional
--outdir : Path to folder in which to write output file(s). Defaults to .d source folder.
--outfile : User defined filename for output if converting a single file. If input is a folder
            with multiple .d files, this parameter should not be used as it results in each file
            overwriting the previous due to having the same filename.
--ms2_only : Boolean flag that specifies only MS2 spectra should be converted.
--ms1_groupby : Define whether an individual spectrum contains one frame (and multiple scans;
                "frame") or one scan only ("scan"). Defaults to "scan".
--encoding : Choose encoding for binary arrays. 32-bit ("32") or 64-bit ("64"). Defaults to 64-bit.
--maldi_output_file : For MALDI dried droplet data, whether individual scans should be placed in
                      individual files ("individual") or all into a single file ("combined").
                      Defaults to combined.
--maldi_plate_map : Plate map to be used for parsing spots if --maldi_output_file == "individual".
                    Should be a .csv file with no header/index.
--imzml_mode : Whether imzML files should be written in "processed" or "continuous" mode. Defaults
               to "processed".

System
--verbose : Boolean flag to determine whether to print logging output.
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

## Changelog
v 1.0.0
- Initial release.