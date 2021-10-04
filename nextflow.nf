#!~/bin nextflow

// params

// required params
params.input = 'test/data/massive.ucsd.edu/MSV000084402/raw/SRM1950_20min_88_01_6950.d' 
// should be replaced with Bruker .d directory or folder containing .d directories

params.ms2_only = true  // only convert ms2 spectra?
params.ms1_groupby = 'scan'  // group ms1 spectra by 'frame' (will have array of mobilities; in beta) or 'scan' (each spectrum has one RT and mobility)
params.encoding = 64
params.maldi_output_file = 'combined' // choose whether MALDI spectra are output to individual files or a single combined file
params.maldi_plate_map = ''
params.imzml_mode = 'processed'
params.verbose = true

input_ch = Channel.fromPath(params.input, type:'dir', checkIfExists: true)

// Boiler Plate
TOOL_FOLDER = "$baseDir/bin"
params.publishdir = "nf_output"

// Process
process convert {
    publishDir "$params.publishdir", mode: 'copy'

    input:
    file input_file from input_ch

    output:
    file "spectra/*mzML" into _spectra_ch

    script:
    def ms2_flag = params.ms2_only == true ? "--ms2_only" : ''
    def verbose_flag = params.verbose == true ? "--verbose" : ''

    if (params.maldi_plate_map == '')
        """
        mkdir spectra
        python3 $TOOL_FOLDER/run.py \
        --input $input_file \
        --outdir spectra \
        ${ms2_flag} \
        --ms1_groupby ${params.ms1_groupby} \
        --encoding ${params.encoding} \
        --maldi_output_file ${params.maldi_output_file} \
        --imzml_mode = ${params.imzml_mode} \
        ${verbose_flag}
        """

    else if (params.maldi_plate_map != '')
        """
        mkdir spectra
        python3 $TOOL_FOLDER/run.py \
        --input $input_file \
        --outdir spectra \
        ${ms2_flag} \
        --ms1_groupby ${params.ms1_groupby} \
        --encoding ${params.encoding} \
        --maldi_output_file ${params.maldi_output_file} \
        --maldi_plate_map = ${params.maldi_plate_map} \
        --imzml_mode = ${params.imzml_mode} \
        ${verbose_flag}
        """
}

process summarize {
    publishDir "$params.publishdir", mode: 'copy'

    input:
    file "spectra/*" from _spectra_ch.collect()

    output:
    file "results_file.tsv"

    """
    python3 $TOOL_FOLDER/summarize.py \
    spectra \
    results_file.tsv
    """
}


