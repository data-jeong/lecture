-- Chapter 03: DDL and Table Design - Sample Database Setup
-- 이커머스 시스템을 위한 완전한 데이터베이스 스키마

-- 기존 테이블 삭제 (의존성 순서 고려)
DROP TABLE IF EXISTS order_items CASCADE;
DROP TABLE IF EXISTS orders CASCADE;
DROP TABLE IF EXISTS product_reviews CASCADE;
DROP TABLE IF EXISTS products CASCADE;
DROP TABLE IF EXISTS categories CASCADE;
DROP TABLE IF EXISTS customers CASCADE;
DROP TABLE IF EXISTS addresses CASCADE;
DROP TABLE IF EXISTS employees CASCADE;
DROP TABLE IF EXISTS departments CASCADE;
DROP TABLE IF EXISTS suppliers CASCADE;

-- 시퀀스 삭제 (PostgreSQL)
DROP SEQUENCE IF EXISTS customer_number_seq;
DROP SEQUENCE IF EXISTS order_number_seq;

-- 1. 부서 테이블
CREATE TABLE departments (
    dept_id SERIAL PRIMARY KEY,
    dept_name VARCHAR(100) NOT NULL UNIQUE,
    description TEXT,
    manager_id INTEGER,
    budget DECIMAL(15,2) CHECK (budget >= 0),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    is_active BOOLEAN DEFAULT TRUE
);

-- 2. 직원 테이블
CREATE TABLE employees (
    employee_id SERIAL PRIMARY KEY,
    employee_number VARCHAR(20) UNIQUE NOT NULL,
    first_name VARCHAR(50) NOT NULL,
    last_name VARCHAR(50) NOT NULL,
    email VARCHAR(100) UNIQUE NOT NULL,
    phone VARCHAR(20),
    hire_date DATE NOT NULL DEFAULT CURRENT_DATE,
    job_title VARCHAR(100) NOT NULL,
    salary DECIMAL(10,2) CHECK (salary > 0),
    commission_rate DECIMAL(5,4) DEFAULT 0.00 CHECK (commission_rate >= 0 AND commission_rate <= 1),
    department_id INTEGER,
    manager_id INTEGER,
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    -- 제약조건
    CONSTRAINT fk_employees_dept 
        FOREIGN KEY (department_id) REFERENCES departments(dept_id),
    CONSTRAINT fk_employees_manager 
        FOREIGN KEY (manager_id) REFERENCES employees(employee_id),
    CONSTRAINT check_hire_date 
        CHECK (hire_date <= CURRENT_DATE),
    CONSTRAINT check_salary_range 
        CHECK (salary BETWEEN 30000 AND 500000)
);

-- 부서 테이블의 manager_id 외래키 설정 (순환 참조 해결)
ALTER TABLE departments 
ADD CONSTRAINT fk_departments_manager 
    FOREIGN KEY (manager_id) REFERENCES employees(employee_id);

-- 3. 공급업체 테이블
CREATE TABLE suppliers (
    supplier_id SERIAL PRIMARY KEY,
    company_name VARCHAR(255) NOT NULL,
    contact_name VARCHAR(100),
    contact_title VARCHAR(50),
    address TEXT,
    city VARCHAR(50),
    postal_code VARCHAR(20),
    country VARCHAR(50) DEFAULT 'South Korea',
    phone VARCHAR(20),
    fax VARCHAR(20),
    email VARCHAR(100),
    website VARCHAR(255),
    rating INTEGER CHECK (rating BETWEEN 1 AND 5),
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 4. 카테고리 테이블 (계층 구조)
CREATE TABLE categories (
    category_id SERIAL PRIMARY KEY,
    category_name VARCHAR(100) NOT NULL,
    parent_category_id INTEGER,
    description TEXT,
    image_url VARCHAR(500),
    sort_order INTEGER DEFAULT 0,
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    -- 제약조건
    CONSTRAINT fk_categories_parent 
        FOREIGN KEY (parent_category_id) REFERENCES categories(category_id),
    CONSTRAINT uq_category_parent_name 
        UNIQUE (parent_category_id, category_name)
);

-- 5. 상품 테이블
CREATE TABLE products (
    product_id SERIAL PRIMARY KEY,
    sku VARCHAR(50) UNIQUE NOT NULL,
    product_name VARCHAR(255) NOT NULL,
    description TEXT,
    category_id INTEGER NOT NULL,
    supplier_id INTEGER,
    unit_price DECIMAL(10,2) NOT NULL CHECK (unit_price >= 0),
    units_in_stock INTEGER DEFAULT 0 CHECK (units_in_stock >= 0),
    units_on_order INTEGER DEFAULT 0 CHECK (units_on_order >= 0),
    reorder_level INTEGER DEFAULT 0 CHECK (reorder_level >= 0),
    discontinued BOOLEAN DEFAULT FALSE,
    weight REAL CHECK (weight > 0),
    dimensions VARCHAR(50),
    color VARCHAR(30),
    size VARCHAR(20),
    warranty_months INTEGER DEFAULT 12 CHECK (warranty_months >= 0),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    -- 제약조건
    CONSTRAINT fk_products_category 
        FOREIGN KEY (category_id) REFERENCES categories(category_id),
    CONSTRAINT fk_products_supplier 
        FOREIGN KEY (supplier_id) REFERENCES suppliers(supplier_id),
    CONSTRAINT check_stock_logic 
        CHECK (units_in_stock + units_on_order >= reorder_level)
);

-- 6. 주소 테이블
CREATE TABLE addresses (
    address_id SERIAL PRIMARY KEY,
    address_type VARCHAR(20) NOT NULL CHECK (address_type IN ('billing', 'shipping')),
    first_name VARCHAR(50) NOT NULL,
    last_name VARCHAR(50) NOT NULL,
    company VARCHAR(100),
    address_line1 VARCHAR(255) NOT NULL,
    address_line2 VARCHAR(255),
    city VARCHAR(50) NOT NULL,
    state_province VARCHAR(50),
    postal_code VARCHAR(20) NOT NULL,
    country VARCHAR(50) NOT NULL DEFAULT 'South Korea',
    is_default BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 7. 고객 테이블
CREATE SEQUENCE customer_number_seq START WITH 10000 INCREMENT BY 1;

CREATE TABLE customers (
    customer_id SERIAL PRIMARY KEY,
    customer_number VARCHAR(20) UNIQUE DEFAULT 'CUST' || nextval('customer_number_seq'),
    company_name VARCHAR(255),
    contact_name VARCHAR(100) NOT NULL,
    contact_title VARCHAR(50),
    email VARCHAR(100) UNIQUE NOT NULL,
    phone VARCHAR(20),
    fax VARCHAR(20),
    date_of_birth DATE,
    gender CHAR(1) CHECK (gender IN ('M', 'F')),
    billing_address_id INTEGER,
    shipping_address_id INTEGER,
    credit_limit DECIMAL(15,2) DEFAULT 10000.00 CHECK (credit_limit >= 0),
    current_balance DECIMAL(15,2) DEFAULT 0.00,
    customer_since DATE DEFAULT CURRENT_DATE,
    last_order_date DATE,
    total_orders INTEGER DEFAULT 0 CHECK (total_orders >= 0),
    is_active BOOLEAN DEFAULT TRUE,
    newsletter_opt_in BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    -- 제약조건
    CONSTRAINT fk_customers_billing 
        FOREIGN KEY (billing_address_id) REFERENCES addresses(address_id),
    CONSTRAINT fk_customers_shipping 
        FOREIGN KEY (shipping_address_id) REFERENCES addresses(address_id),
    CONSTRAINT check_birth_date 
        CHECK (date_of_birth <= CURRENT_DATE - INTERVAL '13 years'),
    CONSTRAINT check_balance_limit 
        CHECK (current_balance <= credit_limit)
);

-- 8. 주문 테이블
CREATE SEQUENCE order_number_seq START WITH 100000 INCREMENT BY 1;

CREATE TABLE orders (
    order_id SERIAL PRIMARY KEY,
    order_number VARCHAR(20) UNIQUE DEFAULT 'ORD' || nextval('order_number_seq'),
    customer_id INTEGER NOT NULL,
    employee_id INTEGER,
    order_date DATE NOT NULL DEFAULT CURRENT_DATE,
    required_date DATE,
    shipped_date DATE,
    ship_via VARCHAR(50),
    freight DECIMAL(10,2) DEFAULT 0.00 CHECK (freight >= 0),
    ship_name VARCHAR(100),
    ship_address TEXT,
    ship_city VARCHAR(50),
    ship_postal_code VARCHAR(20),
    ship_country VARCHAR(50),
    order_status VARCHAR(20) DEFAULT 'pending' CHECK (
        order_status IN ('pending', 'processing', 'shipped', 'delivered', 'cancelled', 'returned')
    ),
    payment_method VARCHAR(30),
    payment_status VARCHAR(20) DEFAULT 'pending' CHECK (
        payment_status IN ('pending', 'paid', 'failed', 'refunded')
    ),
    subtotal DECIMAL(15,2) DEFAULT 0.00 CHECK (subtotal >= 0),
    tax_amount DECIMAL(15,2) DEFAULT 0.00 CHECK (tax_amount >= 0),
    discount_amount DECIMAL(15,2) DEFAULT 0.00 CHECK (discount_amount >= 0),
    total_amount DECIMAL(15,2) DEFAULT 0.00 CHECK (total_amount >= 0),
    notes TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    -- 제약조건
    CONSTRAINT fk_orders_customer 
        FOREIGN KEY (customer_id) REFERENCES customers(customer_id),
    CONSTRAINT fk_orders_employee 
        FOREIGN KEY (employee_id) REFERENCES employees(employee_id),
    CONSTRAINT check_order_dates 
        CHECK (shipped_date IS NULL OR shipped_date >= order_date),
    CONSTRAINT check_required_date 
        CHECK (required_date IS NULL OR required_date >= order_date),
    CONSTRAINT check_total_calculation 
        CHECK (total_amount = subtotal + tax_amount - discount_amount)
);

-- 9. 주문 상세 테이블
CREATE TABLE order_items (
    order_id INTEGER,
    product_id INTEGER,
    quantity INTEGER NOT NULL CHECK (quantity > 0),
    unit_price DECIMAL(10,2) NOT NULL CHECK (unit_price >= 0),
    discount_rate DECIMAL(5,4) DEFAULT 0.00 CHECK (discount_rate >= 0 AND discount_rate < 1),
    line_total DECIMAL(15,2) GENERATED ALWAYS AS (
        quantity * unit_price * (1 - discount_rate)
    ) STORED,
    
    -- 복합 기본키
    PRIMARY KEY (order_id, product_id),
    
    -- 제약조건
    CONSTRAINT fk_order_items_order 
        FOREIGN KEY (order_id) REFERENCES orders(order_id) ON DELETE CASCADE,
    CONSTRAINT fk_order_items_product 
        FOREIGN KEY (product_id) REFERENCES products(product_id)
);

-- 10. 상품 리뷰 테이블
CREATE TABLE product_reviews (
    review_id SERIAL PRIMARY KEY,
    product_id INTEGER NOT NULL,
    customer_id INTEGER NOT NULL,
    rating INTEGER NOT NULL CHECK (rating BETWEEN 1 AND 5),
    title VARCHAR(200),
    review_text TEXT,
    helpful_votes INTEGER DEFAULT 0 CHECK (helpful_votes >= 0),
    verified_purchase BOOLEAN DEFAULT FALSE,
    review_date DATE DEFAULT CURRENT_DATE,
    is_approved BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    -- 제약조건
    CONSTRAINT fk_reviews_product 
        FOREIGN KEY (product_id) REFERENCES products(product_id),
    CONSTRAINT fk_reviews_customer 
        FOREIGN KEY (customer_id) REFERENCES customers(customer_id),
    CONSTRAINT uq_customer_product_review 
        UNIQUE (customer_id, product_id)
);

-- 인덱스 생성
-- 성능 최적화를 위한 주요 인덱스들

-- 직원 테이블 인덱스
CREATE INDEX idx_employees_dept ON employees (department_id);
CREATE INDEX idx_employees_manager ON employees (manager_id);
CREATE INDEX idx_employees_email ON employees (email);
CREATE INDEX idx_employees_active ON employees (is_active);

-- 상품 테이블 인덱스
CREATE INDEX idx_products_category ON products (category_id);
CREATE INDEX idx_products_supplier ON products (supplier_id);
CREATE INDEX idx_products_sku ON products (sku);
CREATE INDEX idx_products_name ON products USING GIN (to_tsvector('english', product_name));
CREATE INDEX idx_products_price ON products (unit_price);
CREATE INDEX idx_products_stock ON products (units_in_stock);

-- 고객 테이블 인덱스
CREATE INDEX idx_customers_email ON customers (email);
CREATE INDEX idx_customers_company ON customers (company_name);
CREATE INDEX idx_customers_active ON customers (is_active);
CREATE INDEX idx_customers_since ON customers (customer_since);

-- 주문 테이블 인덱스
CREATE INDEX idx_orders_customer ON orders (customer_id);
CREATE INDEX idx_orders_employee ON orders (employee_id);
CREATE INDEX idx_orders_date ON orders (order_date);
CREATE INDEX idx_orders_status ON orders (order_status);
CREATE INDEX idx_orders_shipped ON orders (shipped_date);
CREATE INDEX idx_orders_customer_date ON orders (customer_id, order_date);

-- 주문 상세 테이블 인덱스
CREATE INDEX idx_order_items_product ON order_items (product_id);

-- 리뷰 테이블 인덱스
CREATE INDEX idx_reviews_product ON product_reviews (product_id);
CREATE INDEX idx_reviews_customer ON product_reviews (customer_id);
CREATE INDEX idx_reviews_rating ON product_reviews (rating);
CREATE INDEX idx_reviews_approved ON product_reviews (is_approved);

-- 카테고리 계층 인덱스
CREATE INDEX idx_categories_parent ON categories (parent_category_id);

-- 뷰 생성
-- 자주 사용되는 조인을 단순화하는 뷰들

-- 직원 상세 정보 뷰
CREATE VIEW employee_details AS
SELECT 
    e.employee_id,
    e.employee_number,
    e.first_name || ' ' || e.last_name AS full_name,
    e.email,
    e.phone,
    e.job_title,
    e.salary,
    d.dept_name,
    m.first_name || ' ' || m.last_name AS manager_name,
    e.hire_date,
    EXTRACT(YEAR FROM AGE(CURRENT_DATE, e.hire_date)) AS years_of_service,
    e.is_active
FROM employees e
LEFT JOIN departments d ON e.department_id = d.dept_id
LEFT JOIN employees m ON e.manager_id = m.employee_id;

-- 상품 상세 정보 뷰
CREATE VIEW product_catalog AS
SELECT 
    p.product_id,
    p.sku,
    p.product_name,
    p.description,
    c.category_name,
    s.company_name AS supplier_name,
    p.unit_price,
    p.units_in_stock,
    p.discontinued,
    CASE 
        WHEN p.units_in_stock = 0 THEN 'Out of Stock'
        WHEN p.units_in_stock <= p.reorder_level THEN 'Low Stock'
        ELSE 'In Stock'
    END AS stock_status,
    COALESCE(AVG(pr.rating), 0) AS avg_rating,
    COUNT(pr.review_id) AS review_count
FROM products p
LEFT JOIN categories c ON p.category_id = c.category_id
LEFT JOIN suppliers s ON p.supplier_id = s.supplier_id
LEFT JOIN product_reviews pr ON p.product_id = pr.product_id AND pr.is_approved = TRUE
GROUP BY p.product_id, p.sku, p.product_name, p.description, 
         c.category_name, s.company_name, p.unit_price, p.units_in_stock, 
         p.discontinued, p.reorder_level;

-- 고객 요약 뷰
CREATE VIEW customer_summary AS
SELECT 
    c.customer_id,
    c.customer_number,
    c.contact_name,
    c.company_name,
    c.email,
    c.customer_since,
    c.total_orders,
    c.current_balance,
    c.credit_limit,
    COALESCE(SUM(o.total_amount), 0) AS total_spent,
    COUNT(o.order_id) AS completed_orders,
    MAX(o.order_date) AS last_order_date,
    CASE 
        WHEN MAX(o.order_date) >= CURRENT_DATE - INTERVAL '30 days' THEN 'Active'
        WHEN MAX(o.order_date) >= CURRENT_DATE - INTERVAL '90 days' THEN 'Recent'
        WHEN MAX(o.order_date) >= CURRENT_DATE - INTERVAL '365 days' THEN 'Inactive'
        ELSE 'Dormant'
    END AS customer_status
FROM customers c
LEFT JOIN orders o ON c.customer_id = o.customer_id 
    AND o.order_status NOT IN ('cancelled', 'returned')
GROUP BY c.customer_id, c.customer_number, c.contact_name, c.company_name, 
         c.email, c.customer_since, c.total_orders, c.current_balance, c.credit_limit;

-- 월별 매출 머티리얼라이즈드 뷰
CREATE MATERIALIZED VIEW monthly_sales_summary AS
SELECT 
    DATE_TRUNC('month', o.order_date) AS month,
    COUNT(DISTINCT o.order_id) AS total_orders,
    COUNT(DISTINCT o.customer_id) AS unique_customers,
    SUM(o.total_amount) AS total_revenue,
    AVG(o.total_amount) AS avg_order_value,
    SUM(oi.quantity) AS total_items_sold
FROM orders o
JOIN order_items oi ON o.order_id = oi.order_id
WHERE o.order_status NOT IN ('cancelled', 'returned')
GROUP BY DATE_TRUNC('month', o.order_date)
ORDER BY month;

-- 트리거 함수 (updated_at 자동 업데이트)
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ language 'plpgsql';

-- 트리거 생성
CREATE TRIGGER update_employees_updated_at 
    BEFORE UPDATE ON employees 
    FOR EACH ROW 
    EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_customers_updated_at 
    BEFORE UPDATE ON customers 
    FOR EACH ROW 
    EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_products_updated_at 
    BEFORE UPDATE ON products 
    FOR EACH ROW 
    EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_orders_updated_at 
    BEFORE UPDATE ON orders 
    FOR EACH ROW 
    EXECUTE FUNCTION update_updated_at_column();

-- 샘플 데이터 삽입
INSERT INTO departments (dept_name, description, budget) VALUES
('Sales', '영업 부서', 500000.00),
('Marketing', '마케팅 부서', 300000.00),
('IT', '정보기술 부서', 800000.00),
('HR', '인사 부서', 200000.00),
('Finance', '재무 부서', 150000.00);

INSERT INTO employees (employee_number, first_name, last_name, email, job_title, salary, department_id) VALUES
('EMP001', '김', '철수', 'kim.cs@company.com', 'Sales Manager', 80000, 1),
('EMP002', '이', '영희', 'lee.yh@company.com', 'Marketing Specialist', 60000, 2),
('EMP003', '박', '민수', 'park.ms@company.com', 'Software Engineer', 90000, 3),
('EMP004', '정', '지은', 'jung.je@company.com', 'HR Manager', 75000, 4),
('EMP005', '최', '동준', 'choi.dj@company.com', 'Financial Analyst', 70000, 5);

-- 관리자 정보 업데이트
UPDATE departments SET manager_id = 1 WHERE dept_name = 'Sales';
UPDATE departments SET manager_id = 2 WHERE dept_name = 'Marketing';
UPDATE departments SET manager_id = 3 WHERE dept_name = 'IT';
UPDATE departments SET manager_id = 4 WHERE dept_name = 'HR';
UPDATE departments SET manager_id = 5 WHERE dept_name = 'Finance';

-- 머티리얼라이즈드 뷰 새로고침을 위한 함수
CREATE OR REPLACE FUNCTION refresh_monthly_sales()
RETURNS void AS $$
BEGIN
    REFRESH MATERIALIZED VIEW monthly_sales_summary;
END;
$$ LANGUAGE plpgsql;

-- 설정 완료 메시지
SELECT 'Chapter 03 DDL Database Setup Complete!' AS status;