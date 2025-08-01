-- Chapter 01: 실습용 테이블 생성 스크립트
-- PostgreSQL과 MySQL 모두 호환

-- employees 테이블
DROP TABLE IF EXISTS employees;
CREATE TABLE employees (
    employee_id INT PRIMARY KEY,
    first_name VARCHAR(50) NOT NULL,
    last_name VARCHAR(50) NOT NULL,
    department VARCHAR(50),
    job_title VARCHAR(100),
    salary DECIMAL(10, 2),
    hire_date DATE
);

-- products 테이블
DROP TABLE IF EXISTS products;
CREATE TABLE products (
    product_id INT PRIMARY KEY,
    product_name VARCHAR(200) NOT NULL,
    category VARCHAR(50),
    price DECIMAL(10, 2),
    stock_quantity INT DEFAULT 0
);

-- customers 테이블
DROP TABLE IF EXISTS customers;
CREATE TABLE customers (
    customer_id INT PRIMARY KEY,
    company_name VARCHAR(200) NOT NULL,
    contact_name VARCHAR(100),
    country VARCHAR(50),
    city VARCHAR(50)
);

-- 샘플 데이터 삽입
-- employees 데이터
INSERT INTO employees (employee_id, first_name, last_name, department, job_title, salary, hire_date) VALUES
(1, 'John', 'Doe', 'Sales', 'Sales Manager', 75000, '2019-01-15'),
(2, 'Jane', 'Smith', 'Marketing', 'Marketing Director', 85000, '2018-03-20'),
(3, 'Bob', 'Johnson', 'IT', 'Senior Developer', 90000, '2020-06-01'),
(4, 'Alice', 'Williams', 'Sales', 'Sales Representative', 55000, '2021-02-10'),
(5, 'Charlie', 'Brown', 'IT', 'Junior Developer', 60000, '2022-01-05'),
(6, 'Diana', 'Davis', 'HR', 'HR Manager', 70000, '2019-07-15'),
(7, 'Eve', 'Miller', 'Finance', 'Financial Analyst', 65000, '2020-09-01'),
(8, 'Frank', 'Wilson', 'Sales', 'Sales Representative', 58000, '2021-11-20'),
(9, 'Grace', 'Moore', 'Marketing', 'Marketing Specialist', 62000, '2020-04-12'),
(10, 'Henry', 'Taylor', 'IT', 'DevOps Engineer', 85000, '2019-12-01'),
(11, 'Ivy', 'Anderson', 'Finance', 'Senior Accountant', 72000, '2018-08-15'),
(12, 'Jack', 'Thomas', 'Sales', 'Regional Sales Manager', 80000, '2017-05-20'),
(13, 'Kate', 'Jackson', 'HR', 'HR Specialist', 58000, '2021-03-10'),
(14, 'Leo', 'White', 'IT', 'Data Analyst', 68000, '2020-11-15'),
(15, 'Mia', 'Harris', 'Marketing', 'Content Manager', 67000, '2019-09-01'),
(16, 'Noah', 'Martin', 'Sales', 'Sales Representative', 56000, '2022-02-01'),
(17, 'Olivia', 'Thompson', 'Finance', 'Finance Director', 95000, '2017-01-10'),
(18, 'Peter', 'Garcia', 'IT', 'Senior Developer', 88000, '2018-06-20'),
(19, 'Quinn', 'Martinez', 'HR', 'Recruiter', 60000, '2021-07-01'),
(20, 'Rachel', 'Robinson', 'Marketing', 'Marketing Manager', 78000, '2019-04-15');

-- products 데이터
INSERT INTO products (product_id, product_name, category, price, stock_quantity) VALUES
(1, 'Laptop Pro 15', 'Electronics', 1299.99, 25),
(2, 'Wireless Mouse', 'Electronics', 29.99, 150),
(3, 'Office Chair Deluxe', 'Furniture', 399.99, 40),
(4, 'Standing Desk', 'Furniture', 599.99, 20),
(5, 'Python Programming Book', 'Books', 49.99, 100),
(6, 'SQL Mastery Guide', 'Books', 39.99, 80),
(7, 'Mechanical Keyboard', 'Electronics', 149.99, 60),
(8, '27-inch Monitor', 'Electronics', 349.99, 35),
(9, 'Desk Lamp LED', 'Furniture', 79.99, 90),
(10, 'Webcam HD', 'Electronics', 89.99, 8),
(11, 'Bluetooth Headphones', 'Electronics', 199.99, 45),
(12, 'Data Science Handbook', 'Books', 59.99, 70),
(13, 'Ergonomic Mouse Pad', 'Accessories', 24.99, 200),
(14, 'USB-C Hub', 'Electronics', 69.99, 5),
(15, 'Coffee Machine', 'Appliances', 299.99, 15),
(16, 'Water Bottle', 'Accessories', 19.99, 250),
(17, 'Notebook Set', 'Stationery', 14.99, 300),
(18, 'Smartphone Stand', 'Accessories', 34.99, 120),
(19, 'External SSD 1TB', 'Electronics', 179.99, 30),
(20, 'JavaScript Guide', 'Books', 44.99, 95);

-- customers 데이터
INSERT INTO customers (customer_id, company_name, contact_name, country, city) VALUES
(1, 'Tech Solutions Inc', 'John Smith', 'USA', 'New York'),
(2, 'Global Marketing Ltd', 'Emma Johnson', 'UK', 'London'),
(3, 'Innovation Labs', 'Michael Chen', 'Canada', 'Toronto'),
(4, 'Digital Services GmbH', 'Anna Mueller', 'Germany', 'Berlin'),
(5, 'Creative Agency', 'Sophie Martin', 'France', 'Paris'),
(6, 'Data Systems Corp', 'Robert Lee', 'USA', 'San Francisco'),
(7, 'Cloud Networks', 'Lisa Wang', 'China', 'Shanghai'),
(8, 'Mobile First Ltd', 'James Wilson', 'UK', 'Manchester'),
(9, 'E-Commerce Plus', 'Maria Garcia', 'Spain', 'Madrid'),
(10, 'Software House', 'David Kim', 'South Korea', 'Seoul'),
(11, 'Consulting Group', 'Sarah Davis', 'USA', 'Chicago'),
(12, 'Finance Tech', 'Thomas Anderson', 'Switzerland', 'Zurich'),
(13, 'Retail Solutions', 'Jennifer Brown', 'Australia', 'Sydney'),
(14, 'Manufacturing Co', 'Carlos Rodriguez', 'Mexico', 'Mexico City'),
(15, 'Healthcare Systems', 'Patricia Jones', 'USA', 'Boston'),
(16, 'Education Platform', 'Mark Taylor', 'Canada', 'Vancouver'),
(17, 'Energy Corp', 'Nina Petrov', 'Russia', 'Moscow'),
(18, 'Transport Services', 'Ahmed Hassan', 'UAE', 'Dubai'),
(19, 'Food & Beverage Co', 'Emily White', 'USA', 'Los Angeles'),
(20, 'Entertainment Group', 'Lucas Silva', 'Brazil', 'São Paulo');