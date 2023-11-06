Advanced Usage
==============

Docker Container Installation and Usage
---------------------------------------
A Dockerfile has also been provided to run TIMSCONVERT inside a Docker container.

1. Build the Docker image.

   .. code-block::

        docker build --tag timsconvert -f [path to]/timsconvert/Dockerfile .

2. Run the Docker image in a container.

   .. code-block::

        docker run --rm -it -v [path to data]:/data timsconvert --input /data --outdir /data

Nextflow Installation and Usage
-------------------------------
A Nextflow workflow has also been provided to run TIMSCONVERT.

1. Create a conda instance. You must be using Python 3.11. Newer versions of Python are not guaranteed to be compatible with Bruker's API in Linux.

   .. code-block::

        conda create -n timsconvert python=3.11

2. Activate conda environment.

   .. code-block::

        conda activate timsconvert

3. Install `Nextflow <https://www.nextflow.io/>`_ to your ``conda`` environment.

   .. code-block::

        conda install -c bioconda nextflow

3. Download TIMSCONVERT by cloning the Github repo.

   * You will need to have `Git <https://git-scm.com/downloads>`_ installed and ensure that the option to enable symbolic links was checked during installation.

   .. code-block::

        git clone https://www.github.com/gtluu/timsconvert

   * It may be necessary to explicitly allow for the use of symbolic links by adding the -c core.symlinks=True

   .. code-block::

        git clone -c core.symlinks=true https://www.github.com/gtluu/timsconvert

4. Install TIMSCONVERT's dependencies via ``pip``.

   .. code-block::

        pip install -r [path to timsconvert directory]/requirements.txt

5. You will also need to install our forked version of ``pyimzML``, which has added support for ion mobility arrays in imzML data from imaging mass spectrometry experiments.

   .. code-block::

        pip install git+https://github.com/gtluu/pyimzML

6. Configure ``nextflow.nf`` script to your liking. See :doc:`Local Usage <local>` for a list of parameters.

7. Run TIMSCONVERT in Nextflow.

   .. code-block::

        nextflow run [path to timsconvert]/nextflow.nf --input [path to your data]
