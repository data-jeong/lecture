# SQL 마스터 코스: 기초부터 실무까지

## 📚 코스 개요

이 코스는 SQL 초보자부터 데이터 분석가 인터뷰를 준비하는 고급 사용자까지 모두를 위한 종합적인 SQL 학습 프로그램입니다. 12개의 챕터를 통해 SQL의 기초부터 PostgreSQL과 MySQL의 고급 기능까지 마스터할 수 있습니다.

## 🎯 학습 목표

- SQL 기본 문법부터 고급 쿼리까지 완벽 마스터
- 데이터베이스 설계 및 최적화 능력 함양
- PostgreSQL과 MySQL의 특화 기능 습득
- 실전 데이터 분석가 인터뷰 대비

## 📋 커리큘럼

### Chapter 01: SQL 기초 - 데이터베이스 개념과 기본 쿼리
- 데이터베이스 개념과 RDBMS 이해
- SELECT, FROM, WHERE 기본 문법
- ORDER BY, LIMIT, DISTINCT
- 기본 집계 함수 (COUNT, SUM, AVG, MIN, MAX)

### Chapter 02: 데이터 조작 언어(DML) 심화
- INSERT, UPDATE, DELETE 심화
- MERGE 문 (UPSERT)
- 트랜잭션 기초
- 데이터 타입과 형변환

### Chapter 03: 데이터 정의 언어(DDL)와 테이블 설계
- CREATE, ALTER, DROP
- 제약조건 (PRIMARY KEY, FOREIGN KEY, UNIQUE, CHECK)
- 뷰(VIEW)와 인덱스 기초
- 테이블 설계 베스트 프랙티스

### Chapter 04: 조인(JOIN) 마스터하기
- INNER JOIN 완벽 이해
- LEFT/RIGHT/FULL OUTER JOIN
- CROSS JOIN과 SELF JOIN
- 다중 테이블 조인과 성능 최적화

### Chapter 05: 서브쿼리와 고급 쿼리 기법
- 스칼라 서브쿼리
- 인라인 뷰와 상관 서브쿼리
- EXISTS, IN, ANY, ALL
- WITH 절 (CTE - Common Table Expression)

### Chapter 06: 윈도우 함수와 분석 함수
- ROW_NUMBER, RANK, DENSE_RANK
- LAG, LEAD, FIRST_VALUE, LAST_VALUE
- 집계 윈도우 함수
- PARTITION BY와 ORDER BY의 활용

### Chapter 07: 인덱스와 쿼리 최적화
- 인덱스의 원리와 종류
- 실행 계획 분석
- 쿼리 최적화 기법
- 인덱스 설계 전략

### Chapter 08: 트랜잭션과 동시성 제어
- ACID 속성
- 격리 수준 (Isolation Level)
- 잠금(Lock)과 데드락
- MVCC (Multi-Version Concurrency Control)

### Chapter 09: 데이터베이스 설계와 정규화
- ER 다이어그램
- 정규화 (1NF ~ BCNF)
- 반정규화 전략
- 실전 스키마 설계

### Chapter 10: PostgreSQL 심화 - 고급 기능과 최적화
- PostgreSQL 특화 데이터 타입 (JSON, Array, Range)
- 파티셔닝
- 고급 인덱스 (GiST, GIN, BRIN)
- PL/pgSQL과 저장 프로시저

### Chapter 11: MySQL 심화 - 성능 튜닝과 아키텍처
- MySQL 스토리지 엔진 (InnoDB vs MyISAM)
- 복제와 샤딩
- 성능 모니터링과 튜닝
- MySQL 특화 최적화 기법

### Chapter 12: 데이터 분석가 인터뷰 대비 - 실전 문제
- 코호트 분석
- 퍼널 분석
- 리텐션 분석
- A/B 테스트 데이터 분석
- 실전 면접 문제 100선

## 🛠️ 실습 환경

- PostgreSQL 14+
- MySQL 8.0+
- Docker를 통한 실습 환경 구성
- 샘플 데이터셋 제공

## 📊 프로젝트 구조

```
sql_master_course/
├── 01_sql_basics/
│   ├── exercises/    # 실습 문제
│   ├── solutions/    # 해답
│   └── data/         # 샘플 데이터
├── 02_dml_advanced/
│   └── ...
└── 12_interview_prep/
    └── ...
```

## 🚀 시작하기

1. Docker 설치
2. 실습 데이터베이스 환경 구성
3. Chapter 01부터 순차적으로 학습
4. 각 챕터의 실습 문제 풀이
5. 프로젝트 과제 수행

## 💡 학습 팁

- 각 챕터마다 제공되는 실습 문제를 꼭 풀어보세요
- 실제 데이터로 쿼리를 작성해보며 연습하세요
- 실행 계획을 확인하는 습관을 기르세요
- 다양한 해결 방법을 시도해보세요

## 📝 평가 방식

- 각 챕터별 실습 과제
- 중간 프로젝트 (Chapter 6 완료 후)
- 최종 프로젝트 (전체 과정 완료 후)
- 모의 인터뷰 세션