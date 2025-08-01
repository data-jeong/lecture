# SQL 마스터 코스 설정 가이드

## 🚀 빠른 시작

### 1. Docker 환경 설정

```bash
# 프로젝트 디렉토리로 이동
cd sql_master_course

# Docker 컨테이너 실행
docker-compose up -d

# 실행 확인
docker-compose ps
```

### 2. 데이터베이스 연결 확인

#### PostgreSQL 연결
```bash
# 커맨드 라인에서 접속
docker exec -it sql_course_postgres psql -U student -d sql_course

# 또는 Adminer 웹 인터페이스 사용
# http://localhost:8080
# 시스템: PostgreSQL
# 서버: postgres
# 사용자명: student
# 비밀번호: sql_master_2024
# 데이터베이스: sql_course
```

#### MySQL 연결
```bash
# 커맨드 라인에서 접속
docker exec -it sql_course_mysql mysql -u student -p sql_course
# 비밀번호: sql_master_2024

# 또는 Adminer 웹 인터페이스 사용
# http://localhost:8080
# 시스템: MySQL
# 서버: mysql
# 사용자명: student
# 비밀번호: sql_master_2024
# 데이터베이스: sql_course
```

### 3. 기본 데이터 설정

각 챕터별로 순서대로 데이터를 설정하세요:

```bash
# Chapter 01 데이터 설정
docker exec -i sql_course_postgres psql -U student -d sql_course < 01_sql_basics/data/create_tables.sql

# Chapter 02 데이터 설정
docker exec -i sql_course_postgres psql -U student -d sql_course < 02_dml_advanced/data/create_tables.sql

# 이후 챕터들도 동일한 방식으로 설정
```

## 📝 학습 가이드

### 권장 학습 순서

1. **Chapter 01-02**: SQL 기초와 DML 마스터
2. **Chapter 03-04**: DDL과 JOIN 완전 정복
3. **Chapter 05-06**: 고급 쿼리와 분석 함수
4. **Chapter 07-08**: 성능 최적화와 트랜잭션
5. **Chapter 09**: 데이터베이스 설계 이론
6. **Chapter 10-11**: PostgreSQL/MySQL 전문 과정
7. **Chapter 12**: 실전 인터뷰 대비

### 각 챕터 학습 방법

1. **README 읽기** (30분)
   - 학습 목표 확인
   - 개념과 예제 이해

2. **실습 환경 준비** (10분)
   - 해당 챕터 데이터 설정
   - 연결 테스트

3. **기초 문제 풀이** (60분)
   - exercises/01_basic.sql 문제 해결
   - 해답과 비교 검토

4. **심화 문제 풀이** (90분)
   - exercises/02_advanced.sql 도전
   - 다양한 해결 방법 시도

5. **복습과 정리** (30분)
   - 핵심 개념 정리
   - 실제 업무 적용 방안 생각

## 🛠️ 개발 환경별 설정

### VS Code 사용자

추천 확장 프로그램:
- SQLTools
- SQLTools PostgreSQL/MySQL Driver

### JetBrains 사용자

- DataGrip (유료)
- IntelliJ IDEA Database Tools

### 기타 도구

- DBeaver (무료)
- pgAdmin (PostgreSQL 전용)
- MySQL Workbench (MySQL 전용)

## 🔧 트러블슈팅

### 포트 충돌 문제

기존에 PostgreSQL이나 MySQL이 실행 중인 경우:

```bash
# 기존 서비스 중지
sudo service postgresql stop
sudo service mysql stop

# 또는 docker-compose.yml에서 포트 변경
ports:
  - "5433:5432"  # PostgreSQL
  - "3307:3306"  # MySQL
```

### 권한 문제

```bash
# Docker 권한 추가
sudo usermod -aG docker $USER

# 로그아웃 후 재로그인 필요
```

### 데이터 초기화

```bash
# 모든 데이터 삭제 후 재시작
docker-compose down -v
docker-compose up -d
```

## 📊 성과 측정

### 자가 평가 기준

- **기초 (Chapter 1-4)**: 70% 이상 문제 해결
- **중급 (Chapter 5-8)**: 60% 이상 문제 해결  
- **고급 (Chapter 9-12)**: 50% 이상 문제 해결

### 실습 포트폴리오

각 챕터 완료 후:
1. 학습 내용 정리
2. 실제 프로젝트 적용 사례 작성
3. 성능 최적화 경험 기록

## 💡 추가 리소스

### 온라인 자료
- PostgreSQL 공식 문서: https://www.postgresql.org/docs/
- MySQL 공식 문서: https://dev.mysql.com/doc/
- SQL 표준 참조: ISO/IEC 9075

### 실무 데이터셋
- Northwind Database
- Sakila Sample Database
- Stack Overflow Data Dump

## 🎯 인터뷰 대비 팁

1. **기본기 탄탄히**: Chapter 1-4 완벽 숙지
2. **성능 고려**: 모든 쿼리에서 실행 계획 확인
3. **실무 경험**: 실제 비즈니스 문제 해결 경험 쌓기
4. **최신 트렌드**: NoSQL, NewSQL 동향 파악

시간 투자: 전체 과정 완주에 약 80-100시간 소요 예상