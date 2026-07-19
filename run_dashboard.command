#!/bin/bash

# 사용자 친화적인 메시지 출력
echo "=========================================="
echo "🚀 Naver Datalab Dashboard 실행을 준비합니다..."
echo "=========================================="

# 프로젝트 폴더로 이동 (이 파일이 어디에 있든 고정된 경로로 이동)
cd "/Users/jeonsubeen/develop/season-scope" || exit

# 가상환경(.venv)이 존재하면 활성화
if [ -d ".venv" ]; then
    echo "가상환경(.venv)을 활성화합니다."
    source .venv/bin/activate
fi

# Streamlit 앱 실행
echo "대시보드를 구동합니다. 브라우저 창이 열릴 때까지 잠시 기다려주세요..."
streamlit run app.py
