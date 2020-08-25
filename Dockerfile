FROM jupyter/base-notebook

USER root

# install git
RUN apt-get update && \
    apt-get upgrade -y && \
    apt-get install -y git && \
    rm -rf /var/lib/apt/lists/*

USER $NB_UID

# copy scripts across
COPY requirements.txt requirements.txt

# install requirements
RUN conda update -n base conda --yes && \
    conda install -c conda-forge --file requirements.txt --yes && \
    conda clean --all -f --yes

# get english model
RUN python -m spacy download en

RUN jupyter lab build
