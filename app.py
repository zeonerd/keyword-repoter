import streamlit as st
import threading
import os
import time
import pandas as pd
import markdown
from datetime import date
from scraper_main import run_scraper

# --- Page Config ---
st.set_page_config(
    page_title="DataLab Scraper Pro",
    page_icon="✨",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# --- Custom CSS (Aesthetics) ---
# We use modern HSL colors, glassmorphism, and Pretendard font
CUSTOM_CSS = """
<style>
    @import url('https://cdn.jsdelivr.net/gh/orioncactus/pretendard/dist/web/static/pretendard.css');

    /* Global Typography & Colors */
    html, body, [class*="css"] {
        font-family: 'Pretendard', -apple-system, BlinkMacSystemFont, system-ui, Roboto, 'Helvetica Neue', 'Segoe UI', 'Apple SD Gothic Neo', 'Noto Sans KR', 'Malgun Gothic', sans-serif !important;
    }
    
    /* Background & Theme */
    .stApp {
        background-color: #0f111a;
        color: #e2e8f0;
    }
    
    /* Hide Default Elements */
    header {visibility: hidden;}
    footer {visibility: hidden;}
    
    /* Dashboard Widget / Card Style */
    .glass-card {
        background: rgba(30, 33, 43, 0.6);
        backdrop-filter: blur(12px);
        -webkit-backdrop-filter: blur(12px);
        border: 1px solid rgba(255, 255, 255, 0.08);
        border-radius: 16px;
        padding: 24px;
        margin-bottom: 24px;
        box-shadow: 0 8px 32px 0 rgba(0, 0, 0, 0.3);
        transition: transform 0.3s ease, box-shadow 0.3s ease;
    }
    .glass-card:hover {
        transform: translateY(-2px);
        box-shadow: 0 12px 40px 0 rgba(0, 0, 0, 0.4);
    }
    
    /* Headings */
    h1, h2, h3 {
        color: #ffffff !important;
        font-weight: 700 !important;
        letter-spacing: -0.5px !important;
    }
    
    .gradient-text {
        background: linear-gradient(135deg, #a8c0ff 0%, #3f2b96 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        display: inline-block;
    }

    /* Buttons */
    .stButton>button {
        background: linear-gradient(135deg, #6366f1 0%, #8b5cf6 100%) !important;
        color: white !important;
        border: none !important;
        padding: 12px 28px !important;
        border-radius: 12px !important;
        font-weight: 600 !important;
        font-size: 16px !important;
        transition: all 0.3s ease !important;
        box-shadow: 0 4px 15px rgba(99, 102, 241, 0.4) !important;
        width: 100% !important;
    }
    .stButton>button:hover {
        transform: translateY(-2px) !important;
        box-shadow: 0 8px 25px rgba(99, 102, 241, 0.6) !important;
        background: linear-gradient(135deg, #4f46e5 0%, #7c3aed 100%) !important;
    }
    .stButton>button:active {
        transform: translateY(1px) !important;
    }

    /* Progress Bar */
    .stProgress > div > div > div > div {
        background-image: linear-gradient(to right, #4facfe 0%, #00f2fe 100%);
        border-radius: 10px;
    }
    
    /* Log Terminal */
    .log-terminal {
        background-color: #0d0d0d;
        color: #00ffcc;
        font-family: 'Courier New', Courier, monospace;
        padding: 16px;
        border-radius: 12px;
        height: 300px;
        overflow-y: auto;
        border: 1px solid #333;
        font-size: 13px;
        line-height: 1.5;
        box-shadow: inset 0 2px 10px rgba(0,0,0,0.5);
    }
    
    /* Badges */
    .badge {
        display: inline-block;
        padding: 4px 12px;
        border-radius: 20px;
        font-size: 12px;
        font-weight: 600;
        background: rgba(99, 102, 241, 0.2);
        color: #a5b4fc;
        border: 1px solid rgba(99, 102, 241, 0.3);
    }
</style>
"""
st.markdown(CUSTOM_CSS, unsafe_allow_html=True)

# --- Session State Initialization ---
if 'is_running' not in st.session_state:
    st.session_state.is_running = False
if 'thread' not in st.session_state:
    st.session_state.thread = None
if 'log_content' not in st.session_state:
    st.session_state.log_content = ""
if 'progress' not in st.session_state:
    st.session_state.progress = 0
if 'status_msg' not in st.session_state:
    st.session_state.status_msg = "대기 중"
if 'needs_report' not in st.session_state:
    st.session_state.needs_report = False

# --- Threading Function ---
def scraper_worker():
    try:
        run_scraper()
    except Exception as e:
        print(f"Scraper Error: {e}")

def start_scraper():
    if not st.session_state.is_running:
        st.session_state.is_running = True
        st.session_state.progress = 0
        st.session_state.status_msg = "초기화 중..."
        thread = threading.Thread(target=scraper_worker)
        
        # Streamlit 스레드 컨텍스트 연결 (missing ScriptRunContext 에러 방지)
        from streamlit.runtime.scriptrunner import add_script_run_ctx
        add_script_run_ctx(thread)
        
        st.session_state.thread = thread
        thread.start()

# --- UI Components ---
st.markdown("<h1 style='text-align: center;'><span class='gradient-text'>DataLab Scraper Pro ✨</span></h1>", unsafe_allow_html=True)
st.markdown("<p style='text-align: center; color: #94a3b8; font-size: 1.1rem; margin-bottom: 2rem;'>네이버 데이터랩 쇼핑인사이트 Top 500 자동화 시스템</p>", unsafe_allow_html=True)

col1, col2 = st.columns([1, 2])

today_str = date.today().strftime('%Y-%m-%d')
log_file_path = os.path.join("logs", f"scraper_{today_str}.log")
results_dir = os.path.join("results", today_str)

# --- 로그 기반 진행률 계산 (컬럼 렌더링 전 수행) ---
_log_text = "로그 대기 중..."
_progress_count = 0
_latest_status = st.session_state.status_msg

if os.path.exists(log_file_path):
    with open(log_file_path, "r", encoding="utf-8") as f:
        _lines = f.readlines()
        if _lines:
            _log_text = "".join(_lines)
            _success_count = sum(1 for line in _lines if "저장 성공" in line or "데이터 없음" in line or "에러 발생" in line)
            _progress_count = min(_success_count, 8)
            for line in reversed(_lines):
                if "수집 시작" in line:
                    _latest_status = line.split("]")[-1].strip()
                    break
                elif "모든 데이터 수집 완료" in line:
                    _latest_status = "수집 완료!"
                    _progress_count = 8
                    break

# --- 수집 완료 감지 ---
if st.session_state.is_running:
    st.session_state.progress = _progress_count
    st.session_state.status_msg = f"{_progress_count} / 8 개 완료 (최근: {_latest_status})"
    if _progress_count >= 8:
        st.session_state.is_running = False
        st.toast("✅ 데이터 수집이 성공적으로 완료되었습니다!", icon="🎉")
    elif st.session_state.thread is not None and not st.session_state.thread.is_alive():
        st.session_state.is_running = False
        st.toast("⚠️ 데이터 수집이 중단되었습니다. 로그를 확인하세요.", icon="⚠️")

with col1:
    st.markdown("""
        <div class="glass-card">
            <h3>⚙️ 스크래핑 설정 요약</h3>
            <hr style="border-color: rgba(255,255,255,0.1); margin: 12px 0;">
            <ul style="list-style: none; padding: 0; margin: 0; color: #cbd5e1; line-height: 1.8;">
                <li>📍 <b>타겟</b> : 식품 하위 4개 카테고리</li>
                <li>📅 <b>기간</b> : 최근 7일 / 미래예측 7일 (총 8회)</li>
                <li>👥 <b>연령</b> : 40대 / 50대 / 60대 이상</li>
                <li>📊 <b>수집량</b> : 카테고리당 최대 500건</li>
            </ul>
        </div>
    """, unsafe_allow_html=True)
    
    
    c1, c2 = st.columns(2)
    with c1:
        if st.button("🕷️ 수집 실행 (TOP500)" if not st.session_state.is_running else "⏳ 진행 중...", disabled=st.session_state.is_running, help="식품 4개 카테고리 TOP 500 데이터 수집"):
            start_scraper()
            st.rerun()
    with c2:
        if st.button("📝 보고서만 재생성", disabled=st.session_state.is_running, help="스크래핑 생략, 기존 데이터 기반"):
            st.session_state.needs_report = True
            st.rerun()

    if st.session_state.is_running:
        st.markdown(f"**진행 상태:** {st.session_state.status_msg}")
        st.progress(st.session_state.progress / 8.0)
        st.markdown("<p style='font-size: 13px; color: #94a3b8; text-align: center;'>UI 스레드는 안전하게 분리되어 있습니다. 창을 닫지 마세요.</p>", unsafe_allow_html=True)
        time.sleep(2) # Auto refresh trigger
        st.rerun()

with col2:
    st.markdown("""
        <div class="glass-card" style="padding: 16px 24px;">
            <h3 style="margin-bottom: 12px;">🖥️ 실시간 로그 뷰어</h3>
        </div>
    """, unsafe_allow_html=True)
    
    # Autoscroll to bottom logic using JS injected with markdown or simple text area
    st.markdown(f"""
        <div class="log-terminal" id="log-container">
            {_log_text.replace(chr(10), '<br>')}
        </div>
        <script>
            var logContainer = document.getElementById("log-container");
            logContainer.scrollTop = logContainer.scrollHeight;
        </script>
    """, unsafe_allow_html=True)

# --- Report Generation Section ---
if st.session_state.get('needs_report', False):
    st.markdown("<br><br>", unsafe_allow_html=True)
    st.markdown("<h3 style='text-align: center; color: #a5b4fc;'>🤖 AI가 데이터를 분석하여 인사이트를 도출하고 있습니다...</h3>", unsafe_allow_html=True)
    
    with st.spinner("보고서를 생성하고 있습니다... 잠시만 기다려주세요."):
        from generate_report import run_report_generation
        today_str = date.today().strftime('%Y-%m-%d')
        run_report_generation(today_str)
        
    st.session_state.needs_report = False
    st.toast("✅ 보고서 생성이 완료되었습니다!", icon="🎉")
    st.rerun()

# --- Results Section ---
st.markdown("<br><br>", unsafe_allow_html=True)
st.markdown("## 📂 분석 결과 및 수집 데이터 확인")

report_dir = "reports"
report_file = os.path.join(report_dir, f"{today_str}_종합분석보고서.md")

has_results = os.path.exists(results_dir)
csv_files = [f for f in os.listdir(results_dir) if f.endswith(".csv")] if has_results else []

tab_names = []
if os.path.exists(report_file):
    tab_names.append("📝 종합 분석 보고서")
tab_names.extend([f.replace(".csv", "") for f in csv_files])

if tab_names:
    tabs = st.tabs(tab_names)
    tab_idx = 0
    
    if os.path.exists(report_file):
        with tabs[tab_idx]:
            with open(report_file, "r", encoding="utf-8") as f:
                report_content = f.read()
            st.markdown(report_content)
            
            html_content = markdown.markdown(report_content, extensions=['tables'])
            styled_html = f"""
            <!DOCTYPE html>
            <html>
            <head>
            <meta charset="utf-8">
            <title>종합 분석 보고서 ({today_str})</title>
            <style>
                body {{ font-family: 'Pretendard', 'Malgun Gothic', 'Apple SD Gothic Neo', sans-serif; line-height: 1.6; padding: 40px; max-width: 900px; margin: 0 auto; color: #333; }}
                h1, h2, h3, h4 {{ color: #2c3e50; margin-top: 1.5em; }}
                h1 {{ border-bottom: 2px solid #2c3e50; padding-bottom: 10px; }}
                table {{ border-collapse: collapse; width: 100%; margin-bottom: 20px; font-size: 14px; }}
                th, td {{ border: 1px solid #ddd; padding: 12px; text-align: left; }}
                th {{ background-color: #f8fafc; font-weight: bold; }}
                tr:nth-child(even) {{ background-color: #fcfcfc; }}
                ul {{ margin-bottom: 20px; }}
                li {{ margin-bottom: 8px; }}
                @media print {{
                    body {{ padding: 0; max-width: none; }}
                }}
            </style>
            </head>
            <body>
            {html_content}
            </body>
            </html>
            """
            
            c1, c2 = st.columns(2)
            with c1:
                st.download_button(
                    label="📥 마크다운 원본 다운로드 (.md)",
                    data=report_content,
                    file_name=f"{today_str}_종합분석보고서.md",
                    mime="text/markdown",
                    key="dl_report_md"
                )
            with c2:
                st.download_button(
                    label="🖨️ 인쇄용 웹 문서 다운로드 (.html)",
                    data=styled_html,
                    file_name=f"{today_str}_종합분석보고서_인쇄용.html",
                    mime="text/html",
                    key="dl_report_html"
                )
        tab_idx += 1
        
    for i, file_name in enumerate(csv_files):
        with tabs[tab_idx]:
            file_path = os.path.join(results_dir, file_name)
            df = pd.read_csv(file_path)
            
            c1, c2 = st.columns([4, 1])
            with c1:
                st.dataframe(df.head(100), use_container_width=True)
            with c2:
                st.markdown(f"**총 데이터:** {len(df)} 건")
                csv_data = df.to_csv(index=False, encoding='utf-8-sig').encode('utf-8')
                st.download_button(
                    label="📥 CSV 다운로드",
                    data=csv_data,
                    file_name=file_name,
                    mime="text/csv",
                    key=f"dl_{i}"
                )
        tab_idx += 1
else:
    st.info("오늘 생성된 결과 파일이나 보고서가 없습니다.")
