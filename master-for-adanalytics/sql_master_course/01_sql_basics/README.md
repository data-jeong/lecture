# Chapter 01: SQL 기초 - 데이터베이스 개념과 기본 쿼리

## 학습 목표
- 데이터베이스와 RDBMS의 기본 개념 이해
- SQL의 기본 문법 습득
- SELECT 문을 사용한 데이터 조회
- 기본 집계 함수 활용

## 목차

### 1. 데이터베이스 기초 개념
- 데이터베이스란?
- RDBMS (Relational Database Management System)
- 테이블, 행(Row), 열(Column)
- Primary Key와 Foreign Key

### 2. SQL 소개
- SQL이란?
- SQL의 종류 (DDL, DML, DCL, TCL)
- SQL 표준과 방언

### 3. SELECT 기본 문법
```sql
-- 기본 SELECT 문법
SELECT column1, column2
FROM table_name;

-- 모든 컬럼 조회
SELECT *
FROM table_name;
```

### 4. WHERE 절을 사용한 조건 검색
```sql
-- 조건 검색
SELECT *
FROM employees
WHERE department = 'Sales';

-- 비교 연산자
-- =, <>, !=, <, >, <=, >=
SELECT *
FROM products
WHERE price > 100;
```

### 5. 논리 연산자 (AND, OR, NOT)
```sql
-- AND 연산자
SELECT *
FROM employees
WHERE department = 'Sales' AND salary > 50000;

-- OR 연산자
SELECT *
FROM products
WHERE category = 'Electronics' OR category = 'Books';

-- NOT 연산자
SELECT *
FROM customers
WHERE NOT country = 'USA';
```

### 6. 정렬 (ORDER BY)
```sql
-- 오름차순 정렬 (기본값)
SELECT *
FROM employees
ORDER BY salary;

-- 내림차순 정렬
SELECT *
FROM employees
ORDER BY salary DESC;

-- 다중 정렬
SELECT *
FROM employees
ORDER BY department, salary DESC;
```

### 7. 결과 제한 (LIMIT)
```sql
-- 상위 10개만 조회
SELECT *
FROM products
ORDER BY price DESC
LIMIT 10;

-- OFFSET과 함께 사용 (페이징)
SELECT *
FROM products
ORDER BY product_id
LIMIT 10 OFFSET 20;  -- 21번째부터 10개
```

### 8. 중복 제거 (DISTINCT)
```sql
-- 중복 제거
SELECT DISTINCT department
FROM employees;

-- 다중 컬럼 중복 제거
SELECT DISTINCT department, job_title
FROM employees;
```

### 9. 기본 집계 함수
```sql
-- COUNT: 행 수 세기
SELECT COUNT(*)
FROM employees;

SELECT COUNT(DISTINCT department)
FROM employees;

-- SUM: 합계
SELECT SUM(salary)
FROM employees;

-- AVG: 평균
SELECT AVG(salary)
FROM employees;

-- MIN/MAX: 최소값/최대값
SELECT MIN(salary), MAX(salary)
FROM employees;
```

### 10. GROUP BY와 HAVING
```sql
-- 부서별 평균 급여
SELECT department, AVG(salary) as avg_salary
FROM employees
GROUP BY department;

-- HAVING: 그룹에 대한 조건
SELECT department, AVG(salary) as avg_salary
FROM employees
GROUP BY department
HAVING AVG(salary) > 60000;
```

## 실습 데이터베이스

이번 장에서는 다음과 같은 샘플 테이블을 사용합니다:

1. **employees** (직원)
   - employee_id (직원 ID)
   - first_name (이름)
   - last_name (성)
   - department (부서)
   - job_title (직책)
   - salary (급여)
   - hire_date (입사일)

2. **products** (상품)
   - product_id (상품 ID)
   - product_name (상품명)
   - category (카테고리)
   - price (가격)
   - stock_quantity (재고)

3. **customers** (고객)
   - customer_id (고객 ID)
   - company_name (회사명)
   - contact_name (담당자명)
   - country (국가)
   - city (도시)

## 실습 문제

실습 문제는 `exercises/` 폴더에 있으며, 해답은 `solutions/` 폴더에서 확인할 수 있습니다.

### 기초 문제 (exercises/01_basic.sql)
1. employees 테이블에서 모든 직원 조회
2. 급여가 70000 이상인 직원의 이름과 급여 조회
3. Sales 부서 직원 수 계산
4. 각 부서별 직원 수와 평균 급여 조회

### 중급 문제 (exercises/02_intermediate.sql)
1. 가장 비싼 상품 TOP 5 조회
2. 재고가 10개 미만인 Electronics 카테고리 상품 조회
3. 국가별 고객 수 조회 (고객이 5명 이상인 국가만)
4. 2020년 이후 입사한 직원 중 급여가 부서 평균보다 높은 직원 조회

## 다음 단계

Chapter 01을 완료했다면, Chapter 02에서 INSERT, UPDATE, DELETE 등의 데이터 조작 언어(DML)를 심화 학습합니다.