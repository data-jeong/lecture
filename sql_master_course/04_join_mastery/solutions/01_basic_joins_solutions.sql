-- Chapter 04: 조인(JOIN) 마스터하기 - 기본 조인 연습 해답
-- 난이도: 초급

-- =============================================================================
-- 1. INNER JOIN 기초
-- =============================================================================

-- 1-1. 모든 직원의 이름과 부서명를 조회하세요.
SELECT 
    e.first_name,
    e.last_name,
    d.dept_name
FROM employees e
INNER JOIN departments d ON e.department_id = d.dept_id;

-- 1-2. 주문이 있는 고객의 이름과 주문 번호를 조회하세요.
SELECT 
    c.customer_name,
    o.order_number
FROM customers c
INNER JOIN orders o ON c.customer_id = o.customer_id;

-- 1-3. 상품이 포함된 주문 항목의 상품명, 수량, 단가를 조회하세요.
SELECT 
    p.product_name,
    oi.quantity,
    oi.unit_price
FROM order_items oi
INNER JOIN products p ON oi.product_id = p.product_id;

-- =============================================================================
-- 2. LEFT JOIN 기초
-- =============================================================================

-- 2-1. 모든 고객의 이름과 주문 정보를 조회하세요. (주문이 없는 고객도 포함)
SELECT 
    c.customer_name,
    o.order_number,
    o.order_date,
    o.total_amount
FROM customers c
LEFT JOIN orders o ON c.customer_id = o.customer_id;

-- 2-2. 모든 직원의 이름과 매니저 이름을 조회하세요. (매니저가 없는 직원도 포함)
SELECT 
    e.first_name || ' ' || e.last_name AS employee_name,
    m.first_name || ' ' || m.last_name AS manager_name
FROM employees e
LEFT JOIN employees m ON e.manager_id = m.employee_id;

-- 2-3. 모든 카테고리와 해당 카테고리의 상품 개수를 조회하세요.
SELECT 
    c.category_name,
    COALESCE(COUNT(p.product_id), 0) AS product_count
FROM categories c
LEFT JOIN products p ON c.category_id = p.category_id
GROUP BY c.category_id, c.category_name;

-- =============================================================================
-- 3. 다중 테이블 JOIN
-- =============================================================================

-- 3-1. 고객명, 주문일, 상품명, 수량을 모두 포함한 주문 상세 정보를 조회하세요.
SELECT 
    c.customer_name,
    o.order_date,
    p.product_name,
    oi.quantity
FROM customers c
JOIN orders o ON c.customer_id = o.customer_id
JOIN order_items oi ON o.order_id = oi.order_id
JOIN products p ON oi.product_id = p.product_id;

-- 3-2. 직원명, 부서명, 매니저명을 모두 포함한 정보를 조회하세요.
SELECT 
    e.first_name || ' ' || e.last_name AS employee_name,
    d.dept_name,
    m.first_name || ' ' || m.last_name AS manager_name
FROM employees e
LEFT JOIN departments d ON e.department_id = d.dept_id
LEFT JOIN employees m ON e.manager_id = m.employee_id;

-- 3-3. 2024년 1월 이후 주문에 대해 고객명, 주문일, 총 주문 금액을 조회하세요.
SELECT 
    c.customer_name,
    o.order_date,
    SUM(oi.quantity * oi.unit_price) AS total_order_amount
FROM customers c
JOIN orders o ON c.customer_id = o.customer_id
JOIN order_items oi ON o.order_id = oi.order_id
WHERE o.order_date >= '2024-01-01'
GROUP BY c.customer_name, o.order_date, o.order_id
ORDER BY o.order_date;

-- =============================================================================
-- 4. 조건부 JOIN
-- =============================================================================

-- 4-1. 2024년도에 주문한 고객만 조회하되, 고객 정보도 함께 표시하세요.
SELECT DISTINCT
    c.customer_id,
    c.customer_name,
    c.email,
    c.phone
FROM customers c
JOIN orders o ON c.customer_id = o.customer_id 
    AND EXTRACT(YEAR FROM o.order_date) = 2024;

-- 4-2. 가격이 100 이상인 상품을 주문한 고객의 정보를 조회하세요.
SELECT DISTINCT
    c.customer_name,
    c.email
FROM customers c
JOIN orders o ON c.customer_id = o.customer_id
JOIN order_items oi ON o.order_id = oi.order_id
JOIN products p ON oi.product_id = p.product_id 
    AND p.price >= 100;

-- 4-3. 특정 부서(department_id = 1)의 직원들과 그들의 매니저 정보를 조회하세요.
SELECT 
    e.first_name || ' ' || e.last_name AS employee_name,
    e.job_title,
    m.first_name || ' ' || m.last_name AS manager_name
FROM employees e
LEFT JOIN employees m ON e.manager_id = m.employee_id
WHERE e.department_id = 1;

-- =============================================================================
-- 5. NULL 값 처리
-- =============================================================================

-- 5-1. 주문하지 않은 고객의 목록을 조회하세요.
SELECT 
    c.customer_id,
    c.customer_name,
    c.email
FROM customers c
LEFT JOIN orders o ON c.customer_id = o.customer_id
WHERE o.customer_id IS NULL;

-- 5-2. 매니저가 없는 직원의 목록을 조회하세요.
SELECT 
    e.employee_id,
    e.first_name || ' ' || e.last_name AS employee_name,
    e.job_title
FROM employees e
WHERE e.manager_id IS NULL;

-- 5-3. 2024년에 주문하지 않은 고객의 목록을 조회하세요.
SELECT 
    c.customer_id,
    c.customer_name
FROM customers c
LEFT JOIN orders o ON c.customer_id = o.customer_id 
    AND EXTRACT(YEAR FROM o.order_date) = 2024
WHERE o.customer_id IS NULL;

-- =============================================================================
-- 6. CROSS JOIN 활용
-- =============================================================================

-- 6-1. 모든 카테고리와 모든 색상의 조합을 생성하세요.
SELECT 
    c.category_name,
    col.color_name
FROM categories c
CROSS JOIN colors col
ORDER BY c.category_name, col.color_name;

-- 6-2. 모든 학생과 모든 과목의 조합을 만들어 성적표 템플릿을 생성하세요.
SELECT 
    s.student_id,
    s.student_name,
    sub.subject_id,
    sub.subject_name,
    COALESCE(e.grade, 'Not Enrolled') AS enrollment_status,
    COALESCE(e.score, 0) AS score
FROM students s
CROSS JOIN subjects sub
LEFT JOIN enrollments e ON s.student_id = e.student_id 
    AND sub.subject_id = e.subject_id
ORDER BY s.student_name, sub.subject_name;

-- =============================================================================
-- 7. 집계 함수와 JOIN
-- =============================================================================

-- 7-1. 각 고객별 총 주문 횟수와 총 주문 금액을 조회하세요.
SELECT 
    c.customer_name,
    COUNT(o.order_id) AS total_orders,
    COALESCE(SUM(oi.quantity * oi.unit_price), 0) AS total_amount
FROM customers c
LEFT JOIN orders o ON c.customer_id = o.customer_id
LEFT JOIN order_items oi ON o.order_id = oi.order_id
GROUP BY c.customer_id, c.customer_name
ORDER BY total_amount DESC;

-- 7-2. 각 부서별 직원 수와 평균 급여를 조회하세요.
SELECT 
    d.dept_name,
    COUNT(e.employee_id) AS employee_count,
    ROUND(AVG(e.salary), 2) AS avg_salary
FROM departments d
LEFT JOIN employees e ON d.dept_id = e.department_id
GROUP BY d.dept_id, d.dept_name
ORDER BY employee_count DESC;

-- 7-3. 각 상품별 총 판매 수량과 총 판매 금액을 조회하세요.
SELECT 
    p.product_name,
    COALESCE(SUM(oi.quantity), 0) AS total_quantity,
    COALESCE(SUM(oi.quantity * oi.unit_price), 0) AS total_sales
FROM products p
LEFT JOIN order_items oi ON p.product_id = oi.product_id
GROUP BY p.product_id, p.product_name
ORDER BY total_sales DESC;

-- =============================================================================
-- 8. 실전 문제
-- =============================================================================

-- 8-1. 최고 매출 고객 TOP 5를 조회하세요.
SELECT 
    c.customer_name,
    SUM(oi.quantity * oi.unit_price) AS total_spent,
    COUNT(DISTINCT o.order_id) AS order_count
FROM customers c
JOIN orders o ON c.customer_id = o.customer_id
JOIN order_items oi ON o.order_id = oi.order_id
GROUP BY c.customer_id, c.customer_name
ORDER BY total_spent DESC
LIMIT 5;

-- 8-2. 각 부서에서 가장 높은 급여를 받는 직원의 정보를 조회하세요.
SELECT 
    d.dept_name,
    e.first_name || ' ' || e.last_name AS employee_name,
    e.salary
FROM employees e
JOIN departments d ON e.department_id = d.dept_id
WHERE e.salary = (
    SELECT MAX(e2.salary)
    FROM employees e2
    WHERE e2.department_id = e.department_id
)
ORDER BY e.salary DESC;

-- 8-3. 가장 많이 팔린 상품 TOP 10을 조회하세요.
SELECT 
    p.product_name,
    c.category_name,
    SUM(oi.quantity) AS total_quantity,
    SUM(oi.quantity * oi.unit_price) AS total_revenue
FROM products p
JOIN categories c ON p.category_id = c.category_id
JOIN order_items oi ON p.product_id = oi.product_id
GROUP BY p.product_id, p.product_name, c.category_name
ORDER BY total_quantity DESC
LIMIT 10;

-- 8-4. 2024년 각 월별 매출 현황을 조회하세요.
SELECT 
    EXTRACT(YEAR FROM o.order_date) AS year,
    EXTRACT(MONTH FROM o.order_date) AS month,
    COUNT(DISTINCT o.order_id) AS order_count,
    SUM(oi.quantity * oi.unit_price) AS total_revenue,
    COUNT(DISTINCT o.customer_id) AS unique_customers
FROM orders o
JOIN order_items oi ON o.order_id = oi.order_id
WHERE EXTRACT(YEAR FROM o.order_date) = 2024
GROUP BY EXTRACT(YEAR FROM o.order_date), EXTRACT(MONTH FROM o.order_date)
ORDER BY year, month;