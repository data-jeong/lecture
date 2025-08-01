-- Chapter 06: 윈도우 함수와 분석 함수 실습용 테이블 생성 스크립트
-- PostgreSQL과 MySQL 모두 호환

-- 기존 테이블들은 Chapter 05에서 생성된 것들을 사용

-- daily_sales 테이블 (일별 매출 분석용)
DROP TABLE IF EXISTS daily_sales;
CREATE TABLE daily_sales (
    sale_date DATE PRIMARY KEY,
    daily_revenue DECIMAL(12, 2) NOT NULL,
    order_count INT NOT NULL DEFAULT 0,
    avg_order_value DECIMAL(10, 2) DEFAULT 0
);

-- employee_performance 테이블 (직원 성과 분석용)
DROP TABLE IF EXISTS employee_performance;
CREATE TABLE employee_performance (
    performance_id INT PRIMARY KEY,
    employee_id INT NOT NULL,
    performance_date DATE NOT NULL,
    score DECIMAL(5, 2) CHECK (score >= 0 AND score <= 100),
    goals_met INT DEFAULT 0,
    total_goals INT DEFAULT 5,
    quarter VARCHAR(10),
    FOREIGN KEY (employee_id) REFERENCES employees(employee_id)
);

-- stock_movements 테이블 (재고 이동 분석용)
DROP TABLE IF EXISTS stock_movements;
CREATE TABLE stock_movements (
    movement_id INT PRIMARY KEY,
    product_id INT NOT NULL,
    movement_date DATE NOT NULL,
    movement_type VARCHAR(10) CHECK (movement_type IN ('IN', 'OUT')),
    quantity INT NOT NULL,
    reference_type VARCHAR(20), -- 'PURCHASE', 'SALE', 'ADJUSTMENT'
    reference_id INT,
    FOREIGN KEY (product_id) REFERENCES products(product_id)
);

-- monthly_targets 테이블 (월별 목표 관리)
DROP TABLE IF EXISTS monthly_targets;
CREATE TABLE monthly_targets (
    target_id INT PRIMARY KEY,
    department VARCHAR(50) NOT NULL,
    target_month DATE NOT NULL,
    revenue_target DECIMAL(12, 2),
    customer_target INT,
    order_target INT
);

-- customer_segments 테이블 (고객 세그멘테이션 분석용)
DROP TABLE IF EXISTS customer_segments;
CREATE TABLE customer_segments (
    segment_id INT PRIMARY KEY,
    customer_id INT NOT NULL,
    segment_date DATE NOT NULL,
    rfm_score VARCHAR(10),
    segment_name VARCHAR(50),
    clv_estimate DECIMAL(10, 2), -- Customer Lifetime Value
    FOREIGN KEY (customer_id) REFERENCES customers(customer_id)
);

-- 샘플 데이터 삽입

-- daily_sales 데이터 (2023년 전체)
INSERT INTO daily_sales (sale_date, daily_revenue, order_count, avg_order_value) VALUES
-- 2023년 1월
('2023-01-01', 1250.50, 5, 250.10),
('2023-01-02', 2100.75, 8, 262.59),
('2023-01-03', 1875.25, 7, 267.89),
('2023-01-04', 3200.00, 12, 266.67),
('2023-01-05', 2750.80, 10, 275.08),
('2023-01-06', 1980.45, 6, 330.08),
('2023-01-07', 2890.30, 11, 262.75),
('2023-01-08', 3450.75, 13, 265.44),
('2023-01-09', 2680.90, 9, 297.88),
('2023-01-10', 4100.25, 15, 273.35),
-- 2월 샘플 (매출 성장 패턴)
('2023-02-01', 3200.75, 12, 266.73),
('2023-02-02', 3850.50, 14, 275.04),
('2023-02-03', 4200.25, 16, 262.52),
('2023-02-04', 3900.80, 15, 260.05),
('2023-02-05', 4500.60, 18, 250.03),
('2023-02-06', 3750.90, 14, 267.92),
('2023-02-07', 4800.45, 19, 252.65),
('2023-02-08', 5200.75, 21, 247.66),
('2023-02-09', 4650.30, 17, 273.55),
('2023-02-10', 5850.80, 23, 254.38),
-- 3월 샘플 (계절성 반영)
('2023-03-01', 5100.25, 19, 268.44),
('2023-03-02', 5750.80, 22, 261.40),
('2023-03-03', 6200.45, 24, 258.35),
('2023-03-04', 5890.70, 21, 280.51),
('2023-03-05', 6800.90, 26, 261.57),
('2023-03-06', 6450.35, 23, 280.45),
('2023-03-07', 7200.60, 28, 257.16),
('2023-03-08', 6950.80, 25, 278.03),
('2023-03-09', 7500.45, 29, 258.64),
('2023-03-10', 8100.75, 31, 261.31),
-- 추가 월별 데이터 (트렌드 분석용)
('2023-04-15', 7800.50, 28, 278.59),
('2023-05-15', 8200.75, 30, 273.36),
('2023-06-15', 8900.25, 33, 269.70),
('2023-07-15', 9500.80, 35, 271.45),
('2023-08-15', 9200.45, 34, 270.60),
('2023-09-15', 10100.90, 37, 273.00),
('2023-10-15', 11200.75, 42, 266.69),
('2023-11-15', 12800.50, 48, 266.68),
('2023-12-15', 15200.25, 55, 276.37);

-- employee_performance 데이터
INSERT INTO employee_performance (performance_id, employee_id, performance_date, score, goals_met, total_goals, quarter) VALUES
-- 2023 Q1 성과
(1, 1, '2023-03-31', 92.5, 5, 5, '2023-Q1'),
(2, 2, '2023-03-31', 88.7, 4, 5, '2023-Q1'),
(3, 3, '2023-03-31', 95.2, 5, 5, '2023-Q1'),
(4, 4, '2023-03-31', 78.9, 3, 5, '2023-Q1'),
(5, 5, '2023-03-31', 85.6, 4, 5, '2023-Q1'),
(6, 6, '2023-03-31', 91.3, 5, 5, '2023-Q1'),
(7, 7, '2023-03-31', 87.4, 4, 5, '2023-Q1'),
(8, 8, '2023-03-31', 82.1, 4, 5, '2023-Q1'),
(9, 9, '2023-03-31', 89.8, 4, 5, '2023-Q1'),
(10, 10, '2023-03-31', 93.7, 5, 5, '2023-Q1'),
-- 2023 Q2 성과
(11, 1, '2023-06-30', 89.2, 4, 5, '2023-Q2'),
(12, 2, '2023-06-30', 91.5, 5, 5, '2023-Q2'),
(13, 3, '2023-06-30', 94.8, 5, 5, '2023-Q2'),
(14, 4, '2023-06-30', 81.7, 4, 5, '2023-Q2'),
(15, 5, '2023-06-30', 87.9, 4, 5, '2023-Q2'),
(16, 6, '2023-06-30', 88.6, 4, 5, '2023-Q2'),
(17, 7, '2023-06-30', 90.1, 5, 5, '2023-Q2'),
(18, 8, '2023-06-30', 84.3, 4, 5, '2023-Q2'),
(19, 9, '2023-06-30', 86.7, 4, 5, '2023-Q2'),
(20, 10, '2023-06-30', 92.4, 5, 5, '2023-Q2'),
-- 2023 Q3 성과
(21, 1, '2023-09-30', 94.1, 5, 5, '2023-Q3'),
(22, 2, '2023-09-30', 89.9, 4, 5, '2023-Q3'),
(23, 3, '2023-09-30', 96.3, 5, 5, '2023-Q3'),
(24, 4, '2023-09-30', 83.5, 4, 5, '2023-Q3'),
(25, 5, '2023-09-30', 88.2, 4, 5, '2023-Q3'),
(26, 6, '2023-09-30', 90.7, 5, 5, '2023-Q3'),
(27, 7, '2023-09-30', 85.8, 4, 5, '2023-Q3'),
(28, 8, '2023-09-30', 87.6, 4, 5, '2023-Q3'),
(29, 9, '2023-09-30', 91.4, 5, 5, '2023-Q3'),
(30, 10, '2023-09-30', 95.8, 5, 5, '2023-Q3'),
-- 2023 Q4 성과
(31, 1, '2023-12-31', 96.7, 5, 5, '2023-Q4'),
(32, 2, '2023-12-31', 92.8, 5, 5, '2023-Q4'),
(33, 3, '2023-12-31', 98.1, 5, 5, '2023-Q4'),
(34, 4, '2023-12-31', 85.9, 4, 5, '2023-Q4'),
(35, 5, '2023-12-31', 90.5, 5, 5, '2023-Q4'),
(36, 6, '2023-12-31', 93.2, 5, 5, '2023-Q4'),
(37, 7, '2023-12-31', 88.9, 4, 5, '2023-Q4'),
(38, 8, '2023-12-31', 89.7, 4, 5, '2023-Q4'),
(39, 9, '2023-12-31', 93.6, 5, 5, '2023-Q4'),
(40, 10, '2023-12-31', 97.4, 5, 5, '2023-Q4');

-- stock_movements 데이터 (재고 이동 내역)
INSERT INTO stock_movements (movement_id, product_id, movement_date, movement_type, quantity, reference_type, reference_id) VALUES
-- 1월 재고 이동
(1, 1, '2023-01-01', 'IN', 50, 'PURCHASE', 1001),
(2, 2, '2023-01-01', 'IN', 200, 'PURCHASE', 1001),
(3, 3, '2023-01-01', 'IN', 30, 'PURCHASE', 1002),
(4, 1, '2023-01-15', 'OUT', 1, 'SALE', 1),
(5, 2, '2023-01-15', 'OUT', 1, 'SALE', 1),
(6, 5, '2023-01-15', 'OUT', 5, 'SALE', 1),
(7, 3, '2023-01-18', 'OUT', 1, 'SALE', 2),
(8, 9, '2023-01-18', 'OUT', 1, 'SALE', 2),
-- 2월 재고 이동
(9, 11, '2023-02-01', 'OUT', 1, 'SALE', 3),
(10, 16, '2023-02-10', 'OUT', 1, 'SALE', 4),
(11, 13, '2023-02-10', 'OUT', 2, 'SALE', 4),
(12, 17, '2023-02-10', 'OUT', 1, 'SALE', 4),
(13, 8, '2023-02-15', 'OUT', 1, 'SALE', 5),
(14, 7, '2023-02-15', 'OUT', 1, 'SALE', 5),
(15, 19, '2023-02-15', 'OUT', 1, 'SALE', 5),
-- 3월 재고 이동 및 입고
(16, 8, '2023-03-01', 'OUT', 1, 'SALE', 6),
(17, 10, '2023-03-05', 'OUT', 1, 'SALE', 7),
(18, 13, '2023-03-05', 'OUT', 3, 'SALE', 7),
(19, 15, '2023-03-12', 'OUT', 1, 'SALE', 8),
(20, 1, '2023-03-15', 'IN', 25, 'PURCHASE', 1003),
(21, 8, '2023-03-15', 'IN', 20, 'PURCHASE', 1003),
(22, 11, '2023-03-15', 'IN', 40, 'PURCHASE', 1004),
-- 재고 조정
(23, 10, '2023-03-20', 'IN', 5, 'ADJUSTMENT', NULL),
(24, 14, '2023-03-25', 'OUT', 2, 'ADJUSTMENT', NULL),
-- 더 많은 판매 데이터
(25, 19, '2023-04-01', 'OUT', 1, 'SALE', 10),
(26, 2, '2023-04-01', 'OUT', 2, 'SALE', 10),
(27, 18, '2023-04-01', 'OUT', 5, 'SALE', 10),
(28, 19, '2023-04-08', 'OUT', 1, 'SALE', 11),
(29, 4, '2023-04-15', 'OUT', 1, 'SALE', 12),
(30, 7, '2023-05-01', 'OUT', 1, 'SALE', 13),
-- 대량 입고
(31, 1, '2023-05-10', 'IN', 30, 'PURCHASE', 1005),
(32, 2, '2023-05-10', 'IN', 150, 'PURCHASE', 1005),
(33, 7, '2023-05-10', 'IN', 40, 'PURCHASE', 1005),
(34, 8, '2023-05-10', 'IN', 25, 'PURCHASE', 1005),
-- 연말 대량 판매
(35, 1, '2023-12-20', 'OUT', 1, 'SALE', 30),
(36, 11, '2023-12-20', 'OUT', 3, 'SALE', 15),
(37, 4, '2023-12-20', 'OUT', 1, 'SALE', 30);

-- monthly_targets 데이터
INSERT INTO monthly_targets (target_id, department, target_month, revenue_target, customer_target, order_target) VALUES
-- 2023년 월별 목표
(1, 'Sales', '2023-01-01', 80000.00, 50, 200),
(2, 'Marketing', '2023-01-01', 40000.00, 30, 100),
(3, 'Sales', '2023-02-01', 85000.00, 55, 220),
(4, 'Marketing', '2023-02-01', 42000.00, 32, 105),
(5, 'Sales', '2023-03-01', 90000.00, 60, 240),
(6, 'Marketing', '2023-03-01', 45000.00, 35, 110),
(7, 'Sales', '2023-04-01', 95000.00, 65, 260),
(8, 'Marketing', '2023-04-01', 48000.00, 38, 115),
(9, 'Sales', '2023-05-01', 100000.00, 70, 280),
(10, 'Marketing', '2023-05-01', 50000.00, 40, 120),
(11, 'Sales', '2023-06-01', 105000.00, 75, 300),
(12, 'Marketing', '2023-06-01', 52000.00, 42, 125),
(13, 'Sales', '2023-07-01', 110000.00, 80, 320),
(14, 'Marketing', '2023-07-01', 55000.00, 45, 130),
(15, 'Sales', '2023-08-01', 115000.00, 85, 340),
(16, 'Marketing', '2023-08-01', 58000.00, 48, 135),
(17, 'Sales', '2023-09-01', 120000.00, 90, 360),
(18, 'Marketing', '2023-09-01', 60000.00, 50, 140),
(19, 'Sales', '2023-10-01', 125000.00, 95, 380),
(20, 'Marketing', '2023-10-01', 62000.00, 52, 145),
(21, 'Sales', '2023-11-01', 130000.00, 100, 400),
(22, 'Marketing', '2023-11-01', 65000.00, 55, 150),
(23, 'Sales', '2023-12-01', 150000.00, 120, 450),
(24, 'Marketing', '2023-12-01', 75000.00, 65, 170);

-- customer_segments 데이터 (분기별 세그멘테이션)
INSERT INTO customer_segments (segment_id, customer_id, segment_date, rfm_score, segment_name, clv_estimate) VALUES
-- Q1 2023 세그멘테이션
(1, 1, '2023-03-31', '555', 'Champions', 5000.00),
(2, 2, '2023-03-31', '344', 'Loyal Customers', 2500.00),
(3, 3, '2023-03-31', '433', 'Loyal Customers', 3000.00),
(4, 4, '2023-03-31', '322', 'Potential Loyalists', 1800.00),
(5, 5, '2023-03-31', '211', 'New Customers', 900.00),
(6, 6, '2023-03-31', '412', 'Potential Loyalists', 2200.00),
(7, 7, '2023-03-31', '155', 'At Risk', 800.00),
(8, 8, '2023-03-31', '324', 'Loyal Customers', 2800.00),
(9, 9, '2023-03-31', '245', 'Potential Loyalists', 1500.00),
(10, 10, '2023-03-31', '356', 'Loyal Customers', 3200.00),
-- Q2 2023 업데이트
(11, 1, '2023-06-30', '545', 'Champions', 5200.00),
(12, 2, '2023-06-30', '354', 'Loyal Customers', 2700.00),
(13, 3, '2023-06-30', '444', 'Champions', 3500.00),
(14, 4, '2023-06-30', '333', 'Loyal Customers', 2000.00),
(15, 5, '2023-06-30', '222', 'Potential Loyalists', 1100.00),
-- Q3 2023 업데이트
(16, 1, '2023-09-30', '555', 'Champions', 5800.00),
(17, 2, '2023-09-30', '345', 'Loyal Customers', 2900.00),
(18, 3, '2023-09-30', '454', 'Champions', 4000.00),
(19, 4, '2023-09-30', '334', 'Loyal Customers', 2300.00),
(20, 5, '2023-09-30', '233', 'Potential Loyalists', 1400.00);

-- 성능 최적화를 위한 인덱스 생성
CREATE INDEX idx_daily_sales_date ON daily_sales(sale_date);
CREATE INDEX idx_employee_performance_emp_date ON employee_performance(employee_id, performance_date);
CREATE INDEX idx_stock_movements_product_date ON stock_movements(product_id, movement_date);
CREATE INDEX idx_stock_movements_date_type ON stock_movements(movement_date, movement_type);
CREATE INDEX idx_monthly_targets_dept_month ON monthly_targets(department, target_month);
CREATE INDEX idx_customer_segments_customer_date ON customer_segments(customer_id, segment_date);

-- 뷰 생성 (복잡한 분석을 위한 사전 정의된 뷰)
CREATE OR REPLACE VIEW monthly_revenue_summary AS
SELECT 
    EXTRACT(YEAR FROM sale_date) as year,
    EXTRACT(MONTH FROM sale_date) as month,
    SUM(daily_revenue) as total_revenue,
    AVG(daily_revenue) as avg_daily_revenue,
    SUM(order_count) as total_orders,
    AVG(avg_order_value) as avg_order_value
FROM daily_sales
GROUP BY EXTRACT(YEAR FROM sale_date), EXTRACT(MONTH FROM sale_date);

CREATE OR REPLACE VIEW employee_performance_summary AS
SELECT 
    e.employee_id,
    e.first_name,
    e.last_name,
    e.department,
    AVG(ep.score) as avg_score,
    COUNT(ep.performance_id) as evaluation_count,
    SUM(ep.goals_met) as total_goals_met,
    SUM(ep.total_goals) as total_goals_assigned
FROM employees e
LEFT JOIN employee_performance ep ON e.employee_id = ep.employee_id
GROUP BY e.employee_id, e.first_name, e.last_name, e.department;