-- Chapter 05: 고급 서브쿼리 실습 문제 해답

-- 문제 1: 각 부서에서 급여 순위 TOP 2인 직원을 조회하세요.
SELECT 
    e1.department,
    e1.first_name,
    e1.last_name,
    e1.salary,
    (SELECT COUNT(*) 
     FROM employees e2 
     WHERE e2.department = e1.department 
     AND e2.salary > e1.salary) + 1 as dept_rank
FROM employees e1
WHERE (
    SELECT COUNT(*) 
    FROM employees e2 
    WHERE e2.department = e1.department 
    AND e2.salary > e1.salary
) < 2
ORDER BY e1.department, e1.salary DESC;

-- 문제 2: 고객별 총 주문 금액과 평균 주문 금액을 조회하되,
-- 평균 주문 금액이 전체 고객 평균보다 높은 고객만 표시하세요.
SELECT 
    customer_stats.company_name,
    customer_stats.total_amount,
    customer_stats.avg_amount
FROM (
    SELECT 
        c.company_name,
        SUM(o.total_amount) as total_amount,
        AVG(o.total_amount) as avg_amount
    FROM customers c
    JOIN orders o ON c.customer_id = o.customer_id
    GROUP BY c.customer_id, c.company_name
) customer_stats
WHERE customer_stats.avg_amount > (
    SELECT AVG(o.total_amount) 
    FROM orders o
)
ORDER BY customer_stats.avg_amount DESC;

-- 문제 3: 재고가 해당 카테고리 평균보다 적으면서, 동시에 
-- 평균 평점이 4.0 이상인 상품의 카테고리별 통계를 조회하세요.
SELECT 
    category,
    COUNT(*) as product_count,
    AVG(price) as avg_price
FROM products p
WHERE stock_quantity < (
    SELECT AVG(stock_quantity) 
    FROM products p2 
    WHERE p2.category = p.category
)
AND EXISTS (
    SELECT 1 
    FROM product_reviews pr 
    WHERE pr.product_id = p.product_id
    GROUP BY pr.product_id
    HAVING AVG(pr.rating) >= 4.0
)
GROUP BY category
ORDER BY product_count DESC;

-- 문제 4: 2023년 각 월 대비 다음 달 주문 증가율을 계산하세요.
SELECT 
    current_month.order_month,
    current_month.order_count as current_orders,
    next_month.order_count as next_orders,
    CASE 
        WHEN current_month.order_count > 0 THEN
            ROUND(((next_month.order_count - current_month.order_count) * 100.0 / current_month.order_count), 2)
        ELSE NULL 
    END as growth_rate_percent
FROM (
    SELECT 
        EXTRACT(MONTH FROM order_date) as order_month,
        COUNT(*) as order_count
    FROM orders
    WHERE EXTRACT(YEAR FROM order_date) = 2023
    GROUP BY EXTRACT(MONTH FROM order_date)
) current_month
LEFT JOIN (
    SELECT 
        EXTRACT(MONTH FROM order_date) as order_month,
        COUNT(*) as order_count
    FROM orders
    WHERE EXTRACT(YEAR FROM order_date) = 2023
    GROUP BY EXTRACT(MONTH FROM order_date)
) next_month ON current_month.order_month + 1 = next_month.order_month
ORDER BY current_month.order_month;

-- 문제 5: 연속으로 3번 이상 주문한 고객을 찾으세요.
SELECT 
    c.company_name,
    COUNT(*) as consecutive_orders
FROM customers c
JOIN orders o ON c.customer_id = o.customer_id
WHERE EXISTS (
    SELECT 1
    FROM orders o2
    WHERE o2.customer_id = c.customer_id
    AND o2.order_date BETWEEN o.order_date - INTERVAL '90 days' AND o.order_date + INTERVAL '90 days'
    GROUP BY o2.customer_id
    HAVING COUNT(*) >= 3
)
GROUP BY c.customer_id, c.company_name
HAVING COUNT(*) >= 3
ORDER BY consecutive_orders DESC;

-- 문제 6: 각 상품에 대해 "대체 상품" 추천 로직을 구현하세요.
SELECT 
    p1.product_name as original_product,
    p2.product_name as alternative_product,
    p2.price - p1.price as price_difference,
    COALESCE(p2_avg.avg_rating, 0) - COALESCE(p1_avg.avg_rating, 0) as rating_difference
FROM products p1
JOIN products p2 ON p1.category = p2.category 
    AND p1.product_id != p2.product_id
    AND p2.price BETWEEN p1.price * 0.8 AND p1.price * 1.2
LEFT JOIN (
    SELECT product_id, AVG(rating) as avg_rating
    FROM product_reviews
    GROUP BY product_id
) p1_avg ON p1.product_id = p1_avg.product_id
LEFT JOIN (
    SELECT product_id, AVG(rating) as avg_rating
    FROM product_reviews
    GROUP BY product_id
) p2_avg ON p2.product_id = p2_avg.product_id
WHERE COALESCE(p2_avg.avg_rating, 0) > COALESCE(p1_avg.avg_rating, 0)
ORDER BY p1.product_name, rating_difference DESC;

-- 문제 7: 부서별 "스타 직원"을 찾으세요.
SELECT 
    e1.department,
    e1.first_name,
    e1.last_name,
    e1.salary,
    (SELECT COUNT(*) 
     FROM employees e2 
     WHERE e2.department = e1.department 
     AND e2.salary > e1.salary) + 1 as dept_salary_rank
FROM employees e1
WHERE e1.salary >= (
    SELECT 
        salary
    FROM employees e2
    WHERE e2.department = e1.department
    ORDER BY salary DESC
    LIMIT 1 OFFSET (
        SELECT CAST(COUNT(*) * 0.25 AS INT) 
        FROM employees e3 
        WHERE e3.department = e1.department
    )
)
AND e1.hire_date <= CURRENT_DATE - INTERVAL '2 years'
ORDER BY e1.department, e1.salary DESC;

-- 문제 8: 계절별 베스트셀러 상품을 찾으세요.
SELECT 
    seasonal_sales.quarter,
    p.product_name,
    seasonal_sales.total_quantity,
    seasonal_sales.total_revenue
FROM (
    SELECT 
        CASE 
            WHEN EXTRACT(MONTH FROM o.order_date) IN (1,2,3) THEN 'Q1'
            WHEN EXTRACT(MONTH FROM o.order_date) IN (4,5,6) THEN 'Q2'
            WHEN EXTRACT(MONTH FROM o.order_date) IN (7,8,9) THEN 'Q3'
            ELSE 'Q4'
        END as quarter,
        oi.product_id,
        SUM(oi.quantity) as total_quantity,
        SUM(oi.quantity * oi.unit_price) as total_revenue,
        ROW_NUMBER() OVER (
            PARTITION BY CASE 
                WHEN EXTRACT(MONTH FROM o.order_date) IN (1,2,3) THEN 'Q1'
                WHEN EXTRACT(MONTH FROM o.order_date) IN (4,5,6) THEN 'Q2'
                WHEN EXTRACT(MONTH FROM o.order_date) IN (7,8,9) THEN 'Q3'
                ELSE 'Q4'
            END 
            ORDER BY SUM(oi.quantity) DESC
        ) as rn
    FROM orders o
    JOIN order_items oi ON o.order_id = oi.order_id
    WHERE EXTRACT(YEAR FROM o.order_date) = 2023
    GROUP BY 
        CASE 
            WHEN EXTRACT(MONTH FROM o.order_date) IN (1,2,3) THEN 'Q1'
            WHEN EXTRACT(MONTH FROM o.order_date) IN (4,5,6) THEN 'Q2'
            WHEN EXTRACT(MONTH FROM o.order_date) IN (7,8,9) THEN 'Q3'
            ELSE 'Q4'
        END,
        oi.product_id
) seasonal_sales
JOIN products p ON seasonal_sales.product_id = p.product_id
WHERE seasonal_sales.rn = 1
ORDER BY seasonal_sales.quarter;

-- 문제 9: 고객 이탈 위험도를 계산하세요.
SELECT 
    c.company_name,
    last_orders.last_order_date,
    avg_intervals.avg_order_interval,
    CURRENT_DATE - last_orders.last_order_date as days_since_last_order,
    CASE 
        WHEN CURRENT_DATE - last_orders.last_order_date > avg_intervals.avg_order_interval + 90 THEN 'High Risk'
        WHEN CURRENT_DATE - last_orders.last_order_date > avg_intervals.avg_order_interval + 30 THEN 'Medium Risk'
        ELSE 'Low Risk'
    END as churn_risk
FROM customers c
JOIN (
    SELECT 
        customer_id,
        MAX(order_date) as last_order_date
    FROM orders
    GROUP BY customer_id
) last_orders ON c.customer_id = last_orders.customer_id
JOIN (
    SELECT 
        customer_id,
        AVG(day_diff) as avg_order_interval
    FROM (
        SELECT 
            customer_id,
            order_date - LAG(order_date) OVER (PARTITION BY customer_id ORDER BY order_date) as day_diff
        FROM orders
    ) order_intervals
    WHERE day_diff IS NOT NULL
    GROUP BY customer_id
) avg_intervals ON c.customer_id = avg_intervals.customer_id
WHERE CURRENT_DATE - last_orders.last_order_date >= 90
ORDER BY days_since_last_order DESC;

-- 문제 10: 상품 재주문률을 계산하세요.
SELECT 
    p.product_name,
    total_customers.total_customers,
    repeat_customers.repeat_customers,
    ROUND((repeat_customers.repeat_customers * 100.0 / total_customers.total_customers), 2) as repeat_rate_percent
FROM products p
JOIN (
    SELECT 
        oi.product_id,
        COUNT(DISTINCT o.customer_id) as total_customers
    FROM order_items oi
    JOIN orders o ON oi.order_id = o.order_id
    GROUP BY oi.product_id
) total_customers ON p.product_id = total_customers.product_id
JOIN (
    SELECT 
        oi.product_id,
        COUNT(DISTINCT o.customer_id) as repeat_customers
    FROM order_items oi
    JOIN orders o ON oi.order_id = o.order_id
    WHERE EXISTS (
        SELECT 1
        FROM order_items oi2
        JOIN orders o2 ON oi2.order_id = o2.order_id
        WHERE oi2.product_id = oi.product_id
        AND o2.customer_id = o.customer_id
        AND o2.order_date > o.order_date
    )
    GROUP BY oi.product_id
) repeat_customers ON p.product_id = repeat_customers.product_id
WHERE total_customers.total_customers > 1
ORDER BY repeat_rate_percent DESC;