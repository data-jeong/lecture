# 🐍 Python3 마스터 클래스 - 실전 프로젝트 모음

파이썬 초급부터 고급까지 단계별 학습을 위한 10개의 실전 프로젝트

## 📚 프로젝트 목록

### 🎯 기초 레벨 (Beginner)

#### [01. Python Basics - 계산기](./01_python_basics)
- **학습 목표**: Python 기본 문법, 함수, 모듈
- **주요 기능**: 사칙연산, 공학용 계산, 단위 변환
- **핵심 개념**: 함수, 조건문, 반복문, 모듈화

#### [02. Functions & Modules - 텍스트 처리 유틸리티](./02_functions_modules)
- **학습 목표**: 모듈 설계, 패키지 구조, 함수형 프로그래밍
- **주요 기능**: 텍스트 분석, 변환, 패턴 검색, 인코딩
- **핵심 개념**: 모듈, 패키지, 정규표현식, 파일 I/O

#### [03. OOP Design - 도서관 관리 시스템](./03_oop_design)
- **학습 목표**: 객체지향 프로그래밍, 클래스 설계
- **주요 기능**: 도서 대출/반납, 회원 관리, 연체료 계산
- **핵심 개념**: 클래스, 상속, 다형성, 캡슐화

### 🚀 중급 레벨 (Intermediate)

#### [04. Type Hints & Modern Python - Type-Safe ToDo App](./04_type_hints_modern)
- **학습 목표**: Type Hints, Generic, Protocol, 현대적 Python
- **주요 기능**: 타입 안전 ToDo 관리, 제네릭 Repository 패턴
- **핵심 개념**: typing, Generic, Protocol, mypy

#### [05. GIL & Async - 비동기 파일 처리기](./05_gil_async)
- **학습 목표**: GIL 이해, 비동기 프로그래밍, 동시성
- **주요 기능**: 비동기 파일 처리, 성능 벤치마크, 모니터링
- **핵심 개념**: asyncio, threading, multiprocessing, GIL

#### [06. Web Scraping - 뉴스 크롤러](./06_web_scraping)
- **학습 목표**: 웹 크롤링, 데이터 수집, 반크롤링 대응
- **주요 기능**: 뉴스 수집, 키워드 분석, 트렌드 분석
- **핵심 개념**: BeautifulSoup, Scrapy, Selenium, 프록시

### 🎓 고급 레벨 (Advanced)

#### [07. API Basics - 날씨 API 클라이언트](./07_api_basics)
- **학습 목표**: RESTful API, HTTP 클라이언트, 데이터 시각화
- **주요 기능**: 날씨 정보 조회, 예보, 지도 시각화
- **핵심 개념**: requests, API 인증, 캐싱, 시각화

#### [08. Database - 성적 관리 시스템](./08_database)
- **학습 목표**: 데이터베이스 설계, ORM, 트랜잭션
- **주요 기능**: 학생/과목 관리, 성적 처리, 리포트 생성
- **핵심 개념**: SQLAlchemy, 관계형 DB, 마이그레이션

#### [09. FastAPI Backend - 블로그 API](./09_fastapi_backend)
- **학습 목표**: RESTful API 설계, 인증, 비동기 웹 개발
- **주요 기능**: 포스트 CRUD, JWT 인증, 댓글, WebSocket
- **핵심 개념**: FastAPI, Pydantic, JWT, async/await

#### [10. Streamlit - 종합 대시보드](./10_streamlit_project)
- **학습 목표**: 데이터 시각화, 인터랙티브 웹 앱
- **주요 기능**: 실시간 모니터링, 데이터 분석, 통합 대시보드
- **핵심 개념**: Streamlit, Plotly, 캐싱, 세션 관리

## 🛠️ 기술 스택

### 언어 & 프레임워크
- **Python 3.11+**
- **FastAPI** - 고성능 웹 API
- **Streamlit** - 데이터 앱
- **SQLAlchemy** - ORM
- **Scrapy** - 웹 크롤링

### 데이터베이스
- **PostgreSQL** - 관계형 DB
- **Redis** - 캐싱
- **SQLite** - 경량 DB

### 도구 & 라이브러리
- **Docker** - 컨테이너화
- **pytest** - 테스팅
- **mypy** - 타입 체킹
- **black** - 코드 포맷팅

## 🚀 시작하기

### 전체 프로젝트 설치

```bash
# 저장소 클론
git clone https://github.com/yourusername/python3_tutorial.git
cd python3_tutorial

# 가상환경 생성
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# 각 프로젝트로 이동하여 실행
cd 01_python_basics
pip install -r requirements.txt
python calculator.py
```

### Docker로 실행

```bash
# 각 프로젝트 디렉토리에서
docker-compose up -d
```

## 📖 학습 가이드

### 추천 학습 순서

1. **기초 다지기** (1-3주)
   - Project 01-03 순차 학습
   - 각 프로젝트 예제 코드 실행 및 수정

2. **중급 스킬** (3-4주)
   - Project 04-06 심화 학습
   - 타입 힌트와 비동기 프로그래밍 집중

3. **실전 응용** (4-6주)
   - Project 07-10 프로젝트 구현
   - 자신만의 기능 추가 및 확장

### 학습 팁

- 📝 각 프로젝트의 README를 먼저 읽기
- 🧪 테스트 코드 실행하여 동작 확인
- 🔧 코드를 직접 수정하며 실험
- 📚 관련 문서와 레퍼런스 참고

## 🤝 기여하기

프로젝트 개선 제안이나 버그 리포트는 이슈로 등록해주세요.

### 기여 가이드라인

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## 📄 라이선스

MIT License - 자유롭게 사용하고 수정하세요!

## 📞 문의

- GitHub Issues: [프로젝트 이슈](https://github.com/yourusername/python3_tutorial/issues)
- Email: your.email@example.com

## 🌟 도움이 되셨다면

이 프로젝트가 도움이 되셨다면 ⭐ 스타를 눌러주세요!

---

**Made with ❤️ for Python Learners**