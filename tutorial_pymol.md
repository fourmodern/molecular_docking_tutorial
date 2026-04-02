# PyMOL 도킹 결과 시각화 튜토리얼

Colab에서 도킹을 완료한 후, 결과 파일을 Windows PyMOL에서 시각화하는 실습 가이드입니다.

---

## 준비물

- **PyMOL** (Windows 설치): https://pymol.org/2/
- **도킹 결과 파일** (Colab에서 다운로드한 zip):
  - `*_clean_H.pdb` — 준비된 단백질
  - `*_lig_H.mol2` — co-crystal 리간드 (참조용)
  - `*_vina_out.sdf` — Vina 도킹 결과
  - `*_smina_out.sdf` — smina 도킹 결과

---

## 실습 1: 단백질-리간드 복합체 보기

### 1-1. 파일 열기

PyMOL에서 File → Open → `6nzp_clean_H.pdb` 선택.

또는 PyMOL 명령줄에서:

```
load 6nzp_clean_H.pdb, protein
load 6nzp_lig_H.mol2, ref_ligand
```

### 1-2. 기본 표현 설정

```
# 단백질: 리본
show cartoon, protein
color palegreen, protein

# 리간드: 막대 모델
show sticks, ref_ligand
color magenta, ref_ligand
util.cbam ref_ligand
```

### 1-3. 결합 부위 확대

```
# 리간드 주변 5A 잔기 선택
select pocket, protein within 5 of ref_ligand
show sticks, pocket
color skyblue, pocket
util.cbac pocket

# 리간드 중심으로 줌
zoom ref_ligand, 8
```

### 1-4. 수소 결합 표시

```
distance hbonds, ref_ligand, pocket, mode=2
set dash_color, yellow, hbonds
set dash_width, 2.5
set dash_gap, 0.15
hide labels, hbonds
```

### 1-5. 표면 표시

```
show surface, pocket
set transparency, 0.7, pocket
set surface_color, white, pocket
```

---

## 실습 2: 도킹 포즈 분석

### 2-1. 도킹 결과 로드

```
load 6nzp_lig_vina_out.sdf, docked_vina
```

SDF에 여러 포즈가 있으면 자동으로 multi-state object로 로드됨.

### 2-2. 최적 포즈 보기

```
# 첫 번째 포즈(best score)만 표시
set all_states, 0
frame 1

show sticks, docked_vina
color green, docked_vina
util.cbag docked_vina
```

### 2-3. 참조 리간드와 비교

```
# 마젠타 = 실험 구조 (crystal)
# 초록 = 도킹 예측 (docked)
show sticks, ref_ligand
color magenta, ref_ligand

# 두 리간드 겹쳐서 RMSD 시각 확인
zoom ref_ligand, 8
```

### 2-4. 여러 포즈 순회

```
# 모든 포즈 동시에 보기
set all_states, 1
set state, 0

# 하나씩 넘기기
frame 1   # 1번 포즈
frame 2   # 2번 포즈
frame 3   # 3번 포즈

# 포즈별 색상 구분
split_states docked_vina
color green, docked_vina_0001
color yellow, docked_vina_0002
color salmon, docked_vina_0003
color cyan, docked_vina_0004
color orange, docked_vina_0005
```

### 2-5. 특정 포즈의 상호작용 분석

```
# 3번 포즈 선택
frame 3

# 이 포즈와 단백질 사이 수소결합
distance hb_pose3, docked_vina and state 3, pocket, mode=2

# 거리 측정 (특정 원자 간)
distance d1, /docked_vina//A/UNK`1/N1, /protein//A/LEU`932/O
```

---

## 실습 3: Vina vs smina 비교

```
# 두 결과 동시 로드
load 6nzp_lig_vina_out.sdf, vina_poses
load 6nzp_native_smina_out.sdf, smina_poses

# best pose만
set all_states, 0
frame 1

# 색상 구분
color green, vina_poses
color cyan, smina_poses
show sticks, vina_poses
show sticks, smina_poses

# 겹쳐서 비교
zoom ref_ligand, 8
```

---

## 실습 4: EGFR 변이체 비교 (EGFR 노트북용)

### 4-1. WT vs T790M 구조 정렬

```
load WT_Erlotinib/1m17_clean_H.pdb, WT
load T790M_Neratinib/2jit_clean_H.pdb, T790M

# CE-Align (구조 정렬)
cealign WT, T790M

# 색상 구분
color palegreen, WT
color salmon, T790M
show cartoon, WT or T790M
```

### 4-2. 변이 잔기 하이라이트

```
# 790번 잔기 (Thr→Met gatekeeper mutation)
select gatekeeper_wt, WT and resi 790
select gatekeeper_mut, T790M and resi 790

show spheres, gatekeeper_wt or gatekeeper_mut
color blue, gatekeeper_wt
color red, gatekeeper_mut

# 라벨
label gatekeeper_wt and name CA, "T790 (WT)"
label gatekeeper_mut and name CA, "M790 (Mut)"
set label_size, 18
```

### 4-3. 약물 도킹 포즈 비교

```
# WT에 도킹된 Osimertinib
load WT_Erlotinib/Osimertinib_smina_out.sdf, osi_in_WT

# T790M에 도킹된 Osimertinib
load T790M_Neratinib/Osimertinib_smina_out.sdf, osi_in_T790M

color green, osi_in_WT
color orange, osi_in_T790M
show sticks, osi_in_WT or osi_in_T790M

# → Osimertinib이 T790M에 더 잘 결합하는지 시각적 확인
```

---

## 실습 5: Kinase Panel 비교 (Kinase Panel 노트북용)

```
# 여러 키나아제 결합 부위 비교
load EGFR/1m17_clean_H.pdb, EGFR
load ABL1/1iep_clean_H.pdb, ABL1
load BRAF/3og7_clean_H.pdb, BRAF

# 모두 정렬
cealign EGFR, ABL1
cealign EGFR, BRAF

# 색상
color palegreen, EGFR
color lightblue, ABL1
color salmon, BRAF
show cartoon, all

# 결합 부위 비교
select site_egfr, EGFR within 5 of (EGFR and organic)
select site_abl1, ABL1 within 5 of (ABL1 and organic)
show sticks, site_egfr or site_abl1
```

---

## 이미지 저장

```
# 배경 흰색
bg_color white

# 고해상도 렌더링
ray 2400, 1800
png docking_result.png, dpi=300

# 세션 저장 (나중에 다시 열기)
save my_session.pse
```

---

## PyMOL 스크립트 파일 (.pml) 사용

`pymol_scripts/` 폴더의 스크립트를 PyMOL에서 실행:

```
@pymol_scripts/01_load_structure.pml
@pymol_scripts/02_docking_pose.pml
@pymol_scripts/03_compare_mutations.pml
```

또는 File → Run Script → .pml 파일 선택.
