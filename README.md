# Season Scope (네이버 데이터랩 쇼핑인사이트 스크래퍼)

네이버 데이터랩 쇼핑인사이트를 활용하여 최신 데이터 동향 분석을 위한 인기 검색어(TOP 500) 데이터를 자동으로 수집하고 분석하는 프로젝트입니다. 특히 1차 산물(식품) 위주의 시장 트렌드를 파악하는 데 특화되어 있습니다.

## 🎯 주요 기능
- **자동화 데이터 수집**: 식품 카테고리(축산물, 수산물, 농산물>과일, 농산물>채소)의 TOP 500 인기 검색어를 자동 스크래핑합니다.
- **기간별 트렌드 분석**: '최근 7일' 데이터와 '미래 예측 7일(전년도 동기 기준)' 데이터를 함께 수집하여 트렌드를 비교 분석합니다.
- **타겟 연령층 설정**: 구매력이 높은 40대, 50대, 60대 이상의 데이터를 집중적으로 수집합니다.
- **결과물 자동 정리**: 수집된 데이터는 `results/YYYY-MM-DD/` 폴더에 CSV 형태로 자동 분류되어 저장됩니다.
- **보고서 생성**: 수집된 데이터를 바탕으로 마크다운(`.md`) 형태의 종합 분석 보고서를 자동 생성합니다.
- **대시보드 UI**: Streamlit을 활용하여 사용자가 직접 편리하게 실행할 수 있는 웹 UI를 제공합니다.

## 🛠️ 기술 스택
- **Language**: Python 3.x
- **Web Scraping**: Selenium / Playwright
- **Data Processing**: Pandas, dateutil
- **UI**: Streamlit
- **Automation**: GitHub Actions

## 🚀 설치 및 실행 방법

### 1. 패키지 설치
```bash
pip install -r requirements.txt
```

### 2. 대시보드 실행 (UI 모드)
터미널에서 아래 명령어를 실행하여 Streamlit 웹 대시보드를 엽니다.
```bash
streamlit run app.py
```
*(Windows 사용자는 `run_dashboard.bat`, Mac 사용자는 `run_dashboard.command` 파일을 더블클릭하여 실행할 수도 있습니다.)*

### 3. 백그라운드 파이프라인 실행
UI 없이 크롤링부터 보고서 생성까지 전체 프로세스를 백그라운드에서 바로 실행하려면 아래 스크립트를 사용합니다.
```bash
python run_pipeline.py
```

## 📁 프로젝트 구조
- `app.py`: Streamlit 기반 웹 UI 대시보드
- `scraper_main.py`: 네이버 데이터랩 크롤링 메인 로직
- `generate_report.py`: 크롤링된 데이터를 기반으로 분석 보고서 생성
- `run_pipeline.py`: 스크래핑 및 보고서 생성을 순차적으로 실행하는 통합 파이프라인
- `date_utils.py`: 조회 기간 산출 및 윤년 처리 등 날짜 계산 유틸리티
- `results/`: 수집된 CSV 데이터가 실행 일자별로 저장되는 디렉토리
- `reports/`: 생성된 분석 보고서(.md)가 저장되는 디렉토리
- `docs/`: 프로젝트 기획서 및 프롬프트 등 관련 문서 보관

## ⏱️ 자동화 스케줄링
GitHub Actions(`.github/workflows/scraper_schedule.yml`)를 통해 매주 토요일 오전 9시에 정기적으로 자동 수집 파이프라인이 동작하도록 구성되어 있습니다.
