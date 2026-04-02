# ============================================================
# 02. 도킹 포즈 분석: Crystal vs Docked 비교
# 01_load_structure.pml 실행 후 이 스크립트를 실행하세요
# ============================================================

# --- Vina 도킹 결과 로드 ---
load 6nzp_lig_vina_out.sdf, docked_vina

# 첫 번째 포즈(best score)만 표시
set all_states, 0
frame 1

# 도킹 포즈: 초록색
show sticks, docked_vina
color green, docked_vina and elem C
set stick_radius, 0.15, docked_vina

# 참조 리간드: 마젠타 (이미 로드됨)
color magenta, ref_ligand and elem C

# --- 비교 뷰 ---
# 마젠타 = 실험(crystal), 초록 = 예측(docked)
zoom ref_ligand, 8

# --- 여러 포즈 보기 ---
# 아래 주석을 해제하면 상위 5개 포즈를 분리하여 색상 구분
# split_states docked_vina, prefix=pose_
# color green, pose_0001
# color yellow, pose_0002
# color salmon, pose_0003
# color cyan, pose_0004
# color orange, pose_0005
# show sticks, pose_*

# --- smina 결과 추가 (선택) ---
# load 6nzp_native_smina_out.sdf, docked_smina
# show sticks, docked_smina
# color cyan, docked_smina and elem C

# --- 도킹 포즈의 수소 결합 ---
distance hb_docked, docked_vina, pocket, mode=2
set dash_color, chartreuse, hb_docked
set dash_width, 2.0
hide labels, hb_docked

print("02_docking_pose.pml complete")
print("  magenta = crystal pose")
print("  green   = docked pose (Vina best)")
