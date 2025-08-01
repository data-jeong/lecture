-- Chapter 09: 데이터베이스 설계와 정규화 실습용 데이터베이스

-- ===========================
-- 1. 비정규화된 테이블 (정규화 실습용)
-- ===========================

-- 비정규화된 주문 테이블 (1NF 위반)
DROP TABLE IF EXISTS denormalized_orders;
CREATE TABLE denormalized_orders (
    order_id INT PRIMARY KEY,
    customer_name VARCHAR(100),
    customer_email VARCHAR(100),
    customer_phone VARCHAR(20),
    customer_address VARCHAR(500),
    order_date DATE,
    products VARCHAR(1000), -- 콤마로 구분된 상품 목록
    quantities VARCHAR(500), -- 콤마로 구분된 수량
    prices VARCHAR(500), -- 콤마로 구분된 가격
    total_amount DECIMAL(10, 2)
);

-- 부분적으로 정규화된 테이블 (2NF 위반)
DROP TABLE IF EXISTS partial_normalized_orders;
CREATE TABLE partial_normalized_orders (
    order_id INT,
    product_id INT,
    customer_id INT,
    customer_name VARCHAR(100),
    customer_email VARCHAR(100),
    product_name VARCHAR(200),
    product_category VARCHAR(50),
    quantity INT,
    unit_price DECIMAL(10, 2),
    order_date DATE,
    PRIMARY KEY (order_id, product_id)
);

-- ===========================
-- 2. 온라인 서점 시스템 (정규화된 설계)
-- ===========================

-- 저자 테이블
DROP TABLE IF EXISTS authors;
CREATE TABLE authors (
    author_id INT PRIMARY KEY AUTO_INCREMENT,
    first_name VARCHAR(50) NOT NULL,
    last_name VARCHAR(50) NOT NULL,
    birth_date DATE,
    nationality VARCHAR(50),
    biography TEXT
);

-- 출판사 테이블
DROP TABLE IF EXISTS publishers;
CREATE TABLE publishers (
    publisher_id INT PRIMARY KEY AUTO_INCREMENT,
    publisher_name VARCHAR(200) NOT NULL,
    country VARCHAR(50),
    founded_year INT,
    website VARCHAR(200)
);

-- 도서 테이블
DROP TABLE IF EXISTS books;
CREATE TABLE books (
    isbn VARCHAR(13) PRIMARY KEY,
    title VARCHAR(300) NOT NULL,
    publisher_id INT,
    publication_date DATE,
    pages INT,
    price DECIMAL(10, 2),
    stock_quantity INT DEFAULT 0,
    FOREIGN KEY (publisher_id) REFERENCES publishers(publisher_id)
);

-- 도서-저자 다대다 관계
DROP TABLE IF EXISTS book_authors;
CREATE TABLE book_authors (
    isbn VARCHAR(13),
    author_id INT,
    author_order INT DEFAULT 1,
    PRIMARY KEY (isbn, author_id),
    FOREIGN KEY (isbn) REFERENCES books(isbn),
    FOREIGN KEY (author_id) REFERENCES authors(author_id)
);

-- 카테고리 테이블
DROP TABLE IF EXISTS categories;
CREATE TABLE categories (
    category_id INT PRIMARY KEY AUTO_INCREMENT,
    category_name VARCHAR(100) NOT NULL,
    parent_category_id INT,
    FOREIGN KEY (parent_category_id) REFERENCES categories(category_id)
);

-- 도서-카테고리 다대다 관계
DROP TABLE IF EXISTS book_categories;
CREATE TABLE book_categories (
    isbn VARCHAR(13),
    category_id INT,
    PRIMARY KEY (isbn, category_id),
    FOREIGN KEY (isbn) REFERENCES books(isbn),
    FOREIGN KEY (category_id) REFERENCES categories(category_id)
);

-- 고객 테이블
DROP TABLE IF EXISTS bookstore_customers;
CREATE TABLE bookstore_customers (
    customer_id INT PRIMARY KEY AUTO_INCREMENT,
    email VARCHAR(100) UNIQUE NOT NULL,
    first_name VARCHAR(50),
    last_name VARCHAR(50),
    registration_date DATE,
    customer_type VARCHAR(20) DEFAULT 'REGULAR'
);

-- 주소 테이블 (고객과 1:N 관계)
DROP TABLE IF EXISTS customer_addresses;
CREATE TABLE customer_addresses (
    address_id INT PRIMARY KEY AUTO_INCREMENT,
    customer_id INT,
    address_type VARCHAR(20), -- BILLING, SHIPPING
    street_address VARCHAR(200),
    city VARCHAR(50),
    state_province VARCHAR(50),
    postal_code VARCHAR(20),
    country VARCHAR(50),
    is_default BOOLEAN DEFAULT FALSE,
    FOREIGN KEY (customer_id) REFERENCES bookstore_customers(customer_id)
);

-- 주문 테이블
DROP TABLE IF EXISTS bookstore_orders;
CREATE TABLE bookstore_orders (
    order_id INT PRIMARY KEY AUTO_INCREMENT,
    customer_id INT,
    order_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    shipping_address_id INT,
    order_status VARCHAR(20) DEFAULT 'PENDING',
    total_amount DECIMAL(10, 2),
    FOREIGN KEY (customer_id) REFERENCES bookstore_customers(customer_id),
    FOREIGN KEY (shipping_address_id) REFERENCES customer_addresses(address_id)
);

-- 주문 상세 테이블
DROP TABLE IF EXISTS order_details;
CREATE TABLE order_details (
    order_id INT,
    isbn VARCHAR(13),
    quantity INT,
    unit_price DECIMAL(10, 2),
    discount_percent DECIMAL(5, 2) DEFAULT 0,
    PRIMARY KEY (order_id, isbn),
    FOREIGN KEY (order_id) REFERENCES bookstore_orders(order_id),
    FOREIGN KEY (isbn) REFERENCES books(isbn)
);

-- ===========================
-- 3. 병원 관리 시스템 (복잡한 관계)
-- ===========================

-- 의사 테이블
DROP TABLE IF EXISTS doctors;
CREATE TABLE doctors (
    doctor_id INT PRIMARY KEY AUTO_INCREMENT,
    license_number VARCHAR(50) UNIQUE NOT NULL,
    first_name VARCHAR(50),
    last_name VARCHAR(50),
    specialization VARCHAR(100),
    hire_date DATE
);

-- 환자 테이블
DROP TABLE IF EXISTS patients;
CREATE TABLE patients (
    patient_id INT PRIMARY KEY AUTO_INCREMENT,
    medical_record_number VARCHAR(50) UNIQUE NOT NULL,
    first_name VARCHAR(50),
    last_name VARCHAR(50),
    birth_date DATE,
    blood_type VARCHAR(5)
);

-- 진료 예약 테이블
DROP TABLE IF EXISTS appointments;
CREATE TABLE appointments (
    appointment_id INT PRIMARY KEY AUTO_INCREMENT,
    patient_id INT,
    doctor_id INT,
    appointment_datetime TIMESTAMP,
    duration_minutes INT DEFAULT 30,
    status VARCHAR(20) DEFAULT 'SCHEDULED',
    FOREIGN KEY (patient_id) REFERENCES patients(patient_id),
    FOREIGN KEY (doctor_id) REFERENCES doctors(doctor_id)
);

-- 진료 기록 테이블
DROP TABLE IF EXISTS medical_records;
CREATE TABLE medical_records (
    record_id INT PRIMARY KEY AUTO_INCREMENT,
    appointment_id INT,
    diagnosis TEXT,
    treatment_plan TEXT,
    notes TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (appointment_id) REFERENCES appointments(appointment_id)
);

-- 처방전 테이블
DROP TABLE IF EXISTS prescriptions;
CREATE TABLE prescriptions (
    prescription_id INT PRIMARY KEY AUTO_INCREMENT,
    record_id INT,
    medication_name VARCHAR(200),
    dosage VARCHAR(100),
    frequency VARCHAR(100),
    duration_days INT,
    FOREIGN KEY (record_id) REFERENCES medical_records(record_id)
);

-- ===========================
-- 4. 샘플 데이터
-- ===========================

-- 비정규화된 주문 데이터
INSERT INTO denormalized_orders VALUES
(1, 'John Doe', 'john@email.com', '123-456-7890', '123 Main St, City', '2024-01-15', 
 'Laptop,Mouse,Keyboard', '1,2,1', '999.99,29.99,79.99', 1139.96),
(2, 'Jane Smith', 'jane@email.com', '098-765-4321', '456 Oak Ave, Town', '2024-01-16',
 'Monitor,Cable', '2,3', '299.99,19.99', 659.95);

-- 저자 데이터
INSERT INTO authors (first_name, last_name, birth_date, nationality) VALUES
('George', 'Orwell', '1903-06-25', 'British'),
('Jane', 'Austen', '1775-12-16', 'British'),
('Mark', 'Twain', '1835-11-30', 'American'),
('Haruki', 'Murakami', '1949-01-12', 'Japanese'),
('Margaret', 'Atwood', '1939-11-18', 'Canadian');

-- 출판사 데이터
INSERT INTO publishers (publisher_name, country, founded_year) VALUES
('Penguin Random House', 'USA', 1927),
('HarperCollins', 'USA', 1989),
('Macmillan', 'UK', 1843),
('Simon & Schuster', 'USA', 1924),
('Hachette', 'France', 1826);

-- 카테고리 데이터
INSERT INTO categories (category_name, parent_category_id) VALUES
('Fiction', NULL),
('Non-Fiction', NULL),
('Science Fiction', 1),
('Romance', 1),
('Biography', 2),
('Self-Help', 2),
('Classic Literature', 1),
('Modern Literature', 1);

-- 의사 데이터
INSERT INTO doctors (license_number, first_name, last_name, specialization, hire_date) VALUES
('DOC001', 'Sarah', 'Johnson', 'Cardiology', '2015-03-15'),
('DOC002', 'Michael', 'Chen', 'Pediatrics', '2018-07-01'),
('DOC003', 'Emily', 'Williams', 'Neurology', '2016-09-20'),
('DOC004', 'Robert', 'Davis', 'Orthopedics', '2019-01-10'),
('DOC005', 'Lisa', 'Anderson', 'General Practice', '2017-05-05');

-- 환자 데이터
INSERT INTO patients (medical_record_number, first_name, last_name, birth_date, blood_type) VALUES
('MRN001', 'Alice', 'Brown', '1985-04-12', 'A+'),
('MRN002', 'Bob', 'Taylor', '1972-08-23', 'O-'),
('MRN003', 'Carol', 'Wilson', '1990-12-05', 'B+'),
('MRN004', 'David', 'Moore', '1968-03-18', 'AB+'),
('MRN005', 'Eva', 'Martin', '1995-07-30', 'A-');

-- 뷰 생성: 정규화 전후 비교
CREATE OR REPLACE VIEW v_denormalized_issues AS
SELECT 
    'Repeating Groups' as issue_type,
    'products, quantities, prices columns contain comma-separated values' as description,
    '1NF Violation' as normalization_form
UNION ALL
SELECT 
    'Redundant Customer Data',
    'Customer information repeated for each order',
    '2NF/3NF Violation'
UNION ALL
SELECT 
    'Update Anomalies',
    'Changing customer info requires updating multiple rows',
    'General Design Issue';

-- 정규화 프로세스 추적 테이블
DROP TABLE IF EXISTS normalization_steps;
CREATE TABLE normalization_steps (
    step_id INT PRIMARY KEY AUTO_INCREMENT,
    normalization_form VARCHAR(10),
    table_name VARCHAR(100),
    description TEXT,
    before_state TEXT,
    after_state TEXT
);