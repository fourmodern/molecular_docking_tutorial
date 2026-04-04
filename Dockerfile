FROM condaforge/mambaforge:latest

LABEL description="Molecular Docking Workshop (conda-based)"

ENV DEBIAN_FRONTEND=noninteractive
ENV BIN_DIR=/opt/bin
ENV PATH="${BIN_DIR}:${PATH}"

# System tools
RUN apt-get update && apt-get install -y --no-install-recommends \
    wget curl git \
    && rm -rf /var/lib/apt/lists/*

RUN mkdir -p ${BIN_DIR}

# smina binary
RUN wget -q -L -O ${BIN_DIR}/smina \
    "https://sourceforge.net/projects/smina/files/smina.static/download" \
    && chmod +x ${BIN_DIR}/smina

# ADFRsuite (skip if fails)
RUN cd /tmp \
    && wget -q --timeout=120 -O ADFRsuite.tar.gz \
       "https://ccsb.scripps.edu/adfr/download/1038/" \
    && tar xzf ADFRsuite.tar.gz \
    && cd ADFRsuite_* \
    && echo "Y" | ./install.sh -d ${BIN_DIR}/ADFRsuite -c 0 \
    && ln -sf ${BIN_DIR}/ADFRsuite/bin/prepare_receptor ${BIN_DIR}/prepare_receptor \
    && ln -sf ${BIN_DIR}/ADFRsuite/bin/prepare_ligand ${BIN_DIR}/prepare_ligand \
    && rm -rf /tmp/ADFRsuite* \
    || echo "WARNING: ADFRsuite install failed"

# Conda packages (pymol-open-source works reliably via conda-forge)
RUN mamba install -y -c conda-forge \
    python=3.10 \
    rdkit \
    pymol-open-source \
    openbabel \
    pdbfixer \
    openmm \
    mdanalysis \
    prolif \
    meeko \
    scipy scikit-learn \
    seaborn matplotlib pandas numpy \
    py3dmol \
    vina \
    gemmi \
    jupyter notebook \
    && mamba clean -afy

WORKDIR /workspace
COPY *.ipynb /workspace/
COPY run_docking.py run_all.sh mol_utils.py /workspace/
COPY practical_docking/ /workspace/practical_docking/
COPY pymol_scripts/ /workspace/pymol_scripts/

VOLUME /workspace/results

EXPOSE 8888

CMD ["jupyter", "notebook", "--ip=0.0.0.0", "--port=8888", "--no-browser", "--allow-root", "--NotebookApp.token=docking"]
