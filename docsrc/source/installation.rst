Installation
============

TIMSCONVERT GUI
---------------
The GUI version of TIMSCONVERT can be run by downloading it from
`the Github releases page for this repo <https://github.com/gtluu/timsconvert/releases>`_. Unzip the file and run
``TIMSCONVERT.exe``. See the :doc:`Local Usage <local>` page for basic usage of TIMSCONVERT.

Manual Installation
-------------------
If you prefer to run TIMSCONVERT locally via the command line interface, you can set up a ``conda`` environment to do
so. Please note that TIMSCONVERT should be run under Windows or Linux. macOS is not supported.

Manual Installation on Windows
------------------------------
1. Download and install `Anaconda for Windows <https://repo.anaconda.com/archive/Anaconda3-2024.06-1-Windows-x86_64.exe>`_ if not already installed. Anaconda3-2024.06-1 for Windows is used as an example here. Follow the prompts to complete installation.

2. Download and install `Git for Windows <https://github.com/git-for-windows/git/releases/download/v2.42.0.windows.2/Git-2.42.0.2-64-bit.exe>`_ if not already installed.

3. Run ``Anaconda Prompt``.

4. Create a conda instance.

   .. code-block::

        conda create -n timsconvert python=3.11

5. Activate conda environment.

   .. code-block::

        conda activate timsconvert

6. Install TIMSCONVERT.

   .. code-block::

        pip install git+https://github.com/gtluu/timsconvert

7. TIMSCONVERT is now ready to use. See the :doc:`Local Usage <local>` page for basic usage of TIMSCONVERT.

Manual Installation on Linux
----------------------------
Please note that while these instructions should apply to most Linux distros, TIMSCONVERT is tested on Ubuntu 22.04.3
LTS. We recommend using this distro if you encounter compatibility issues in others.

1. If not already installed, download and install `Anaconda for Linux <https://repo.anaconda.com/archive/Anaconda3-2024.06-1-Linux-x86_64.sh>`_. Anaconda3-2024.06-1 for Linux is used as an example here.

   * Alternatively, the script can be downloaded in the ``Terminal`` using the following command.

   .. code-block::

        wget https://repo.anaconda.com/archive/Anaconda3-2024.06-1-Linux-x86_64.sh

2. If not already installed, install ``git``. On Ubuntu 22.04.3 LTS, this can be done using the following command.

   .. code-block::

        sudo apt-get install git

2. Install Anaconda for Linux via the bash script that was downloaded. After installation, restart the terminal (or open a new terminal window).

   .. code-block::

        bash [path to]/Anaconda3-2023.07-2-Linux-x86_64.sh

3. In the terminal, create a conda virtual environment.

   .. code-block::

        conda create -n timsconvert python=3.11

4. Activate conda environment.

   .. code-block::

        conda activate timsconvert

5. Install TIMSCONVERT.

   .. code-block::

        pip install git+https://github.com/gtluu/timsconvert

6. TIMSCONVERT is now ready to use. See the :doc:`Local Usage <local>` page for basic usage of TIMSCONVERT.
