#!/bin/bash
# ============================================================
# Molecular Docking - WSL/Docker 실행 스크립트
#
# 사용법:
#   bash run_all.sh                     # TYK2 기본 도킹
#   bash run_all.sh --pdb 1M17          # 다른 타겟
#   bash run_all.sh --smiles "CCO"      # 커스텀 리간드 추가
#
# 결과 위치:
#   ./docking_output/results/           # PyMOL, DataWarrior용 파일
#
# Windows에서 결과 열기:
#   WSL:    \\wsl$\Ubuntu\home\사용자\...\results\
#   Docker: ./results/ (마운트된 볼륨)
# ============================================================
set -e

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
OUTPUT_DIR="${SCRIPT_DIR}/docking_output"

echo ""
echo "============================================"
echo "  Molecular Docking Pipeline"
echo "============================================"
echo ""

# --- Activate venv if exists (WSL) ---
if [ -f "$HOME/docking_env/bin/activate" ]; then
    source "$HOME/docking_env/bin/activate"
    echo "  venv activated: $VIRTUAL_ENV"
fi

# --- Run docking ---
echo ""
echo "  Starting docking..."
echo "  Output: ${OUTPUT_DIR}"
echo ""

python3 "${SCRIPT_DIR}/run_docking.py" \
    --output "${OUTPUT_DIR}" \
    "$@"

# --- Organize results for Windows ---
RESULTS_DIR="${OUTPUT_DIR}/results"

if [ -d "$RESULTS_DIR" ]; then
    echo ""
    echo "============================================"
    echo "  Results ready!"
    echo "============================================"
    echo ""
    echo "  Files for PyMOL (.pdb, .sdf):"
    ls -1 "${RESULTS_DIR}"/*.pdb "${RESULTS_DIR}"/*.sdf 2>/dev/null | while read f; do
        echo "    $(basename "$f")"
    done
    echo ""
    echo "  Files for DataWarrior (.csv):"
    ls -1 "${RESULTS_DIR}"/*.csv 2>/dev/null | while read f; do
        echo "    $(basename "$f")"
    done
    echo ""

    # --- Copy PyMOL scripts ---
    if [ -d "${SCRIPT_DIR}/pymol_scripts" ]; then
        cp "${SCRIPT_DIR}/pymol_scripts"/*.pml "${RESULTS_DIR}/" 2>/dev/null
        echo "  PyMOL scripts copied to results/"
    fi

    # --- Show Windows path ---
    if grep -qi microsoft /proc/version 2>/dev/null; then
        # WSL detected
        WIN_PATH=$(wslpath -w "${RESULTS_DIR}" 2>/dev/null || echo "")
        if [ -n "$WIN_PATH" ]; then
            echo ""
            echo "  Windows path:"
            echo "    ${WIN_PATH}"
            echo ""
            echo "  Windows에서 열기:"
            echo "    1. PyMOL: File → Open → ${WIN_PATH}\\*.sdf"
            echo "    2. DataWarrior: File → Open → ${WIN_PATH}\\*.csv"
        fi
    fi

    echo ""
    echo "  Docker 사용 시:"
    echo "    결과가 ./results/ 폴더에 마운트되어 있습니다."
fi
