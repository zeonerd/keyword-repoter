@echo off
chcp 65001 > nul
echo ==========================================
echo 🚀 Naver Datalab Dashboard 실행을 준비합니다...
echo ==========================================

:: 배치 파일이 위치한 폴더(프로젝트 루트)로 이동
cd /d "%~dp0"

set "VENV_PYTHON=%~dp0.venv\Scripts\python.exe"

:: 가상환경(.venv)이 존재하지 않으면 생성
if not exist "%VENV_PYTHON%" (
    echo [안내] 가상환경이 존재하지 않아 새로 생성합니다. 시간이 다소 소요될 수 있습니다...
    python -m venv .venv
    if errorlevel 1 (
        echo [오류] 가상환경 생성 실패. Python 설치 여부를 확인하세요.
        pause
        exit /b 1
    )
)

:: requirements.txt 기준으로 패키지 동기화 (이미 설치된 패키지는 건너뜀)
echo 1/2: 패키지 확인 중...
"%VENV_PYTHON%" -m pip install -q -r requirements.txt
if errorlevel 1 echo [경고] 패키지 설치 중 문제가 발생했습니다. 계속 진행합니다.

:: 웹 스크래핑용 브라우저(Chromium) 확인 (이미 설치되어 있으면 건너뜀)
echo 2/2: 웹 스크래핑용 브라우저 확인 중...
"%VENV_PYTHON%" -m playwright install chromium
if errorlevel 1 echo [경고] 브라우저 설치 중 문제가 발생했습니다. 계속 진행합니다.

:: 반드시 .venv의 python으로 Streamlit 실행
echo 대시보드를 구동합니다. 브라우저 창이 열릴 때까지 잠시 기다려주세요...
"%VENV_PYTHON%" -m streamlit run app.py

pause
