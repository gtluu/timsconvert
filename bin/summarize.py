import pandas as pd
import glob
import os
import argparse


# Reading arguments
parser = argparse.ArgumentParser()
parser.add_argument("input_spectra_folder", help="Input directory")
parser.add_argument("output_file", help="Output file")
args = parser.parse_args()

all_spectra_files = glob.glob(os.path.join(args.input_spectra_folder, "*.mzML"))

# creating dataframe for all spectra
df = pd.DataFrame()
df["filename"] = [os.path.basename(f) for f in all_spectra_files]
df["spectra_count"] = 0

df.to_csv(args.output_file, sep="\t", index=False)

