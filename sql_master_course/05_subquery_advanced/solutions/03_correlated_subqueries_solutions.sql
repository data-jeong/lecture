-- Chapter 05: 상관 서브쿼리 실습 문제 해답
-- 각 문제를 해결하는 SQL 쿼리 해답

-- 문제 1: 각 부서에서 급여가 상위 3위 안에 드는 직원을 조회하세요.
SELECT 
    d.dept_name,
    e.first_name || ' ' || e.last_name AS employee_name,
    e.salary,
    (SELECT COUNT(*) + 1 
     FROM employees e2 
     WHERE e2.department_id = e.department_id 
     AND e2.salary > e.salary) AS dept_rank
FROM employees e
JOIN departments d ON e.department_id = d.dept_id
WHERE (SELECT COUNT(*) 
       FROM employees e2 
       WHERE e2.department_id = e.department_id 
       AND e2.salary > e.salary) < 3
ORDER BY d.dept_name, e.salary DESC;

-- 문제 2: 각 고객의 최신 주문 정보를 조회하세요.
SELECT 
    c.customer_name,
    o.order_date AS latest_order_date,
    o.total_amount
FROM customers c
JOIN orders o ON c.customer_id = o.customer_id
WHERE o.order_date = (SELECT MAX(o2.order_date)
                      FROM orders o2 
                      WHERE o2.customer_id = c.customer_id)
ORDER BY c.customer_name;

-- 문제 3: 각 카테고리에서 가장 인기있는 상품(주문 수량 기준)을 조회하세요.
SELECT 
    cat.category_name,
    p.product_name,
    SUM(oi.quantity) AS total_quantity
FROM categories cat
JOIN products p ON cat.category_id = p.category_id
JOIN order_items oi ON p.product_id = oi.product_id
GROUP BY cat.category_name, p.product_name, p.category_id
HAVING SUM(oi.quantity) = (
    SELECT MAX(total_qty)
    FROM (
        SELECT SUM(oi2.quantity) AS total_qty
        FROM products p2
        JOIN order_items oi2 ON p2.product_id = oi2.product_id
        WHERE p2.category_id = p.category_id
        GROUP BY p2.product_id
    ) sub
)
ORDER BY cat.category_name;

-- 문제 4: 각 직원보다 급여가 높은 동일 부서 직원의 수를 조회하세요.
SELECT 
    e.first_name || ' ' || e.last_name AS employee_name,
    d.dept_name,
    e.salary,
    (SELECT COUNT(*) 
     FROM employees e2 
     WHERE e2.department_id = e.department_id 
     AND e2.salary > e.salary) AS higher_paid_colleagues
FROM employees e
JOIN departments d ON e.department_id = d.dept_id
ORDER BY d.dept_name, e.salary DESC;

-- 문제 5: 평균 주문 금액보다 큰 주문을 한 고객의 총 주문 수를 조회하세요.
SELECT 
    c.customer_name,
    (SELECT COUNT(*) 
     FROM orders o1 
     WHERE o1.customer_id = c.customer_id) AS total_orders,
    (SELECT COUNT(*) 
     FROM orders o2 
     WHERE o2.customer_id = c.customer_id 
     AND o2.total_amount > (SELECT AVG(total_amount) FROM orders)) AS above_avg_orders,
    ROUND(
        (SELECT COUNT(*) 
         FROM orders o2 
         WHERE o2.customer_id = c.customer_id 
         AND o2.total_amount > (SELECT AVG(total_amount) FROM orders)) * 100.0 /
        NULLIF((SELECT COUNT(*) FROM orders o1 WHERE o1.customer_id = c.customer_id), 0), 2
    ) AS above_avg_percentage
FROM customers c
WHERE EXISTS (SELECT 1 FROM orders o WHERE o.customer_id = c.customer_id)
ORDER BY above_avg_percentage DESC;

-- 문제 6: 각 상품에 대해 해당 카테고리의 평균 가격과 비교하여 비싼지 저렴한지 표시하세요.
SELECT 
    p.product_name,
    p.price,
    ROUND((SELECT AVG(p2.price) 
           FROM products p2 
           WHERE p2.category_id = p.category_id), 2) AS category_avg_price,
    CASE 
        WHEN p.price > (SELECT AVG(p2.price) * 1.1 
                        FROM products p2 
                        WHERE p2.category_id = p.category_id) THEN '비쌌'
        WHEN p.price < (SELECT AVG(p2.price) * 0.9 
                        FROM products p2 
                        WHERE p2.category_id = p.category_id) THEN '저렴'
        ELSE '평균'
    END AS price_category
FROM products p
ORDER BY p.category_id, p.price DESC;

-- 문제 7: 재고가 부족한 상품을 식별하세요.
SELECT 
    p.product_name,
    p.current_stock,
    ROUND((SELECT AVG(p2.current_stock) 
           FROM products p2 
           WHERE p2.category_id = p.category_id), 2) AS category_avg_stock,
    ROUND(
        (p.current_stock * 100.0) / 
        (SELECT AVG(p2.current_stock) FROM products p2 WHERE p2.category_id = p.category_id), 2
    ) AS stock_ratio_percent
FROM products p
WHERE p.current_stock < (SELECT AVG(p2.current_stock) * 0.5 
                         FROM products p2 
                         WHERE p2.category_id = p.category_id)
ORDER BY stock_ratio_percent ASC;

-- 문제 8: 각 월별로 신규 고객 수를 조회하세요.
SELECT 
    TO_CHAR(o.order_date, 'YYYY-MM') AS year_month,
    COUNT(DISTINCT o.customer_id) AS total_customers,
    COUNT(DISTINCT CASE 
        WHEN NOT EXISTS (
            SELECT 1 FROM orders o2 
            WHERE o2.customer_id = o.customer_id 
            AND o2.order_date < DATE_TRUNC('month', o.order_date)
        ) THEN o.customer_id 
    END) AS new_customers,
    ROUND(
        COUNT(DISTINCT CASE 
            WHEN NOT EXISTS (
                SELECT 1 FROM orders o2 
                WHERE o2.customer_id = o.customer_id 
                AND o2.order_date < DATE_TRUNC('month', o.order_date)
            ) THEN o.customer_id 
        END) * 100.0 / COUNT(DISTINCT o.customer_id), 2
    ) AS new_customer_percentage
FROM orders o
GROUP BY TO_CHAR(o.order_date, 'YYYY-MM')
ORDER BY year_month;

-- 문제 9: 각 직원의 성과를 동일 직급의 평균과 비교하세요.
-- 가정: employee_performance 테이블이 있다고 가정
SELECT 
    e.first_name || ' ' || e.last_name AS employee_name,
    e.job_title,
    COALESCE(ep.performance_score, 0) AS individual_performance,
    ROUND((SELECT AVG(ep2.performance_score) 
           FROM employees e2 
           JOIN employee_performance ep2 ON e2.employee_id = ep2.employee_id
           WHERE e2.job_title = e.job_title), 2) AS title_avg_performance,
    ROUND(
        COALESCE(ep.performance_score, 0) - 
        (SELECT AVG(ep2.performance_score) 
         FROM employees e2 
         JOIN employee_performance ep2 ON e2.employee_id = ep2.employee_id
         WHERE e2.job_title = e.job_title), 2
    ) AS relative_performance
FROM employees e
LEFT JOIN employee_performance ep ON e.employee_id = ep.employee_id
ORDER BY relative_performance DESC;

-- 문제 10: 고객별 충성도 점수를 계산하세요.
WITH customer_metrics AS (
    SELECT 
        c.customer_id,
        c.customer_name,
        COUNT(o.order_id) AS order_frequency,
        AVG(o.total_amount) AS avg_order_amount,
        MAX(o.order_date) AS last_order_date
    FROM customers c
    LEFT JOIN orders o ON c.customer_id = o.customer_id
    GROUP BY c.customer_id, c.customer_name
)
SELECT 
    cm.customer_name,
    -- 주문 빈도 점수 (상위 백분위)
    ROUND(
        (SELECT COUNT(*) FROM customer_metrics cm2 WHERE cm2.order_frequency < cm.order_frequency) * 100.0 / 
        (SELECT COUNT(*) FROM customer_metrics), 0
    ) AS frequency_score,
    -- 평균 주문 금액 점수
    ROUND(
        (SELECT COUNT(*) FROM customer_metrics cm2 WHERE cm2.avg_order_amount < cm.avg_order_amount) * 100.0 / 
        (SELECT COUNT(*) FROM customer_metrics), 0
    ) AS amount_score,
    -- 최신성 점수 (최근 주문일 기준)
    ROUND(
        (SELECT COUNT(*) FROM customer_metrics cm2 WHERE cm2.last_order_date < cm.last_order_date) * 100.0 / 
        (SELECT COUNT(*) FROM customer_metrics), 0
    ) AS recency_score,
    -- 총 충성도 점수 (가중 평균)
    ROUND((
        (SELECT COUNT(*) FROM customer_metrics cm2 WHERE cm2.order_frequency < cm.order_frequency) * 100.0 / 
        (SELECT COUNT(*) FROM customer_metrics) * 0.4 +
        (SELECT COUNT(*) FROM customer_metrics cm2 WHERE cm2.avg_order_amount < cm.avg_order_amount) * 100.0 / 
        (SELECT COUNT(*) FROM customer_metrics) * 0.3 +
        (SELECT COUNT(*) FROM customer_metrics cm2 WHERE cm2.last_order_date < cm.last_order_date) * 100.0 / 
        (SELECT COUNT(*) FROM customer_metrics) * 0.3
    ), 0) AS total_loyalty_score
FROM customer_metrics cm
ORDER BY total_loyalty_score DESC;

-- 문제 11: 각 상품의 계절별 판매 성과를 분석하세요.
SELECT 
    p.product_name,
    EXTRACT(QUARTER FROM o.order_date) AS quarter,
    SUM(oi.quantity * oi.unit_price) AS quarter_revenue,
    ROUND((SELECT AVG(quarterly_revenue)
           FROM (
               SELECT SUM(oi2.quantity * oi2.unit_price) AS quarterly_revenue
               FROM order_items oi2
               JOIN orders o2 ON oi2.order_id = o2.order_id
               WHERE oi2.product_id = p.product_id
               GROUP BY EXTRACT(QUARTER FROM o2.order_date)
           ) sub), 2) AS annual_avg_revenue,
    ROUND(
        SUM(oi.quantity * oi.unit_price) / 
        (SELECT AVG(quarterly_revenue)
         FROM (
             SELECT SUM(oi2.quantity * oi2.unit_price) AS quarterly_revenue
             FROM order_items oi2
             JOIN orders o2 ON oi2.order_id = o2.order_id
             WHERE oi2.product_id = p.product_id
             GROUP BY EXTRACT(QUARTER FROM o2.order_date)
         ) sub), 2
    ) AS performance_index
FROM products p
JOIN order_items oi ON p.product_id = oi.product_id
JOIN orders o ON oi.order_id = o.order_id
GROUP BY p.product_id, p.product_name, EXTRACT(QUARTER FROM o.order_date)
ORDER BY p.product_name, quarter;

-- 문제 12: 경쟁 상품 분석을 수행하세요.
SELECT 
    p1.product_name,
    p1.price,
    (SELECT COUNT(*) 
     FROM products p2 
     WHERE p2.category_id = p1.category_id 
     AND p2.product_id != p1.product_id
     AND p2.price BETWEEN p1.price * 0.9 AND p1.price * 1.1) AS competing_products,
    ROUND(
        (SELECT COUNT(*) 
         FROM products p2 
         WHERE p2.category_id = p1.category_id 
         AND p2.price < p1.price) * 100.0 / 
        (SELECT COUNT(*) - 1 
         FROM products p2 
         WHERE p2.category_id = p1.category_id), 2
    ) AS price_percentile
FROM products p1
ORDER BY p1.category_id, competing_products DESC;

-- 문제 13: 부서별 급여 분산도를 계산하세요.
SELECT 
    d.dept_name,
    ROUND(AVG(e.salary), 2) AS avg_salary,
    ROUND(STDDEV(e.salary), 2) AS salary_stddev,
    ROUND(STDDEV(e.salary) / AVG(e.salary) * 100, 2) AS coefficient_of_variation,
    ROUND(
        STDDEV(e.salary) / (SELECT STDDEV(salary) FROM employees), 2
    ) AS relative_dispersion
FROM departments d
JOIN employees e ON d.dept_id = e.department_id
GROUP BY d.dept_id, d.dept_name
ORDER BY coefficient_of_variation DESC;

-- 문제 14: 고객의 구매 패턴 변화를 분석하세요.
SELECT 
    c.customer_name,
    COALESCE((SELECT SUM(o1.total_amount)
              FROM orders o1 
              WHERE o1.customer_id = c.customer_id 
              AND o1.order_date >= CURRENT_DATE - INTERVAL '3 months'), 0) AS recent_3m_amount,
    COALESCE((SELECT SUM(o2.total_amount)
              FROM orders o2 
              WHERE o2.customer_id = c.customer_id 
              AND o2.order_date >= CURRENT_DATE - INTERVAL '6 months'
              AND o2.order_date < CURRENT_DATE - INTERVAL '3 months'), 0) AS previous_3m_amount,
    ROUND(
        CASE 
            WHEN (SELECT SUM(o2.total_amount)
                  FROM orders o2 
                  WHERE o2.customer_id = c.customer_id 
                  AND o2.order_date >= CURRENT_DATE - INTERVAL '6 months'
                  AND o2.order_date < CURRENT_DATE - INTERVAL '3 months') > 0
            THEN ((SELECT SUM(o1.total_amount)
                   FROM orders o1 
                   WHERE o1.customer_id = c.customer_id 
                   AND o1.order_date >= CURRENT_DATE - INTERVAL '3 months') - 
                  (SELECT SUM(o2.total_amount)
                   FROM orders o2 
                   WHERE o2.customer_id = c.customer_id 
                   AND o2.order_date >= CURRENT_DATE - INTERVAL '6 months'
                   AND o2.order_date < CURRENT_DATE - INTERVAL '3 months')) * 100.0 /
                  (SELECT SUM(o2.total_amount)
                   FROM orders o2 
                   WHERE o2.customer_id = c.customer_id 
                   AND o2.order_date >= CURRENT_DATE - INTERVAL '6 months'
                   AND o2.order_date < CURRENT_DATE - INTERVAL '3 months')
            ELSE NULL
        END, 2
    ) AS change_percentage,
    CASE 
        WHEN (SELECT SUM(o1.total_amount)
              FROM orders o1 
              WHERE o1.customer_id = c.customer_id 
              AND o1.order_date >= CURRENT_DATE - INTERVAL '3 months') > 
             (SELECT SUM(o2.total_amount)
              FROM orders o2 
              WHERE o2.customer_id = c.customer_id 
              AND o2.order_date >= CURRENT_DATE - INTERVAL '6 months'
              AND o2.order_date < CURRENT_DATE - INTERVAL '3 months') * 1.1 THEN '증가'
        WHEN (SELECT SUM(o1.total_amount)
              FROM orders o1 
              WHERE o1.customer_id = c.customer_id 
              AND o1.order_date >= CURRENT_DATE - INTERVAL '3 months') < 
             (SELECT SUM(o2.total_amount)
              FROM orders o2 
              WHERE o2.customer_id = c.customer_id 
              AND o2.order_date >= CURRENT_DATE - INTERVAL '6 months'
              AND o2.order_date < CURRENT_DATE - INTERVAL '3 months') * 0.9 THEN '감소'
        ELSE '유지'
    END AS trend
FROM customers c
WHERE EXISTS (SELECT 1 FROM orders o WHERE o.customer_id = c.customer_id)
ORDER BY change_percentage DESC NULLS LAST;

-- 문제 15: 상품별 교차 판매(Cross-selling) 기회를 식별하세요.
SELECT 
    p1.product_name AS base_product,
    c2.category_name AS related_category,
    COUNT(*) AS co_purchase_count,
    ROUND(
        COUNT(*) * 100.0 / 
        (SELECT COUNT(DISTINCT oi1.order_id) 
         FROM order_items oi1 
         WHERE oi1.product_id = p1.product_id), 2
    ) AS association_percentage
FROM products p1
JOIN order_items oi1 ON p1.product_id = oi1.product_id
JOIN orders o ON oi1.order_id = o.order_id
JOIN order_items oi2 ON o.order_id = oi2.order_id
JOIN products p2 ON oi2.product_id = p2.product_id
JOIN categories c2 ON p2.category_id = c2.category_id
WHERE p1.category_id != p2.category_id  -- 다른 카테고리만
GROUP BY p1.product_id, p1.product_name, c2.category_id, c2.category_name
HAVING COUNT(*) >= 5  -- 최소 5회 이상 동시 구매
ORDER BY p1.product_name, association_percentage DESC;