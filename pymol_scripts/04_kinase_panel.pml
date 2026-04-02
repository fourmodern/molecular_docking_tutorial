# ============================================================
# 04. Kinase Panel 결합 부위 비교 (Kinase Panel 노트북 결과용)
# Kinase_Panel_Docking_Colab 결과 폴더에서 실행
# ============================================================

reinitialize
bg_color white
set ray_shadow, 0

# --- 대표 키나아제 3종 로드 ---
# 경로를 본인의 결과 폴더에 맞게 수정
load EGFR/1m17_clean_H.pdb, EGFR
load ABL1/1iep_clean_H.pdb, ABL1
load BRAF/3og7_clean_H.pdb, BRAF

# --- 구조 정렬 ---
cealign EGFR, ABL1
cealign EGFR, BRAF

# --- 리본 표현 ---
show cartoon, all
color palegreen, EGFR
color lightblue, ABL1
color lightorange, BRAF

# --- 결합 부위 비교 ---
select site_egfr, EGFR within 5 of (EGFR and organic)
select site_abl1, ABL1 within 5 of (ABL1 and organic)
select site_braf, BRAF within 5 of (BRAF and organic)

show sticks, site_egfr or site_abl1 or site_braf

# --- 리간드 표시 ---
select lig_egfr, EGFR and organic
select lig_abl1, ABL1 and organic
select lig_braf, BRAF and organic

show sticks, lig_egfr or lig_abl1 or lig_braf
color green, lig_egfr and elem C
color blue, lig_abl1 and elem C
color orange, lig_braf and elem C
set stick_radius, 0.2, lig_egfr or lig_abl1 or lig_braf

# --- 도킹 결과 비교 (선택) ---
# load EGFR/native_smina_out.sdf, dock_egfr
# load ABL1/native_smina_out.sdf, dock_abl1
# set all_states, 0
# frame 1

# --- 카메라 ---
zoom lig_egfr, 10

print("04_kinase_panel.pml complete")
print("  green  = EGFR (Erlotinib)")
print("  blue   = ABL1 (Imatinib)")
print("  orange = BRAF (Vemurafenib)")
