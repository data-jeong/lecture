# Python 실습형 튜토리얼 프로젝트

## 프로젝트 개요
Python 기초부터 고급 기능까지 10개의 미니 프로젝트를 통해 실습하며 배우는 튜토리얼

## 프로젝트 구성

### 01_python_basics - 계산기 앱
- **학습 내용**: 변수, 자료형, 조건문, 반복문, 기본 입출력
- **프로젝트**: 공학용 계산기 만들기
- **핵심 기능**: 사칙연산, 제곱근, 삼각함수, 계산 히스토리

### 02_functions_modules - 텍스트 처리 유틸리티
- **학습 내용**: 함수 정의, 매개변수, 반환값, 모듈화, 패키지
- **프로젝트**: 텍스트 분석 도구 (단어 빈도, 문장 분석 등)
- **핵심 기능**: 텍스트 통계, 패턴 검색, 텍스트 변환

### 03_oop_design - 도서관 관리 시스템
- **학습 내용**: 클래스, 상속, 다형성, 캡슐화, 추상화
- **프로젝트**: 도서 대출/반납 시스템
- **핵심 기능**: 도서 관리, 회원 관리, 대출 기록

### 04_type_hints_modern - 타입 안전 ToDo 앱
- **학습 내용**: Type Hints, Generic, Protocol, TypeVar, 최신 Python 문법
- **프로젝트**: 타입 안전성이 보장된 할 일 관리 앱
- **핵심 기능**: CRUD 작업, 우선순위 관리, 데이터 검증

### 05_gil_async - 비동기 파일 처리기
- **학습 내용**: GIL 이해, async/await, asyncio, 동시성 vs 병렬성
- **프로젝트**: 대용량 파일 동시 처리 시스템
- **핵심 기능**: 비동기 파일 읽기/쓰기, 진행률 표시

### 06_web_scraping - 멀티 크롤러 시스템
- **학습 내용**: requests, BeautifulSoup, Selenium, Scrapy, httpx, curl 명령어 활용
- **프로젝트**: 다양한 방식의 웹 크롤링 도구 모음
- **핵심 기능**: 
  - requests + BeautifulSoup로 정적 페이지 크롤링
  - Selenium으로 동적 페이지 크롤링 (JavaScript 렌더링)
  - Scrapy로 대규모 크롤링 프레임워크 구축
  - httpx로 비동기 HTTP 요청
  - subprocess로 curl 명령어 래핑
  - 프록시, User-Agent 로테이션
  - 크롤링 데이터 저장 (JSON, CSV, Database)
  - robots.txt 준수 및 rate limiting

### 07_api_basics - 날씨 API 클라이언트
- **학습 내용**: REST API, JSON 처리, 외부 API 활용
- **프로젝트**: 날씨 정보 조회 앱
- **핵심 기능**: API 호출, 데이터 파싱, 시각화

### 08_database - 학생 성적 관리 시스템
- **학습 내용**: SQLite, SQL 기초, ORM (SQLAlchemy)
- **프로젝트**: 성적 입력/조회/통계 시스템
- **핵심 기능**: CRUD 작업, 통계 분석, 리포트 생성

### 09_fastapi_backend - RESTful 블로그 API
- **학습 내용**: FastAPI, Pydantic, API 설계, 인증
- **프로젝트**: 블로그 백엔드 API 서버
- **핵심 기능**: 게시글 CRUD, 사용자 인증, API 문서화

### 10_streamlit_project - 종합 대시보드 앱
- **학습 내용**: Streamlit, 데이터 시각화, 통합 프로젝트
- **프로젝트**: 위 프로젝트들을 통합한 대시보드
- **핵심 기능**: 실시간 데이터 표시, 차트, 인터랙티브 UI

## 학습 방법
1. 각 폴더의 PROJECT_PLAN.md를 먼저 읽고 개념 이해
2. step_by_step.md를 따라 단계별로 코딩
3. 완성된 코드를 분석하고 개선점 찾기
4. 추가 기능을 직접 구현해보기
5. 각 프로젝트 완료 시 Git commit & push

## 필요한 Python 버전
- Python 3.12 이상 권장 (GIL 개선 사항 활용)

## Git 워크플로우
각 프로젝트 완료 시:
```bash
git add .
git commit -m "Complete project_name"
git push origin main
```