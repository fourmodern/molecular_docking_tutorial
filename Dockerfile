FROM python:3.10-slim

LABEL maintainer="Molecular Docking Workshop"
LABEL description="Molecular docking environment with Vina, smina, ADFRsuite"

ENV DEBIAN_FRONTEND=noninteractive
ENV BIN_DIR=/opt/bin
ENV PATH="${BIN_DIR}:${PATH}"

# System dependencies (libboost-all-dev needed for vina pip build)
RUN apt-get update && apt-get install -y --no-install-recommends \
    wget curl git build-essential \
    libxml2 libxslt1.1 \
    libboost-all-dev swig \
    && rm -rf /var/lib/apt/lists/*

RUN mkdir -p ${BIN_DIR}

# smina (follow redirects with -L)
RUN wget -q -L -O ${BIN_DIR}/smina \
    "https://sourceforge.net/projects/smina/files/smina.static/download" \
    && chmod +x ${BIN_DIR}/smina

# ADFRsuite (skip if download fails — Scripps server can be flaky)
RUN cd /tmp \
    && wget -q --timeout=120 -O ADFRsuite.tar.gz \
       "https://ccsb.scripps.edu/adfr/download/1038/" \
    && tar xzf ADFRsuite.tar.gz \
    && cd ADFRsuite_* \
    && echo "Y" | ./install.sh -d ${BIN_DIR}/ADFRsuite -c 0 \
    && ln -sf ${BIN_DIR}/ADFRsuite/bin/prepare_receptor ${BIN_DIR}/prepare_receptor \
    && ln -sf ${BIN_DIR}/ADFRsuite/bin/prepare_ligand ${BIN_DIR}/prepare_ligand \
    && rm -rf /tmp/ADFRsuite* \
    || echo "WARNING: ADFRsuite install failed — PDBQT conversion will use Open Babel fallback"

# Python packages (pymol excluded — use Windows PyMOL for visualization)
RUN pip install --no-cache-dir \
    rdkit-pypi \
    meeko vina \
    openbabel-wheel \
    pdbfixer openmm \
    py3Dmol \
    MDAnalysis \
    prolif \
    seaborn scipy scikit-learn \
    jupyter notebook

# Working directory
WORKDIR /workspace
COPY *.ipynb /workspace/
COPY run_docking.py run_all.sh /workspace/
COPY pymol_scripts/ /workspace/pymol_scripts/

VOLUME /workspace/results

EXPOSE 8888

CMD ["jupyter", "notebook", "--ip=0.0.0.0", "--port=8888", "--no-browser", "--allow-root", "--NotebookApp.token=docking"]
