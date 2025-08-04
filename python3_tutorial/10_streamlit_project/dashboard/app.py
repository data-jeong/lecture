"""
Streamlit Dashboard Application
Main entry point for the comprehensive dashboard
"""

import streamlit as st
from streamlit_option_menu import option_menu
import sys
from pathlib import Path

# Add parent directory to path for imports
sys.path.append(str(Path(__file__).parent.parent))

from components.sidebar import create_sidebar
from components.header import create_header
from services.data_service import DataService
from services.cache_service import CacheService
from utils.config import load_config
from utils.auth import check_authentication


def initialize_session_state():
    """Initialize session state variables"""
    if 'authenticated' not in st.session_state:
        st.session_state.authenticated = False
    if 'user' not in st.session_state:
        st.session_state.user = None
    if 'theme' not in st.session_state:
        st.session_state.theme = 'light'
    if 'notifications' not in st.session_state:
        st.session_state.notifications = []
    if 'cache' not in st.session_state:
        st.session_state.cache = CacheService()
    if 'data_service' not in st.session_state:
        st.session_state.data_service = DataService()


def main():
    # Page configuration
    st.set_page_config(
        page_title="종합 대시보드",
        page_icon="📊",
        layout="wide",
        initial_sidebar_state="expanded",
        menu_items={
            'Get Help': 'https://github.com/yourusername/dashboard',
            'Report a bug': "https://github.com/yourusername/dashboard/issues",
            'About': "# 종합 대시보드 v1.0\n통합 데이터 분석 및 모니터링 플랫폼"
        }
    )
    
    # Initialize session state
    initialize_session_state()
    
    # Load custom CSS
    with open('dashboard/assets/style.css', 'r', encoding='utf-8') as f:
        st.markdown(f'<style>{f.read()}</style>', unsafe_allow_html=True)
    
    # Authentication check
    if not st.session_state.authenticated:
        show_login_page()
        return
    
    # Create header
    create_header()
    
    # Create sidebar with navigation
    with st.sidebar:
        selected = option_menu(
            "메인 메뉴",
            ["🏠 대시보드", "📊 분석", "📝 텍스트 도구", "🎓 성적 관리", 
             "🌤️ 날씨", "📰 블로그", "📁 파일 처리", "🕷️ 크롤러", "⚙️ 설정"],
            icons=['house', 'graph-up', 'file-text', 'mortarboard', 
                   'cloud-sun', 'newspaper', 'folder', 'bug', 'gear'],
            menu_icon="cast",
            default_index=0,
            styles={
                "container": {"padding": "0!important", "background-color": "#fafafa"},
                "icon": {"color": "orange", "font-size": "20px"}, 
                "nav-link": {"font-size": "16px", "text-align": "left", "margin":"0px", "--hover-color": "#eee"},
                "nav-link-selected": {"background-color": "#4CAF50"},
            }
        )
    
    # Display selected page
    if selected == "🏠 대시보드":
        show_main_dashboard()
    elif selected == "📊 분석":
        show_analytics()
    elif selected == "📝 텍스트 도구":
        show_text_tools()
    elif selected == "🎓 성적 관리":
        show_grade_management()
    elif selected == "🌤️ 날씨":
        show_weather()
    elif selected == "📰 블로그":
        show_blog_management()
    elif selected == "📁 파일 처리":
        show_file_processing()
    elif selected == "🕷️ 크롤러":
        show_crawler_monitor()
    elif selected == "⚙️ 설정":
        show_settings()


def show_login_page():
    """Display login page"""
    st.markdown("# 🔐 로그인")
    
    col1, col2, col3 = st.columns([1, 2, 1])
    
    with col2:
        with st.form("login_form"):
            username = st.text_input("사용자명", placeholder="username")
            password = st.text_input("비밀번호", type="password", placeholder="password")
            remember = st.checkbox("로그인 상태 유지")
            
            col_btn1, col_btn2 = st.columns(2)
            with col_btn1:
                login_button = st.form_submit_button("로그인", use_container_width=True, type="primary")
            with col_btn2:
                register_button = st.form_submit_button("회원가입", use_container_width=True)
            
            if login_button:
                if username == "admin" and password == "admin":  # 간단한 예제
                    st.session_state.authenticated = True
                    st.session_state.user = {"username": username, "role": "admin"}
                    st.rerun()
                else:
                    st.error("잘못된 사용자명 또는 비밀번호입니다.")
            
            if register_button:
                st.info("회원가입 기능은 준비 중입니다.")


def show_main_dashboard():
    """Display main dashboard"""
    st.title("📊 종합 대시보드")
    
    # Metrics row
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric(
            label="총 사용자",
            value="1,234",
            delta="12% ↑",
            delta_color="normal"
        )
    
    with col2:
        st.metric(
            label="활성 세션",
            value="89",
            delta="5% ↑",
            delta_color="normal"
        )
    
    with col3:
        st.metric(
            label="API 호출",
            value="45.2K",
            delta="-2% ↓",
            delta_color="inverse"
        )
    
    with col4:
        st.metric(
            label="시스템 상태",
            value="정상",
            delta="99.9%",
            delta_color="normal"
        )
    
    # Charts row
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("📈 실시간 트래픽")
        # Placeholder for real-time chart
        import pandas as pd
        import numpy as np
        import altair as alt
        
        # Generate sample data
        chart_data = pd.DataFrame(
            np.random.randn(20, 3),
            columns=['서버1', '서버2', '서버3']
        )
        
        chart = alt.Chart(chart_data.reset_index()).transform_fold(
            ['서버1', '서버2', '서버3'],
            as_=['서버', '값']
        ).mark_line().encode(
            x='index:Q',
            y='값:Q',
            color='서버:N'
        ).properties(height=300)
        
        st.altair_chart(chart, use_container_width=True)
    
    with col2:
        st.subheader("🥧 리소스 사용률")
        import plotly.express as px
        
        # Sample data for pie chart
        fig = px.pie(
            values=[30, 25, 20, 15, 10],
            names=['CPU', 'Memory', 'Disk', 'Network', 'Other'],
            title="시스템 리소스 분포"
        )
        st.plotly_chart(fig, use_container_width=True)
    
    # Activity feed
    st.subheader("📋 최근 활동")
    
    activities = [
        {"time": "2분 전", "user": "user1", "action": "파일 업로드", "status": "✅"},
        {"time": "5분 전", "user": "admin", "action": "시스템 백업", "status": "✅"},
        {"time": "10분 전", "user": "user2", "action": "데이터 분석", "status": "⏳"},
        {"time": "15분 전", "user": "user3", "action": "리포트 생성", "status": "✅"},
        {"time": "20분 전", "user": "user1", "action": "API 호출", "status": "❌"},
    ]
    
    activity_df = pd.DataFrame(activities)
    st.dataframe(activity_df, use_container_width=True, hide_index=True)


def show_analytics():
    """Display analytics page"""
    st.title("📊 데이터 분석")
    
    tabs = st.tabs(["📈 트렌드 분석", "📊 통계", "🎯 예측", "📑 리포트"])
    
    with tabs[0]:
        st.subheader("트렌드 분석")
        
        # Date range selector
        col1, col2 = st.columns(2)
        with col1:
            start_date = st.date_input("시작 날짜")
        with col2:
            end_date = st.date_input("종료 날짜")
        
        # Trend chart placeholder
        st.info("선택한 기간의 트렌드 차트가 여기에 표시됩니다.")
    
    with tabs[1]:
        st.subheader("통계 분석")
        
        # Statistical metrics
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("평균", "75.3")
        with col2:
            st.metric("중앙값", "72.5")
        with col3:
            st.metric("표준편차", "12.4")
    
    with tabs[2]:
        st.subheader("예측 모델")
        st.info("머신러닝 기반 예측 모델이 여기에 표시됩니다.")
    
    with tabs[3]:
        st.subheader("리포트 생성")
        
        report_type = st.selectbox("리포트 유형", ["일간", "주간", "월간", "분기", "연간"])
        
        if st.button("리포트 생성", type="primary"):
            st.success(f"{report_type} 리포트가 생성되었습니다!")
            st.download_button(
                label="리포트 다운로드",
                data="Sample report content",
                file_name=f"report_{report_type}.pdf",
                mime="application/pdf"
            )


def show_text_tools():
    """Display text analysis tools"""
    st.title("📝 텍스트 분석 도구")
    
    # Text input
    text_input = st.text_area("분석할 텍스트를 입력하세요", height=200)
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        if st.button("워드 클라우드", use_container_width=True):
            if text_input:
                st.info("워드 클라우드 생성 중...")
                # Placeholder for wordcloud
    
    with col2:
        if st.button("감정 분석", use_container_width=True):
            if text_input:
                st.success("긍정적: 75%, 부정적: 25%")
    
    with col3:
        if st.button("요약", use_container_width=True):
            if text_input:
                st.info("텍스트 요약 생성 중...")
    
    # File upload
    st.divider()
    uploaded_file = st.file_uploader("또는 텍스트 파일을 업로드하세요", type=['txt', 'csv', 'pdf'])
    
    if uploaded_file:
        st.success(f"파일 '{uploaded_file.name}' 업로드 완료!")


def show_grade_management():
    """Display grade management system"""
    st.title("🎓 성적 관리 시스템")
    
    # Student selector
    student = st.selectbox("학생 선택", ["전체", "김철수", "이영희", "박민수"])
    
    # Grade table
    import pandas as pd
    
    grades_data = {
        "과목": ["수학", "영어", "과학", "국어", "역사"],
        "중간고사": [85, 92, 78, 88, 91],
        "기말고사": [88, 90, 82, 85, 93],
        "과제": [95, 88, 90, 92, 87],
        "최종 성적": [89, 90, 83, 88, 90]
    }
    
    df = pd.DataFrame(grades_data)
    st.dataframe(df, use_container_width=True, hide_index=True)
    
    # Statistics
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("평균 성적", "88.0", "2.5 ↑")
    with col2:
        st.metric("최고 성적", "90.0")
    with col3:
        st.metric("최저 성적", "83.0")
    with col4:
        st.metric("학점", "A-")
    
    # Grade chart
    st.subheader("성적 추이")
    import plotly.graph_objects as go
    
    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=["중간고사", "기말고사", "최종"],
        y=[86, 87, 88],
        mode='lines+markers',
        name='평균 성적'
    ))
    
    st.plotly_chart(fig, use_container_width=True)


def show_weather():
    """Display weather information"""
    st.title("🌤️ 날씨 정보")
    
    # Location selector
    location = st.selectbox("지역 선택", ["서울", "부산", "대구", "인천", "광주"])
    
    # Current weather
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("현재 온도", "22°C", "2°C ↑")
    with col2:
        st.metric("체감 온도", "20°C")
    with col3:
        st.metric("습도", "65%")
    with col4:
        st.metric("풍속", "3.5 m/s")
    
    # Weather forecast
    st.subheader("5일 예보")
    
    forecast_data = {
        "날짜": ["월", "화", "수", "목", "금"],
        "최고": [24, 25, 23, 22, 26],
        "최저": [18, 19, 17, 16, 20],
        "날씨": ["☀️", "⛅", "☁️", "🌧️", "☀️"]
    }
    
    forecast_df = pd.DataFrame(forecast_data)
    st.dataframe(forecast_df, use_container_width=True, hide_index=True)
    
    # Weather map
    st.subheader("날씨 지도")
    st.info("날씨 지도가 여기에 표시됩니다.")


def show_blog_management():
    """Display blog management"""
    st.title("📰 블로그 관리")
    
    tabs = st.tabs(["📝 포스트", "💬 댓글", "📊 통계", "✍️ 새 글 작성"])
    
    with tabs[0]:
        st.subheader("최근 포스트")
        
        posts = [
            {"제목": "Python 최적화 팁", "작성자": "admin", "조회수": 234, "댓글": 12},
            {"제목": "Streamlit 활용법", "작성자": "user1", "조회수": 156, "댓글": 8},
            {"제목": "데이터 분석 기초", "작성자": "admin", "조회수": 189, "댓글": 15},
        ]
        
        posts_df = pd.DataFrame(posts)
        st.dataframe(posts_df, use_container_width=True, hide_index=True)
    
    with tabs[1]:
        st.subheader("최근 댓글")
        st.info("최근 댓글 목록이 여기에 표시됩니다.")
    
    with tabs[2]:
        st.subheader("블로그 통계")
        
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("총 포스트", "156")
        with col2:
            st.metric("총 조회수", "12.3K")
        with col3:
            st.metric("총 댓글", "892")
    
    with tabs[3]:
        st.subheader("새 글 작성")
        
        title = st.text_input("제목")
        category = st.selectbox("카테고리", ["기술", "일상", "리뷰", "튜토리얼"])
        content = st.text_area("내용", height=300)
        
        if st.button("게시", type="primary"):
            if title and content:
                st.success("포스트가 성공적으로 게시되었습니다!")


def show_file_processing():
    """Display file processing"""
    st.title("📁 파일 처리")
    
    # File uploader
    uploaded_files = st.file_uploader(
        "파일을 선택하세요",
        accept_multiple_files=True,
        type=['txt', 'csv', 'json', 'pdf', 'xlsx']
    )
    
    if uploaded_files:
        st.subheader("업로드된 파일")
        
        for file in uploaded_files:
            col1, col2, col3 = st.columns([3, 1, 1])
            
            with col1:
                st.text(f"📄 {file.name}")
            with col2:
                st.text(f"{file.size / 1024:.1f} KB")
            with col3:
                if st.button("처리", key=f"process_{file.name}"):
                    with st.spinner("처리 중..."):
                        # Process file
                        st.success(f"{file.name} 처리 완료!")
    
    # Processing options
    st.subheader("처리 옵션")
    
    col1, col2 = st.columns(2)
    
    with col1:
        processing_type = st.selectbox("처리 유형", ["압축", "변환", "분석", "병합"])
    
    with col2:
        output_format = st.selectbox("출력 형식", ["CSV", "JSON", "XLSX", "PDF"])
    
    if st.button("일괄 처리 시작", type="primary", use_container_width=True):
        progress_bar = st.progress(0)
        for i in range(100):
            progress_bar.progress(i + 1)
        st.success("모든 파일 처리 완료!")


def show_crawler_monitor():
    """Display web crawler monitor"""
    st.title("🕷️ 웹 크롤러 모니터")
    
    # Crawler status
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("활성 크롤러", "3", "1 ↑")
    with col2:
        st.metric("수집된 페이지", "1,234")
    with col3:
        st.metric("대기 중", "45")
    with col4:
        st.metric("오류", "2", "-1 ↓")
    
    # Crawler tasks
    st.subheader("크롤링 작업")
    
    tasks = [
        {"사이트": "example.com", "상태": "🟢 실행 중", "진행률": 75, "수집": 234},
        {"사이트": "news.com", "상태": "🟡 대기 중", "진행률": 0, "수집": 0},
        {"사이트": "blog.com", "상태": "🔴 중지됨", "진행률": 45, "수집": 123},
    ]
    
    for task in tasks:
        col1, col2, col3, col4 = st.columns([2, 1, 2, 1])
        
        with col1:
            st.text(task["사이트"])
        with col2:
            st.text(task["상태"])
        with col3:
            st.progress(task["진행률"] / 100)
        with col4:
            st.text(f"{task['수집']} 페이지")
    
    # Add new crawler
    st.divider()
    st.subheader("새 크롤러 추가")
    
    col1, col2 = st.columns(2)
    
    with col1:
        url = st.text_input("URL")
        depth = st.number_input("크롤링 깊이", min_value=1, max_value=10, value=3)
    
    with col2:
        interval = st.selectbox("실행 주기", ["1시간", "6시간", "12시간", "24시간"])
        if st.button("크롤러 시작", type="primary", use_container_width=True):
            st.success("크롤러가 시작되었습니다!")


def show_settings():
    """Display settings page"""
    st.title("⚙️ 설정")
    
    tabs = st.tabs(["👤 프로필", "🎨 테마", "🔔 알림", "🔐 보안", "💾 백업"])
    
    with tabs[0]:
        st.subheader("사용자 프로필")
        
        col1, col2 = st.columns([1, 2])
        
        with col1:
            st.image("https://via.placeholder.com/150", caption="프로필 사진")
            st.button("사진 변경", use_container_width=True)
        
        with col2:
            username = st.text_input("사용자명", value="admin")
            email = st.text_input("이메일", value="admin@example.com")
            bio = st.text_area("소개", value="시스템 관리자")
            
            if st.button("프로필 저장", type="primary"):
                st.success("프로필이 저장되었습니다!")
    
    with tabs[1]:
        st.subheader("테마 설정")
        
        theme = st.selectbox("테마 선택", ["라이트", "다크", "자동"])
        primary_color = st.color_picker("주 색상", "#4CAF50")
        
        st.info(f"선택한 테마: {theme}, 주 색상: {primary_color}")
    
    with tabs[2]:
        st.subheader("알림 설정")
        
        st.checkbox("이메일 알림", value=True)
        st.checkbox("푸시 알림", value=True)
        st.checkbox("SMS 알림", value=False)
        
        st.multiselect(
            "알림 받을 이벤트",
            ["새 사용자", "시스템 오류", "백업 완료", "리포트 생성"],
            default=["시스템 오류", "백업 완료"]
        )
    
    with tabs[3]:
        st.subheader("보안 설정")
        
        st.checkbox("2단계 인증", value=False)
        st.number_input("세션 타임아웃 (분)", min_value=5, max_value=120, value=30)
        
        if st.button("비밀번호 변경"):
            st.info("비밀번호 변경 페이지로 이동합니다.")
    
    with tabs[4]:
        st.subheader("백업 설정")
        
        backup_freq = st.selectbox("백업 주기", ["매일", "매주", "매월"])
        st.checkbox("자동 백업", value=True)
        
        if st.button("지금 백업", type="primary"):
            with st.spinner("백업 중..."):
                st.success("백업이 완료되었습니다!")


if __name__ == "__main__":
    main()