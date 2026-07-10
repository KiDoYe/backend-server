#!/bin/bash
# =========================================================
# 잡코리아 크롤러 실행 스크립트 (라즈베리파이 / 리눅스 서버용)
#
# 사용법:
#   chmod +x run.sh
#   ./run.sh
#
# 하는 일:
#   1) 가상환경(venv)이 없으면 생성
#   2) 가상환경 활성화
#   3) requirements.txt 기준으로 패키지 설치
#   4) crawl.py 실행
#
# 참고: requests 기반이라 브라우저(Chromium) 설치가 필요 없습니다.
#       (라즈베리파이 2B처럼 32비트/저사양 환경에서도 가볍게 동작)
# =========================================================
set -e

# 이 스크립트 파일이 있는 폴더로 이동 (어디서 실행하든 동작하도록)
cd "$(dirname "$0")"

VENV_DIR="venv"
PYTHON_SCRIPT="crawl.py"
REQUIREMENTS_FILE="requirements.txt"

# 1) python3 / venv 모듈 확인
if ! command -v python3 &> /dev/null; then
    echo "[오류] python3이 설치되어 있지 않습니다. 먼저 설치해주세요: sudo apt install -y python3 python3-venv python3-pip"
    exit 1
fi

# 2) 가상환경 생성 (없을 때만)
if [ ! -d "$VENV_DIR" ]; then
    echo "[INFO] 가상환경(venv) 생성 중..."
    python3 -m venv "$VENV_DIR"
fi

# 3) 가상환경 활성화
source "$VENV_DIR/bin/activate"

# 4) pip 업그레이드 및 패키지 설치
echo "[INFO] 패키지 설치 중..."
pip install --upgrade pip
pip install -r "$REQUIREMENTS_FILE"

# 5) 크롤링 스크립트 실행
echo "[INFO] $PYTHON_SCRIPT 실행..."
python "$PYTHON_SCRIPT"

echo "[INFO] 완료."
