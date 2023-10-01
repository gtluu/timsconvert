![TIMSCONVERT Logo](imgs/timsconvert_logo.png)

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
doi: [10.1093/bioinformatics/btac419](https://doi.org/10.1093/bioinformatics/btac419).

For more information about timsTOF data formats and TIMSCONVERT, see the 
[documentation](https://gtluu.github.io/timsconvert/).

## Installation

Installation instructions are linked below:
- [Windows](https://gtluu.github.io/timsconvert/installation.html#installing-on-windows)
- [Linux](https://gtluu.github.io/timsconvert/installation.html#installing-on-linux)

Unfortunately, macOS is not compatible with the Bruker TDF-SDK API that is necessary to run TIMSCONVERT.

## Usage

### GNPS TIMSCONVERT Workflow

The [web version of TIMSCONVERT](https://proteomics2.ucsd.edu/ProteoSAFe/index.jsp?params=%7b%22workflow%22%3A%20%22TIMSCONVERT%22%7d) 
currently supports various data formats listed below. No installation is necessary. All that's required is a GNPS 
account. Usage instructions can be found [here](https://gtluu.github.io/timsconvert/gnps.html).

### Using TIMSCONVERT Locally

The CLI version of TIMSCONVERT supports conversion of all experimental data types specified above. The 
```timsconvert``` command can be used to run TIMSCONVERT. Unless specified, all other default values for all other 
parameters will be used.

```
timsconvert --input [path to data]
```

Depending on the size of your data/number of files, TIMSCONVERT may take some time to finish conversion.

See the documentation for more details on [running TIMSCONVERT locally](https://gtluu.github.io/timsconvert/local.html),
a description of the CLI [parameters](https://gtluu.github.io/timsconvert/local.html#parameters), 
and [advanced usage](https://gtluu.github.io/timsconvert/advanced.html) (i.e. Docker, Nextflow).