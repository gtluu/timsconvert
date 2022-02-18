from timsconvert.parse_lcms import *
from timsconvert.write_mzml import *
import os
import logging
import numpy as np
from lxml import etree as et
from psims.mzml import MzMLWriter


def write_maldi_dd_mzml(data, infile, outdir, outfile, ms2_only):
    pass