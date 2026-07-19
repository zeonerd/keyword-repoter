from datetime import date
from dateutil.relativedelta import relativedelta

def get_recent_7days():
    """
    최근 7일: 오늘 날짜부터 7일 전까지
    반환: (start_date, end_date) datetime.date 객체 튜플
    """
    end_date = date.today()
    start_date = end_date - relativedelta(days=7)
    return start_date, end_date

def get_future_pred_7days():
    """
    미래 예측 7일: 작년의 오늘 날짜부터 7일 후까지
    반환: (start_date, end_date) datetime.date 객체 튜플
    """
    start_date = date.today() - relativedelta(years=1)
    end_date = start_date + relativedelta(days=7)
    return start_date, end_date

if __name__ == "__main__":
    r_s, r_e = get_recent_7days()
    f_s, f_e = get_future_pred_7days()
    print("최근 7일:", r_s.strftime('%Y-%m-%d'), "~", r_e.strftime('%Y-%m-%d'))
    print("미래 예측 7일:", f_s.strftime('%Y-%m-%d'), "~", f_e.strftime('%Y-%m-%d'))
