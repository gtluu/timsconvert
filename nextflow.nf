#!~/bin nextflow

// params

// required params
params.input = ''

params.mode = 'centroid'  // mode can be 'centroid', 'profile', or 'raw'
params.ms2_only = false  // only convert ms2 spectra
params.encoding = 64
params.maldi_output_file = 'combined' // choose whether MALDI spectra are output to individual files or a single combined file
params.maldi_plate_map = ''
params.imzml_mode = 'processed'

// system params
params.chunk_size = 10
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
        --mode ${params.mode} \
        ${ms2_flag} \
        --encoding ${params.encoding} \
        --maldi_output_file ${params.maldi_output_file} \
        --imzml_mode ${params.imzml_mode} \
        --chunk_size ${params.chunk_size} \
        ${verbose_flag}
        """

    else if (params.maldi_plate_map != '')
        """
        mkdir spectra
        python3 $TOOL_FOLDER/run.py \
        --input $input_file \
        --outdir spectra \
        --mode ${params.mode} \
        ${ms2_flag} \
        --encoding ${params.encoding} \
        --maldi_output_file ${params.maldi_output_file} \
        --maldi_plate_map = ${params.maldi_plate_map} \
        --imzml_mode ${params.imzml_mode} \
        --chunk_size ${params.chunk_size} \
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


