![TIMSCONVERT Logo](imgs/timsconvert_logo.png)

## About

TIMSCONVERT is a workflow designed for mass spectrometrists that allows for the conversion of raw data from Bruker
timsTOF series mass spectrometers (i.e. Pro, fleX, SCP, HT, etc.) to open data formats (i.e. mzML and imzML) that:

1. are compatible with downstream open source data analysis platforms.
2. incorporate trapped ion mobility spectrometry (TIMS) data into these open formats.
3. does not require any programming experience.

If you use TIMSCONVERT, please cite us:

Gordon T. Luu, Michael A. Freitas, Itzel Lizama-Chamu, Catherine S. McCaughey, Laura M. Sanchez, Mingxun Wang. (2022). 
TIMSCONVERT: A workflow to convert trapped ion mobility data to open formats. *Bioinformatics*; btac419. 
doi: [10.1093/bioinformatics/btac419](https://doi.org/10.1093/bioinformatics/btac419).

For more information about timsTOF data formats and TIMSCONVERT, see the 
[documentation](https://gtluu.github.io/timsconvert/).

Included software components: Copyright © 2022 by Bruker Daltonics GmbH & Co. KG. All rights reserved

## Installation

Installation instructions are linked below:
- [Windows](https://gtluu.github.io/timsconvert/installation.html#installing-on-windows)
- [Linux](https://gtluu.github.io/timsconvert/installation.html#installing-on-linux)

macOS is not compatible with the Bruker TDF-SDK API that is necessary to run TIMSCONVERT.

## Usage

The GUI version of TIMSCONVERT can be run by downloading it from 
[the Github releases page for this repo](https://github.com/gtluu/timsconvert/releases). Unzip the file and run 
```TIMSCONVERT.exe```.

Alternatively, the TIMSCONVERT GUI can be started after installing to your own Python virtual environment using the 
```timsconvert_gui``` command.

```timsconvert_gui```

The CLI version of TIMSCONVERT can be run using the ```timsconvert``` command. Unless specified, all other default 
values for all other parameters will be used.

```
timsconvert --input [path to data]
```

Depending on the size of your data/number of files, TIMSCONVERT may take some time to finish conversion.

See the documentation for more details on [running TIMSCONVERT locally](https://gtluu.github.io/timsconvert/local.html),
a description of the [parameters](https://gtluu.github.io/timsconvert/local.html#parameters), 
and [advanced usage](https://gtluu.github.io/timsconvert/advanced.html).
