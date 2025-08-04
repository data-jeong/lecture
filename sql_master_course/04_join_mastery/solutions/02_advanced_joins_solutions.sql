-- Chapter 04: 조인(JOIN) 마스터하기 - 고급 조인 연습 해답
-- 난이도: 중급-고급

-- =============================================================================
-- 1. 복잡한 SELF JOIN
-- =============================================================================

-- 1-1. 조직도 생성: 각 직원과 그의 모든 상급자들을 계층적으로 조회하세요.
WITH RECURSIVE org_hierarchy AS (
    -- 기본 케이스: 모든 직원
    SELECT 
        employee_id,
        first_name || ' ' || last_name AS employee_name,
        manager_id,
        job_title,
        1 AS level,
        ARRAY[employee_id] AS path
    FROM employees
    WHERE manager_id IS NULL
    
    UNION ALL
    
    -- 재귀 케이스: 각 레벨의 직원들
    SELECT 
        e.employee_id,
        e.first_name || ' ' || e.last_name,
        e.manager_id,
        e.job_title,
        oh.level + 1,
        oh.path || e.employee_id
    FROM employees e
    JOIN org_hierarchy oh ON e.manager_id = oh.employee_id
)
SELECT 
    level,
    REPEAT('  ', level - 1) || employee_name AS hierarchical_name,
    job_title
FROM org_hierarchy
ORDER BY path;

-- 1-2. 같은 부서 내에서 자신보다 급여가 높은 동료가 몇 명인지 조회하세요.
SELECT 
    e1.first_name || ' ' || e1.last_name AS employee_name,
    d.dept_name,
    e1.salary,
    COUNT(e2.employee_id) AS higher_paid_colleagues
FROM employees e1
JOIN departments d ON e1.department_id = d.dept_id
LEFT JOIN employees e2 ON e1.department_id = e2.department_id 
    AND e1.salary < e2.salary
GROUP BY e1.employee_id, e1.first_name, e1.last_name, d.dept_name, e1.salary
ORDER BY d.dept_name, e1.salary DESC;

-- 1-3. 연속된 날짜에 주문한 고객들을 찾으세요.
SELECT 
    c.customer_name,
    o1.order_date AS first_order_date,
    o2.order_date AS second_order_date,
    o2.order_date - o1.order_date AS days_difference
FROM orders o1
JOIN orders o2 ON o1.customer_id = o2.customer_id 
    AND o2.order_date = o1.order_date + 1
JOIN customers c ON o1.customer_id = c.customer_id
ORDER BY c.customer_name, o1.order_date;

-- =============================================================================
-- 2. 조건부 복합 JOIN
-- =============================================================================

-- 2-1. 고객 유형에 따라 다른 할인 정책을 적용한 주문 정보를 조회하세요.
SELECT 
    c.customer_name,
    o.order_number,
    o.total_amount AS original_amount,
    CASE c.customer_type
        WHEN 'VIP' THEN 10
        WHEN 'regular' THEN 5
        WHEN 'new' THEN 3
        ELSE 0
    END AS discount_rate,
    o.total_amount * (1 - CASE c.customer_type
        WHEN 'VIP' THEN 0.10
        WHEN 'regular' THEN 0.05
        WHEN 'new' THEN 0.03
        ELSE 0
    END) AS discounted_amount
FROM customers c
JOIN orders o ON c.customer_id = o.customer_id
ORDER BY c.customer_type, o.order_date;

-- 2-2. 상품 카테고리별로 다른 배송비 정책을 적용한 주문 내역을 조회하세요.
SELECT 
    c.customer_name,
    o.order_number,
    cat.category_name,
    SUM(oi.quantity * oi.unit_price) AS order_subtotal,
    CASE 
        WHEN cat.category_name = '전자제품' AND SUM(oi.quantity * oi.unit_price) >= 500000 THEN 0
        WHEN cat.category_name = '전자제품' THEN 0
        WHEN cat.category_name = '의류' AND SUM(oi.quantity * oi.unit_price) >= 30000 THEN 0
        WHEN cat.category_name = '의류' THEN 3000
        WHEN SUM(oi.quantity * oi.unit_price) >= 50000 THEN 0
        ELSE 5000
    END AS shipping_fee
FROM customers c
JOIN orders o ON c.customer_id = o.customer_id
JOIN order_items oi ON o.order_id = oi.order_id
JOIN products p ON oi.product_id = p.product_id
JOIN categories cat ON p.category_id = cat.category_id
GROUP BY c.customer_name, o.order_number, cat.category_name
ORDER BY c.customer_name, o.order_date;

-- 2-3. 계절별 할인 상품과 일반 상품을 구분하여 판매 현황을 조회하세요.
SELECT 
    p.product_name,
    c.category_name,
    CASE 
        WHEN EXTRACT(MONTH FROM o.order_date) IN (12, 1, 2) THEN '겨울'
        WHEN EXTRACT(MONTH FROM o.order_date) IN (3, 4, 5) THEN '봄'
        WHEN EXTRACT(MONTH FROM o.order_date) IN (6, 7, 8) THEN '여름'
        ELSE '가을'
    END AS season,
    p.price AS original_price,
    CASE 
        WHEN sd.discount_rate IS NOT NULL THEN p.price * (1 - sd.discount_rate)
        ELSE p.price
    END AS sale_price,
    SUM(oi.quantity) AS total_quantity,
    SUM(oi.quantity * oi.unit_price) AS total_revenue
FROM products p
JOIN categories c ON p.category_id = c.category_id
JOIN order_items oi ON p.product_id = oi.product_id
JOIN orders o ON oi.order_id = o.order_id
LEFT JOIN seasonal_discounts sd ON p.product_id = sd.product_id 
    AND EXTRACT(MONTH FROM o.order_date) BETWEEN sd.start_month AND sd.end_month
GROUP BY p.product_name, c.category_name, p.price, 
         EXTRACT(MONTH FROM o.order_date), sd.discount_rate
ORDER BY total_revenue DESC;

-- =============================================================================
-- 3. 서브쿼리와 JOIN 조합
-- =============================================================================

-- 3-1. 평균 주문 금액보다 큰 주문을 한 고객들의 상세 정보를 조회하세요.
WITH avg_order AS (
    SELECT AVG(total_amount) AS overall_avg
    FROM orders
),
high_value_customers AS (
    SELECT DISTINCT o.customer_id
    FROM orders o
    CROSS JOIN avg_order ao
    WHERE o.total_amount > ao.overall_avg
)
SELECT 
    c.customer_name,
    COUNT(o.order_id) AS order_count,
    ROUND(AVG(o.total_amount), 2) AS avg_order_amount,
    MAX(o.total_amount) AS max_order_amount
FROM customers c
JOIN high_value_customers hvc ON c.customer_id = hvc.customer_id
JOIN orders o ON c.customer_id = o.customer_id
GROUP BY c.customer_id, c.customer_name
ORDER BY avg_order_amount DESC;

-- 3-2. 각 카테고리에서 가장 많이 팔린 상품과, 해당 카테고리의 총 매출을 조회하세요.
WITH category_sales AS (
    SELECT 
        p.category_id,
        p.product_id,
        p.product_name,
        SUM(oi.quantity) AS total_quantity,
        ROW_NUMBER() OVER (PARTITION BY p.category_id ORDER BY SUM(oi.quantity) DESC) AS rn
    FROM products p
    JOIN order_items oi ON p.product_id = oi.product_id
    GROUP BY p.category_id, p.product_id, p.product_name
),
category_totals AS (
    SELECT 
        c.category_id,
        c.category_name,
        SUM(oi.quantity * oi.unit_price) AS category_total_revenue
    FROM categories c
    JOIN products p ON c.category_id = p.category_id
    JOIN order_items oi ON p.product_id = oi.product_id
    GROUP BY c.category_id, c.category_name
)
SELECT 
    ct.category_name,
    cs.product_name AS best_selling_product,
    cs.total_quantity AS product_sales_quantity,
    ct.category_total_revenue
FROM category_sales cs
JOIN category_totals ct ON cs.category_id = ct.category_id
WHERE cs.rn = 1
ORDER BY ct.category_total_revenue DESC;

-- 3-3. 직원별 매출 실적이 부서 평균보다 높은 직원들을 조회하세요.
WITH employee_sales AS (
    SELECT 
        e.employee_id,
        e.first_name || ' ' || e.last_name AS employee_name,
        e.department_id,
        COALESCE(SUM(o.total_amount), 0) AS personal_sales
    FROM employees e
    LEFT JOIN orders o ON e.employee_id = o.sales_rep_id
    GROUP BY e.employee_id, e.first_name, e.last_name, e.department_id
),
department_avg AS (
    SELECT 
        department_id,
        AVG(personal_sales) AS dept_avg_sales
    FROM employee_sales
    GROUP BY department_id
)
SELECT 
    d.dept_name,
    es.employee_name,
    es.personal_sales,
    ROUND(da.dept_avg_sales, 2) AS dept_avg_sales,
    ROUND(es.personal_sales - da.dept_avg_sales, 2) AS difference
FROM employee_sales es
JOIN department_avg da ON es.department_id = da.department_id
JOIN departments d ON es.department_id = d.dept_id
WHERE es.personal_sales > da.dept_avg_sales
ORDER BY difference DESC;

-- =============================================================================
-- 4. 윈도우 함수와 JOIN
-- =============================================================================

-- 4-1. 각 고객의 주문 이력과 누적 주문 금액을 조회하세요.
SELECT 
    c.customer_name,
    o.order_date,
    o.total_amount,
    SUM(o.total_amount) OVER (
        PARTITION BY c.customer_id 
        ORDER BY o.order_date 
        ROWS UNBOUNDED PRECEDING
    ) AS cumulative_amount,
    ROW_NUMBER() OVER (
        PARTITION BY c.customer_id 
        ORDER BY o.order_date
    ) AS order_sequence
FROM customers c
JOIN orders o ON c.customer_id = o.customer_id
ORDER BY c.customer_name, o.order_date;

-- 4-2. 월별 매출 현황과 전월 대비 증감률을 조회하세요.
WITH monthly_sales AS (
    SELECT 
        EXTRACT(YEAR FROM o.order_date) AS year,
        EXTRACT(MONTH FROM o.order_date) AS month,
        SUM(o.total_amount) AS monthly_revenue
    FROM orders o
    GROUP BY EXTRACT(YEAR FROM o.order_date), EXTRACT(MONTH FROM o.order_date)
)
SELECT 
    year,
    month,
    monthly_revenue,
    LAG(monthly_revenue) OVER (ORDER BY year, month) AS prev_month_revenue,
    ROUND(
        (monthly_revenue - LAG(monthly_revenue) OVER (ORDER BY year, month)) * 100.0 / 
        NULLIF(LAG(monthly_revenue) OVER (ORDER BY year, month), 0), 2
    ) AS growth_rate_percent,
    ROW_NUMBER() OVER (ORDER BY monthly_revenue DESC) AS revenue_rank
FROM monthly_sales
ORDER BY year, month;

-- 4-3. 각 상품의 일별 판매량과 7일 이동평균을 조회하세요.
WITH daily_sales AS (
    SELECT 
        p.product_name,
        o.order_date,
        SUM(oi.quantity) AS daily_quantity
    FROM products p
    JOIN order_items oi ON p.product_id = oi.product_id
    JOIN orders o ON oi.order_id = o.order_id
    GROUP BY p.product_name, o.order_date
)
SELECT 
    product_name,
    order_date,
    daily_quantity,
    ROUND(
        AVG(daily_quantity) OVER (
            PARTITION BY product_name 
            ORDER BY order_date 
            ROWS BETWEEN 6 PRECEDING AND CURRENT ROW
        ), 2
    ) AS seven_day_moving_avg
FROM daily_sales
ORDER BY product_name, order_date;

-- =============================================================================
-- 5. FULL OUTER JOIN과 데이터 품질 검증
-- =============================================================================

-- 5-1. 고객 테이블과 주문 테이블의 데이터 무결성을 검증하세요.
SELECT 
    COALESCE(c.customer_id, o.customer_id) AS customer_id,
    c.customer_name,
    o.order_id,
    CASE 
        WHEN c.customer_id IS NULL THEN 'Missing Customer Record'
        WHEN o.order_id IS NULL THEN 'Customer with No Orders'
        ELSE 'Valid Data'
    END AS data_status
FROM customers c
FULL OUTER JOIN orders o ON c.customer_id = o.customer_id
WHERE c.customer_id IS NULL OR o.order_id IS NULL
ORDER BY data_status, customer_id;

-- 5-2. 상품 재고와 실제 판매 데이터의 일치성을 검증하세요.
SELECT 
    COALESCE(p.product_id, oi.product_id) AS product_id,
    p.product_name,
    p.current_stock,
    COALESCE(SUM(oi.quantity), 0) AS total_sold,
    CASE 
        WHEN p.product_id IS NULL THEN 'Sales without Product Record'
        WHEN oi.product_id IS NULL THEN 'Product never sold'
        ELSE 'Valid Data'
    END AS data_status
FROM products p
FULL OUTER JOIN order_items oi ON p.product_id = oi.product_id
WHERE p.product_id IS NULL OR oi.product_id IS NULL
GROUP BY p.product_id, p.product_name, p.current_stock, oi.product_id
ORDER BY data_status, product_id;

-- 5-3. 직원 테이블과 급여 테이블의 데이터 일관성을 검증하세요.
SELECT 
    COALESCE(e.employee_id, s.employee_id) AS employee_id,
    e.first_name || ' ' || e.last_name AS employee_name,
    s.salary,
    s.effective_date,
    CASE 
        WHEN e.employee_id IS NULL THEN 'Salary without Employee Record'
        WHEN s.employee_id IS NULL THEN 'Employee without Salary Record'
        ELSE 'Valid Data'
    END AS data_status
FROM employees e
FULL OUTER JOIN salaries s ON e.employee_id = s.employee_id
WHERE e.employee_id IS NULL OR s.employee_id IS NULL
ORDER BY data_status, employee_id;

-- =============================================================================
-- 6. 성능 최적화 문제
-- =============================================================================

-- 6-1. 대용량 주문 데이터에서 최근 1개월 고객별 구매 패턴을 효율적으로 조회하세요.
-- 권장 인덱스: CREATE INDEX idx_orders_date_customer ON orders (order_date, customer_id);
-- 권장 인덱스: CREATE INDEX idx_order_items_order_product ON order_items (order_id, product_id);

WITH recent_orders AS (
    SELECT 
        o.customer_id,
        o.order_date,
        o.total_amount,
        oi.product_id,
        oi.quantity
    FROM orders o
    JOIN order_items oi ON o.order_id = oi.order_id
    WHERE o.order_date >= CURRENT_DATE - INTERVAL '1 month'
)
SELECT 
    c.customer_name,
    COUNT(DISTINCT ro.order_date) AS purchase_days,
    COUNT(DISTINCT ro.product_id) AS unique_products,
    SUM(ro.total_amount) AS total_spent,
    AVG(ro.total_amount) AS avg_order_value,
    ROUND(
        COUNT(DISTINCT ro.order_date)::DECIMAL / 
        EXTRACT(DAYS FROM CURRENT_DATE - (CURRENT_DATE - INTERVAL '1 month')), 3
    ) AS purchase_frequency
FROM customers c
JOIN recent_orders ro ON c.customer_id = ro.customer_id
GROUP BY c.customer_id, c.customer_name
ORDER BY total_spent DESC;

-- 6-2. 상품 추천을 위한 고객별 구매 유사도를 계산하세요.
WITH customer_products AS (
    SELECT DISTINCT 
        o.customer_id,
        oi.product_id
    FROM orders o
    JOIN order_items oi ON o.order_id = oi.order_id
),
customer_pairs AS (
    SELECT 
        cp1.customer_id AS customer_a,
        cp2.customer_id AS customer_b,
        COUNT(*) AS common_products,
        (SELECT COUNT(DISTINCT product_id) FROM customer_products WHERE customer_id = cp1.customer_id) AS products_a,
        (SELECT COUNT(DISTINCT product_id) FROM customer_products WHERE customer_id = cp2.customer_id) AS products_b
    FROM customer_products cp1
    JOIN customer_products cp2 ON cp1.product_id = cp2.product_id 
        AND cp1.customer_id < cp2.customer_id
    GROUP BY cp1.customer_id, cp2.customer_id
)
SELECT 
    ca.customer_name AS customer_a_name,
    cb.customer_name AS customer_b_name,
    cp.common_products,
    ROUND(
        cp.common_products::DECIMAL / 
        (cp.products_a + cp.products_b - cp.common_products), 3
    ) AS jaccard_similarity
FROM customer_pairs cp
JOIN customers ca ON cp.customer_a = ca.customer_id
JOIN customers cb ON cp.customer_b = cb.customer_id
WHERE cp.common_products >= 3
ORDER BY jaccard_similarity DESC
LIMIT 20;

-- 6-3. 재고 회전율이 낮은 상품들을 효율적으로 찾는 쿼리를 작성하세요.
WITH product_sales AS (
    SELECT 
        p.product_id,
        p.product_name,
        p.current_stock,
        p.price,
        COALESCE(SUM(oi.quantity), 0) AS total_sold_6months
    FROM products p
    LEFT JOIN order_items oi ON p.product_id = oi.product_id
    LEFT JOIN orders o ON oi.order_id = o.order_id 
        AND o.order_date >= CURRENT_DATE - INTERVAL '6 months'
    WHERE p.is_active = TRUE
    GROUP BY p.product_id, p.product_name, p.current_stock, p.price
)
SELECT 
    product_name,
    current_stock,
    total_sold_6months,
    CASE 
        WHEN current_stock = 0 THEN NULL
        ELSE ROUND(total_sold_6months::DECIMAL / current_stock, 2)
    END AS turnover_ratio,
    current_stock * price AS inventory_value,
    CASE 
        WHEN total_sold_6months = 0 THEN 'No Sales'
        WHEN ROUND(total_sold_6months::DECIMAL / NULLIF(current_stock, 0), 2) < 0.5 THEN 'Low Turnover'
        WHEN ROUND(total_sold_6months::DECIMAL / NULLIF(current_stock, 0), 2) < 1.0 THEN 'Medium Turnover'
        ELSE 'High Turnover'
    END AS turnover_category
FROM product_sales
WHERE current_stock > 0
ORDER BY turnover_ratio ASC NULLS FIRST, inventory_value DESC;