#!~/bin nextflow

nextflow.enable.dsl=2

// params

// required params
params.input = ''

// optional params
params.mode = 'centroid'  // mode can be 'centroid' or 'raw'
params.compression = 'zlib' // zlib or none

// timsconvert params
params.ms2_only = 'False'  // only convert ms2 spectra?
params.exclude_mobility = 'True'  // exclude mobility arrays from MS1 spectra?
params.encoding = 64  // 64 or 32 bit encoding
params.barebones_metadata = 'False'  // only use barebones metadata if downstream tools are not compatible with timstof cv params
params.maldi_output_file = 'combined' // choose whether MALDI spectra are output to individual files, a single combined file with multiple spectra, or grouped by sample via maldi_plate_map
params.maldi_plate_map = ''
params.imzml_mode = 'processed'

// timsconvert system params
params.chunk_size = 10
params.verbose = 'True'

// local or GNPS server
// choose whether to run locally or via GNPS servers ('local' or 'server')
params.location = 'local'

// Boiler Plate
TOOL_FOLDER = "$baseDir/bin"
CLIENT_FOLDER = "$baseDir/client/bin"
params.publishdir = "nf_output"

// Process
process convert {
    publishDir "$params.publishdir", mode: 'copy'

    input:
    file input_file

    output:
    file "spectra/*"

    script:
    def ms2_flag = params.ms2_only == 'True' ? "--ms2_only" : ''
    def verbose_flag = params.verbose == 'True' ? "--verbose" : ''
    def exclude_mobility_flag = params.exclude_mobility == 'True' ? "--exclude_mobility" : ''
    def barebones_metadata_flag = params.barebones_metadata == 'True' ? "--barebones_metadata" : ''

    if (params.location == 'local') {
        if (params.maldi_plate_map == '') {
            """
            mkdir spectra
            python3 $TOOL_FOLDER/run.py \
            --input $input_file \
            --outdir spectra \
            --mode ${params.mode} \
            --compression ${params.compression} \
            ${ms2_flag} \
            ${exclude_mobility_flag} \
            --encoding ${params.encoding} \
            ${barebones_metadata_flag} \
            --maldi_output_file ${params.maldi_output_file} \
            --imzml_mode ${params.imzml_mode} \
            --chunk_size ${params.chunk_size} \
            ${verbose_flag}
            """
        } else if (params.maldi_plate_map != '') {
            """
            mkdir spectra
            python3 $TOOL_FOLDER/run.py \
            --input $input_file \
            --outdir spectra \
            --mode ${params.mode} \
            --compression ${params.compression} \
            ${ms2_flag} \
            ${exclude_mobility_flag} \
            --encoding ${params.encoding} \
            ${barebones_metadata_flag} \
            --maldi_output_file ${params.maldi_output_file} \
            --maldi_plate_map = ${params.maldi_plate_map} \
            --imzml_mode ${params.imzml_mode} \
            --chunk_size ${params.chunk_size} \
            ${verbose_flag}
            """
        }
    } else if (params.location == 'server') {
        """
        mkdir spectra
        python3 $CLIENT_FOLDER/client.py \
        --input $input_file \
        --outdir spectra \
        --host "gnpsserver1.ucsd.edu:6521"
        """
    }
}

process summarize {
    publishDir "$params.publishdir", mode: 'copy'

    input:
    file "spectra/*"

    output:
    file "results_file.tsv"

    """
    python3 $TOOL_FOLDER/summarize.py \
    spectra \
    results_file.tsv
    """
}


workflow {
    input_ch = Channel.fromPath(params.input, type:'dir', checkIfExists: true)
    converted_data_ch = convert(input_ch)
    summarize(converted_data_ch.collect())
}