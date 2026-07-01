curl -O https://repo.anaconda.com/miniconda/Miniconda3-latest-Linux-x86_64.sh
bash ./Miniconda3-latest-Linux-x86_64.sh

source ~/.bashrc

conda config --add channels bioconda & /
conda config --add channels conda-forge & /
conda config --set channel_priority strict & /
conda create --name bio-prak & /
conda activate bio-prak & /
conda instapp python=3.13 -y & /
conda install viennarna=2.7.2 bedtools jupyterlab scipy matplotlib pandas biopython samtools fasta -y