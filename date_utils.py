from datetime import date, timedelta

def get_weekly_periods(today=None):
    """
    수집 기간 7개를 (용도, 시작일, 종료일) 리스트로 반환합니다. 모든 기간은 월~일 한 주 단위입니다.
    - 기준 주: 가장 최근에 끝난 주 (네이버 데이터랩은 어제까지만 조회 가능하므로 진행 중인 주는 제외)
    - 작년 같은 주: 기준 주의 52주(364일) 전 (요일이 맞고 윤년 영향 없음)
    """
    today = today or date.today()
    yesterday = today - timedelta(days=1)
    base_end = yesterday - timedelta(days=(yesterday.weekday() - 6) % 7)  # 어제 이전의 가장 가까운 일요일
    base_start = base_end - timedelta(days=6)
    last_year_start = base_start - timedelta(weeks=52)

    starts = [
        ("올해 이번 주", base_start),
        ("올해 지난주", base_start - timedelta(weeks=1)),
        ("작년 같은 주", last_year_start),
    ]
    starts += [(f"작년 +{n}주", last_year_start + timedelta(weeks=n)) for n in range(1, 5)]
    return [(label, start, start + timedelta(days=6)) for label, start in starts]

if __name__ == "__main__":
    for label, start, end in get_weekly_periods():
        print(f"{label}: {start:%Y-%m-%d} ~ {end:%Y-%m-%d}")
