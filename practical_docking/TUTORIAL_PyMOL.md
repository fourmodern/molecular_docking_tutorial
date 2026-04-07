# PyMOL로 도킹 결과 보기

practical_docking 노트북에서 다운로드한 결과 파일을 PyMOL에서 시각화하는 가이드입니다.

---

## 결과 파일 구조

ZIP 다운로드 후 압축을 풀면:

```
results_for_viewer/
├── *_protein.pdb          ← 단백질 구조
├── *_docked.sdf           ← 도킹 포즈 (여러 개)
├── *_crystal.sdf          ← Crystal 리간드 포즈
└── *.pml                  ← PyMOL 자동 스크립트
```

---

## 방법 1: PML 스크립트 실행 (가장 쉬움)

1. PyMOL 실행
2. **File → Run Script** → `.pml` 파일 선택
3. 자동으로 단백질 + 도킹 포즈가 로드됨

---

## 방법 2: 수동으로 열기

### Step 1: 단백질 로드

```
File → Open → *_protein.pdb
```

또는 명령줄:
```
load protein.pdb, protein
```

### Step 2: 단백질 표현 설정

```
show cartoon, protein
color white, protein
```

### Step 3: 도킹 포즈 로드

```
File → Open → *_docked.sdf
```

SDF에 여러 포즈가 있으면 multi-state object로 로드됩니다.

```
# 첫 번째 포즈(best score)만 보기
set all_states, 0
frame 1

# 모든 포즈 동시에 보기
set all_states, 1
```

### Step 4: 리간드 색상 설정

```
show sticks, *_docked
color green, *_docked
```

### Step 5: 결합 부위 표시

```
# 리간드 주변 5Å 잔기
select pocket, protein within 5 of *_docked
show sticks, pocket
color skyblue, pocket
```

### Step 6: 수소 결합

```
distance hbonds, *_docked, pocket, mode=2
set dash_color, yellow, hbonds
set dash_width, 2.5
```

---

## 노트북별 결과 보기

### 01. Structure Search — 여러 PDB 비교

```
# 정렬된 구조들 로드
load 8s99_protein.pdb, PDB1
load 4wov_protein.pdb, PDB2

# 각각 다른 색
color palegreen, PDB1
color salmon, PDB2
show cartoon, all

# 도킹 포즈 비교
load 8s99_docked.sdf, dock1
load 4wov_docked.sdf, dock2
color green, dock1
color orange, dock2
```

### 02. Ligand Screening — 여러 리간드 랭킹

```
# 단백질 + 여러 리간드 포즈
load protein.pdb, protein
show cartoon, protein
color white, protein

# Top 5 리간드 각각 로드
load Erlotinib_docked.sdf, Erlotinib
load Gefitinib_docked.sdf, Gefitinib
load Osimertinib_docked.sdf, Osimertinib

# 각각 다른 색
color green, Erlotinib
color cyan, Gefitinib
color orange, Osimertinib
show sticks, Erlotinib or Gefitinib or Osimertinib
```

### 03. SAR Matrix — R-group별 포즈 비교

```
# Best 조합과 Worst 조합 비교
load R1=F_R2=OH_docked.sdf, best
load R1=OCH3_R2=H_docked.sdf, worst

color green, best      # 좋은 스코어
color red, worst       # 나쁜 스코어

# 어떤 상호작용 차이가 있는지 확인
distance hb_best, best, pocket, mode=2
distance hb_worst, worst, pocket, mode=2
```

### 04. Kinase Panel — 선택성 비교

```
# 정렬된 키나아제 구조들
load EGFR_protein.pdb, EGFR
load ABL1_protein.pdb, ABL1
load BRAF_protein.pdb, BRAF

# 같은 리간드의 다른 키나아제 포즈
load EGFR/Erlotinib_docked.sdf, Erl_EGFR
load ABL1/Erlotinib_docked.sdf, Erl_ABL1
load BRAF/Erlotinib_docked.sdf, Erl_BRAF

# 포켓 형태 비교
show surface, EGFR within 5 of Erl_EGFR
set transparency, 0.7
```

### 05. EGFR Mutants — 변이체별 약물 결합 비교

```
# WT vs T790M
load WT_Erlotinib_protein.pdb, WT
load T790M_Neratinib_protein.pdb, T790M
color palegreen, WT
color salmon, T790M

# 변이 잔기 표시
select gate, T790M and resi 790
show spheres, gate
color red, gate
label gate and name CA, "T790M"

# Osimertinib 포즈 비교
load WT_Erlotinib/Osimertinib_docked.sdf, Osi_WT
load T790M_Neratinib/Osimertinib_docked.sdf, Osi_T790M
color green, Osi_WT
color orange, Osi_T790M
```

---

## 여러 포즈 분석

### 포즈별 순회

```
# 키보드 ← → 로 포즈 넘기기
frame 1   # best score
frame 2   # 2nd best
frame 3   # 3rd

# 또는 포즈 분리
split_states *_docked
color green, *_docked_0001   # best
color yellow, *_docked_0002
color salmon, *_docked_0003
```

### Crystal vs Docked 비교

```
# Crystal 포즈 (마젠타)
load *_crystal.sdf, crystal
color magenta, crystal
show sticks, crystal

# Docked 포즈 (초록)
load *_docked.sdf, docked
color green, docked
show sticks, docked

# 겹쳐서 RMSD 시각적 확인
# magenta = 실험, green = 예측
```

---

## 이미지 저장

```
# 배경 흰색
bg_color white

# 고해상도 렌더링
ray 2400, 1800
png docking_result.png, dpi=300

# 세션 저장 (나중에 수정 가능)
save my_session.pse
```

---

## 추천 색상 규칙

| 대상 | 색상 | 명령 |
|------|------|------|
| 단백질 리본 | 흰색/연초록 | `color white, protein` |
| 결합 부위 잔기 | 하늘색 | `color skyblue, pocket` |
| Crystal 리간드 | 마젠타 | `color magenta, crystal` |
| 도킹 포즈 | 초록 | `color green, docked` |
| 수소 결합 | 노랑 점선 | `set dash_color, yellow` |
| WT 구조 | 연초록 | `color palegreen, WT` |
| Mutant 구조 | 연어색 | `color salmon, mutant` |
| 변이 잔기 | 빨강 구 | `color red, mutation` |
