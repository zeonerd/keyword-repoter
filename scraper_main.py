import os
import time
import re
import pandas as pd
import logging
import sys
from datetime import date
from playwright.sync_api import sync_playwright
from date_utils import get_recent_7days, get_future_pred_7days

logger = logging.getLogger("scraper")

def set_date_dropdown(page, index, value):
    """
    네이버 데이터랩 기간 설정 드롭다운을 제어합니다.
    index: 0(기준), 1(시작연), 2(시작월), 3(시작일), 4(종료연), 5(종료월), 6(종료일)
    """
    # 특정 컨테이너에 갇히지 않고, 화면에 보이는 전체 드롭다운(div.select)을 추출
    divs = page.locator("div.select").all()
    visible_divs = [d for d in divs if d.is_visible()]
    
    if index >= len(visible_divs):
        raise Exception(f"보이는 드롭다운 요소가 부족합니다. (index: {index})")
        
    div = visible_divs[index]
    
    # 네이버의 JS가 드롭다운 텍스트를 채울 때까지 최대 10초 대기
    for _ in range(20):
        current_val = div.locator("span.select_btn").inner_text().strip()
        if current_val != "":
            break
        time.sleep(0.5)
        
    current_val = div.locator("span.select_btn").inner_text().strip()
    if value in current_val:
        return
        
    try:
        # 강제 클릭(force=True)을 사용하여 요소 겹침이나 애니메이션 방해를 완벽히 무시하고 클릭
        div.locator("span.select_btn").click(force=True)
        time.sleep(0.5)
        
        # 닫혀있는 드롭다운의 옵션 텍스트를 정확히 읽어오기 위해 text_content() 사용
        options = div.locator("a.option").all()
        for opt in options:
            opt_text = opt.text_content() or ""
            if value in opt_text.strip():
                opt.click(force=True)
                break
        time.sleep(0.5)
    except Exception as e:
        logger.error(f"드롭다운 클릭 에러 ({value}): {e}")

def setup_logger(log_file):
    """
    실행할 때마다 핸들러를 새로 연결합니다.
    (logging.basicConfig는 프로세스당 한 번만 적용되어, Streamlit을 켜둔 채 날짜가 바뀌면 이전 날짜 파일에 기록되는 문제 방지)
    """
    logger.setLevel(logging.INFO)
    logger.propagate = False
    for handler in list(logger.handlers):
        logger.removeHandler(handler)
        handler.close()

    formatter = logging.Formatter('%(asctime)s [%(levelname)s] %(message)s')
    for handler in (logging.FileHandler(log_file, encoding='utf-8'), logging.StreamHandler()):
        handler.setFormatter(formatter)
        logger.addHandler(handler)

def run_scraper():
    """
    전체 수집을 실행하고 실패한 수집 대상 목록을 반환합니다.
    브라우저 실행 실패 등 치명적 오류는 로그에 남긴 뒤 다시 발생시킵니다.
    """
    today_str = date.today().strftime('%Y-%m-%d')

    # 로깅 설정
    log_dir = "logs"
    os.makedirs(log_dir, exist_ok=True)
    log_file = os.path.join(log_dir, f"scraper_{today_str}.log")

    setup_logger(log_file)
    logger.info("데이터 수집 스크립트 시작")

    output_dir = os.path.join("results", today_str)
    os.makedirs(output_dir, exist_ok=True)

    failures = []
    try:
        total = _scrape_all(output_dir, failures)
    except Exception:
        logger.exception("치명적 오류로 수집 중단")
        raise

    if failures:
        logger.warning(f"수집 실패 {len(failures)}건: {', '.join(failures)}")
    logger.info(f"모든 데이터 수집 완료 (성공 {total - len(failures)} / {total})")
    return failures

def _scrape_all(output_dir, failures):
    categories = [
        ("축산물", None),
        ("수산물", None),
        ("농산물", "과일"),
        ("농산물", "채소")
    ]
    
    periods = [
        ("최근7일", get_recent_7days()),
        ("미래예측7일", get_future_pred_7days())
    ]
    
    with sync_playwright() as p:
        # GitHub Actions 등 CI 환경에서는 headless=True, 로컬에서는 headless=False 로 동작하게 설정
        is_ci = os.getenv("GITHUB_ACTIONS") == "true"
        browser = p.chromium.launch(headless=is_ci)
        
        for cat2, cat3 in categories:
            for period_name, (start_date, end_date) in periods:
                cat_name_for_file = f"{cat2}_{cat3}" if cat3 else cat2
                output_file = os.path.join(output_dir, f"{cat_name_for_file}_{period_name}.csv")
                
                logger.info(f"[{period_name}] {cat_name_for_file} 수집 시작... (기간: {start_date} ~ {end_date})")
                
                # 매 반복마다 완전 독립된 새 브라우저 컨텍스트(탭/쿠키 초기화) 생성
                context = browser.new_context(viewport={'width': 1280, 'height': 800})
                page = context.new_page()
                
                try:
                    # 페이지 이동 후 네트워크 안정화 대기
                    page.goto("https://datalab.naver.com/shoppingInsight/sCategory.naver", wait_until="networkidle")
                    time.sleep(3)
                    
                    # 1. 기간 설정 (전체 페이지 기준 인덱스 2~8이 실제 일자 세팅 드롭다운임)
                    set_date_dropdown(page, 2, "일간")
                    set_date_dropdown(page, 3, str(start_date.year))
                    set_date_dropdown(page, 4, f"{start_date.month:02d}")
                    set_date_dropdown(page, 5, f"{start_date.day:02d}")
                    set_date_dropdown(page, 6, str(end_date.year))
                    set_date_dropdown(page, 7, f"{end_date.month:02d}")
                    set_date_dropdown(page, 8, f"{end_date.day:02d}")
                    
                    # 2. 카테고리 설정 (숨겨진 모바일 요소 필터링)
                    def select_category(cat_name):
                        # DOM에 해당 카테고리가 렌더링될 때까지 대기 (AJAX)
                        page.wait_for_selector(f"a.option:has-text('{cat_name}')", state="attached", timeout=15000)
                        
                        # 해당 카테고리를 포함하는 모든 드롭다운 컨테이너 찾기
                        divs = page.locator("div.select", has=page.locator(f"a.option:has-text('{cat_name}')")).all()
                        
                        # 모바일용 숨겨진 요소를 제외하고 '화면에 보이는' 컨테이너만 선택
                        target_div = next((d for d in divs if d.is_visible()), None)
                        if not target_div:
                            raise Exception(f"'{cat_name}' 카테고리가 화면에 보이지 않습니다.")
                            
                        target_div.locator("span.select_btn").click(force=True)
                        time.sleep(0.5)
                        target_div.locator("a.option", has_text=re.compile(f"^{cat_name}$")).first.click(force=True)
                        time.sleep(0.5)
                        
                    select_category("식품")
                    select_category(cat2)
                    if cat3:
                        select_category(cat3)
                        
                    # 3. 연령 설정 (40, 50, 60대)
                    page.locator("label", has_text="40").first.click(force=True)
                    page.locator("label", has_text="50").first.click(force=True)
                    page.locator("label", has_text="60").first.click(force=True)
                    
                    # 4. 조회 클릭
                    page.locator("a.btn_submit").first.click(force=True)
                    time.sleep(4)
                    
                    # 5. 데이터 수집
                    all_data = []
                    for p_num in range(1, 26):
                        items = page.locator("ul.rank_top1000_list li").all()
                        for item in items:
                            rank_text = item.locator("span.rank_top1000_num").inner_text().strip()
                            full_text = item.locator("a.link_text").inner_text().strip()
                            
                            if full_text.startswith(rank_text):
                                keyword_text = full_text[len(rank_text):].strip()
                            else:
                                keyword_text = full_text
                                
                            all_data.append({
                                "순위": rank_text,
                                "검색어": keyword_text,
                                "수집기간": f"{start_date.strftime('%Y-%m-%d')}~{end_date.strftime('%Y-%m-%d')}"
                            })
                            
                        if p_num < 25:
                            next_btn = page.locator("a.btn_page_next")
                            if next_btn.is_visible():
                                next_btn.click(force=True)
                                time.sleep(1.5)
                            else:
                                break
                                
                    # 6. 저장
                    if all_data:
                        df = pd.DataFrame(all_data)
                        df.to_csv(output_file, index=False, encoding='utf-8-sig')
                        logger.info(f"저장 성공: {output_file} (총 {len(df)}건)")
                    else:
                        logger.warning(f"데이터 없음: {output_file}")
                        failures.append(f"{cat_name_for_file}_{period_name}")
                        
                except Exception as e:
                    logger.error(f"에러 발생 ({cat_name_for_file} - {period_name}): {e}")
                    failures.append(f"{cat_name_for_file}_{period_name}")
                finally:
                    context.close()
                    
                logger.info("봇 탐지 방지: 3초 대기...")
                time.sleep(3)
                
        browser.close()

    return len(categories) * len(periods)

if __name__ == "__main__":
    # 일부라도 실패하면 종료 코드 1 (GitHub Actions에서 실패로 표시)
    sys.exit(1 if run_scraper() else 0)
