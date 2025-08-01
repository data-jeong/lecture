-- Chapter 04: JOIN Mastery - Sample Database Setup
-- 복잡한 JOIN 연습을 위한 전자상거래 데이터베이스

-- 기존 테이블 삭제
DROP TABLE IF EXISTS order_items CASCADE;
DROP TABLE IF EXISTS orders CASCADE;
DROP TABLE IF EXISTS product_reviews CASCADE;
DROP TABLE IF EXISTS products CASCADE;
DROP TABLE IF EXISTS categories CASCADE;
DROP TABLE IF EXISTS individual_customers CASCADE;
DROP TABLE IF EXISTS business_customers CASCADE;
DROP TABLE IF EXISTS suppliers CASCADE;
DROP TABLE IF EXISTS employees CASCADE;
DROP TABLE IF EXISTS departments CASCADE;
DROP TABLE IF EXISTS inventory_movements CASCADE;
DROP TABLE IF EXISTS daily_sales CASCADE;

-- 부서 테이블
CREATE TABLE departments (
    dept_id SERIAL PRIMARY KEY,
    dept_name VARCHAR(100) NOT NULL,
    manager_id INTEGER,
    budget DECIMAL(15,2),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 직원 테이블 (자기 참조 관계)
CREATE TABLE employees (
    employee_id SERIAL PRIMARY KEY,
    first_name VARCHAR(50) NOT NULL,
    last_name VARCHAR(50) NOT NULL,
    email VARCHAR(100) UNIQUE NOT NULL,
    job_title VARCHAR(100),
    salary DECIMAL(10,2),
    department_id INTEGER REFERENCES departments(dept_id),
    manager_id INTEGER REFERENCES employees(employee_id),
    hire_date DATE DEFAULT CURRENT_DATE,
    is_active BOOLEAN DEFAULT TRUE
);

-- 부서-관리자 관계 설정
ALTER TABLE departments 
ADD CONSTRAINT fk_dept_manager 
FOREIGN KEY (manager_id) REFERENCES employees(employee_id);

-- 공급업체 테이블
CREATE TABLE suppliers (
    supplier_id SERIAL PRIMARY KEY,
    supplier_name VARCHAR(255) NOT NULL,
    contact_person VARCHAR(100),
    email VARCHAR(100),
    phone VARCHAR(20),
    address TEXT,
    reliability_score INTEGER CHECK (reliability_score BETWEEN 0 AND 100),
    is_active BOOLEAN DEFAULT TRUE
);

-- 카테고리 테이블 (계층 구조)
CREATE TABLE categories (
    category_id SERIAL PRIMARY KEY,
    category_name VARCHAR(100) NOT NULL,
    parent_category_id INTEGER REFERENCES categories(category_id),
    description TEXT,
    is_active BOOLEAN DEFAULT TRUE
);

-- 상품 테이블
CREATE TABLE products (
    product_id SERIAL PRIMARY KEY,
    product_name VARCHAR(255) NOT NULL,
    category_id INTEGER REFERENCES categories(category_id),
    supplier_id INTEGER REFERENCES suppliers(supplier_id),
    price DECIMAL(10,2) NOT NULL,
    cost DECIMAL(10,2),
    current_stock INTEGER DEFAULT 0,
    reorder_level INTEGER DEFAULT 10,
    lead_time_days INTEGER DEFAULT 7,
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 개인 고객 테이블
CREATE TABLE individual_customers (
    customer_id SERIAL PRIMARY KEY,
    first_name VARCHAR(50) NOT NULL,
    last_name VARCHAR(50) NOT NULL,
    email VARCHAR(100) UNIQUE NOT NULL,
    phone VARCHAR(20),
    date_of_birth DATE,
    acquisition_date DATE DEFAULT CURRENT_DATE,
    is_active BOOLEAN DEFAULT TRUE
);

-- 기업 고객 테이블
CREATE TABLE business_customers (
    customer_id SERIAL PRIMARY KEY,
    company_name VARCHAR(255) NOT NULL,
    contact_person VARCHAR(100),
    contact_email VARCHAR(100),
    phone VARCHAR(20),
    tax_id VARCHAR(50),
    established_date DATE,
    acquisition_date DATE DEFAULT CURRENT_DATE,
    is_active BOOLEAN DEFAULT TRUE
);

-- 주문 테이블 (다형성 관계 - 개인/기업 고객)
CREATE TABLE orders (
    order_id SERIAL PRIMARY KEY,
    customer_id INTEGER NOT NULL,
    customer_type VARCHAR(20) CHECK (customer_type IN ('individual', 'business')),
    employee_id INTEGER REFERENCES employees(employee_id),
    order_date DATE DEFAULT CURRENT_DATE,
    total_amount DECIMAL(15,2) DEFAULT 0,
    status VARCHAR(20) DEFAULT 'pending',
    notes TEXT
);

-- 주문 상세 테이블  
CREATE TABLE order_items (
    order_id INTEGER REFERENCES orders(order_id),
    product_id INTEGER REFERENCES products(product_id),
    quantity INTEGER NOT NULL CHECK (quantity > 0),
    unit_price DECIMAL(10,2) NOT NULL,
    discount_rate DECIMAL(5,4) DEFAULT 0,
    line_total DECIMAL(15,2),
    PRIMARY KEY (order_id, product_id)
);

-- 상품 리뷰 테이블
CREATE TABLE product_reviews (
    review_id SERIAL PRIMARY KEY,
    product_id INTEGER REFERENCES products(product_id),
    customer_id INTEGER NOT NULL,
    customer_type VARCHAR(20) CHECK (customer_type IN ('individual', 'business')),
    rating INTEGER CHECK (rating BETWEEN 1 AND 5),
    review_text TEXT,
    review_date DATE DEFAULT CURRENT_DATE,
    is_verified BOOLEAN DEFAULT FALSE
);

-- 재고 이동 테이블
CREATE TABLE inventory_movements (
    movement_id SERIAL PRIMARY KEY,
    product_id INTEGER REFERENCES products(product_id),
    movement_type VARCHAR(20) CHECK (movement_type IN ('in', 'out', 'adjustment')),
    quantity INTEGER NOT NULL,
    reference_type VARCHAR(20), -- 'order', 'supplier', 'adjustment'
    reference_id INTEGER,
    movement_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    notes TEXT
);

-- 일별 매출 테이블 (집계 데이터)
CREATE TABLE daily_sales (
    sale_date DATE,
    category_id INTEGER REFERENCES categories(category_id),
    sales_amount DECIMAL(15,2),
    order_count INTEGER,
    PRIMARY KEY (sale_date, category_id)
);

-- 인덱스 생성
CREATE INDEX idx_employees_department ON employees(department_id);
CREATE INDEX idx_employees_manager ON employees(manager_id);
CREATE INDEX idx_products_category ON products(category_id);
CREATE INDEX idx_products_supplier ON products(supplier_id);
CREATE INDEX idx_orders_customer ON orders(customer_id, customer_type);
CREATE INDEX idx_orders_employee ON orders(employee_id);
CREATE INDEX idx_orders_date ON orders(order_date);
CREATE INDEX idx_order_items_product ON order_items(product_id);
CREATE INDEX idx_reviews_product ON product_reviews(product_id);
CREATE INDEX idx_reviews_customer ON product_reviews(customer_id, customer_type);
CREATE INDEX idx_inventory_product ON inventory_movements(product_id);
CREATE INDEX idx_daily_sales_date ON daily_sales(sale_date);

-- 샘플 데이터 삽입

-- 부서 데이터
INSERT INTO departments (dept_name, budget) VALUES
('Sales', 500000),
('Marketing', 300000),
('IT', 800000),
('HR', 200000),
('Operations', 600000);

-- 직원 데이터
INSERT INTO employees (first_name, last_name, email, job_title, salary, department_id) VALUES
('John', 'Smith', 'john.smith@company.com', 'Sales Director', 95000, 1),
('Sarah', 'Johnson', 'sarah.johnson@company.com', 'Marketing Manager', 75000, 2),
('Mike', 'Davis', 'mike.davis@company.com', 'IT Manager', 85000, 3),
('Lisa', 'Wilson', 'lisa.wilson@company.com', 'HR Manager', 70000, 4),
('Tom', 'Brown', 'tom.brown@company.com', 'Operations Manager', 80000, 5);

-- 관리자 관계 설정
UPDATE employees SET manager_id = 1 WHERE employee_id IN (2, 3, 4, 5);
UPDATE departments SET manager_id = 1 WHERE dept_id = 1;
UPDATE departments SET manager_id = 2 WHERE dept_id = 2;
UPDATE departments SET manager_id = 3 WHERE dept_id = 3;
UPDATE departments SET manager_id = 4 WHERE dept_id = 4;
UPDATE departments SET manager_id = 5 WHERE dept_id = 5;

-- 추가 직원들
INSERT INTO employees (first_name, last_name, email, job_title, salary, department_id, manager_id) VALUES
('Alice', 'Garcia', 'alice.garcia@company.com', 'Sales Rep', 55000, 1, 1),
('Bob', 'Miller', 'bob.miller@company.com', 'Sales Rep', 52000, 1, 1),
('Carol', 'Rodriguez', 'carol.rodriguez@company.com', 'Marketing Specialist', 48000, 2, 2),
('David', 'Martinez', 'david.martinez@company.com', 'Developer', 72000, 3, 3),
('Eva', 'Anderson', 'eva.anderson@company.com', 'HR Specialist', 45000, 4, 4);

-- 공급업체 데이터
INSERT INTO suppliers (supplier_name, contact_person, email, phone, reliability_score) VALUES
('Tech Solutions Inc', 'James Wong', 'james@techsolutions.com', '555-0101', 95),
('Global Electronics', 'Maria Santos', 'maria@globalelectronics.com', '555-0102', 88),
('Digital World', 'Peter Kim', 'peter@digitalworld.com', '555-0103', 92),
('Smart Devices Co', 'Anna Chen', 'anna@smartdevices.com', '555-0104', 85),
('Future Tech Ltd', 'Robert Lee', 'robert@futuretech.com', '555-0105', 78);

-- 카테고리 데이터 (계층 구조)
INSERT INTO categories (category_name, parent_category_id, description) VALUES
('Electronics', NULL, 'Electronic devices and accessories'),
('Computers', 1, 'Desktop and laptop computers'),
('Mobile Devices', 1, 'Smartphones and tablets'),
('Audio Equipment', 1, 'Headphones, speakers, and audio devices'),
('Gaming', 1, 'Gaming consoles and accessories'),
('Laptops', 2, 'Portable computers'),
('Desktops', 2, 'Desktop computers'),
('Smartphones', 3, 'Mobile phones'),
('Tablets', 3, 'Tablet computers');

-- 상품 데이터
INSERT INTO products (product_name, category_id, supplier_id, price, cost, current_stock, reorder_level) VALUES
('MacBook Pro 16"', 6, 1, 2499.99, 1800.00, 15, 5),
('Dell XPS 13', 6, 2, 1299.99, 950.00, 20, 8),
('iPhone 15 Pro', 8, 1, 1199.99, 850.00, 25, 10),
('Samsung Galaxy S24', 8, 3, 999.99, 720.00, 18, 8),
('iPad Air', 9, 1, 599.99, 420.00, 12, 6),
('Surface Pro 9', 9, 4, 1099.99, 800.00, 10, 5),
('Gaming Desktop', 7, 2, 1899.99, 1350.00, 8, 4),
('Sony WH-1000XM5', 4, 5, 399.99, 280.00, 30, 12),
('AirPods Pro', 4, 1, 249.99, 175.00, 40, 15),
('PlayStation 5', 5, 3, 499.99, 350.00, 5, 3);

-- 개인 고객 데이터
INSERT INTO individual_customers (first_name, last_name, email, phone, date_of_birth, acquisition_date) VALUES
('Jennifer', 'Davis', 'jennifer.davis@email.com', '555-1001', '1985-03-15', '2023-01-15'),
('Michael', 'Wilson', 'michael.wilson@email.com', '555-1002', '1990-07-22', '2023-02-20'),
('Emily', 'Taylor', 'emily.taylor@email.com', '555-1003', '1988-11-08', '2023-03-10'),
('Daniel', 'Anderson', 'daniel.anderson@email.com', '555-1004', '1992-05-30', '2023-04-05'),
('Jessica', 'Thomas', 'jessica.thomas@email.com', '555-1005', '1987-09-12', '2023-05-18');

-- 기업 고객 데이터
INSERT INTO business_customers (company_name, contact_person, contact_email, phone, tax_id, established_date, acquisition_date) VALUES
('ABC Corporation', 'Robert Johnson', 'robert@abccorp.com', '555-2001', 'TAX123456', '2010-01-01', '2023-01-20'),
('XYZ Technologies', 'Susan Brown', 'susan@xyztech.com', '555-2002', 'TAX234567', '2015-05-15', '2023-02-25'),
('Global Solutions', 'Mark Davis', 'mark@globalsolutions.com', '555-2003', 'TAX345678', '2018-03-20', '2023-03-15'),
('Innovation Labs', 'Rachel Green', 'rachel@innovationlabs.com', '555-2004', 'TAX456789', '2020-07-10', '2023-04-10'),
('Tech Startup', 'Kevin White', 'kevin@techstartup.com', '555-2005', 'TAX567890', '2022-01-01', '2023-05-22');

-- 주문 데이터
INSERT INTO orders (customer_id, customer_type, employee_id, order_date, total_amount, status) VALUES
(1, 'individual', 6, '2024-01-15', 2499.99, 'completed'),
(2, 'individual', 7, '2024-01-20', 1199.99, 'completed'),
(1, 'business', 6, '2024-01-25', 8999.96, 'completed'),
(3, 'individual', 6, '2024-02-01', 599.99, 'completed'),
(2, 'business', 7, '2024-02-05', 5499.95, 'completed'),
(4, 'individual', 6, '2024-02-10', 1299.99, 'pending'),
(3, 'business', 7, '2024-02-15', 12000.00, 'shipped'),
(5, 'individual', 6, '2024-02-20', 249.99, 'completed'),
(4, 'business', 7, '2024-02-25', 15999.84, 'processing'),
(1, 'individual', 6, '2024-03-01', 399.99, 'completed');

-- 주문 상세 데이터
INSERT INTO order_items (order_id, product_id, quantity, unit_price, discount_rate, line_total) VALUES
(1, 1, 1, 2499.99, 0.0, 2499.99),
(2, 3, 1, 1199.99, 0.0, 1199.99),
(3, 7, 3, 1899.99, 0.05, 5414.97),
(3, 1, 2, 2499.99, 0.1, 4499.98),
(4, 5, 1, 599.99, 0.0, 599.99),
(5, 2, 3, 1299.99, 0.0, 3899.97),
(5, 8, 2, 399.99, 0.05, 759.98),
(5, 9, 4, 249.99, 0.0, 999.96),
(6, 2, 1, 1299.99, 0.0, 1299.99),
(7, 1, 5, 2499.99, 0.15, 10624.96),
(7, 6, 2, 1099.99, 0.0, 2199.98),
(8, 9, 1, 249.99, 0.0, 249.99),
(9, 7, 8, 1899.99, 0.05, 14439.92),
(9, 10, 2, 499.99, 0.0, 999.98),
(10, 8, 1, 399.99, 0.0, 399.99);

-- 상품 리뷰 데이터
INSERT INTO product_reviews (product_id, customer_id, customer_type, rating, review_text, is_verified) VALUES
(1, 1, 'individual', 5, 'Excellent laptop, very fast and reliable!', TRUE),
(3, 2, 'individual', 4, 'Great phone, camera quality is amazing.', TRUE),
(1, 1, 'business', 5, 'Perfect for our development team.', TRUE),
(5, 3, 'individual', 4, 'Good tablet for work and entertainment.', TRUE),
(2, 4, 'individual', 5, 'Best laptop I ever owned!', FALSE),
(8, 5, 'individual', 5, 'Amazing sound quality!', TRUE),
(7, 3, 'business', 4, 'Good gaming performance.', TRUE),
(9, 1, 'individual', 4, 'Great for music and calls.', TRUE);

-- 재고 이동 데이터
INSERT INTO inventory_movements (product_id, movement_type, quantity, reference_type, reference_id, movement_date) VALUES
(1, 'out', 1, 'order', 1, '2024-01-15 10:00:00'),
(3, 'out', 1, 'order', 2, '2024-01-20 11:00:00'),
(7, 'out', 3, 'order', 3, '2024-01-25 09:30:00'),
(1, 'out', 2, 'order', 3, '2024-01-25 09:30:00'),
(5, 'out', 1, 'order', 4, '2024-02-01 14:15:00'),
(2, 'out', 3, 'order', 5, '2024-02-05 16:20:00'),
(8, 'out', 2, 'order', 5, '2024-02-05 16:20:00'),
(9, 'out', 4, 'order', 5, '2024-02-05 16:20:00'),
(1, 'in', 10, 'supplier', 1, '2024-02-10 08:00:00'),
(3, 'in', 15, 'supplier', 1, '2024-02-12 09:00:00');

-- 일별 매출 데이터
INSERT INTO daily_sales (sale_date, category_id, sales_amount, order_count) VALUES
('2024-01-15', 6, 2499.99, 1),
('2024-01-20', 8, 1199.99, 1),
('2024-01-25', 7, 5414.97, 1),
('2024-01-25', 6, 4499.98, 1),
('2024-02-01', 9, 599.99, 1),
('2024-02-05', 6, 3899.97, 1),
('2024-02-05', 4, 1759.94, 2),
('2024-02-10', 6, 1299.99, 1),
('2024-02-15', 6, 10624.96, 1),
('2024-02-15', 9, 2199.98, 1),
('2024-02-20', 4, 249.99, 1),
('2024-02-25', 7, 14439.92, 1),
('2024-02-25', 5, 999.98, 1),
('2024-03-01', 4, 399.99, 1);

-- 뷰 생성: 통합 고객 정보
CREATE VIEW unified_customers AS
SELECT 
    'individual' AS customer_type,
    customer_id,
    first_name || ' ' || last_name AS customer_name,
    email,
    phone,
    acquisition_date,
    is_active
FROM individual_customers
WHERE is_active = TRUE

UNION ALL

SELECT 
    'business' AS customer_type,
    customer_id,
    company_name AS customer_name,
    contact_email AS email,
    phone,
    acquisition_date,
    is_active
FROM business_customers
WHERE is_active = TRUE;

-- 완료 메시지
SELECT 'Chapter 04 JOIN Database Setup Complete!' AS status;