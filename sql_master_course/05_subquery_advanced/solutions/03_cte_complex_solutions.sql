-- Chapter 05: CTE(Common Table Expression) 복합 실습 문제 해답

-- 문제 1: 고객 세그멘테이션 분석을 CTE로 구현하세요. (RFM 분석)
WITH customer_rfm AS (
    SELECT 
        c.customer_id,
        c.company_name,
        MAX(o.order_date) as last_order_date,
        COUNT(o.order_id) as frequency,
        SUM(o.total_amount) as monetary,
        CURRENT_DATE - MAX(o.order_date) as recency_days
    FROM customers c
    LEFT JOIN orders o ON c.customer_id = o.customer_id
    GROUP BY c.customer_id, c.company_name
),
rfm_scores AS (
    SELECT *,
        CASE 
            WHEN recency_days <= 30 THEN 5
            WHEN recency_days <= 90 THEN 4
            WHEN recency_days <= 180 THEN 3
            WHEN recency_days <= 365 THEN 2
            ELSE 1
        END as recency_score,
        CASE 
            WHEN frequency >= 5 THEN 5
            WHEN frequency >= 4 THEN 4
            WHEN frequency >= 3 THEN 3
            WHEN frequency >= 2 THEN 2
            ELSE 1
        END as frequency_score,
        CASE 
            WHEN monetary >= 2000 THEN 5
            WHEN monetary >= 1000 THEN 4
            WHEN monetary >= 500 THEN 3
            WHEN monetary >= 200 THEN 2
            ELSE 1
        END as monetary_score
    FROM customer_rfm
),
customer_segments AS (
    SELECT *,
        (recency_score + frequency_score + monetary_score) as rfm_total,
        CASE 
            WHEN (recency_score + frequency_score + monetary_score) >= 13 THEN 'Champions'
            WHEN (recency_score + frequency_score + monetary_score) >= 10 THEN 'Loyal Customers'
            WHEN (recency_score + frequency_score + monetary_score) >= 7 THEN 'Potential Loyalists'
            WHEN (recency_score + frequency_score + monetary_score) >= 5 THEN 'At Risk'
            ELSE 'Lost Customers'
        END as customer_segment
    FROM rfm_scores
)
SELECT 
    company_name,
    last_order_date,
    frequency,
    monetary,
    rfm_total,
    customer_segment
FROM customer_segments
ORDER BY rfm_total DESC, monetary DESC;

-- 문제 2: 조직도를 재귀 CTE로 구현하세요.
WITH RECURSIVE employee_hierarchy AS (
    -- Anchor: 최상위 관리자
    SELECT 
        employee_id,
        first_name,
        last_name,
        manager_id,
        position_level,
        department,
        CAST(first_name || ' ' || last_name AS TEXT) as org_path,
        1 as level
    FROM employees_hierarchy
    WHERE manager_id IS NULL
    
    UNION ALL
    
    -- Recursive: 하위 직원들
    SELECT 
        e.employee_id,
        e.first_name,
        e.last_name,
        e.manager_id,
        e.position_level,
        e.department,
        eh.org_path || ' -> ' || e.first_name || ' ' || e.last_name,
        eh.level + 1
    FROM employees_hierarchy e
    INNER JOIN employee_hierarchy eh ON e.manager_id = eh.employee_id
)
SELECT 
    first_name || ' ' || last_name as employee_name,
    department,
    level,
    org_path,
    (SELECT first_name || ' ' || last_name 
     FROM employees_hierarchy m 
     WHERE m.employee_id = employee_hierarchy.manager_id) as manager_name
FROM employee_hierarchy
ORDER BY level, department, first_name;

-- 문제 3: 제품 성과 분석을 다중 CTE로 구현하세요.
WITH product_sales AS (
    SELECT 
        p.product_id,
        p.product_name,
        p.category,
        p.price,
        COALESCE(SUM(oi.quantity * oi.unit_price), 0) as total_revenue,
        COALESCE(SUM(oi.quantity), 0) as total_quantity_sold
    FROM products p
    LEFT JOIN order_items oi ON p.product_id = oi.product_id
    GROUP BY p.product_id, p.product_name, p.category, p.price
),
product_ratings AS (
    SELECT 
        product_id,
        AVG(rating) as avg_rating,
        COUNT(*) as review_count
    FROM product_reviews
    GROUP BY product_id
),
product_repurchase AS (
    SELECT 
        oi.product_id,
        COUNT(DISTINCT o.customer_id) as total_customers,
        COUNT(DISTINCT CASE WHEN repeat_orders.customer_id IS NOT NULL THEN o.customer_id END) as repeat_customers
    FROM order_items oi
    JOIN orders o ON oi.order_id = o.order_id
    LEFT JOIN (
        SELECT DISTINCT o1.customer_id, oi1.product_id
        FROM orders o1
        JOIN order_items oi1 ON o1.order_id = oi1.order_id
        WHERE EXISTS (
            SELECT 1
            FROM orders o2
            JOIN order_items oi2 ON o2.order_id = oi2.order_id
            WHERE o2.customer_id = o1.customer_id
            AND oi2.product_id = oi1.product_id
            AND o2.order_date > o1.order_date
        )
    ) repeat_orders ON o.customer_id = repeat_orders.customer_id AND oi.product_id = repeat_orders.product_id
    GROUP BY oi.product_id
),
final_analysis AS (
    SELECT 
        ps.*,
        COALESCE(pr.avg_rating, 0) as avg_rating,
        COALESCE(pr.review_count, 0) as review_count,
        CASE WHEN pp.total_customers > 0 
             THEN ROUND((pp.repeat_customers * 100.0 / pp.total_customers), 2) 
             ELSE 0 END as repurchase_rate,
        -- 종합 점수 계산 (매출 30% + 평점 25% + 재구매율 25% + 리뷰수 20%)
        ROUND((
            (ps.total_revenue / NULLIF((SELECT MAX(total_revenue) FROM product_sales), 0) * 30) +
            (COALESCE(pr.avg_rating, 0) / 5.0 * 25) +
            (CASE WHEN pp.total_customers > 0 THEN pp.repeat_customers * 100.0 / pp.total_customers ELSE 0 END / 100.0 * 25) +
            (LEAST(COALESCE(pr.review_count, 0), 20) / 20.0 * 20)
        ), 2) as performance_score
    FROM product_sales ps
    LEFT JOIN product_ratings pr ON ps.product_id = pr.product_id
    LEFT JOIN product_repurchase pp ON ps.product_id = pp.product_id
)
SELECT 
    product_name,
    category,
    total_revenue,
    avg_rating,
    repurchase_rate,
    performance_score,
    CASE 
        WHEN performance_score >= 80 THEN 'Excellent'
        WHEN performance_score >= 60 THEN 'Good'
        WHEN performance_score >= 40 THEN 'Average'
        WHEN performance_score >= 20 THEN 'Below Average'
        ELSE 'Poor'
    END as performance_grade
FROM final_analysis
ORDER BY performance_score DESC;

-- 문제 4: 이동 평균을 계산하는 CTE를 작성하세요.
WITH monthly_sales AS (
    SELECT 
        EXTRACT(YEAR FROM o.order_date) as year,
        EXTRACT(MONTH FROM o.order_date) as month,
        SUM(o.total_amount) as monthly_revenue
    FROM orders o
    GROUP BY EXTRACT(YEAR FROM o.order_date), EXTRACT(MONTH FROM o.order_date)
),
sales_with_moving_avg AS (
    SELECT 
        year,
        month,
        monthly_revenue,
        AVG(monthly_revenue) OVER (
            ORDER BY year, month 
            ROWS BETWEEN 2 PRECEDING AND CURRENT ROW
        ) as moving_avg_3months,
        LAG(monthly_revenue) OVER (ORDER BY year, month) as prev_month_revenue
    FROM monthly_sales
)
SELECT 
    year || '-' || LPAD(month::TEXT, 2, '0') as year_month,
    monthly_revenue,
    ROUND(moving_avg_3months, 2) as moving_avg_3months,
    CASE 
        WHEN prev_month_revenue IS NOT NULL AND prev_month_revenue > 0 THEN
            ROUND(((monthly_revenue - prev_month_revenue) * 100.0 / prev_month_revenue), 2)
        ELSE NULL
    END as month_over_month_growth
FROM sales_with_moving_avg
ORDER BY year, month;

-- 문제 5: 복잡한 재고 최적화 로직을 CTE로 구현하세요.
WITH monthly_sales_data AS (
    SELECT 
        oi.product_id,
        AVG(oi.quantity) as avg_monthly_sales
    FROM order_items oi
    JOIN orders o ON oi.order_id = o.order_id
    WHERE o.order_date >= CURRENT_DATE - INTERVAL '6 months'
    GROUP BY oi.product_id
),
inventory_analysis AS (
    SELECT 
        p.product_id,
        p.product_name,
        p.category,
        p.stock_quantity as current_stock,
        COALESCE(msd.avg_monthly_sales, 0) as avg_monthly_sales,
        -- 적정 재고 = 월평균 판매량 * 2 (2개월치)
        CEIL(COALESCE(msd.avg_monthly_sales, 0) * 2) as optimal_stock
    FROM products p
    LEFT JOIN monthly_sales_data msd ON p.product_id = msd.product_id
),
stock_recommendations AS (
    SELECT *,
        current_stock - optimal_stock as stock_difference,
        CASE 
            WHEN current_stock = 0 THEN 'Out of Stock'
            WHEN current_stock < optimal_stock * 0.5 THEN 'Critical Low'
            WHEN current_stock < optimal_stock THEN 'Low Stock'
            WHEN current_stock > optimal_stock * 3 THEN 'Overstocked'
            WHEN current_stock > optimal_stock * 2 THEN 'High Stock'
            ELSE 'Optimal'
        END as stock_status,
        CASE 
            WHEN current_stock = 0 THEN 'Urgent Reorder: ' || optimal_stock || ' units'
            WHEN current_stock < optimal_stock * 0.5 THEN 'Reorder: ' || (optimal_stock - current_stock) || ' units'
            WHEN current_stock < optimal_stock THEN 'Consider Reordering: ' || (optimal_stock - current_stock) || ' units'
            WHEN current_stock > optimal_stock * 3 THEN 'Reduce Stock: Consider promotion'
            WHEN current_stock > optimal_stock * 2 THEN 'Monitor: High inventory levels'
            ELSE 'No Action Needed'
        END as recommendation
    FROM inventory_analysis
)
SELECT 
    product_name,
    category,
    current_stock,
    ROUND(avg_monthly_sales, 1) as avg_monthly_sales,
    optimal_stock,
    stock_status,
    recommendation
FROM stock_recommendations
ORDER BY 
    CASE stock_status 
        WHEN 'Out of Stock' THEN 1
        WHEN 'Critical Low' THEN 2
        WHEN 'Low Stock' THEN 3
        WHEN 'Optimal' THEN 4
        WHEN 'High Stock' THEN 5
        WHEN 'Overstocked' THEN 6
    END,
    avg_monthly_sales DESC;