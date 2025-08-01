# Chapter 03: 데이터 정의 언어(DDL)와 테이블 설계

## 학습 목표
- CREATE, ALTER, DROP 문의 완전한 이해
- 제약조건(Constraints)의 종류와 활용법
- 뷰(View)와 인덱스의 기초 개념
- 효율적인 테이블 설계 원칙과 베스트 프랙티스

## 목차

### 1. DDL 기초와 CREATE 문

#### 1.1 데이터베이스 생성
```sql
-- 데이터베이스 생성
CREATE DATABASE company_db
    WITH ENCODING = 'UTF8'
    LC_COLLATE = 'en_US.UTF-8'
    LC_CTYPE = 'en_US.UTF-8';

-- MySQL
CREATE DATABASE company_db
    CHARACTER SET utf8mb4
    COLLATE utf8mb4_unicode_ci;
```

#### 1.2 테이블 생성 기본
```sql
-- 기본 테이블 생성
CREATE TABLE employees (
    employee_id SERIAL PRIMARY KEY,
    first_name VARCHAR(50) NOT NULL,
    last_name VARCHAR(50) NOT NULL,
    email VARCHAR(100) UNIQUE,
    phone VARCHAR(20),
    hire_date DATE DEFAULT CURRENT_DATE,
    salary DECIMAL(10,2) CHECK (salary > 0),
    department_id INTEGER
);

-- 다양한 데이터 타입 활용
CREATE TABLE products (
    product_id SERIAL PRIMARY KEY,
    product_name VARCHAR(255) NOT NULL,
    description TEXT,
    price DECIMAL(10,2) NOT NULL,
    category_id INTEGER,
    in_stock BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    metadata JSONB  -- PostgreSQL
);
```

### 2. 제약조건 (Constraints)

#### 2.1 PRIMARY KEY
```sql
-- 단일 컬럼 Primary Key
CREATE TABLE departments (
    dept_id SERIAL PRIMARY KEY,
    dept_name VARCHAR(100) NOT NULL
);

-- 복합 Primary Key
CREATE TABLE order_items (
    order_id INTEGER,
    product_id INTEGER,
    quantity INTEGER NOT NULL,
    unit_price DECIMAL(10,2) NOT NULL,
    PRIMARY KEY (order_id, product_id)
);

-- 명명된 제약조건
CREATE TABLE customers (
    customer_id SERIAL CONSTRAINT pk_customers PRIMARY KEY,
    customer_name VARCHAR(255) NOT NULL
);
```

#### 2.2 FOREIGN KEY
```sql
-- 외래키 제약조건
CREATE TABLE employees (
    employee_id SERIAL PRIMARY KEY,
    first_name VARCHAR(50) NOT NULL,
    department_id INTEGER,
    FOREIGN KEY (department_id) REFERENCES departments(dept_id)
);

-- 참조 무결성 옵션
CREATE TABLE orders (
    order_id SERIAL PRIMARY KEY,
    customer_id INTEGER,
    order_date DATE DEFAULT CURRENT_DATE,
    FOREIGN KEY (customer_id) REFERENCES customers(customer_id)
        ON DELETE CASCADE
        ON UPDATE RESTRICT
);

-- 명명된 외래키
CREATE TABLE order_items (
    order_id INTEGER,
    product_id INTEGER,
    quantity INTEGER,
    CONSTRAINT fk_order_items_order 
        FOREIGN KEY (order_id) REFERENCES orders(order_id),
    CONSTRAINT fk_order_items_product 
        FOREIGN KEY (product_id) REFERENCES products(product_id)
);
```

#### 2.3 UNIQUE 제약조건
```sql
-- 단일 컬럼 UNIQUE
CREATE TABLE users (
    user_id SERIAL PRIMARY KEY,
    username VARCHAR(50) UNIQUE,
    email VARCHAR(100) UNIQUE
);

-- 복합 UNIQUE
CREATE TABLE enrollments (
    student_id INTEGER,
    course_id INTEGER,
    enrollment_date DATE,
    UNIQUE (student_id, course_id)
);

-- 조건부 UNIQUE (PostgreSQL)
CREATE TABLE products (
    product_id SERIAL PRIMARY KEY,
    sku VARCHAR(50),
    is_active BOOLEAN,
    UNIQUE (sku) WHERE is_active = TRUE
);
```

#### 2.4 CHECK 제약조건
```sql
-- 단순 CHECK 제약조건
CREATE TABLE employees (
    employee_id SERIAL PRIMARY KEY,
    age INTEGER CHECK (age >= 18 AND age <= 65),
    salary DECIMAL(10,2) CHECK (salary > 0),
    gender CHAR(1) CHECK (gender IN ('M', 'F'))
);

-- 복잡한 CHECK 제약조건
CREATE TABLE orders (
    order_id SERIAL PRIMARY KEY,
    order_date DATE,
    ship_date DATE,
    status VARCHAR(20) CHECK (status IN ('pending', 'shipped', 'delivered', 'cancelled')),
    CONSTRAINT check_ship_after_order CHECK (ship_date >= order_date)
);

-- 명명된 CHECK 제약조건
CREATE TABLE products (
    product_id SERIAL PRIMARY KEY,
    price DECIMAL(10,2),
    discount_price DECIMAL(10,2),
    CONSTRAINT check_discount_valid 
        CHECK (discount_price IS NULL OR discount_price < price)
);
```

#### 2.5 NOT NULL과 DEFAULT
```sql
CREATE TABLE customers (
    customer_id SERIAL PRIMARY KEY,
    company_name VARCHAR(255) NOT NULL,
    contact_name VARCHAR(100),
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    is_active BOOLEAN NOT NULL DEFAULT TRUE,
    credit_limit DECIMAL(15,2) DEFAULT 10000.00
);

-- 계산된 DEFAULT 값
CREATE TABLE audit_log (
    log_id SERIAL PRIMARY KEY,
    user_id INTEGER NOT NULL,
    action VARCHAR(50) NOT NULL,
    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    session_id VARCHAR(100) DEFAULT gen_random_uuid()::TEXT  -- PostgreSQL
);
```

### 3. ALTER 문을 통한 테이블 수정

#### 3.1 컬럼 추가/삭제/수정
```sql
-- 컬럼 추가
ALTER TABLE employees 
ADD COLUMN middle_name VARCHAR(50);

ALTER TABLE employees 
ADD COLUMN birth_date DATE,
ADD COLUMN manager_id INTEGER;

-- 컬럼 삭제
ALTER TABLE employees 
DROP COLUMN middle_name;

-- 컬럼 타입 변경
ALTER TABLE employees 
ALTER COLUMN salary TYPE DECIMAL(12,2);

-- 컬럼명 변경
ALTER TABLE employees 
RENAME COLUMN birth_date TO date_of_birth;

-- DEFAULT 값 설정/제거
ALTER TABLE employees 
ALTER COLUMN hire_date SET DEFAULT CURRENT_DATE;

ALTER TABLE employees 
ALTER COLUMN hire_date DROP DEFAULT;

-- NOT NULL 제약조건 추가/제거
ALTER TABLE employees 
ALTER COLUMN email SET NOT NULL;

ALTER TABLE employees 
ALTER COLUMN phone DROP NOT NULL;
```

#### 3.2 제약조건 추가/삭제
```sql
-- PRIMARY KEY 추가
ALTER TABLE employees 
ADD CONSTRAINT pk_employees PRIMARY KEY (employee_id);

-- FOREIGN KEY 추가
ALTER TABLE employees 
ADD CONSTRAINT fk_employees_dept 
    FOREIGN KEY (department_id) REFERENCES departments(dept_id);

-- UNIQUE 제약조건 추가
ALTER TABLE employees 
ADD CONSTRAINT uq_employees_email UNIQUE (email);

-- CHECK 제약조건 추가
ALTER TABLE employees 
ADD CONSTRAINT check_salary_positive CHECK (salary > 0);

-- 제약조건 삭제
ALTER TABLE employees 
DROP CONSTRAINT check_salary_positive;

-- 제약조건 이름 변경
ALTER TABLE employees 
RENAME CONSTRAINT uq_employees_email TO unique_employee_email;
```

#### 3.3 테이블명 변경
```sql
-- 테이블명 변경
ALTER TABLE employees RENAME TO staff;

-- 스키마 이동 (PostgreSQL)
ALTER TABLE employees SET SCHEMA hr;
```

### 4. 인덱스 기초

#### 4.1 인덱스 생성과 삭제
```sql
-- 단일 컬럼 인덱스
CREATE INDEX idx_employees_email ON employees (email);

-- 복합 인덱스
CREATE INDEX idx_employees_dept_salary ON employees (department_id, salary);

-- 유니크 인덱스
CREATE UNIQUE INDEX idx_employees_ssn ON employees (ssn);

-- 부분 인덱스 (PostgreSQL)
CREATE INDEX idx_active_employees ON employees (last_name) 
WHERE is_active = TRUE;

-- 함수 기반 인덱스
CREATE INDEX idx_employees_upper_name ON employees (UPPER(last_name));

-- 인덱스 삭제
DROP INDEX idx_employees_email;
```

#### 4.2 인덱스 종류 (PostgreSQL)
```sql
-- B-Tree 인덱스 (기본값)
CREATE INDEX idx_employees_salary ON employees USING BTREE (salary);

-- Hash 인덱스
CREATE INDEX idx_employees_dept ON employees USING HASH (department_id);

-- GIN 인덱스 (배열, JSONB용)
CREATE INDEX idx_products_tags ON products USING GIN (tags);

-- GiST 인덱스 (지리 정보, 전문 검색용)
CREATE INDEX idx_locations_point ON locations USING GIST (location_point);
```

### 5. 뷰(View) 활용

#### 5.1 뷰 생성과 활용
```sql
-- 기본 뷰 생성
CREATE VIEW employee_summary AS
SELECT 
    e.employee_id,
    e.first_name || ' ' || e.last_name AS full_name,
    e.email,
    d.dept_name,
    e.salary
FROM employees e
JOIN departments d ON e.department_id = d.dept_id;

-- 집계 뷰
CREATE VIEW department_stats AS
SELECT 
    d.dept_name,
    COUNT(*) as employee_count,
    AVG(e.salary) as avg_salary,
    MIN(e.salary) as min_salary,
    MAX(e.salary) as max_salary
FROM employees e
JOIN departments d ON e.department_id = d.dept_id
GROUP BY d.dept_id, d.dept_name;

-- 복잡한 비즈니스 로직 뷰
CREATE VIEW high_value_customers AS
SELECT 
    c.customer_id,
    c.company_name,
    COUNT(o.order_id) as total_orders,
    SUM(oi.quantity * oi.unit_price) as total_spent,
    AVG(oi.quantity * oi.unit_price) as avg_order_value
FROM customers c
JOIN orders o ON c.customer_id = o.customer_id
JOIN order_items oi ON o.order_id = oi.order_id
GROUP BY c.customer_id, c.company_name
HAVING SUM(oi.quantity * oi.unit_price) > 10000;
```

#### 5.2 뷰 수정과 삭제
```sql
-- 뷰 수정
CREATE OR REPLACE VIEW employee_summary AS
SELECT 
    e.employee_id,
    e.first_name || ' ' || e.last_name AS full_name,
    e.email,
    d.dept_name,
    e.salary,
    e.hire_date
FROM employees e
JOIN departments d ON e.department_id = d.dept_id
WHERE e.is_active = TRUE;

-- 뷰 삭제
DROP VIEW employee_summary;
```

#### 5.3 머티리얼라이즈드 뷰 (PostgreSQL)
```sql
-- 머티리얼라이즈드 뷰 생성
CREATE MATERIALIZED VIEW monthly_sales AS
SELECT 
    DATE_TRUNC('month', o.order_date) as month,
    SUM(oi.quantity * oi.unit_price) as total_sales,
    COUNT(DISTINCT o.customer_id) as unique_customers,
    COUNT(o.order_id) as total_orders
FROM orders o
JOIN order_items oi ON o.order_id = oi.order_id
GROUP BY DATE_TRUNC('month', o.order_date);

-- 머티리얼라이즈드 뷰 새로고침
REFRESH MATERIALIZED VIEW monthly_sales;

-- 동시성을 고려한 새로고침
REFRESH MATERIALIZED VIEW CONCURRENTLY monthly_sales;
```

### 6. 테이블 설계 베스트 프랙티스

#### 6.1 네이밍 컨벤션
```sql
-- 권장 네이밍 컨벤션
CREATE TABLE customers (          -- 테이블명: 복수형, 소문자, 언더스코어
    customer_id SERIAL PRIMARY KEY,  -- 컬럼명: 소문자, 언더스코어
    first_name VARCHAR(50),       -- 의미있는 컬럼명
    created_at TIMESTAMP,         -- 일관된 시간 컬럼명
    is_active BOOLEAN             -- Boolean: is_, has_ 접두사
);

-- 제약조건 네이밍
CONSTRAINT pk_customers PRIMARY KEY (customer_id),
CONSTRAINT fk_orders_customer FOREIGN KEY (customer_id) REFERENCES customers(customer_id),
CONSTRAINT uq_customers_email UNIQUE (email),
CONSTRAINT chk_customers_age CHECK (age >= 0)
```

#### 6.2 데이터 타입 선택 가이드
```sql
-- 적절한 데이터 타입 선택
CREATE TABLE products (
    product_id SERIAL PRIMARY KEY,           -- AUTO INCREMENT용 SERIAL
    sku VARCHAR(20) NOT NULL,                -- 고정 길이면 CHAR, 가변이면 VARCHAR
    product_name VARCHAR(255) NOT NULL,      -- 제목: 255자로 충분
    description TEXT,                        -- 긴 텍스트: TEXT
    price DECIMAL(10,2) NOT NULL,            -- 금액: DECIMAL (정확성)
    weight REAL,                             -- 무게: REAL or FLOAT
    is_active BOOLEAN DEFAULT TRUE,          -- 플래그: BOOLEAN
    created_at TIMESTAMP DEFAULT NOW(),      -- 시간: TIMESTAMP
    category_id INTEGER,                     -- 외래키: INTEGER
    tags TEXT[],                             -- 배열: PostgreSQL
    metadata JSONB                           -- JSON: PostgreSQL JSONB
);
```

#### 6.3 성능 고려사항
```sql
-- 성능을 위한 테이블 설계
CREATE TABLE orders (
    order_id SERIAL PRIMARY KEY,
    customer_id INTEGER NOT NULL,           -- 자주 조인되는 컬럼
    order_date DATE NOT NULL,               -- 자주 필터링되는 컬럼
    status VARCHAR(20) NOT NULL,            -- 자주 필터링되는 컬럼
    total_amount DECIMAL(15,2) NOT NULL,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

-- 적절한 인덱스 생성
CREATE INDEX idx_orders_customer_date ON orders (customer_id, order_date);
CREATE INDEX idx_orders_status ON orders (status);
CREATE INDEX idx_orders_date ON orders (order_date);
```

### 7. 시퀀스와 자동 증가

#### 7.1 시퀀스 활용 (PostgreSQL)
```sql
-- 시퀀스 생성
CREATE SEQUENCE employee_id_seq
    START WITH 1000
    INCREMENT BY 1
    MINVALUE 1000
    MAXVALUE 999999
    CACHE 1;

-- 시퀀스를 사용하는 테이블
CREATE TABLE employees (
    employee_id INTEGER DEFAULT nextval('employee_id_seq') PRIMARY KEY,
    first_name VARCHAR(50) NOT NULL
);

-- 시퀀스 값 조회/설정
SELECT nextval('employee_id_seq');
SELECT currval('employee_id_seq');
SELECT setval('employee_id_seq', 2000);
```

#### 7.2 AUTO_INCREMENT (MySQL)
```sql
-- MySQL AUTO_INCREMENT
CREATE TABLE employees (
    employee_id INT AUTO_INCREMENT PRIMARY KEY,
    first_name VARCHAR(50) NOT NULL
) AUTO_INCREMENT = 1000;

-- AUTO_INCREMENT 값 변경
ALTER TABLE employees AUTO_INCREMENT = 2000;
```

### 8. 파티셔닝 기초

#### 8.1 PostgreSQL 파티셔닝
```sql
-- 범위 파티셔닝
CREATE TABLE sales (
    sale_id SERIAL,
    sale_date DATE NOT NULL,
    amount DECIMAL(10,2),
    customer_id INTEGER
) PARTITION BY RANGE (sale_date);

-- 파티션 테이블 생성
CREATE TABLE sales_2023 PARTITION OF sales
    FOR VALUES FROM ('2023-01-01') TO ('2024-01-01');

CREATE TABLE sales_2024 PARTITION OF sales
    FOR VALUES FROM ('2024-01-01') TO ('2025-01-01');

-- 해시 파티셔닝
CREATE TABLE user_activities (
    user_id INTEGER,
    activity_date DATE,
    activity_type VARCHAR(50)
) PARTITION BY HASH (user_id);

CREATE TABLE user_activities_0 PARTITION OF user_activities
    FOR VALUES WITH (MODULUS 4, REMAINDER 0);
```

### 9. 임시 테이블과 CTE

#### 9.1 임시 테이블
```sql
-- 세션 임시 테이블 (PostgreSQL)
CREATE TEMP TABLE temp_calculations (
    id SERIAL PRIMARY KEY,
    value DECIMAL(10,2),
    calculated_value DECIMAL(10,2)
);

-- 트랜잭션 임시 테이블
CREATE TEMP TABLE temp_report 
ON COMMIT DROP AS
SELECT 
    customer_id,
    COUNT(*) as order_count,
    SUM(total_amount) as total_spent
FROM orders
WHERE order_date >= CURRENT_DATE - INTERVAL '30 days'
GROUP BY customer_id;
```

## 실습 과제

### 과제 1: 이커머스 데이터베이스 설계
- 고객, 상품, 주문, 주문상세 테이블 설계
- 적절한 제약조건과 인덱스 적용
- 성능을 고려한 테이블 구조

### 과제 2: 뷰를 활용한 데이터 접근 계층
- 복잡한 조인을 숨기는 뷰 생성
- 보안을 위한 뷰 활용
- 머티리얼라이즈드 뷰를 통한 성능 최적화

### 과제 3: 대용량 데이터를 위한 파티셔닝
- 시간 기반 파티셔닝 설계
- 파티션 관리 자동화
- 파티션 프루닝 최적화

## 주요 개념 정리

### DDL의 핵심 원칙
1. **일관성**: 네이밍 컨벤션 준수
2. **무결성**: 적절한 제약조건 적용
3. **성능**: 인덱스와 파티셔닝 고려
4. **유지보수성**: 명확한 구조와 문서화

### 제약조건 설계 가이드
- PRIMARY KEY: 모든 테이블에 필수
- FOREIGN KEY: 참조 무결성 보장
- UNIQUE: 비즈니스 규칙 반영
- CHECK: 데이터 품질 보장
- NOT NULL: 필수 데이터 정의

### 인덱스 설계 전략
- WHERE 절에 자주 사용되는 컬럼
- JOIN 조건에 사용되는 컬럼
- ORDER BY에 사용되는 컬럼
- 복합 인덱스의 컬럼 순서 고려

## 다음 단계

Chapter 04에서는 JOIN의 모든 유형을 마스터하고, 복잡한 다중 테이블 조인과 성능 최적화 기법을 학습합니다.