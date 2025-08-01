# 📚 프로그래밍 강의 시리즈

프로그래밍 초보자부터 실무 개발자까지 단계별로 학습할 수 있는 종합 교육 프로그램입니다.

## 🎯 프로젝트 개요

이 저장소는 Python, SQL, 그리고 데이터 분석을 위한 체계적인 학습 자료를 제공합니다. 각 과정은 이론과 실습을 균형있게 구성하여 실무에서 바로 활용할 수 있는 능력을 기를 수 있도록 설계되었습니다.

## 📋 강의 목록

### 1. 🐍 Python3 Tutorial Series
Python 기초부터 고급 기능까지 10개의 프로젝트를 통해 학습하는 과정

- **01_python_basics**: 파이썬 기초 - 계산기 프로젝트
- **02_functions_modules**: 함수와 모듈 - 텍스트 처리 유틸리티
- **03_oop_design**: 객체지향 프로그래밍 - 도서관 관리 시스템
- **04_type_hints_modern**: 타입 힌트와 모던 파이썬 - TODO 앱
- **05_gil_async**: GIL과 비동기 프로그래밍 - 파일 처리 시스템
- **06_testing**: 테스팅과 TDD - 뱅킹 시스템
- **07_web_scraping**: 웹 스크래핑 - 뉴스 수집기
- **08_flask_backend**: Flask 백엔드 - RESTful API
- **09_data_science**: 데이터 사이언스 기초 - 주가 분석
- **10_django_fullstack**: Django 풀스택 - 블로그 플랫폼

### 2. 💾 SQL Master Course
기초부터 실무까지 12개 챕터로 구성된 SQL 완전 정복 과정

- **Chapter 01**: SQL 기초 - 데이터베이스 개념과 기본 쿼리
- **Chapter 02**: 데이터 조작 언어(DML) 심화
- **Chapter 03**: 데이터 정의 언어(DDL)와 테이블 설계
- **Chapter 04**: 조인(JOIN) 마스터하기
- **Chapter 05**: 서브쿼리와 고급 쿼리 기법
- **Chapter 06**: 윈도우 함수와 분석 함수
- **Chapter 07**: 인덱스와 쿼리 최적화
- **Chapter 08**: 트랜잭션과 동시성 제어
- **Chapter 09**: 데이터베이스 설계와 정규화
- **Chapter 10**: PostgreSQL 심화 - 고급 기능과 최적화
- **Chapter 11**: MySQL 심화 - 성능 튜닝과 아키텍처
- **Chapter 12**: 데이터 분석가 인터뷰 대비 - 실전 문제

### 3. 📊 Data Analytics Master Course (개발 중)
광고 데이터 분석가를 위한 전문 과정

## 🚀 시작하기

### 필수 요구사항
- Python 3.8 이상
- Docker & Docker Compose
- Git

### 설치 방법

1. 저장소 클론
```bash
git clone https://github.com/data-jeong/lecture.git
cd lecture
```

2. Python 가상환경 설정
```bash
python3 -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
```

3. SQL 실습 환경 구성
```bash
cd sql_master_course
docker-compose up -d
```

## 📖 학습 방법

### Python Tutorial
1. 각 프로젝트 폴더의 `step_by_step.md` 파일 참고
2. 단계별 실습 진행
3. 최종 프로젝트 완성

### SQL Master Course
1. `SETUP.md` 파일로 환경 구성
2. Chapter 순서대로 학습
3. 각 챕터의 연습문제 풀이
4. 솔루션과 비교 검토

## 🛠️ 개발 환경

### 권장 IDE
- VS Code + Python/SQL 확장
- PyCharm Professional
- DataGrip (SQL 전용)

### 유용한 도구
- Jupyter Notebook (데이터 분석)
- Postman (API 테스트)
- DBeaver (데이터베이스 관리)

## 📝 기여 방법

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## 📜 라이선스

이 프로젝트는 MIT 라이선스 하에 배포됩니다.

## 📞 문의

- GitHub Issues: [https://github.com/data-jeong/lecture/issues](https://github.com/data-jeong/lecture/issues)
- Email: data.jeong@example.com

## 🙏 감사의 말

이 프로젝트는 많은 오픈소스 커뮤니티의 도움으로 만들어졌습니다.

---

**Happy Coding! 🎉**