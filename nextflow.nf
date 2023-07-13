#!~/bin nextflow

nextflow.enable.dsl=2

// params

// required params
params.input = ''

// optional params
params.mode = 'centroid'  // mode can be 'centroid' or 'raw'
params.compression = 'zlib' // zlib or none

// timsconvert params
params.ms2_only = 'False'  // only convert ms2 spectra
params.exclude_mobility = 'True'  // exclude mobility arrays from MS1 spectra
params.encoding = 64
params.maldi_output_file = 'combined' // choose whether MALDI spectra are output to individual files or a single combined file
params.maldi_plate_map = ''
params.imzml_mode = 'processed'

// timsconvert system params
params.lcms_backend = 'timsconvert'
params.chunk_size = 10
params.verbose = 'True'

// tdf2mzml params
params.start_frame = -1
params.end_frame = -1
params.precision = 10.0
params.ms1_threshold = 100
params.ms2_threshold = 10
params.ms2_nlargest = -1

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
            --maldi_output_file ${params.maldi_output_file} \
            --imzml_mode ${params.imzml_mode} \
            --lcms_backend ${params.lcms_backend} \
            --chunk_size ${params.chunk_size} \
            ${verbose_flag} \
            --start_frame ${params.start_frame} \
            --end_frame ${params.end_frame} \
            --precision ${params.precision} \
            --ms1_threshold ${params.ms1_threshold} \
            --ms2_threshold ${params.ms2_threshold} \
            --ms2_nlargest ${params.ms2_nlargest}
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
            --maldi_output_file ${params.maldi_output_file} \
            --maldi_plate_map = ${params.maldi_plate_map} \
            --imzml_mode ${params.imzml_mode} \
            --lcms_backend ${params.lcms_backend} \
            --chunk_size ${params.chunk_size} \
            ${verbose_flag} \
            --start_frame ${params.start_frame} \
            --end_frame ${params.end_frame} \
            --precision ${params.precision} \
            --ms1_threshold ${params.ms1_threshold} \
            --ms2_threshold ${params.ms2_threshold} \
            --ms2_nlargest ${params.ms2_nlargest}
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