# GitHub Actions 자동화 구축 및 운영 가이드

본 문서는 네이버 데이터랩 크롤링 스크립트(`scraper_main.py`)를 GitHub Actions를 통해 매주 토요일 새벽 4시에 자동 실행되도록 구축하고 운영하는 단계별 안내서입니다.

## 1. 개요 및 사전 준비

이번 자동화 작업을 위해 프로젝트에 다음 세 가지 주요 변경사항이 적용되었습니다:
1. **`.github/workflows/scraper_schedule.yml`**: 스케줄링 및 봇 실행 환경(Ubuntu, Python, Playwright)을 정의한 GitHub Actions 설정 파일입니다.
2. **`requirements.txt`**: CI 서버에서 설치해야 할 필수 라이브러리(`pandas`, `playwright`) 목록입니다.
3. **`scraper_main.py` 수정**: 로컬 실행 시에는 기존처럼 화면이 보이도록(`headless=False`), GitHub 서버 환경에서는 화면 없이 백그라운드 구동되도록(`headless=True`) 자동 분기 처리했습니다.

## 2. GitHub에 적용하기 (배포 단계)

로컬에 추가/변경된 파일들을 원격 GitHub 저장소로 올려야만 스케줄러가 활성화됩니다.
터미널을 열고 다음 Git 명령어들을 순서대로 실행하세요.

```bash
# 1. 추가 및 변경된 모든 파일을 스테이징합니다.
git add .github/workflows/scraper_schedule.yml requirements.txt scraper_main.py

# 2. 커밋 메시지와 함께 변경사항을 저장합니다.
git commit -m "feat: Playwright 크롤러 GitHub Actions 스케줄링 구축"

# 3. 원격 저장소(GitHub)에 푸시합니다.
git push origin main
```
> **참고**: 현재 사용 중인 브랜치가 `main`이 아닐 경우, 알맞은 브랜치명으로 푸시하시기 바랍니다.

## 3. 구축 확인 및 수동 실행 방법

코드가 GitHub에 성공적으로 푸시되면, 스케줄링 시스템이 즉시 활성화됩니다. 

1. **Actions 탭 확인**: 
   - GitHub 레포지토리 웹페이지 상단의 **[Actions]** 탭에 들어갑니다.
   - 왼쪽 사이드바에 `Naver Datalab Scraper`라는 워크플로우가 보인다면 정상적으로 등록된 것입니다.
2. **수동 테스트 (강제 실행)**:
   - 토요일 새벽까지 기다리지 않고 즉시 테스트해 볼 수 있습니다.
   - `Naver Datalab Scraper`를 클릭한 후, 우측의 **[Run workflow]** 버튼을 눌러 스크래퍼를 강제 실행합니다.
3. **로그 모니터링**:
   - 실행 중인 워크플로우를 클릭하면 실시간으로 패키지를 설치하고 데이터를 크롤링하는 로그 화면을 확인할 수 있습니다.

## 4. 수집된 결과물(CSV) 다운로드

GitHub Actions가 스크래퍼 실행을 완료하면, 수집된 데이터를 압축 파일(Artifacts) 형태로 제공합니다.

1. **[Actions]** 탭에서 실행이 완료된 워크플로우(초록색 체크 표시)를 클릭합니다.
2. 하단의 **Artifacts** 섹션을 확인합니다.
3. `datalab-scraping-results`라는 이름의 링크를 클릭하면 `results/` 폴더 내의 CSV 파일들과 `logs/` 폴더 내의 실행 로그가 포함된 `.zip` 파일이 다운로드됩니다.

## 5. (차후) Slack 알림 연동 방법

현재는 알림 없이 저장소에 파일만 저장되지만, 추후 에러 발생 또는 작업 완료 시 Slack 메신저로 실시간 알림을 받고 싶으시다면 다음 절차를 따릅니다.

1. Slack 워크스페이스에서 **Incoming Webhook URL**을 발급받습니다.
2. GitHub 저장소의 `Settings` > `Secrets and variables` > `Actions` 메뉴로 이동합니다.
3. `New repository secret`을 클릭하고 이름은 `SLACK_WEBHOOK_URL`, 값은 발급받은 URL을 입력합니다.
4. `scraper_main.py` 내의 `try-except` 구문에 `requests` 모듈을 이용해 해당 URL로 에러/성공 메시지 JSON을 POST 요청하는 코드를 두세 줄 추가합니다.

이후부터는 스크래퍼 구동에 문제가 생기거나 완료될 때마다 폰/PC로 즉시 알림을 받을 수 있게 됩니다.
