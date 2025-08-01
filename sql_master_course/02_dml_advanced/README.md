# Chapter 02: 데이터 조작 언어(DML) 심화

## 학습 목표
- INSERT, UPDATE, DELETE 문의 고급 사용법 마스터
- MERGE 문(UPSERT)의 이해와 활용
- 트랜잭션의 기본 개념과 ACID 속성
- 다양한 데이터 타입과 형변환 기법

## 목차

### 1. INSERT 문 심화
```sql
-- 기본 INSERT
INSERT INTO table_name (column1, column2)
VALUES (value1, value2);

-- 다중 행 INSERT
INSERT INTO employees (first_name, last_name, department)
VALUES 
    ('John', 'Doe', 'IT'),
    ('Jane', 'Smith', 'HR'),
    ('Bob', 'Johnson', 'Sales');

-- SELECT를 이용한 INSERT
INSERT INTO employees_backup
SELECT * FROM employees
WHERE department = 'IT';

-- INSERT ... RETURNING (PostgreSQL)
INSERT INTO products (product_name, price)
VALUES ('New Product', 99.99)
RETURNING product_id;
```

### 2. UPDATE 문 심화
```sql
-- 기본 UPDATE
UPDATE employees
SET salary = salary * 1.1
WHERE department = 'Sales';

-- 다중 컬럼 UPDATE
UPDATE products
SET price = price * 0.9,
    last_modified = CURRENT_TIMESTAMP
WHERE category = 'Electronics';

-- JOIN을 이용한 UPDATE (PostgreSQL)
UPDATE employees e
SET salary = e.salary * 1.15
FROM departments d
WHERE e.department_id = d.department_id
  AND d.department_name = 'IT';

-- CASE를 이용한 조건부 UPDATE
UPDATE employees
SET salary = CASE 
    WHEN performance_rating = 'A' THEN salary * 1.15
    WHEN performance_rating = 'B' THEN salary * 1.10
    WHEN performance_rating = 'C' THEN salary * 1.05
    ELSE salary
END;
```

### 3. DELETE 문 심화
```sql
-- 기본 DELETE
DELETE FROM employees
WHERE hire_date < '2010-01-01';

-- JOIN을 이용한 DELETE (PostgreSQL)
DELETE FROM order_items
USING orders
WHERE order_items.order_id = orders.order_id
  AND orders.order_date < '2020-01-01';

-- TRUNCATE vs DELETE
-- DELETE: 조건부 삭제, 트랜잭션 로그 기록, 롤백 가능
DELETE FROM table_name WHERE condition;

-- TRUNCATE: 전체 삭제, 빠름, 롤백 불가(일부 DB)
TRUNCATE TABLE table_name;
```

### 4. MERGE 문 (UPSERT)
```sql
-- PostgreSQL: INSERT ... ON CONFLICT
INSERT INTO products (product_id, product_name, price)
VALUES (1, 'Laptop', 999.99)
ON CONFLICT (product_id) 
DO UPDATE SET 
    product_name = EXCLUDED.product_name,
    price = EXCLUDED.price;

-- MySQL: INSERT ... ON DUPLICATE KEY UPDATE
INSERT INTO products (product_id, product_name, price)
VALUES (1, 'Laptop', 999.99)
ON DUPLICATE KEY UPDATE
    product_name = VALUES(product_name),
    price = VALUES(price);

-- 조건부 UPSERT (PostgreSQL)
INSERT INTO inventory (product_id, quantity)
VALUES (1, 100)
ON CONFLICT (product_id)
DO UPDATE SET quantity = inventory.quantity + EXCLUDED.quantity
WHERE inventory.quantity < 1000;
```

### 5. 트랜잭션 기초
```sql
-- 트랜잭션 시작
BEGIN; -- 또는 START TRANSACTION;

-- 작업 수행
UPDATE accounts SET balance = balance - 100 WHERE account_id = 1;
UPDATE accounts SET balance = balance + 100 WHERE account_id = 2;

-- 커밋 또는 롤백
COMMIT; -- 변경사항 확정
-- 또는
ROLLBACK; -- 변경사항 취소

-- SAVEPOINT 사용
BEGIN;
UPDATE employees SET salary = salary * 1.1;
SAVEPOINT before_delete;
DELETE FROM employees WHERE performance = 'Poor';
-- 문제 발생 시
ROLLBACK TO before_delete;
COMMIT;
```

### 6. 데이터 타입과 형변환

#### 6.1 주요 데이터 타입
```sql
-- 숫자 타입
INTEGER, BIGINT, DECIMAL(10,2), FLOAT, REAL

-- 문자 타입
CHAR(10), VARCHAR(255), TEXT

-- 날짜/시간 타입
DATE, TIME, TIMESTAMP, INTERVAL

-- Boolean
BOOLEAN

-- JSON (PostgreSQL, MySQL 5.7+)
JSON, JSONB (PostgreSQL)
```

#### 6.2 형변환 (CAST)
```sql
-- 명시적 형변환
SELECT CAST('123' AS INTEGER);
SELECT CAST(price AS VARCHAR(10)) FROM products;

-- PostgreSQL :: 연산자
SELECT '123'::INTEGER;
SELECT price::TEXT FROM products;

-- 날짜 형변환
SELECT CAST('2024-01-01' AS DATE);
SELECT TO_DATE('01-01-2024', 'DD-MM-YYYY'); -- PostgreSQL

-- 숫자 포맷팅
SELECT TO_CHAR(price, '$999,999.99') FROM products; -- PostgreSQL
SELECT FORMAT(price, 2) FROM products; -- MySQL
```

### 7. NULL 처리
```sql
-- NULL 체크
SELECT * FROM employees WHERE manager_id IS NULL;
SELECT * FROM employees WHERE manager_id IS NOT NULL;

-- COALESCE: 첫 번째 NOT NULL 값 반환
SELECT COALESCE(phone, email, 'No contact') FROM customers;

-- NULLIF: 두 값이 같으면 NULL 반환
SELECT NULLIF(quantity, 0) FROM inventory;

-- NULL과 집계 함수
SELECT 
    COUNT(*),           -- NULL 포함
    COUNT(manager_id),  -- NULL 제외
    AVG(salary)         -- NULL 제외하고 평균
FROM employees;
```

### 8. 문자열 처리 함수
```sql
-- 문자열 연결
SELECT first_name || ' ' || last_name AS full_name FROM employees; -- PostgreSQL
SELECT CONCAT(first_name, ' ', last_name) AS full_name FROM employees; -- MySQL

-- 문자열 함수들
SELECT 
    UPPER(name),        -- 대문자
    LOWER(name),        -- 소문자
    LENGTH(name),       -- 길이
    TRIM(name),         -- 공백 제거
    SUBSTRING(name, 1, 3), -- 부분 문자열
    REPLACE(name, 'old', 'new') -- 치환
FROM customers;
```

### 9. 날짜/시간 함수
```sql
-- 현재 날짜/시간
SELECT CURRENT_DATE, CURRENT_TIME, CURRENT_TIMESTAMP;

-- 날짜 연산
SELECT 
    hire_date,
    hire_date + INTERVAL '1 year',
    EXTRACT(YEAR FROM hire_date),
    DATE_PART('month', hire_date), -- PostgreSQL
    DATEDIFF(CURRENT_DATE, hire_date) -- MySQL
FROM employees;

-- 날짜 포맷팅
SELECT TO_CHAR(hire_date, 'YYYY-MM-DD') FROM employees; -- PostgreSQL
SELECT DATE_FORMAT(hire_date, '%Y-%m-%d') FROM employees; -- MySQL
```

## 실습 과제

### 과제 1: 대량 데이터 처리
- 성능을 고려한 대량 INSERT/UPDATE 작업
- 트랜잭션을 활용한 안전한 데이터 처리

### 과제 2: 데이터 마이그레이션
- 구조가 다른 테이블 간 데이터 이동
- 데이터 타입 변환과 NULL 처리

### 과제 3: UPSERT 활용
- 재고 관리 시스템 구현
- 동시성을 고려한 데이터 업데이트

## 다음 단계

Chapter 03에서는 DDL을 통한 테이블 설계와 제약조건, 인덱스의 기초를 학습합니다.