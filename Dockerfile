FROM jupyter/base-notebook

USER $NB_UID

# copy scripts across
COPY requirements.txt requirements.txt

# install requirements
RUN conda update -n base conda --yes && \
    conda install -c conda-forge --file requirements.txt --yes && \
    conda clean --all -f -y

# get english model
RUN python -m spacy download en
