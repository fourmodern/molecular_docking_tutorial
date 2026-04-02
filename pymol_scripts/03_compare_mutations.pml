# ============================================================
# 03. EGFR 변이체 비교 (EGFR 노트북 결과용)
# EGFR_WT_Mutant_Docking_Colab 결과 폴더에서 실행
# ============================================================

reinitialize
bg_color white
set ray_shadow, 0

# --- 구조 로드 ---
# 경로를 본인의 결과 폴더에 맞게 수정
load WT_Erlotinib/1m17_clean_H.pdb, WT
load T790M_Neratinib/2jit_clean_H.pdb, T790M

# --- 구조 정렬 ---
cealign WT, T790M

# --- 리본 표현 ---
show cartoon, WT
show cartoon, T790M
color palegreen, WT
color salmon, T790M

# --- Gatekeeper 잔기 (790) ---
select gate_wt, WT and resi 790
select gate_mut, T790M and resi 790

show spheres, gate_wt or gate_mut
set sphere_scale, 0.8
color blue, gate_wt
color red, gate_mut

label gate_wt and name CA, "Thr790 (WT)"
label gate_mut and name CA, "Met790 (Mut)"
set label_size, 16
set label_color, black

# --- 결합 부위 잔기 ---
select site_wt, WT within 5 of (WT and organic)
select site_mut, T790M within 5 of (T790M and organic)
show sticks, site_wt or site_mut

# --- 도킹된 약물 비교 (있을 경우) ---
# load WT_Erlotinib/Osimertinib_smina_out.sdf, osi_WT
# load T790M_Neratinib/Osimertinib_smina_out.sdf, osi_T790M
# set all_states, 0
# frame 1
# show sticks, osi_WT or osi_T790M
# color green, osi_WT and elem C
# color orange, osi_T790M and elem C

# --- 카메라 ---
zoom gate_wt, 12

print("03_compare_mutations.pml complete")
print("  green  = WT (wild-type)")
print("  salmon = T790M (mutant)")
print("  blue sphere  = Thr790 (WT)")
print("  red sphere   = Met790 (mutant)")
