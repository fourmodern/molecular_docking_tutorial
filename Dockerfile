FROM python:3.10-slim

LABEL maintainer="Molecular Docking Workshop"
LABEL description="Molecular docking environment with Vina, smina, ADFRsuite"

ENV DEBIAN_FRONTEND=noninteractive
ENV BIN_DIR=/opt/bin
ENV PATH="${BIN_DIR}:${PATH}"

# System dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    wget curl git build-essential \
    libxml2 libxslt1.1 libopenbabel-dev \
    fpocket \
    && rm -rf /var/lib/apt/lists/*

RUN mkdir -p ${BIN_DIR}

# smina
RUN wget -q -O ${BIN_DIR}/smina \
    "https://sourceforge.net/projects/smina/files/smina.static/download" \
    && chmod +x ${BIN_DIR}/smina

# ADFRsuite
RUN cd /tmp \
    && wget -q -O ADFRsuite.tar.gz \
       "https://ccsb.scripps.edu/adfr/download/1038/" \
    && tar xzf ADFRsuite.tar.gz \
    && cd ADFRsuite_* \
    && echo "Y" | ./install.sh -d ${BIN_DIR}/ADFRsuite -c 0 \
    && ln -sf ${BIN_DIR}/ADFRsuite/bin/prepare_receptor ${BIN_DIR}/prepare_receptor \
    && ln -sf ${BIN_DIR}/ADFRsuite/bin/prepare_ligand ${BIN_DIR}/prepare_ligand \
    && rm -rf /tmp/ADFRsuite*

# Python packages
RUN pip install --no-cache-dir \
    rdkit-pypi \
    meeko vina \
    openbabel-wheel \
    pdbfixer openmm \
    pymol-open-source \
    py3Dmol \
    MDAnalysis \
    prolif \
    seaborn scipy scikit-learn \
    jupyter notebook

# Working directory
WORKDIR /workspace
COPY *.ipynb /workspace/

EXPOSE 8888

CMD ["jupyter", "notebook", "--ip=0.0.0.0", "--port=8888", "--no-browser", "--allow-root", "--NotebookApp.token=docking"]
