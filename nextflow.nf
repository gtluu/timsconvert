#!~/bin nextflow

// params

// required params
params.input = 'test/data/massive.ucsd.edu/MSV000084402/raw/SRM1950_20min_88_01_6950.d'  // should be replaced with Bruker .d directory or folder containing .d directories

// optional params; '' == default parameters will be used
// uncomment param and add to script to use
// not sure if there's a programmatic way to do this yet; everything is hardcoded for now

params.centroid = 'True'  // should spectra be centroided?
// params.ms2_centroiding_window = '5'  // centroiding window for ms2 spectra
// params.ms2_keep_n_most_abundant_peaks = '1'  // keep N most abundant peaks in ms2 spectra
params.ms2_only = 'True'  // only convert ms2 spectra?
params.ms1_groupby = 'scan'  // group ms1 spectra by 'frame' (will have array of mobilities; in beta) or 'scan' (each spectrum has one RT and mobility)
params.verbose = 'True'

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
    file "output_results"

    """
    mkdir output_results
    python3 $TOOL_FOLDER/run.py \
    --input $input_file \
    --outdir output_results \
    --centroid ${params.centroid} \
    --ms2_only ${params.ms2_only} \
    --ms1_groupby ${params.ms1_groupby} \
    --verbose ${params.verbose}
    """

}
