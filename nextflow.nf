#!~/bin nextflow

// params

// required params
params.input = '/mnt/f/nextflow/raw/**.d'  // should be replaced with Bruker .d directory or folder containing .d directories

// optional params; '' == default parameters will be used
// uncomment param and add to script to use
// not sure if there's a programmatic way to do this yet; everything is hardcoded for now
params.outdir = '/mnt/f/nextflow/mzml'  // directory to output resulting files
// params.outfile = ''  // output filename
params.centroid = 'True'  // should spectra be centroided?
// params.ms2_centroiding_window = '5'  // centroiding window for ms2 spectra
// params.ms2_keep_n_most_abundant_peaks = '1'  // keep N most abundant peaks in ms2 spectra
params.ms2_only = 'True'  // only convert ms2 spectra?
params.ms1_groupby = 'scan'  // group ms1 spectra by 'frame' (will have array of mobilities; in beta) or 'scan' (each spectrum has one RT and mobility)
params.verbose = 'True'

input_ch = Channel.fromPath(params.input, checkIfExists: true)

TOOL_FOLDER = '/mnt/f/code/alphatims_test'

// Process
process convert {

    input:
    file x from input_ch

    //output:
    // no output? this is handled by python right now, so next process would look for /path/to/output_directory/*.mzML

    script:
    """
    python3 $TOOL_FOLDER/run.py \
    --input $x \
    --outdir ${params.outdir} \
    --centroid ${params.centroid} \
    --ms2_only ${params.ms2_only}
    --ms1_groupby ${params.ms1_groupby} \
    --verbose ${params.verbose}
    """

}
