import os
import sys
import datetime
import pandas as pd
import google.generativeai as genai
from dotenv import load_dotenv

load_dotenv()

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

if not GEMINI_API_KEY or GEMINI_API_KEY == "your_gemini_api_key_here":
    print("Error: GEMINI_API_KEY is missing or not set in .env file.")
    sys.exit(1)

genai.configure(api_key=GEMINI_API_KEY)

CATEGORIES = {
    "과일": ("농산물_과일_최근7일.csv", "농산물_과일_미래예측7일.csv"),
    "채소": ("농산물_채소_최근7일.csv", "농산물_채소_미래예측7일.csv"),
    "수산물": ("수산물_최근7일.csv", "수산물_미래예측7일.csv"),
    "축산물": ("축산물_최근7일.csv", "축산물_미래예측7일.csv"),
}

def load_and_merge_data(target_date):
    results_dir = os.path.join("results", target_date)
    if not os.path.exists(results_dir):
        print(f"Error: Directory {results_dir} does not exist.")
        sys.exit(1)

    category_data = {}
    for cat, (recent_file, future_file) in CATEGORIES.items():
        recent_path = os.path.join(results_dir, recent_file)
        future_path = os.path.join(results_dir, future_file)

        if not os.path.exists(recent_path) or not os.path.exists(future_path):
            print(f"Warning: Missing files for {cat}. Skipping.")
            continue

        try:
            df_recent = pd.read_csv(recent_path)
            df_future = pd.read_csv(future_path)

            # Ensure expected columns exist
            if '검색어' not in df_recent.columns or '순위' not in df_recent.columns:
                print(f"Warning: Invalid format in {recent_file}")
                continue

            df_recent = df_recent[['순위', '검색어']].rename(columns={'순위': '최근순위'})
            df_future = df_future[['순위', '검색어']].rename(columns={'순위': '예측순위'})

            # Merge on keyword
            df_merged = pd.merge(df_recent, df_future, on='검색어', how='outer')
            # Fill missing ranks with a high number (e.g., 999) to indicate out of rank
            df_merged['최근순위'] = df_merged['최근순위'].fillna(999).astype(int)
            df_merged['예측순위'] = df_merged['예측순위'].fillna(999).astype(int)
            df_merged['순위변동'] = df_merged['최근순위'] - df_merged['예측순위'] # Positive means rank went UP (e.g., 50 -> 10 = +40)
            
            category_data[cat] = df_merged

        except Exception as e:
            print(f"Error processing {cat}: {e}")

    return category_data

def analyze_keywords(df_merged):
    # 1. 유지/성장형 키워드 (최근순위 <= 30 & 예측순위 <= 30 & 순위변동 >= 0)
    stable_growing = df_merged[
        (df_merged['최근순위'] <= 30) & 
        (df_merged['예측순위'] <= 30) & 
        (df_merged['순위변동'] >= 0)
    ].sort_values(by='예측순위').head(10)

    # 2. 급상승 롱테일 키워드 (예측순위 <= 30 & 최근순위 > 30 또는 순위변동 >= 10)
    rapid_rising = df_merged[
        (df_merged['예측순위'] <= 30) & 
        ((df_merged['최근순위'] > 30) | (df_merged['순위변동'] >= 10))
    ].sort_values(by='순위변동', ascending=False).head(10)

    # 3. 신규 진입 핫 트렌드 (최근순위 <= 100 & 예측순위 == 999)
    new_hot_trend = df_merged[
        (df_merged['최근순위'] <= 100) &
        (df_merged['예측순위'] == 999)
    ].sort_values(by='최근순위').head(10)

    return {
        "stable_growing": stable_growing.to_dict(orient='records'),
        "rapid_rising": rapid_rising.to_dict(orient='records'),
        "new_hot_trend": new_hot_trend.to_dict(orient='records')
    }

def generate_report(target_date, category_data):
    all_keywords_summary = ""
    for cat, df in category_data.items():
        analysis = analyze_keywords(df)
        all_keywords_summary += f"### [{cat} 카테고리]\n"
        all_keywords_summary += "#### [유지·성장형 키워드 (최대 10개)]\n"
        for row in analysis['stable_growing']:
            all_keywords_summary += f"- {row['검색어']} (최근: {row['최근순위']}위 -> 예측: {row['예측순위']}위)\n"
        all_keywords_summary += "#### [급상승 롱테일 키워드 (최대 10개)]\n"
        for row in analysis['rapid_rising']:
            all_keywords_summary += f"- {row['검색어']} (최근: {row['최근순위']}위 -> 예측: {row['예측순위']}위)\n"
        all_keywords_summary += "#### [신규 진입 핫 트렌드 (최대 10개)]\n"
        for row in analysis['new_hot_trend']:
            all_keywords_summary += f"- {row['검색어']} (최근: {row['최근순위']}위 -> 예측 데이터 없음)\n"
        all_keywords_summary += "\n"

    prompt = f"""
당신은 농수산물 위탁판매를 운영하는 1인 기업 사업가를 보좌하는 '수석 데이터 분석가 겸 미래 예측 마케터'입니다.
다음은 {target_date} 기준으로 추출된 카테고리별 핵심 키워드 데이터입니다.

{all_keywords_summary}

이 데이터를 바탕으로 다음 5단계 구조에 맞춘 **심층 분석 보고서**를 마크다운(Markdown) 포맷으로 작성해주세요.

## 1. 데이터 기반 시장 트렌드 총평
- 현재 업로드된 데이터를 관통하는 거시적 시즌 이슈(명절, 휴가철 등) 정의 및 카테고리별 핵심 요약.

## 2. Top 30 심화 황금 키워드 매트릭스
- 위에서 제공된 '유지·성장형 키워드'와 '급상승 롱테일 키워드'를 바탕으로 카테고리별 보기 좋은 표(Table) 형태로 정리.

## 3. 크로스 매칭(Cross-Matching) 상황 인사이트
- 카테고리 간 동시 상승하는 키워드들을 엮어 소비자의 숨은 구매 맥락(예: 삼복 보양식, 야식, 캠핑 등)을 직관적으로 증명하고 설명.

## 4. 신규 진입 핫 트렌드 검토
- 제공된 '신규 진입 핫 트렌드' (최근 7일 데이터에는 등장했으나 과거 동기에는 없던 키워드) 데이터를 바탕으로, 최근 갑자기 등장한 핫한 키워드일 가능성을 검토하고 인사이트 도출.

## 5. 1인 사업가를 위한 실전 마케팅/상품 기획 제안
- 아이디어 A (크로스셀링/기획전 상품 구성)
- 아이디어 B (롱테일 품종 선점/예약 판매)

[Tone & Style Guidelines]
- 데이터 기반 논리적 추론 (Hallucination 배제)
- 든든하고 실행력을 높여주는 비즈니스 파트너 어조
- 볼드체, 구분선, 불릿포인트, 표를 적극 활용하여 스캐너블하게 작성

보고서는 마크다운 양식으로만 반환하세요.
"""
    print("Generating report via Gemini API...")
    
    # Use gemini-1.5-flash or gemini-1.5-pro based on availability
    model = genai.GenerativeModel("gemini-flash-latest")
    response = model.generate_content(prompt)
    
    return response.text

def run_report_generation(target_date=None):
    if target_date is None:
        target_date = datetime.datetime.now().strftime("%Y-%m-%d")

    print(f"Processing data for date: {target_date}")
    category_data = load_and_merge_data(target_date)
    
    if not category_data:
        print("No valid data found.")
        return None

    report_content = generate_report(target_date, category_data)

    reports_dir = "reports"
    os.makedirs(reports_dir, exist_ok=True)
    report_filename = os.path.join(reports_dir, f"{target_date}_종합분석보고서.md")

    with open(report_filename, "w", encoding="utf-8") as f:
        f.write(f"# 시즌 트렌드 종합 분석 보고서 ({target_date})\n\n")
        f.write(report_content)

    print(f"Report successfully saved to {report_filename}")
    return report_filename

def main():
    if len(sys.argv) > 1:
        target_date = sys.argv[1]
    else:
        target_date = None

    result = run_report_generation(target_date)
    if not result:
        sys.exit(1)

if __name__ == "__main__":
    main()
