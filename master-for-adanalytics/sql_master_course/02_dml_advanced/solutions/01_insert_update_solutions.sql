-- Chapter 02: INSERT와 UPDATE 실습 해답

-- 문제 1: IT 부서 직원들을 employees_backup에 복사
INSERT INTO employees_backup (employee_id, first_name, last_name, department, job_title, salary, hire_date)
SELECT employee_id, first_name, last_name, department, job_title, salary, hire_date
FROM employees
WHERE department = 'IT';

-- 문제 2: 새로운 주문 3건을 한 번에 삽입
INSERT INTO orders (order_id, customer_id, order_date, status, total_amount)
VALUES 
    (9, 8, CURRENT_DATE, 'Pending', 500.00),
    (10, 9, CURRENT_DATE, 'Pending', 750.00),
    (11, 10, CURRENT_DATE, 'Pending', 1000.00);

-- 문제 3: Electronics 카테고리 상품 가격 10% 인상
-- 먼저 last_modified 컬럼 추가 (없는 경우)
ALTER TABLE products ADD COLUMN IF NOT EXISTS last_modified TIMESTAMP DEFAULT CURRENT_TIMESTAMP;

-- 가격 인상 및 시간 업데이트
UPDATE products
SET price = price * 1.10,
    last_modified = CURRENT_TIMESTAMP
WHERE category = 'Electronics';

-- 문제 4: 성과 평가에 따른 급여 인상
UPDATE employees
SET salary = CASE 
    WHEN performance_rating = 'A' THEN salary * 1.15
    WHEN performance_rating = 'B' THEN salary * 1.10
    WHEN performance_rating = 'C' THEN salary * 1.05
    ELSE salary
END,
last_modified = CURRENT_TIMESTAMP;

-- 문제 5: 재고가 10개 미만인 상품 재고 50개 추가
UPDATE inventory
SET quantity = quantity + 50,
    last_updated = CURRENT_TIMESTAMP
WHERE quantity < 10;

-- 문제 6: 가격 변경 추적하며 Electronics 상품 5% 인하
-- 먼저 변경 전 가격을 기록
INSERT INTO product_changes (product_id, old_price, new_price, changed_by)
SELECT 
    product_id,
    price as old_price,
    price * 0.95 as new_price,
    'System' as changed_by
FROM products
WHERE category = 'Electronics';

-- 실제 가격 변경
UPDATE products
SET price = price * 0.95,
    last_modified = CURRENT_TIMESTAMP
WHERE category = 'Electronics';

-- 문제 7: 부서별 평균보다 낮은 급여를 평균의 90%로 조정
UPDATE employees e
SET salary = (
    SELECT AVG(salary) * 0.90
    FROM employees e2
    WHERE e2.department = e.department
),
last_modified = CURRENT_TIMESTAMP
WHERE salary < (
    SELECT AVG(salary)
    FROM employees e3
    WHERE e3.department = e.department
);

-- 문제 8: UPSERT를 사용한 inventory 업데이트

-- PostgreSQL 버전
INSERT INTO inventory (product_id, quantity)
VALUES (21, 100), (22, 100), (23, 100)
ON CONFLICT (product_id)
DO UPDATE SET 
    quantity = inventory.quantity + EXCLUDED.quantity,
    last_updated = CURRENT_TIMESTAMP;

-- MySQL 버전
INSERT INTO inventory (product_id, quantity)
VALUES (21, 100), (22, 100), (23, 100)
ON DUPLICATE KEY UPDATE
    quantity = quantity + VALUES(quantity),
    last_updated = CURRENT_TIMESTAMP;