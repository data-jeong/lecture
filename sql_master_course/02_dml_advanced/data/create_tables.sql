-- Chapter 02: DML 심화 실습용 테이블

-- 주문 테이블
DROP TABLE IF EXISTS order_items;
DROP TABLE IF EXISTS orders;
DROP TABLE IF EXISTS inventory;
DROP TABLE IF EXISTS accounts;
DROP TABLE IF EXISTS employees_backup;
DROP TABLE IF EXISTS product_changes;

-- 주문 테이블
CREATE TABLE orders (
    order_id INT PRIMARY KEY,
    customer_id INT,
    order_date DATE,
    status VARCHAR(20),
    total_amount DECIMAL(10, 2)
);

-- 주문 상세 테이블
CREATE TABLE order_items (
    item_id INT PRIMARY KEY,
    order_id INT,
    product_id INT,
    quantity INT,
    unit_price DECIMAL(10, 2),
    FOREIGN KEY (order_id) REFERENCES orders(order_id)
);

-- 재고 테이블
CREATE TABLE inventory (
    product_id INT PRIMARY KEY,
    quantity INT DEFAULT 0,
    last_updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 계좌 테이블 (트랜잭션 실습용)
CREATE TABLE accounts (
    account_id INT PRIMARY KEY,
    account_holder VARCHAR(100),
    balance DECIMAL(15, 2) DEFAULT 0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 직원 백업 테이블
CREATE TABLE employees_backup (
    employee_id INT,
    first_name VARCHAR(50),
    last_name VARCHAR(50),
    department VARCHAR(50),
    job_title VARCHAR(100),
    salary DECIMAL(10, 2),
    hire_date DATE,
    backup_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 상품 변경 이력 테이블
CREATE TABLE product_changes (
    change_id SERIAL PRIMARY KEY,
    product_id INT,
    old_price DECIMAL(10, 2),
    new_price DECIMAL(10, 2),
    changed_by VARCHAR(50),
    change_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 직원 테이블에 성과 평가 컬럼 추가 (이미 존재하는 경우를 위해)
ALTER TABLE employees ADD COLUMN IF NOT EXISTS performance_rating CHAR(1);
ALTER TABLE employees ADD COLUMN IF NOT EXISTS manager_id INT;
ALTER TABLE employees ADD COLUMN IF NOT EXISTS last_modified TIMESTAMP DEFAULT CURRENT_TIMESTAMP;

-- 고객 테이블에 연락처 정보 추가
ALTER TABLE customers ADD COLUMN IF NOT EXISTS phone VARCHAR(20);
ALTER TABLE customers ADD COLUMN IF NOT EXISTS email VARCHAR(100);

-- 샘플 데이터 삽입
-- 주문 데이터
INSERT INTO orders (order_id, customer_id, order_date, status, total_amount) VALUES
(1, 1, '2024-01-15', 'Completed', 1599.97),
(2, 2, '2024-01-16', 'Pending', 299.99),
(3, 3, '2024-01-17', 'Completed', 89.99),
(4, 1, '2024-01-18', 'Cancelled', 449.99),
(5, 4, '2024-01-19', 'Completed', 2099.95),
(6, 5, '2024-01-20', 'Processing', 159.98),
(7, 6, '2019-12-15', 'Completed', 799.99),
(8, 7, '2019-11-20', 'Completed', 399.99);

-- 주문 상세 데이터
INSERT INTO order_items (item_id, order_id, product_id, quantity, unit_price) VALUES
(1, 1, 1, 1, 1299.99),
(2, 1, 2, 10, 29.99),
(3, 2, 2, 10, 29.99),
(4, 3, 10, 1, 89.99),
(5, 4, 8, 1, 349.99),
(6, 4, 13, 4, 24.99),
(7, 5, 19, 5, 179.99),
(8, 5, 1, 1, 1299.99),
(9, 6, 14, 2, 69.99),
(10, 6, 16, 1, 19.99);

-- 재고 데이터
INSERT INTO inventory (product_id, quantity) VALUES
(1, 20),
(2, 140),
(3, 40),
(4, 20),
(5, 95),
(6, 75),
(7, 55),
(8, 30),
(9, 90),
(10, 5),
(11, 40),
(12, 70),
(13, 195),
(14, 3),
(15, 15),
(16, 245),
(17, 295),
(18, 115),
(19, 25),
(20, 90);

-- 계좌 데이터
INSERT INTO accounts (account_id, account_holder, balance) VALUES
(1, 'John Doe', 5000.00),
(2, 'Jane Smith', 10000.00),
(3, 'Bob Johnson', 2500.00),
(4, 'Alice Williams', 7500.00),
(5, 'Charlie Brown', 3000.00);

-- 직원 성과 평가 업데이트
UPDATE employees SET performance_rating = 
    CASE 
        WHEN salary >= 85000 THEN 'A'
        WHEN salary >= 70000 THEN 'B'
        WHEN salary >= 60000 THEN 'C'
        ELSE 'D'
    END;

-- 매니저 관계 설정
UPDATE employees SET manager_id = CASE
    WHEN employee_id IN (1, 4, 8, 16) THEN NULL  -- 최고 관리자
    WHEN department = 'Sales' AND employee_id != 1 THEN 1
    WHEN department = 'IT' AND employee_id != 3 THEN 3
    WHEN department = 'Marketing' AND employee_id != 2 THEN 2
    WHEN department = 'Finance' AND employee_id != 17 THEN 17
    WHEN department = 'HR' AND employee_id != 6 THEN 6
    ELSE NULL
END;

-- 고객 연락처 정보 업데이트
UPDATE customers SET 
    phone = CASE customer_id
        WHEN 1 THEN '+1-212-555-0101'
        WHEN 2 THEN '+44-20-555-0102'
        WHEN 3 THEN '+1-416-555-0103'
        WHEN 4 THEN '+49-30-555-0104'
        WHEN 5 THEN '+33-1-555-0105'
        ELSE '+1-555-' || LPAD(CAST(customer_id AS VARCHAR), 4, '0')
    END,
    email = LOWER(REPLACE(contact_name, ' ', '.')) || '@' || 
    CASE 
        WHEN customer_id <= 5 THEN 'company.com'
        ELSE 'email.com'
    END;