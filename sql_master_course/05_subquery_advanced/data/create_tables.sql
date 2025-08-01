-- Chapter 05: 서브쿼리와 고급 쿼리 실습용 테이블 생성 스크립트
-- PostgreSQL과 MySQL 모두 호환

-- 기존 테이블들 (Chapter 01에서 생성된 것들)
-- employees, products, customers

-- orders 테이블
DROP TABLE IF EXISTS order_items;
DROP TABLE IF EXISTS orders;
CREATE TABLE orders (
    order_id INT PRIMARY KEY,
    customer_id INT NOT NULL,
    order_date DATE NOT NULL,
    total_amount DECIMAL(10, 2) NOT NULL,
    status VARCHAR(20) DEFAULT 'pending',
    shipping_address TEXT,
    FOREIGN KEY (customer_id) REFERENCES customers(customer_id)
);

-- order_items 테이블
CREATE TABLE order_items (
    order_item_id INT PRIMARY KEY,
    order_id INT NOT NULL,
    product_id INT NOT NULL,
    quantity INT NOT NULL DEFAULT 1,
    unit_price DECIMAL(10, 2) NOT NULL,
    FOREIGN KEY (order_id) REFERENCES orders(order_id),
    FOREIGN KEY (product_id) REFERENCES products(product_id)
);

-- employees_hierarchy 테이블 (조직도용)
DROP TABLE IF EXISTS employees_hierarchy;
CREATE TABLE employees_hierarchy (
    employee_id INT PRIMARY KEY,
    first_name VARCHAR(50) NOT NULL,
    last_name VARCHAR(50) NOT NULL,
    manager_id INT,
    position_level INT DEFAULT 1,
    department VARCHAR(50),
    FOREIGN KEY (manager_id) REFERENCES employees_hierarchy(employee_id)
);

-- department_budgets 테이블 (예산 관리용)
DROP TABLE IF EXISTS department_budgets;
CREATE TABLE department_budgets (
    budget_id INT PRIMARY KEY,
    department VARCHAR(50) NOT NULL,
    year INT NOT NULL,
    budget_amount DECIMAL(12, 2) NOT NULL,
    spent_amount DECIMAL(12, 2) DEFAULT 0
);

-- product_reviews 테이블 (상품 리뷰용)
DROP TABLE IF EXISTS product_reviews;
CREATE TABLE product_reviews (
    review_id INT PRIMARY KEY,
    product_id INT NOT NULL,
    customer_id INT NOT NULL,
    rating INT CHECK (rating >= 1 AND rating <= 5),
    review_text TEXT,
    review_date DATE NOT NULL,
    FOREIGN KEY (product_id) REFERENCES products(product_id),
    FOREIGN KEY (customer_id) REFERENCES customers(customer_id)
);

-- 샘플 데이터 삽입

-- orders 데이터 (2022-2024년)
INSERT INTO orders (order_id, customer_id, order_date, total_amount, status, shipping_address) VALUES
(1, 1, '2023-01-15', 1579.97, 'completed', '123 Tech Street, New York, NY'),
(2, 3, '2023-01-18', 449.98, 'completed', '456 Innovation Ave, Toronto, ON'),
(3, 2, '2023-02-01', 199.99, 'completed', '789 Marketing Blvd, London, UK'),
(4, 5, '2023-02-10', 89.99, 'shipped', '321 Creative Lane, Paris, FR'),
(5, 1, '2023-02-15', 679.98, 'completed', '123 Tech Street, New York, NY'),
(6, 4, '2023-03-01', 349.99, 'completed', '654 Digital Str, Berlin, DE'),
(7, 6, '2023-03-05', 159.98, 'completed', '987 Cloud Way, San Francisco, CA'),
(8, 8, '2023-03-12', 299.99, 'completed', '147 Mobile St, Manchester, UK'),
(9, 7, '2023-03-20', 499.99, 'cancelled', '258 Network Rd, Shanghai, CN'),
(10, 10, '2023-04-01', 229.98, 'completed', '369 Software Ave, Seoul, KR'),
(11, 9, '2023-04-08', 179.99, 'completed', '741 Retail Plaza, Madrid, ES'),
(12, 12, '2023-04-15', 599.99, 'shipped', '852 Finance Center, Zurich, CH'),
(13, 11, '2023-05-01', 149.99, 'completed', '963 Consulting St, Chicago, IL'),
(14, 13, '2023-05-10', 89.99, 'completed', '159 Solutions Way, Sydney, AU'),
(15, 1, '2023-05-18', 899.98, 'completed', '123 Tech Street, New York, NY'),
(16, 15, '2023-06-01', 399.99, 'completed', '753 Healthcare Dr, Boston, MA'),
(17, 14, '2023-06-12', 199.99, 'completed', '486 Manufacturing Rd, Mexico City, MX'),
(18, 16, '2023-06-20', 249.98, 'shipped', '297 Education Blvd, Vancouver, BC'),
(19, 18, '2023-07-01', 179.99, 'completed', '108 Transport Ave, Dubai, UAE'),
(20, 17, '2023-07-15', 459.98, 'completed', '219 Energy Plaza, Moscow, RU'),
(21, 19, '2023-08-01', 329.99, 'completed', '330 Food Court, Los Angeles, CA'),
(22, 20, '2023-08-12', 199.99, 'completed', '441 Entertainment St, São Paulo, BR'),
(23, 2, '2023-09-01', 299.99, 'completed', '789 Marketing Blvd, London, UK'),
(24, 3, '2023-09-15', 149.99, 'shipped', '456 Innovation Ave, Toronto, ON'),
(25, 4, '2023-10-01', 699.98, 'completed', '654 Digital Str, Berlin, DE'),
(26, 5, '2023-10-20', 399.99, 'completed', '321 Creative Lane, Paris, FR'),
(27, 6, '2023-11-01', 189.98, 'completed', '987 Cloud Way, San Francisco, CA'),
(28, 7, '2023-11-15', 549.99, 'shipped', '258 Network Rd, Shanghai, CN'),
(29, 8, '2023-12-01', 229.98, 'completed', '147 Mobile St, Manchester, UK'),
(30, 1, '2023-12-20', 1299.99, 'completed', '123 Tech Street, New York, NY'),
-- 2024년 데이터
(31, 9, '2024-01-10', 199.99, 'completed', '741 Retail Plaza, Madrid, ES'),
(32, 10, '2024-01-25', 459.98, 'shipped', '369 Software Ave, Seoul, KR'),
(33, 11, '2024-02-05', 299.99, 'completed', '963 Consulting St, Chicago, IL'),
(34, 12, '2024-02-18', 179.99, 'completed', '852 Finance Center, Zurich, CH'),
(35, 13, '2024-03-01', 399.99, 'completed', '159 Solutions Way, Sydney, AU');

-- order_items 데이터
INSERT INTO order_items (order_item_id, order_id, product_id, quantity, unit_price) VALUES
-- Order 1 items
(1, 1, 1, 1, 1299.99), (2, 1, 2, 1, 29.99), (3, 1, 5, 5, 49.99),
-- Order 2 items
(4, 2, 3, 1, 399.99), (5, 2, 9, 1, 79.99),
-- Order 3 items
(6, 3, 11, 1, 199.99),
-- Order 4 items
(7, 4, 16, 1, 19.99), (8, 4, 13, 2, 24.99), (9, 4, 17, 1, 14.99),
-- Order 5 items
(10, 5, 8, 1, 349.99), (11, 5, 7, 1, 149.99), (12, 5, 19, 1, 179.99),
-- Order 6 items
(13, 6, 8, 1, 349.99),
-- Order 7 items
(14, 7, 10, 1, 89.99), (15, 7, 13, 3, 24.99),
-- Order 8 items
(16, 8, 15, 1, 299.99),
-- Order 9 items (cancelled)
(17, 9, 1, 1, 1299.99), (18, 9, 4, 1, 599.99),
-- Order 10 items
(19, 10, 2, 2, 29.99), (20, 10, 18, 5, 34.99),
-- Order 11 items
(21, 11, 19, 1, 179.99),
-- Order 12 items
(22, 12, 4, 1, 599.99),
-- Order 13 items
(23, 13, 7, 1, 149.99),
-- Order 14 items
(24, 14, 16, 3, 19.99), (25, 14, 17, 2, 14.99),
-- Order 15 items
(26, 15, 1, 1, 1299.99), (27, 15, 11, 3, 199.99),
-- Order 16 items
(28, 16, 3, 1, 399.99),
-- Order 17 items
(29, 17, 11, 1, 199.99),
-- Order 18 items
(30, 18, 2, 5, 29.99), (31, 18, 13, 5, 24.99),
-- Order 19 items
(32, 19, 19, 1, 179.99),
-- Order 20 items
(33, 20, 8, 1, 349.99), (34, 20, 10, 1, 89.99), (35, 20, 17, 2, 14.99),
-- Order 21 items
(36, 21, 15, 1, 299.99), (37, 21, 16, 1, 19.99),
-- Order 22 items
(38, 22, 11, 1, 199.99),
-- Order 23 items
(39, 23, 15, 1, 299.99),
-- Order 24 items
(40, 24, 7, 1, 149.99),
-- Order 25 items
(41, 25, 1, 1, 1299.99), (42, 25, 8, 1, 349.99), (43, 25, 9, 1, 79.99),
-- Order 26 items
(44, 26, 3, 1, 399.99),
-- Order 27 items
(45, 27, 10, 1, 89.99), (46, 27, 2, 3, 29.99),
-- Order 28 items
(47, 28, 4, 1, 599.99),
-- Order 29 items
(48, 29, 2, 5, 29.99), (49, 29, 18, 2, 34.99),
-- Order 30 items
(50, 30, 1, 1, 1299.99),
-- 2024년 주문들
(51, 31, 11, 1, 199.99),
(52, 32, 8, 1, 349.99), (53, 32, 7, 1, 149.99),
(54, 33, 15, 1, 299.99),
(55, 34, 19, 1, 179.99),
(56, 35, 3, 1, 399.99);

-- employees_hierarchy 데이터
INSERT INTO employees_hierarchy (employee_id, first_name, last_name, manager_id, position_level, department) VALUES
-- CEO (Level 1)
(101, 'Michael', 'CEO', NULL, 1, 'Executive'),
-- Directors (Level 2)
(102, 'Sarah', 'CTO', 101, 2, 'IT'),
(103, 'David', 'CFO', 101, 2, 'Finance'),
(104, 'Lisa', 'CMO', 101, 2, 'Marketing'),
(105, 'Robert', 'CHRO', 101, 2, 'HR'),
(106, 'Jennifer', 'VP_Sales', 101, 2, 'Sales'),
-- Managers (Level 3)
(107, 'John', 'IT_Manager', 102, 3, 'IT'),
(108, 'Emma', 'Finance_Manager', 103, 3, 'Finance'),
(109, 'James', 'Marketing_Manager', 104, 3, 'Marketing'),
(110, 'Mary', 'HR_Manager', 105, 3, 'HR'),
(111, 'William', 'Sales_Manager', 106, 3, 'Sales'),
-- Team Leads (Level 4)
(112, 'Daniel', 'Dev_Lead', 107, 4, 'IT'),
(113, 'Jessica', 'QA_Lead', 107, 4, 'IT'),
(114, 'Christopher', 'Finance_Lead', 108, 4, 'Finance'),
(115, 'Ashley', 'Marketing_Lead', 109, 4, 'Marketing'),
(116, 'Matthew', 'Sales_Lead', 111, 4, 'Sales'),
-- Individual Contributors (Level 5)
(117, 'Andrew', 'Senior_Dev', 112, 5, 'IT'),
(118, 'Amanda', 'Senior_Dev', 112, 5, 'IT'),
(119, 'Joshua', 'QA_Engineer', 113, 5, 'IT'),
(120, 'Stephanie', 'Junior_Dev', 112, 5, 'IT'),
(121, 'Ryan', 'Accountant', 114, 5, 'Finance'),
(122, 'Michelle', 'Financial_Analyst', 114, 5, 'Finance'),
(123, 'Jason', 'Marketing_Specialist', 115, 5, 'Marketing'),
(124, 'Nicole', 'Content_Creator', 115, 5, 'Marketing'),
(125, 'Kevin', 'Sales_Rep', 116, 5, 'Sales'),
(126, 'Elizabeth', 'Sales_Rep', 116, 5, 'Sales');

-- department_budgets 데이터
INSERT INTO department_budgets (budget_id, department, year, budget_amount, spent_amount) VALUES
-- 2023년 예산
(1, 'IT', 2023, 1500000.00, 1350000.00),
(2, 'Finance', 2023, 800000.00, 750000.00),
(3, 'Marketing', 2023, 1200000.00, 1100000.00),
(4, 'HR', 2023, 600000.00, 580000.00),
(5, 'Sales', 2023, 2000000.00, 1950000.00),
-- 2024년 예산
(6, 'IT', 2024, 1800000.00, 450000.00),
(7, 'Finance', 2024, 900000.00, 200000.00),
(8, 'Marketing', 2024, 1500000.00, 350000.00),
(9, 'HR', 2024, 700000.00, 175000.00),
(10, 'Sales', 2024, 2200000.00, 550000.00);

-- product_reviews 데이터
INSERT INTO product_reviews (review_id, product_id, customer_id, rating, review_text, review_date) VALUES
(1, 1, 1, 5, 'Excellent laptop with great performance!', '2023-01-20'),
(2, 1, 3, 4, 'Good laptop but a bit expensive.', '2023-02-05'),
(3, 2, 1, 5, 'Perfect wireless mouse, very responsive.', '2023-01-22'),
(4, 3, 2, 4, 'Comfortable chair, good for long work sessions.', '2023-02-15'),
(5, 5, 1, 5, 'Great book for learning Python!', '2023-02-18'),
(6, 7, 6, 5, 'Amazing mechanical keyboard, love the feel.', '2023-03-10'),
(7, 8, 4, 4, 'Good monitor with crisp display.', '2023-03-08'),
(8, 10, 7, 3, 'Webcam quality is okay, not great in low light.', '2023-03-25'),
(9, 11, 8, 5, 'Excellent sound quality on these headphones.', '2023-03-15'),
(10, 15, 21, 4, 'Coffee machine works well, easy to use.', '2023-08-05'),
(11, 1, 25, 5, 'Best laptop I have ever owned!', '2023-10-25'),
(12, 8, 26, 4, 'Great monitor for the price.', '2023-11-02'),
(13, 11, 29, 5, 'These headphones are incredible!', '2023-12-05'),
(14, 19, 31, 4, 'Fast SSD, good storage solution.', '2024-01-15'),
(15, 3, 32, 5, 'Very comfortable office chair.', '2024-01-30'),
(16, 15, 33, 3, 'Coffee machine is decent but could be better.', '2024-02-10'),
(17, 7, 34, 5, 'Love this keyboard for programming!', '2024-02-20'),
(18, 2, 35, 4, 'Good mouse, works perfectly.', '2024-03-05'),
(19, 4, 1, 5, 'Standing desk changed my work life!', '2023-12-25'),
(20, 6, 2, 4, 'Helpful SQL book for beginners.', '2023-03-01');

-- 인덱스 생성 (성능 향상을 위해)
CREATE INDEX idx_orders_customer_id ON orders(customer_id);
CREATE INDEX idx_orders_date ON orders(order_date);
CREATE INDEX idx_order_items_order_id ON order_items(order_id);
CREATE INDEX idx_order_items_product_id ON order_items(product_id);
CREATE INDEX idx_employees_hierarchy_manager ON employees_hierarchy(manager_id);
CREATE INDEX idx_product_reviews_product ON product_reviews(product_id);
CREATE INDEX idx_product_reviews_customer ON product_reviews(customer_id);
CREATE INDEX idx_department_budgets_dept_year ON department_budgets(department, year);