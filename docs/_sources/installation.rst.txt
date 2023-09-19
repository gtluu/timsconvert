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

5. Download TIMSCONVERT by cloning the Github repo.

   * You will need to have `Git <https://git-scm.com/downloads>`_ installed and ensure that the option to enable symbolic links was checked during installation.

   .. code-block::

        git clone https://www.github.com/gtluu/timsconvert

   * It may be necessary to explicitly allow for the use of symbolic links by adding the -c core.symlinks=True

   .. code-block::

        git clone -c core.symlinks=true https://www.github.com/gtluu/timsconvert

6. Install TIMSCONVERT's dependencies via ``pip``.

   .. code-block::

        pip install -r [path to timsconvert directory]/requirements.txt

7. You will also need to install our forked version of ``pyimzML``, which has added support for ion mobility arrays in imzML data from imaging mass spectrometry experiments.

   .. code-block::

        pip install git+https://github.com/gtluu/pyimzML

8. TIMSCONVERT is now ready to use. See the :doc:`Local Usage <local>` page for basic usage of TIMSCONVERT.

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

3. Create a conda instance. You must be using Python 3.7. Newer versions of Python are not guaranteed to be compatible with Bruker's API in Linux.

   .. code-block::

        conda create -n timsconvert python=3.7

4. Activate conda environment.

   .. code-block::

        conda activate timsconvert

5. Download TIMSCONVERT by cloning the Github repo.

   * You will need to have `Git <https://git-scm.com/downloads>`_ installed and ensure that the option to enable symbolic links was checked during installation.

   .. code-block::

        git clone https://www.github.com/gtluu/timsconvert

   * It may be necessary to explicitly allow for the use of symbolic links by adding the -c core.symlinks=True

   .. code-block::

        git clone -c core.symlinks=true https://www.github.com/gtluu/timsconvert

6. Install TIMSCONVERT's dependencies via ``pip``.

   .. code-block::

        pip install -r [path to timsconvert directory]/requirements.txt

7. You will also need to install our forked version of ``pyimzML``, which has added support for ion mobility arrays in imzML data from imaging mass spectrometry experiments.

   .. code-block::

        pip install git+https://github.com/gtluu/pyimzML

8. TIMSCONVERT is now ready to use. See the :doc:`Local Usage <local>` page for basic usage of TIMSCONVERT.
