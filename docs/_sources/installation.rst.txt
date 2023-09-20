Installation
============
If you prefer to run TIMSCONVERT locally via the command line interface, you can set up a ``conda`` environment to do
so. Please note that TIMSCONVERT should be run under Windows or Linux. macOS is not supported.

Installing on Windows
---------------------
1. Download and install `Anaconda for Windows <https://repo.anaconda.com/archive/Anaconda3-2021.11-Windows-x86_64.exe>`_. Follow the prompts to complete installation.

2. Run ``Anaconda Prompt (R-MINI~1)`` as Administrator.

3. Create a conda instance. You must be using Python 3.7. Newer versions of Python are not guaranteed to be compatible with Bruker's API in Linux.

   .. code-block::

        conda create -n timsconvert python=3.7

4. Activate conda environment.

   .. code-block::

        conda activate timsconvert

5. Install TIMSCONVERT.

   .. code-block::

        pip install git+https://github.com/gtluu/timsconvert

6. TIMSCONVERT is now ready to use. See the :doc:`Local Usage <local>` page for basic usage of TIMSCONVERT.

Installing on Linux
-------------------
Please note that while these instructions should apply to most Linux distros, TIMSCONVERT is tested on Ubuntu 22.04.3
LTS. We recommend using this distro if you encounter compatibility issues in others.

1. Download and install `Anaconda for Linux <https://repo.anaconda.com/archive/Anaconda3-2021.11-Linux-x86_64.sh>`_. Anaconda3-2021.11 for LInux is used as an example here.

   * Alternatively, the script can be downloaded in the ``Terminal`` using the following command.

   .. code-block::

        wget https://repo.anaconda.com/archive/Anaconda3-2021.11-Linux-x86_64.sh

2. Install Anaconda for Linux via the bash script that was downloaded.

   .. code-block::

        bash [path to]/Anaconda3-2021.11-Linux-x86_64.sh

3. In the terminal, create a conda virtual environment. You must be using Python 3.7. Newer versions of Python are not guaranteed to be compatible with Bruker's API in Linux.

   .. code-block::

        conda create -n timsconvert python=3.7

4. Activate conda environment.

   .. code-block::

        conda activate timsconvert

5. Install TIMSCONVERT.

   .. code-block::

        pip install git+https://github.com/gtluu/timsconvert

6. TIMSCONVERT is now ready to use. See the :doc:`Local Usage <local>` page for basic usage of TIMSCONVERT.
