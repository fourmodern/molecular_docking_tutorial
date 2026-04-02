# DataWarrior 도킹 결과 분석 튜토리얼

Colab 도킹 결과(SDF/CSV)를 DataWarrior에서 시각적으로 분석하는 실습 가이드입니다.

---

## DataWarrior 설치

- 다운로드: https://openmolecules.org/datawarrior/download.html
- Windows 설치 후 바로 사용 가능 (무료)

---

## 준비물 (Colab에서 다운로드)

| 파일 | 설명 | 사용 실습 |
|------|------|---------|
| `*_vina_out.sdf` | Vina 도킹 결과 (구조+스코어) | 실습 1-3 |
| `*_smina_out.sdf` | smina 도킹 결과 | 실습 1-3 |
| `all_docking_scores.csv` | 전체 스코어 테이블 | 실습 4 |
| `crossdock_matrix.csv` | Cross-docking 매트릭스 | 실습 5 |
| `summary.csv` | 요약 테이블 | 실습 4 |

---

## 실습 1: SDF 파일 열기 & 구조 탐색

### 1-1. SDF 파일 로드

1. DataWarrior 실행
2. File → Open → `6nzp_lig_vina_out.sdf` 선택
3. 자동으로 분자 구조 + 속성 테이블이 로드됨

로드 후 보이는 컬럼:
- **Structure** — 2D 분자 구조
- **minimizedAffinity** — 도킹 스코어 (kcal/mol)
- **Pose** — 포즈 번호

### 1-2. 테이블 정렬

1. `minimizedAffinity` 컬럼 헤더 클릭 → 오름차순 정렬
2. 가장 위가 best score (가장 낮은 음수)

### 1-3. 2D 구조 보기

1. 좌측 Structure 컬럼에 2D 구조가 자동 표시
2. 셀을 더블클릭하면 확대 뷰

### 1-4. 분자 속성 계산

1. Chemistry → From Chemical Structure → Calculate Properties
2. 계산할 항목 선택:
   - **Total Molweight** — 분자량
   - **cLogP** — 소수성
   - **H-Bond Acceptors** — 수소결합 수용체 수
   - **H-Bond Donors** — 수소결합 공여체 수
   - **Total Surface Area** — 표면적
   - **Rotatable Bond Count** — 회전 가능 결합 수
   - **Drug-Likeness** — 약물 유사성 스코어
3. OK → 새 컬럼이 추가됨

---

## 실습 2: 스코어 시각화

### 2-1. 히스토그램 (스코어 분포)

1. 우클릭 빈 영역 → New View → Bar Chart
2. X축: `minimizedAffinity` (자동 binning)
3. → 스코어 분포 확인. -7 kcal/mol 이하가 좋은 결합

### 2-2. 산점도 (Score vs 분자 속성)

1. 우클릭 → New View → 2D-Scatter Plot
2. X축: `minimizedAffinity`
3. Y축: `Total Molweight` (또는 `cLogP`)
4. → 스코어와 분자 크기/소수성의 상관관계 확인

### 2-3. Box Plot (Vina vs smina 비교)

두 SDF 파일을 합친 경우:

1. 우클릭 → New View → Box Plot
2. Category: `Method` (Vina / smina)
3. Value: `minimizedAffinity`
4. → 두 엔진의 스코어 범위와 중앙값 비교

---

## 실습 3: Lipinski Rule of Five 필터

### 3-1. 필터 설정

1. Chemistry → From Chemical Structure → Calculate Properties
   - MW, cLogP, HBA, HBD 계산
2. Edit → New Filter → 다음 조건 설정:

| 규칙 | 조건 |
|------|------|
| MW | < 500 |
| cLogP | < 5 |
| HBD | ≤ 5 |
| HBA | ≤ 10 |

3. → Lipinski Rule of Five 위반 화합물이 자동으로 필터링됨

### 3-2. Drug-Likeness 분포

1. 우클릭 → New View → Bar Chart
2. X축: `Drug-Likeness`
3. → 양수 값이면 약물 유사성 높음

---

## 실습 4: Kinase Panel CSV 분석

### 4-1. CSV 로드

1. File → Open → `all_docking_scores.csv`
2. 자동으로 테이블 로드

### 4-2. 키나아제별 스코어 비교

1. 우클릭 → New View → Box Plot
2. Category: `kinase`
3. Value: `minimizedAffinity`
4. Color by: `group` (TK, CMGC, TKL 등)
5. → 키나아제 그룹별 스코어 패턴 확인

### 4-3. 히트맵 (Cross-docking)

1. File → Open → `crossdock_matrix.csv`
2. 우클릭 → New View → Correlation Matrix 또는 2D-Plot
3. → 선택성이 높은 리간드/타겟 쌍 식별

### 4-4. PCA (주성분 분석)

1. Edit → Extended Copy as → SDF (구조 포함 시)
2. Chemistry → Principal Component Analysis
3. 사용할 descriptor 선택 (FragFp 또는 SkelSpheres)
4. → 키나아제별 리간드가 화학 공간에서 어떻게 분포하는지 확인

---

## 실습 5: SAR (구조-활성 관계) 분석

### 5-1. Activity Cliff 분석

1. Chemistry → From Chemical Structure → Similarity Analysis
   - Descriptor: `FragFp` (fragment fingerprint)
2. 우클릭 → New View → Structure-Activity Landscape (SALI)
   - X/Y: 유사도 좌표
   - Color: `minimizedAffinity`
3. → 구조가 비슷한데 스코어가 크게 다른 쌍 = Activity Cliff

### 5-2. R-Group Decomposition

커스텀 리간드 시리즈가 있을 경우:

1. Chemistry → R-Group Decomposition
2. Core structure 지정 (MCS 자동 감지)
3. → R-group별 스코어 변화를 테이블로 확인

### 5-3. 클러스터링

1. Chemistry → Cluster Compounds
   - Descriptor: `SkelSpheres`
   - Algorithm: `Complete Linkage`
2. → 구조적으로 유사한 포즈끼리 그룹화
3. 우클릭 → New View → Scatter Plot
   - Color by: `Cluster No`
   - Size by: `minimizedAffinity`

---

## 실습 6: 리포트 생성 & 내보내기

### 6-1. 선별된 화합물 내보내기

1. 원하는 행 선택 (Ctrl+클릭 또는 필터)
2. File → Save Special → SD-File
3. → 선별된 포즈만 SDF로 저장
4. → 이 SDF를 PyMOL에서 열어 3D 구조 확인

### 6-2. 이미지 저장

1. 원하는 차트/플롯 우클릭 → Copy Image 또는 Save Image
2. PNG/SVG로 저장 가능

### 6-3. 전체 분석 저장

1. File → Save → `.dwar` 파일 (DataWarrior 세션)
2. 다음에 열면 모든 뷰/필터/설정이 복원됨

---

## DataWarrior → PyMOL 연동 워크플로우

```
[DataWarrior에서 분석]
    ↓ 스코어/속성 기반 필터링
    ↓ Activity Cliff 식별
    ↓ 관심 포즈 선별
    ↓ SDF로 내보내기
[PyMOL에서 시각화]
    ↓ 선별된 SDF 로드
    ↓ 단백질과 함께 3D 보기
    ↓ 수소결합/상호작용 분석
    ↓ 이미지 저장
```

### DataWarrior에서 선별 → PyMOL로 보기

1. DataWarrior: 필터 적용 → File → Save Special → SD-File → `selected_poses.sdf`
2. PyMOL:
```
load protein_H.pdb, protein
load selected_poses.sdf, hits
show cartoon, protein
show sticks, hits
color green, hits
zoom hits, 8
```

---

## 팁

| 기능 | 단축키/메뉴 |
|------|-----------|
| 구조 검색 | Edit → Find Similar → SMARTS 패턴 |
| Substructure 필터 | 필터 패널에서 구조 그리기 |
| 컬럼 숨기기 | 컬럼 헤더 우클릭 → Hide Column |
| 행 색칠 | 우클릭 → Set Row Color |
| 매크로 기록 | Macro → Start Recording |
