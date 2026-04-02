# Windows 설치 가이드

## 방법 1: Google Colab (설치 불필요, 권장)

1. https://colab.research.google.com 접속
2. GitHub 탭 → `fourmodern/molecular_docking_tutorial` 검색
3. 원하는 노트북 선택 → 순서대로 실행
4. 결과 파일은 마지막 셀에서 zip으로 다운로드

---

## 방법 2: Docker (Windows 10/11)

### 1단계: WSL2 설치

PowerShell을 **관리자 권한**으로 열고:

```powershell
wsl --install
```

설치 후 **PC 재부팅**. 재부팅하면 Ubuntu 설정 화면이 뜸 → 사용자명/비밀번호 설정.

WSL 버전 확인:
```powershell
wsl --version
```

### 2단계: Docker Desktop 설치

1. https://www.docker.com/products/docker-desktop/ 에서 다운로드
2. 설치 실행 → **Use WSL 2 based engine** 체크 확인
3. 설치 완료 후 PC 재부팅
4. Docker Desktop 실행 → 좌측 하단에 "Engine running" 확인

### 3단계: 실행

PowerShell에서:

```powershell
git clone https://github.com/fourmodern/molecular_docking_tutorial.git
cd molecular_docking_tutorial
docker compose up --build
```

첫 빌드는 10~15분 소요. 완료되면:

```
http://localhost:8888/?token=docking
```

브라우저에서 접속 → 노트북 실행.

### 결과 파일 → PyMOL

도킹 결과는 `results/` 폴더에 저장됨. PyMOL에서 File → Open:

```
molecular_docking_tutorial\results\*.pdb
molecular_docking_tutorial\results\*.sdf
```

### 종료

```powershell
# Ctrl+C 로 중지, 또는:
docker compose down
```

---

## 방법 3: WSL2 직접 설치 (Docker 없이)

### 1단계: WSL2 설치

위 Docker 방법의 1단계와 동일.

### 2단계: 도킹 환경 설치

WSL Ubuntu 터미널을 열고:

```bash
git clone https://github.com/fourmodern/molecular_docking_tutorial.git
cd molecular_docking_tutorial
bash setup_wsl.sh
```

설치 완료 후:

```bash
source ~/.bashrc
docking-notebook
```

브라우저에서 `http://localhost:8888` 접속.

### 결과 파일 → PyMOL

Windows 탐색기 주소창에 입력:

```
\\wsl$\Ubuntu\home\사용자명\docking_workshop\
```

여기서 PDB/SDF 파일을 PyMOL로 열면 됨.

---

## PyMOL 설치 (Windows)

1. https://pymol.org/2/ 에서 Windows 설치파일 다운로드
2. 또는 conda: `conda install -c conda-forge pymol-open-source`

---

## 문제 해결

| 증상 | 해결 |
|------|------|
| `wsl --install` 실패 | Windows 업데이트 후 재시도 |
| Docker "WSL 2 not found" | `wsl --update` 실행 후 재부팅 |
| Docker 빌드 중 smina 다운로드 실패 | 네트워크 확인, VPN 끄기 |
| Jupyter 접속 안 됨 | 방화벽에서 8888 포트 허용 |
| PyMOL에서 SDF 안 열림 | Open Babel 설치 또는 PDB로 변환 |
| WSL에서 `\\wsl$` 경로 안 보임 | 탐색기에서 `\\wsl.localhost\Ubuntu` 시도 |
