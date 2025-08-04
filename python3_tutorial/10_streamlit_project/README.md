# 📊 10. Streamlit 대시보드 - 데이터 시각화 프로젝트

## 🎯 프로젝트 목표
Streamlit을 활용하여 인터랙티브한 데이터 대시보드를 구축하는 프로젝트입니다. 이전 프로젝트들의 기능을 통합하여 실시간 데이터 시각화, 사용자 상호작용, 대시보드 배포까지 전체 데이터 앱 개발 과정을 경험합니다.

## 📚 핵심 학습 주제
- 📊 **Streamlit 프레임워크**: 빠른 데이터 앱 개발
- 📈 **데이터 시각화**: Plotly, matplotlib, seaborn 통합
- 🔄 **인터랙티브 위젯**: 사용자 입력과 실시간 업데이트
- 🎨 **UI/UX 디자인**: 레이아웃과 스타일링
- 💾 **데이터 소스 연동**: CSV, API, 데이터베이스 연결
- ⚡ **성능 최적화**: 캐싱과 세션 상태 관리
- 🚀 **배포**: Streamlit Cloud, Heroku 배포
- 📱 **반응형 디자인**: 모바일 친화적 대시보드

## 프로젝트 구조

```
10_streamlit_project/
├── dashboard/
│   ├── app.py                 # 메인 Streamlit 애플리케이션
│   ├── components/            # UI 컴포넌트
│   │   ├── sidebar.py        # 사이드바 컴포넌트
│   │   ├── header.py         # 헤더 컴포넌트
│   │   ├── charts.py         # 차트 컴포넌트
│   │   └── widgets.py        # 커스텀 위젯
│   ├── services/             # 비즈니스 로직
│   │   ├── data_service.py   # 데이터 처리
│   │   ├── api_service.py    # API 통합
│   │   └── cache_service.py  # 캐싱 서비스
│   ├── utils/                # 유틸리티
│   │   ├── config.py         # 설정 관리
│   │   ├── helpers.py        # 헬퍼 함수
│   │   ├── validators.py     # 입력 검증
│   │   └── auth.py          # 인증 관리
│   ├── assets/               # 정적 파일
│   │   └── style.css        # 커스텀 CSS
│   └── .streamlit/          # Streamlit 설정
│       └── config.toml      # 애플리케이션 설정
├── requirements.txt          # 의존성
├── Dockerfile               # Docker 설정
└── README.md               # 문서
```

## 설치 방법

### 1. 가상환경 설정

```bash
# 가상환경 생성
python -m venv venv

# 활성화 (Windows)
venv\Scripts\activate

# 활성화 (Mac/Linux)
source venv/bin/activate
```

### 2. 의존성 설치

```bash
pip install -r requirements.txt
```

### 3. 환경 설정

```bash
# 설정 파일 복사
cp .env.example .env

# 필요한 API 키 등 설정
```

## 실행 방법

### 로컬 실행

```bash
# 기본 실행
streamlit run dashboard/app.py

# 포트 지정
streamlit run dashboard/app.py --server.port 8501

# 브라우저 자동 열기 비활성화
streamlit run dashboard/app.py --server.headless true
```

### Docker 실행

```bash
# 이미지 빌드
docker build -t streamlit-dashboard .

# 컨테이너 실행
docker run -p 8501:8501 streamlit-dashboard
```

## 주요 기능

### 1. 🏠 메인 대시보드
- 실시간 시스템 모니터링
- 주요 지표 표시
- 활동 피드
- 빠른 액세스 위젯

### 2. 📊 데이터 분석
- 트렌드 분석
- 통계 시각화
- 예측 모델
- 리포트 생성

### 3. 📝 텍스트 도구
- 텍스트 분석
- 워드 클라우드 생성
- 감정 분석
- 텍스트 요약

### 4. 🎓 성적 관리
- 학생 성적 조회
- 성적 통계
- 성적 추이 그래프
- 리포트 다운로드

### 5. 🌤️ 날씨 정보
- 실시간 날씨
- 5일 예보
- 날씨 지도
- 알림 설정

### 6. 📰 블로그 관리
- 포스트 작성/편집
- 댓글 관리
- 통계 분석
- 카테고리 관리

### 7. 📁 파일 처리
- 파일 업로드/다운로드
- 배치 처리
- 형식 변환
- 진행률 표시

### 8. 🕷️ 웹 크롤러
- 크롤링 작업 관리
- 실시간 모니터링
- 스케줄 설정
- 데이터 수집 현황

### 9. ⚙️ 설정
- 사용자 프로필
- 테마 설정
- 알림 관리
- 보안 설정

## 사용 방법

### 로그인
기본 계정:
- **관리자**: username: `admin`, password: `admin`
- **사용자**: username: `user1`, password: `user123`
- **데모**: username: `demo`, password: `demo`

### 네비게이션
1. 좌측 사이드바에서 원하는 메뉴 선택
2. 각 페이지별 기능 사용
3. 상단 검색바로 빠른 검색

### 데이터 시각화
- 대화형 차트 (Plotly)
- 실시간 업데이트
- 다양한 차트 유형 지원

## API 연동

### 날씨 API
```python
# OpenWeatherMap API 사용
weather_data = api_service.get_weather(city="Seoul", api_key="YOUR_KEY")
```

### 뉴스 API
```python
# NewsAPI 사용
news = api_service.get_news(category="technology", api_key="YOUR_KEY")
```

## 성능 최적화

### 캐싱
```python
@st.cache_data(ttl=3600)
def load_data():
    return pd.read_csv("data.csv")
```

### 세션 상태
```python
if 'counter' not in st.session_state:
    st.session_state.counter = 0
```

### 레이지 로딩
```python
with st.spinner("Loading..."):
    data = expensive_computation()
```

## 배포

### Streamlit Cloud
1. GitHub 저장소에 푸시
2. [share.streamlit.io](https://share.streamlit.io) 접속
3. 저장소 연결 및 배포

### Heroku
```bash
# Procfile 생성
echo "web: streamlit run dashboard/app.py --server.port $PORT" > Procfile

# 배포
heroku create your-app-name
git push heroku main
```

### AWS EC2
```bash
# EC2 인스턴스에서
sudo apt update
sudo apt install python3-pip
pip3 install -r requirements.txt
streamlit run dashboard/app.py --server.port 80
```

## 문제 해결

### 포트 충돌
```bash
# 다른 포트 사용
streamlit run dashboard/app.py --server.port 8502
```

### 메모리 부족
```python
# 캐시 정리
st.cache_data.clear()
```

### 세션 타임아웃
```python
# config.toml에서 설정
[server]
maxMessageSize = 200
```

## 학습 포인트

- **Streamlit Framework**: 웹 앱 빠른 개발
- **Data Visualization**: Plotly, Altair 활용
- **Session Management**: 상태 관리
- **Caching**: 성능 최적화
- **Component Design**: 재사용 가능한 컴포넌트
- **API Integration**: 외부 서비스 연동
- **Deployment**: 클라우드 배포

## 라이선스

MIT License

## 문의

질문이나 버그 리포트는 Issues 섹션을 이용해주세요.