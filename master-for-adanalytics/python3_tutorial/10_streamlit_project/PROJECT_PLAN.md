# 10. Streamlit 프로젝트 - 종합 대시보드 앱

## 프로젝트 개요
이전 프로젝트들의 기능을 통합하여 인터랙티브한 종합 대시보드를 Streamlit으로 구축합니다.

## 학습 목표
- Streamlit 프레임워크 활용
- 데이터 시각화 마스터
- 실시간 데이터 업데이트
- 세션 상태 관리
- 배포 및 공유

## 프로젝트 기능

### 1. 메인 대시보드
- 전체 시스템 상태 모니터링
- 실시간 데이터 업데이트
- 사용자 맞춤 위젯
- 다크/라이트 테마

### 2. 통합 기능
1. **텍스트 분석 도구** (프로젝트 02)
   - 텍스트 업로드 및 분석
   - 워드 클라우드 생성
   - 감정 분석

2. **성적 관리 시스템** (프로젝트 08)
   - 학생 성적 조회
   - 통계 차트
   - PDF 리포트 다운로드

3. **날씨 정보** (프로젝트 07)
   - 실시간 날씨 위젯
   - 날씨 예보 차트
   - 지도 시각화

4. **블로그 관리** (프로젝트 09)
   - 포스트 작성/편집
   - 댓글 모니터링
   - 통계 분석

5. **파일 처리** (프로젝트 05)
   - 파일 업로드/다운로드
   - 처리 진행률 표시
   - 배치 처리

6. **웹 크롤링 모니터** (프로젝트 06)
   - 크롤링 작업 관리
   - 수집 데이터 표시
   - 스케줄 설정

### 3. 고급 기능
- 사용자 인증 시스템
- 실시간 알림
- 데이터 내보내기
- 차트 커스터마이징
- 캐싱 최적화

## 주요 학습 포인트
```python
import streamlit as st
import pandas as pd
import plotly.express as px
import altair as alt
from streamlit_option_menu import option_menu
import asyncio
```

## 코드 구조
```
dashboard/
    app.py                  # 메인 Streamlit 앱
    
    pages/
        __init__.py
        1_📊_Analytics.py    # 분석 대시보드
        2_📝_Text_Tools.py   # 텍스트 도구
        3_🎓_Grades.py       # 성적 관리
        4_🌤️_Weather.py      # 날씨 정보
        5_📰_Blog.py         # 블로그 관리
        6_📁_Files.py        # 파일 처리
        7_🕷️_Crawler.py      # 크롤러 모니터
        8_⚙️_Settings.py      # 설정
        
    components/
        __init__.py
        sidebar.py          # 사이드바 컴포넌트
        header.py           # 헤더 컴포넌트
        charts.py           # 차트 컴포넌트
        widgets.py          # 커스텀 위젯
        auth.py             # 인증 컴포넌트
        
    services/
        __init__.py
        data_service.py     # 데이터 처리
        api_service.py      # API 연동
        cache_service.py    # 캐싱
        
    utils/
        __init__.py
        config.py           # 설정 관리
        helpers.py          # 유틸리티 함수
        validators.py       # 입력 검증
        
    assets/
        style.css           # 커스텀 CSS
        logo.png            # 로고 이미지
        
    data/
        sample_data.csv     # 샘플 데이터
        
requirements.txt            # 의존성
config.toml                # Streamlit 설정
Dockerfile                 # Docker 설정
.streamlit/
    config.toml            # Streamlit 설정
    secrets.toml           # 시크릿 관리
```

## 주요 컴포넌트 예제

### 1. 메인 대시보드
```python
def main():
    st.set_page_config(
        page_title="종합 대시보드",
        page_icon="📊",
        layout="wide",
        initial_sidebar_state="expanded"
    )
    
    # 사이드바 메뉴
    with st.sidebar:
        selected = option_menu(
            "메인 메뉴",
            ["대시보드", "텍스트 분석", "성적 관리", "날씨", "블로그"],
            icons=['house', 'file-text', 'mortarboard', 'cloud-sun', 'newspaper'],
            menu_icon="cast",
            default_index=0
        )
    
    # 메인 컨텐츠
    if selected == "대시보드":
        show_dashboard()
    elif selected == "텍스트 분석":
        show_text_analysis()
    # ...
```

### 2. 실시간 차트
```python
@st.cache_data
def load_data():
    return pd.read_csv('data.csv')

def show_realtime_chart():
    placeholder = st.empty()
    
    while True:
        df = load_data()
        
        with placeholder.container():
            col1, col2, col3 = st.columns(3)
            
            with col1:
                st.metric("총 사용자", df['users'].sum(), "↑ 12%")
            
            with col2:
                fig = px.line(df, x='date', y='value')
                st.plotly_chart(fig, use_container_width=True)
            
            with col3:
                st.altair_chart(create_chart(df))
        
        time.sleep(5)  # 5초마다 업데이트
```

### 3. 파일 업로드
```python
def file_upload_component():
    uploaded_file = st.file_uploader(
        "파일을 선택하세요",
        type=['csv', 'txt', 'json'],
        accept_multiple_files=True
    )
    
    if uploaded_file:
        df = pd.read_csv(uploaded_file)
        
        # 데이터 미리보기
        st.dataframe(df.head())
        
        # 다운로드 버튼
        csv = df.to_csv(index=False)
        st.download_button(
            label="처리된 데이터 다운로드",
            data=csv,
            file_name='processed_data.csv',
            mime='text/csv'
        )
```

## 실행 방법
```bash
# 로컬 실행
streamlit run app.py

# 특정 포트로 실행
streamlit run app.py --server.port 8501

# Docker로 실행
docker build -t streamlit-dashboard .
docker run -p 8501:8501 streamlit-dashboard

# Streamlit Cloud 배포
# 1. GitHub에 푸시
# 2. share.streamlit.io에서 배포
```

## 배포 옵션
1. **Streamlit Cloud** (무료)
2. **Heroku**
3. **AWS EC2**
4. **Google Cloud Run**
5. **Azure App Service**

## 성능 최적화
- `@st.cache_data` 데코레이터 활용
- 세션 상태로 데이터 저장
- 비동기 데이터 로딩
- 레이지 로딩
- 컴포넌트 재사용