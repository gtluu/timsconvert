# Configuration file for the Sphinx documentation builder.
#
# For the full list of built-in configuration values, see the documentation:
# https://www.sphinx-doc.org/en/master/usage/configuration.html

import os
import sys
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))

# -- Project information -----------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#project-information

project = 'TIMSCONVERT'
copyright = '2024, Gordon T. Luu'
author = 'Gordon T. Luu'
<<<<<<< HEAD
release = '2.0.0a3'
=======
release = '1.6.5'
>>>>>>> 3d6859f11b5475b8412da8f077fe0256132042f4

# -- General configuration ---------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#general-configuration

extensions = ['sphinx.ext.duration',
              'sphinx.ext.doctest',
              'sphinx.ext.autodoc',
              'sphinx.ext.napoleon',
              'sphinx.ext.autosectionlabel']

templates_path = ['_templates']
exclude_patterns = []



# -- Options for HTML output -------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#options-for-html-output

html_theme = 'alabaster'
html_static_path = ['_static']
