# Molecular Docking Tutorials

Colab-ready Jupyter notebooks for computational drug discovery — from single-target docking to multi-kinase selectivity analysis.

## Notebooks

| Notebook | Target | Description |
|----------|--------|-------------|
| [TYK2 Docking](TYK2_Molecular_Docking_Colab.ipynb) | TYK2 (6NZP) | Single-target docking pipeline with structure selection, Vina + smina, ProLIF analysis |
| [Kinase Panel](Kinase_Panel_Docking_Colab.ipynb) | 10 kinases | Cross-docking selectivity across 5 kinase groups (TK, CMGC, TKL, AGC, Other) |
| [EGFR WT vs Mutant](EGFR_WT_Mutant_Docking_Colab.ipynb) | EGFR variants | TKI resistance analysis: WT, L858R, T790M, T790M/L858R with 4 generation drugs |

## Quick Start

Click the Colab badge in any notebook to run directly in Google Colab (free GPU).

[![Open TYK2 In Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/fourmodern/molecular_docking_tutorial/blob/main/TYK2_Molecular_Docking_Colab.ipynb)
[![Open Kinase Panel In Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/fourmodern/molecular_docking_tutorial/blob/main/Kinase_Panel_Docking_Colab.ipynb)
[![Open EGFR In Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/fourmodern/molecular_docking_tutorial/blob/main/EGFR_WT_Mutant_Docking_Colab.ipynb)

## Pipeline Overview

Each notebook includes:

1. **Environment Setup** — All dependencies installed via pip (no conda)
2. **Binary Tools** — smina, ADFRsuite (prepare_receptor/prepare_ligand) auto-downloaded
3. **Protein Preparation** — PDB fetch, chain selection, PDBFixer (missing atoms/H), PDBQT conversion
4. **Molecular Docking** — AutoDock Vina and/or smina with configurable parameters
5. **Analysis**
   - Score comparison (boxplot, violin, heatmap)
   - ProLIF interaction fingerprints + LigNetwork visualization
   - 3D visualization (py3Dmol)
6. **Advanced Analysis**
   - RMSD validation (docked vs crystal pose)
   - Ligand efficiency (LE, BEI)
   - Consensus scoring (vina, vinardo, ad4_scoring)
   - IFP Tanimoto similarity + PCA clustering
   - Interaction frequency heatmap
   - ECFP4 molecular fingerprint clustering

## Kinase Panel (10 Kinases)

| Kinase | Group | PDB | Family | Disease |
|--------|-------|-----|--------|---------|
| EGFR | TK | 1M17 | ErbB | NSCLC |
| ABL1 | TK | 1IEP | Abl | CML |
| JAK2 | TK | 3FUP | JAK | MPN |
| CDK2 | CMGC | 1H1S | CDK | Cancer |
| p38a | CMGC | 3GCP | MAPK | Inflammation |
| GSK3b | CMGC | 1Q5K | GSK | Alzheimer's |
| BRAF | TKL | 3OG7 | RAF | Melanoma |
| ALK | TKL | 2XP2 | ALK | NSCLC |
| AKT1 | AGC | 3CQW | AKT | Cancer |
| AURKA | Other | 3E5A | Aurora | Cancer |

## EGFR Resistance Analysis

Models the clinical TKI resistance evolution in NSCLC:

```
Wild-type → (1st gen: Erlotinib/Gefitinib) → L858R activation
                                                    ↓
                                              T790M gatekeeper resistance
                                                    ↓
                                        (3rd gen: Osimertinib) → T790M/C797S
```

Structures: WT (1M17, 2ITY, 1XKK, 4G5J), L858R (2ITZ), T790M (2JIT), T790M/L858R (3IKA)

Cross-docking drugs: Erlotinib, Gefitinib, Afatinib, Osimertinib

## Requirements

All packages are installed automatically in Colab. For local execution:

```
rdkit-pypi, vina, openbabel-wheel, meeko, pdbfixer, openmm,
pymol-open-source, py3Dmol, MDAnalysis, prolif, seaborn,
scipy, scikit-learn
```

## License

MIT
