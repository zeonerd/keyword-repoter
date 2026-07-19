@echo off
chcp 65001 > nul
echo ==========================================
echo 🚀 Naver Datalab Dashboard 실행을 준비합니다...
echo ==========================================

:: 배치 파일이 위치한 폴더(프로젝트 루트)로 이동
cd /d "%~dp0"

:: 가상환경(.venv)이 존재하면 활성화
if exist ".venv\Scripts\activate.bat" (
    echo 가상환경(.venv)을 활성화합니다.
    call .venv\Scripts\activate.bat
) else (
    echo [주의] 가상환경(.venv) 스크립트를 찾을 수 없습니다. 전역 환경을 사용합니다.
)

echo 대시보드를 구동합니다. 브라우저 창이 열릴 때까지 잠시 기다려주세요...
streamlit run app.py

pause
