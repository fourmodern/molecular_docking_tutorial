# Molecular Docking Tutorials

Colab-ready Jupyter notebooks for computational drug discovery — from single-target docking to multi-kinase selectivity analysis.

---

## Practical Docking (실전 도킹)

코드가 숨겨진 실전용 노트북. 입력만 하고 실행하면 됩니다.

| Notebook | Description | Open in Colab |
|----------|-------------|:---:|
| **01. 구조 탐색** | PDB 검색 → 비교 → 정렬 → 최적 구조 선택 | [![Open In Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/fourmodern/molecular_docking_tutorial/blob/main/practical_docking/01_Structure_Search.ipynb) |
| **02. 리간드 스크리닝** | SMILES 리스트 → 일괄 도킹 → 스코어 랭킹 | [![Open In Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/fourmodern/molecular_docking_tutorial/blob/main/practical_docking/02_Ligand_Screening.ipynb) |
| **03. SAR Matrix** | R1×R2 조합 → 도킹 → SAR 히트맵 | [![Open In Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/fourmodern/molecular_docking_tutorial/blob/main/practical_docking/03_SAR_Matrix.ipynb) |
| **04. Kinase Panel** | 5종 키나아제 × 리간드 → 선택성 분석 | [![Open In Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/fourmodern/molecular_docking_tutorial/blob/main/practical_docking/04_Kinase_Panel.ipynb) |
| **05. EGFR 변이체** | WT/변이체 × 4세대 약물 → 내성 분석 | [![Open In Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/fourmodern/molecular_docking_tutorial/blob/main/practical_docking/05_EGFR_Mutants.ipynb) |
| **06. Scoring 검증** | ChEMBL IC50 vs 도킹 스코어 → 최적 모델 | [![Open In Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/fourmodern/molecular_docking_tutorial/blob/main/practical_docking/06_Scoring_Validation.ipynb) |

### 권장 순서

```
01. 구조 탐색  →  최적 PDB 선택
        ↓
02. 리간드 스크리닝  →  후보 화합물 랭킹
        ↓
03. SAR Matrix  →  R-group 최적화
```

```
04. Kinase Panel  →  선택성 프로파일링
05. EGFR 변이체   →  내성 메커니즘 분석
```

### 공통 기능
- **Docking Box**: auto (co-crystal ligand) / residue (잔기 번호) / manual + **py3Dmol 3D 시각화**
- **구조 정렬**: MDAnalysis Cα align + RMSD 매트릭스
- **상호작용 분석**: ProLIF (수소결합, 소수성, π-π stacking)
- **내보내기**: CSV (DataWarrior/Excel) + SDF (DataWarrior) + PyMOL 스크립트

---

## Tutorial Notebooks (교육용)

단계별로 코드를 보며 학습하는 교육용 노트북.

| Notebook | Target | Description | Open in Colab |
|----------|--------|-------------|:---:|
| TYK2 Docking | TYK2 (6NZP) | 단일 타겟 도킹 파이프라인 | [![Open In Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/fourmodern/molecular_docking_tutorial/blob/main/TYK2_Molecular_Docking_Colab.ipynb) |
| Kinase Panel | 10 kinases | Cross-docking 선택성 분석 | [![Open In Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/fourmodern/molecular_docking_tutorial/blob/main/Kinase_Panel_Docking_Colab.ipynb) |
| EGFR WT vs Mutant | EGFR variants | TKI 내성 분석 | [![Open In Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/fourmodern/molecular_docking_tutorial/blob/main/EGFR_WT_Mutant_Docking_Colab.ipynb) |
| SAR Docking | TYK2 | SMILES 시리즈 SAR 분석 | [![Open In Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/fourmodern/molecular_docking_tutorial/blob/main/SAR_Docking_Analysis.ipynb) |
| SAR Matrix | TYK2 | R1×R2 매트릭스 | [![Open In Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/fourmodern/molecular_docking_tutorial/blob/main/SAR_Matrix.ipynb) |

---

## 결과 분석 도구

| 도구 | 용도 | 가이드 |
|------|------|--------|
| **PyMOL** (Windows) | 3D 구조 시각화, 도킹 포즈 비교 | [tutorial_pymol.md](tutorial_pymol.md) |
| **DataWarrior** (Windows) | 스코어 분석, SAR, 클러스터링 | [tutorial_datawarrior.md](tutorial_datawarrior.md) |

PyMOL 스크립트: [pymol_scripts/](pymol_scripts/) 폴더에 바로 실행 가능한 .pml 파일

---

## Docker / WSL 실행

Colab 없이 로컬에서 실행하는 방법. [INSTALL_WINDOWS.md](INSTALL_WINDOWS.md) 참조.

```bash
# Docker (권장)
git clone https://github.com/fourmodern/molecular_docking_tutorial.git
cd molecular_docking_tutorial
docker compose up --build
# → http://localhost:8888/?token=docking
```

```bash
# WSL
bash setup_wsl.sh
docking-notebook
# → http://localhost:8888
```

---

## 강의 슬라이드

| 슬라이드 | 내용 |
|----------|------|
| [Molecular_Docking_Workshop.pptx](Molecular_Docking_Workshop.pptx) | 도킹 워크숍 (18슬라이드) |
| [PyMOL_Tutorial.pptx](PyMOL_Tutorial.pptx) | PyMOL 시각화 (15슬라이드) |
| [DataWarrior_Tutorial.pptx](DataWarrior_Tutorial.pptx) | DataWarrior 분석 (12슬라이드) |
| [Windows_Setup_Guide.pptx](Windows_Setup_Guide.pptx) | WSL/Docker 설치 (12슬라이드) |

---

## License

MIT
