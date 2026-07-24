@echo off
chcp 65001 > nul
echo ==========================================
echo 🚀 Naver Datalab Dashboard 실행을 준비합니다...
echo ==========================================

:: 배치 파일이 위치한 폴더(프로젝트 루트)로 이동
cd /d "%~dp0"

:: 가상환경(.venv)이 존재하지 않으면 생성 및 초기 설정
if not exist ".venv\Scripts\activate.bat" (
    echo [안내] 가상환경이 존재하지 않아 초기 설정을 시작합니다. 시간이 다소 소요될 수 있습니다...
    
    echo 1/3: 가상환경 ^(.venv^) 생성 중...
    python -m venv .venv
    
    echo 2/3: 패키지 설치 중...
    call .venv\Scripts\activate.bat
    pip install -r requirements.txt
    
    echo 3/3: 웹 스크래핑용 브라우저 설치 중...
    playwright install
    
    echo 초기 설정이 완료되었습니다!
) else (
    echo 가상환경 ^(.venv^)을 활성화합니다.
    call .venv\Scripts\activate.bat
)

echo 대시보드를 구동합니다. 브라우저 창이 열릴 때까지 잠시 기다려주세요...
"%~dp0.venv\Scripts\python.exe" -m streamlit run app.py

pause
