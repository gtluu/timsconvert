Local Usage
===========
The command line interface version of TIMSCONVERT supports conversion of all experimental types specified above. Please
note that certain versions of Linux may not be compatible with the Baf2Sql API used to convert BAF files. See
`this issue <https://github.com/gtluu/timsconvert/issues/13>`_ for more details.

Basic Example
-------------
Only the ``input`` parameter is required to run TIMSCONVERT. By default, the output file(s) can be found in the same
directory as the input data using the same filenames as the original .d file(s). Please note that any previously
converted mzML/imzML files in the output directory with the same filename will be overwritten. If no other parameters
are specified, their default values will be used.

.. code-block::

    python [path to timsconvert]/bin/run.py --input [path to data]

In some cases, certain systems/terminals will require the use of the ``python3`` command instead of ``python``.

.. code-block::

    python3 [path to timsconvert]/bin/run.py --input [path to data]

Depending on the size of your data and the number of files being converted, TIMSCONVERT may take some time to finish
conversion.

For a full list of parameters, use the ``--help`` flag.

.. code-block::

    python [path to timsconvert]/bin/run.py --help

See below for a full list of descriptions for each parameter.

Parameters
----------
.. csv-table::
    :file: parameter_descriptions.csv

Testing
-------
To test TIMSCONVERT locally:

* Download test data.

  .. code-block::

        cd [path to timsconvert]/test
        make download_test

* Test Python CLI workflow

  .. code-block::

        cd [path to timsconvert]/test
        make run_test
        make run_test_mobility

* Test Nextflow workflow

  .. code-block::

        cd [path to timsconvert]/test
        make run_nextflow_mobility