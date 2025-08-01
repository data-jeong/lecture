# Chapter 10: PostgreSQL 고급 기능

## 학습 목표
- PostgreSQL 특화 데이터 타입 활용
- 고급 인덱스 기법 마스터
- 파티셔닝과 확장성 구현
- PL/pgSQL을 통한 저장 프로시저 개발
- PostgreSQL 고유 기능을 활용한 최적화

## 목차

### 1. PostgreSQL 특화 데이터 타입
- JSON/JSONB 타입과 연산자
- Array 타입과 배열 함수
- Range 타입과 범위 연산
- UUID와 고유 식별자
- 사용자 정의 타입

### 2. 고급 인덱스 기법
- GiST (Generalized Search Tree)
- GIN (Generalized Inverted Index)
- BRIN (Block Range Index)
- Hash 인덱스
- 부분 인덱스와 조건부 인덱스

### 3. 파티셔닝
- Range 파티셔닝
- List 파티셔닝
- Hash 파티셔닝
- 파티션 프루닝 최적화
- 동적 파티션 관리

### 4. PL/pgSQL 프로그래밍
- 함수와 프로시저 작성
- 변수와 제어구조
- 예외 처리
- 트리거 함수
- 동적 SQL 생성

### 5. 고급 기능 활용
- 윈도우 함수 고급 활용
- 재귀 쿼리 (Recursive CTE)
- Full Text Search
- 병렬 쿼리 처리
- 커스텀 집계 함수

### 6. 성능 튜닝과 모니터링
- 쿼리 성능 분석
- 통계 정보 관리
- 연결 풀링
- 메모리 관리
- 백그라운드 작업 최적화

## 실습 예제

### JSON 데이터 처리
```sql
-- JSONB 타입을 활용한 유연한 데이터 저장
CREATE TABLE user_profiles (
    id SERIAL PRIMARY KEY,
    username VARCHAR(50),
    profile JSONB
);

-- JSON 경로를 통한 데이터 검색
SELECT username, profile->'preferences'->>'theme'
FROM user_profiles
WHERE profile->>'age' > '25';
```

### 배열 데이터 활용
```sql
-- 배열 타입을 활용한 태그 시스템
CREATE TABLE articles (
    id SERIAL PRIMARY KEY,
    title TEXT,
    tags TEXT[]
);

-- 배열 연산을 통한 검색
SELECT title FROM articles
WHERE 'postgresql' = ANY(tags);
```

### 고급 파티셔닝
```sql
-- Range 파티셔닝을 통한 대용량 데이터 관리
CREATE TABLE sales (
    id SERIAL,
    sale_date DATE,
    amount DECIMAL
) PARTITION BY RANGE (sale_date);

CREATE TABLE sales_2023 PARTITION OF sales
    FOR VALUES FROM ('2023-01-01') TO ('2024-01-01');
```

## 실습 문제

### 기초 문제 (exercises/01_postgresql_basics.sql)
1. JSON/JSONB 데이터 처리
2. 배열 타입 활용
3. Range 타입 사용법
4. 기본 PL/pgSQL 함수 작성
5. GIN 인덱스 활용

### 중급 문제 (exercises/02_advanced_features.sql)
1. 복잡한 JSON 쿼리 작성
2. 파티셔닝 구현과 최적화
3. 트리거 함수 개발
4. 전문 검색 구현
5. 병렬 처리 최적화

### 고급 문제 (exercises/03_postgresql_mastery.sql)
1. 복합 데이터 타입 설계
2. 고성능 파티셔닝 전략
3. 복잡한 저장 프로시저 개발
4. 커스텀 집계 함수 생성
5. 대용량 데이터 처리 최적화

## 다음 단계
Chapter 10 완료 후 Chapter 12에서 데이터 분석가 인터뷰 준비를 진행합니다.