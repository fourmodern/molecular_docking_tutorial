#!/bin/bash
# =============================================================
# Molecular Docking Workshop - WSL2 Setup Script
# Windows에서 WSL2 터미널을 열고 실행하세요:
#   bash setup_wsl.sh
# =============================================================
set -e

echo "=========================================="
echo "  Molecular Docking Environment Setup"
echo "  for WSL2 (Ubuntu)"
echo "=========================================="

# --- 1. System packages ---
echo ""
echo "[1/5] System packages..."
sudo apt-get update -qq
sudo apt-get install -y -qq \
    python3 python3-pip python3-venv \
    wget curl git build-essential \
    libxml2-dev libxslt1-dev \
    fpocket 2>/dev/null || echo "fpocket not in repo, skipping"

# --- 2. Python venv ---
echo ""
echo "[2/5] Python virtual environment..."
VENV_DIR="$HOME/docking_env"
python3 -m venv "$VENV_DIR"
source "$VENV_DIR/bin/activate"

pip install --upgrade pip -q

pip install -q \
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

echo "  Python packages installed."

# --- 3. smina ---
echo ""
echo "[3/5] Installing smina..."
BIN_DIR="$HOME/docking_bin"
mkdir -p "$BIN_DIR"

if [ ! -f "$BIN_DIR/smina" ]; then
    wget -q -O "$BIN_DIR/smina" \
        "https://sourceforge.net/projects/smina/files/smina.static/download"
    chmod +x "$BIN_DIR/smina"
    echo "  smina installed."
else
    echo "  smina already exists."
fi

# --- 4. ADFRsuite ---
echo ""
echo "[4/5] Installing ADFRsuite..."
ADFR_DIR="$BIN_DIR/ADFRsuite"

if [ ! -d "$ADFR_DIR" ]; then
    cd /tmp
    wget -q -O ADFRsuite.tar.gz "https://ccsb.scripps.edu/adfr/download/1038/"
    tar xzf ADFRsuite.tar.gz
    cd ADFRsuite_*
    echo "Y" | ./install.sh -d "$ADFR_DIR" -c 0 > /dev/null 2>&1
    ln -sf "$ADFR_DIR/bin/prepare_receptor" "$BIN_DIR/prepare_receptor"
    ln -sf "$ADFR_DIR/bin/prepare_ligand" "$BIN_DIR/prepare_ligand"
    rm -rf /tmp/ADFRsuite*
    echo "  ADFRsuite installed."
else
    echo "  ADFRsuite already exists."
fi

# --- 5. Setup workspace ---
echo ""
echo "[5/5] Setting up workspace..."
WORK_DIR="$HOME/docking_workshop"
mkdir -p "$WORK_DIR"

# Copy notebooks if in the same directory
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
for nb in "$SCRIPT_DIR"/*.ipynb; do
    [ -f "$nb" ] && cp "$nb" "$WORK_DIR/"
done

# Add to PATH in .bashrc
if ! grep -q "docking_bin" "$HOME/.bashrc" 2>/dev/null; then
    cat >> "$HOME/.bashrc" << 'BASHEOF'

# Molecular Docking Workshop
export PATH="$HOME/docking_bin:$PATH"
alias docking='source $HOME/docking_env/bin/activate && cd $HOME/docking_workshop'
alias docking-notebook='source $HOME/docking_env/bin/activate && cd $HOME/docking_workshop && jupyter notebook --no-browser'
BASHEOF
fi

echo ""
echo "=========================================="
echo "  Setup complete!"
echo "=========================================="
echo ""
echo "  사용법:"
echo "  1. 터미널에서: docking"
echo "     → venv 활성화 + 작업 폴더 이동"
echo ""
echo "  2. Jupyter 실행: docking-notebook"
echo "     → 브라우저에서 http://localhost:8888 접속"
echo ""
echo "  3. 도킹 결과 → Windows PyMOL:"
echo "     WSL 경로: ~/docking_workshop/results/"
echo "     Windows: \\\\wsl$\\Ubuntu\\home\\$USER\\docking_workshop\\results\\"
echo ""
echo "  새 터미널을 열거나 source ~/.bashrc 를 실행하세요."
