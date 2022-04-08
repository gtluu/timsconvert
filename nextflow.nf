#!~/bin nextflow

// params

// required params
params.input = ''

// optional params
params.mode = 'centroid'  // mode can be 'centroid', 'profile', or 'raw'
params.compression = 'zlib' // zlib or none

// timsconvert params
params.ms2_only = 'False'  // only convert ms2 spectra
params.exclude_mobility = 'False'  // exclude mobility arrays from MS1 spectra
params.profile_bins = 0
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
    def ms2_flag = params.ms2_only == 'True' ? "--ms2_only" : ''
    def verbose_flag = params.verbose == 'True' ? "--verbose" : ''
    def exclude_mobility_flag = params.exclude_mobility == 'True' ? "--exclude_mobility" : ''

    if (params.maldi_plate_map == '')
        """
        mkdir spectra
        python3 $TOOL_FOLDER/run.py \
        --input $input_file \
        --outdir spectra \
        --mode ${params.mode} \
        --compression ${params.compression} \
        ${ms2_flag} \
        ${exclude_mobility_flag} \
        --profile_bins ${params.profile_bins} \
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

    else if (params.maldi_plate_map != '')
        """
        mkdir spectra
        python3 $TOOL_FOLDER/run.py \
        --input $input_file \
        --outdir spectra \
        --mode ${params.mode} \
        --compression ${params.compression} \
        ${ms2_flag} \
        ${exclude_mobility_flag} \
        --profile_bins ${params.profile_bins} \
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


