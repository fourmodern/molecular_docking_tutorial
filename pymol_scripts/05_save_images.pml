# ============================================================
# 05. 고해상도 이미지 저장
# 다른 스크립트 실행 후 원하는 뷰에서 실행
# ============================================================

# --- 렌더링 설정 ---
set antialias, 2
set ray_shadow, 1
set ray_trace_mode, 1
set ambient, 0.4
set direct, 0.6
set specular, 0.3

# --- 배경 ---
bg_color white

# --- 고해상도 렌더링 & 저장 ---
ray 2400, 1800
png docking_result_hires.png, dpi=300

# --- 세션 저장 ---
save session.pse

print("Images saved:")
print("  docking_result_hires.png (2400x1800, 300dpi)")
print("  session.pse (PyMOL session)")
