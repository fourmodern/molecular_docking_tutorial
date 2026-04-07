# DataWarrior로 도킹 결과 분석하기

practical_docking 노트북에서 다운로드한 CSV/SDF 파일을 DataWarrior에서 분석하는 가이드입니다.

DataWarrior 다운로드: https://openmolecules.org/datawarrior/

---

## 결과 파일 구조

```
results/
├── *.csv                  ← 스코어 테이블 (DataWarrior/Excel)
├── *.sdf                  ← 구조 + 스코어 (DataWarrior 권장)
├── *_docked.sdf           ← 도킹 포즈 (구조 포함)
└── results_for_viewer/    ← PyMOL용 PDB+SDF
```

**SDF vs CSV:**
- SDF: 2D/3D 구조 포함 → 구조 검색, R-Group 분해 가능
- CSV: 숫자만 → 빠른 로드, 차트 분석

---

## Step 1: 파일 열기

1. DataWarrior 실행
2. **File → Open**
3. SDF 또는 CSV 파일 선택

열면 자동으로:
- 왼쪽: 2D 구조 (SDF인 경우)
- 오른쪽: 속성 테이블 (Score, MW, cLogP 등)

---

## Step 2: 분자 속성 계산

**Chemistry → From Chemical Structure → Calculate Properties**

체크할 항목:
- Total Molweight (분자량)
- cLogP (소수성)
- H-Bond Acceptors / Donors
- Rotatable Bond Count
- Total Surface Area (TPSA)
- Drug-Likeness

→ OK 클릭하면 새 컬럼으로 추가됨

---

## 노트북별 분석 방법

### 02. Ligand Screening 결과

**파일:** `screening_results.csv` 또는 `screening_results.sdf`

#### 스코어 랭킹
1. `Best Score` 컬럼 헤더 클릭 → 오름차순 정렬
2. 가장 위가 best (가장 낮은 음수)

#### 스코어 분포 히스토그램
1. 우클릭 빈 영역 → **New View → Bar Chart**
2. X축: `Best Score`
3. → -7 kcal/mol 이하가 좋은 결합

#### Score vs MW 산점도
1. 우클릭 → **New View → 2D Scatter Plot**
2. X축: `Best Score`
3. Y축: `Total Molweight`
4. → 스코어 좋으면서 MW 500 이하인 화합물이 이상적

#### Ligand Efficiency
1. 새 컬럼 추가: **Chemistry → Calculate Properties**
2. 또는 직접 계산: `LE = -Score / Heavy Atoms`
3. LE > 0.3 = drug-like

---

### 03. SAR Matrix 결과

**파일:** `sar_matrix.csv`, `sar_table.csv`, `sar_matrix.sdf`

#### SAR 매트릭스 히트맵
1. `sar_matrix.csv` 열기
2. R1(행) × R2(열) 형태의 스코어 테이블
3. **우클릭 → New View → Correlation Matrix** 또는 Excel에서 조건부 서식

#### R-Group Decomposition (SDF)
1. `sar_matrix.sdf` 열기
2. **Chemistry → From Chemical Structure → R-Group Decomposition**
3. Core structure 자동 감지
4. R1, R2 별도 컬럼 생성
5. → Scatter Plot: R1 vs Score

#### Activity Cliff 분석
1. **Chemistry → From Chemical Structure → Similarity Analysis**
2. Descriptor: FragFp
3. **우클릭 → New View → Structure-Activity Landscape**
4. → 구조 비슷 + 스코어 크게 다른 쌍 = Activity Cliff = SAR 핵심

---

### 04. Kinase Panel 결과

**파일:** `kinase_panel_results.csv`

#### 선택성 바 차트
1. 우클릭 → **New View → Bar Chart**
2. Category: `Kinase`
3. Value: `Best Score`
4. → 타겟에만 강하게 결합하는 리간드가 이상적

#### 선택성 지수
1. 최고 스코어(best)와 각 키나아제 스코어의 차이 계산
2. 차이가 클수록 선택적

---

### 05. EGFR Mutants 결과

**파일:** `egfr_crossdock.csv`, `egfr_matrix.csv`

#### Cross-docking 히트맵
1. `egfr_matrix.csv` 열기
2. 행: EGFR 구조 (WT, L858R, T790M, DM)
3. 열: 약물 (Erlotinib, Gefitinib, Afatinib, Osimertinib)
4. Excel에서 조건부 서식 또는 DataWarrior Correlation Matrix

#### 내성 패턴
- WT → T790M에서 스코어가 나빠지는 약물 = 1세대 (내성)
- T790M에서도 좋은 약물 = 3세대 (내성 극복)

---

### 06. Scoring Validation 결과

**파일:** `scoring_validation.csv`, `model_comparison.csv`

#### Score vs pIC50 산점도
1. `scoring_validation.csv` 열기
2. 우클릭 → **New View → 2D Scatter Plot**
3. X축: `vina_best` (또는 `vinardo_best`, `ad4_scoring_best`)
4. Y축: `pIC50`
5. → 음의 상관관계가 보이면 scoring function이 유효

#### Scoring Function 비교
1. `model_comparison.csv` 열기
2. R² 기준으로 정렬
3. 가장 높은 R² 모델이 최적

---

## Lipinski Rule of Five 필터

1. **Chemistry → Calculate Properties** (MW, cLogP, HBA, HBD)
2. 필터 패널에서 슬라이더 조절:

| 규칙 | 기준 |
|------|------|
| MW | < 500 Da |
| cLogP | < 5 |
| HBD | ≤ 5 |
| HBA | ≤ 10 |

3. 위반 화합물이 자동으로 회색 처리됨

---

## 독성 예측

**Chemistry → From Chemical Structure → Predict Properties**

- Mutagenicity (돌연변이 유발성)
- Tumorigenicity (종양 유발성)
- Irritant (자극성)
- Reproductive Effect (생식 독성)

→ 독성 위험 화합물을 사전에 제거

---

## 클러스터링

1. **Chemistry → Cluster Compounds**
   - Descriptor: SkelSpheres
   - Algorithm: Complete Linkage
2. 우클릭 → **New View → Scatter Plot**
   - Color by: Cluster No
3. 각 클러스터에서 best score 화합물 선택 → 다양한 scaffold 확보

---

## 화합물 선별 → PyMOL로 보기

1. DataWarrior에서 필터 적용 (Score < -8, LE > 0.3, Lipinski 통과)
2. 원하는 행 선택 (Ctrl+클릭)
3. **File → Save Special → SD-File** → `selected.sdf`
4. PyMOL에서:
```
load protein.pdb, protein
load selected.sdf, hits
show cartoon, protein
show sticks, hits
color green, hits
zoom hits, 8
```

---

## 내보내기

| 형식 | 메뉴 | 용도 |
|------|------|------|
| .dwar | File → Save | DataWarrior 세션 (필터/뷰 포함) |
| .sdf | File → Save Special → SD-File | 선별 화합물 (PyMOL로 전달) |
| .csv | File → Save Special → Text File | 스프레드시트 |
| 이미지 | 차트 우클릭 → Copy/Save Image | 보고서용 PNG/SVG |

---

## 팁

| 기능 | 방법 |
|------|------|
| 구조 검색 | 필터 패널에서 구조 그리기 → substructure 검색 |
| 유사 화합물 찾기 | Chemistry → Find Similar Compounds |
| 컬럼 숨기기 | 컬럼 헤더 우클릭 → Hide Column |
| 행 색칠 | 우클릭 → Set Row Color |
| 매크로 기록 | Macro → Start Recording |
