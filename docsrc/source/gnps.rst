GNPS Usage
==========

Using TIMSCONVERT on GNPS
-------------------------
The web version of TIMSCONVERT currently supports various data formats listed below. No installation is necessary. All
that is required is a GNPS account.

1. Upload your data to GNPS using the following `instructions <https://ccms-ucsd.github.io/GNPSDocumentation/fileupload/>`_.
2. Go to the `TIMSCONVERT workflow page <https://proteomics2.ucsd.edu/ProteoSAFe/index.jsp?params=%7b%22workflow%22%3A%20%22TIMSCONVERT%22%7d>`_.
3. Select your dataset.
4. Submit your run.
5. You will receive an email when your job has completed.

Compatible File Types in GNPS TIMSCONVERT Workflow
--------------------------------------------------
.. list-table::
   :header-rows: 1

   * - Acquisition Mode
     - Raw File Format
     - Converted File Format
     - Compatible?
   * - LC-MS(/MS)
     - .d/BAF
     - mzML
     - No
   * - LC-MS(/MS)
     - .d/TSF
     - mzML
     - Yes
   * - LC-TIMS-MS(/MS)
     - .d/TDF
     - mzML
     - Yes
   * - MALDI-MS(/MS) Dried Droplet
     - .d/TSF
     - mzML
     - Yes
   * - MALDI-MS(/MS) Imaging Mass Spectrometry
     - .d/TSF
     - imzML
     - Yes
   * - MALDI-TIMS-MS(/MS) Dried Droplet
     - .d/TDF
     - mzML
     - Yes
   * - MALDI-TIMS-MS(/MS) Imaging Mass Spectrometry
     - .d/TDF
     - imzML
     - Yes
