# ============================================================
# 01. 단백질-리간드 복합체 로드 & 기본 시각화
# 사용법: PyMOL에서 File → Run Script → 이 파일 선택
# 또는 명령줄에서: @01_load_structure.pml
# ============================================================

# --- 파일 경로 수정 ---
# 아래 경로를 본인의 결과 폴더에 맞게 수정하세요
set_name_path = .

# 초기화
reinitialize
bg_color white
set ray_shadow, 0

# 단백질 로드
load 6nzp_clean_H.pdb, protein
# 리간드 로드 (co-crystal)
load 6nzp_lig_H.mol2, ref_ligand

# --- 단백질 표현 ---
hide everything, protein
show cartoon, protein
color palegreen, protein
set cartoon_transparency, 0.1

# --- 리간드 표현 ---
show sticks, ref_ligand
util.cbam ref_ligand
set stick_radius, 0.15, ref_ligand

# --- 결합 부위 ---
select pocket, protein within 5 of ref_ligand
show sticks, pocket
util.cbac pocket
set stick_radius, 0.12, pocket

# --- 표면 ---
show surface, pocket
set transparency, 0.75, pocket
set surface_color, white, pocket

# --- 수소 결합 ---
distance hbonds, ref_ligand, pocket, mode=2
set dash_color, yellow, hbonds
set dash_width, 2.5
set dash_gap, 0.15
hide labels, hbonds

# --- 잔기 라벨 ---
label pocket and name CA, "%s%s" % (resn, resi)
set label_size, 12
set label_color, black
set label_font_id, 7

# --- 카메라 ---
zoom ref_ligand, 8
set depth_cue, 0
set fog, 0

print("01_load_structure.pml complete")
