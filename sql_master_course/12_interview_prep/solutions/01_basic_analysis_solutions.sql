-- Chapter 12: 데이터 분석가 인터뷰 기초 분석 문제 해답

-- 문제 1: 월별 매출 증감률 계산
WITH monthly_revenue AS (
    SELECT 
        EXTRACT(YEAR FROM order_date) as year,
        EXTRACT(MONTH FROM order_date) as month,
        SUM(total_amount) as monthly_revenue
    FROM orders
    GROUP BY EXTRACT(YEAR FROM order_date), EXTRACT(MONTH FROM order_date)
)
SELECT 
    year || '-' || LPAD(month::TEXT, 2, '0') as year_month,
    monthly_revenue,
    LAG(monthly_revenue) OVER (ORDER BY year, month) as prev_month_revenue,
    ROUND(
        (monthly_revenue - LAG(monthly_revenue) OVER (ORDER BY year, month)) * 100.0 / 
        LAG(monthly_revenue) OVER (ORDER BY year, month), 2
    ) as growth_rate_percent
FROM monthly_revenue
ORDER BY year, month;

-- 문제 2: 상위 10% 고객 식별 (파레토 법칙)
WITH customer_revenue AS (
    SELECT 
        customer_id,
        SUM(total_amount) as total_spent
    FROM orders
    GROUP BY customer_id
),
customer_cumulative AS (
    SELECT 
        customer_id,
        total_spent,
        SUM(total_spent) OVER (ORDER BY total_spent DESC) as cumulative_revenue,
        SUM(total_spent) OVER () as total_revenue
    FROM customer_revenue
)
SELECT 
    customer_id,
    total_spent,
    ROUND(cumulative_revenue * 100.0 / total_revenue, 2) as cumulative_percent,
    CASE WHEN cumulative_revenue * 100.0 / total_revenue <= 80 THEN 'VIP' ELSE 'Regular' END as customer_type
FROM customer_cumulative
ORDER BY total_spent DESC;

-- 문제 3: 제품별 재구매율 계산
WITH product_customers AS (
    SELECT 
        oi.product_id,
        p.product_name,
        COUNT(DISTINCT o.customer_id) as total_customers
    FROM order_items oi
    JOIN orders o ON oi.order_id = o.order_id
    JOIN products p ON oi.product_id = p.product_id
    GROUP BY oi.product_id, p.product_name
),
repeat_customers AS (
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
)
SELECT 
    pc.product_name,
    pc.total_customers,
    COALESCE(rc.repeat_customers, 0) as repeat_customers,
    ROUND(COALESCE(rc.repeat_customers, 0) * 100.0 / pc.total_customers, 2) as repurchase_rate
FROM product_customers pc
LEFT JOIN repeat_customers rc ON pc.product_id = rc.product_id
ORDER BY repurchase_rate DESC;

-- 문제 6: 구독 서비스 이탈률 분석
WITH monthly_stats AS (
    SELECT 
        DATE_TRUNC('month', start_date) as month,
        COUNT(*) as new_subscriptions
    FROM subscriptions
    GROUP BY DATE_TRUNC('month', start_date)
),
churn_stats AS (
    SELECT 
        DATE_TRUNC('month', end_date) as month,
        COUNT(*) as churned_subscriptions
    FROM subscriptions
    WHERE end_date IS NOT NULL
    GROUP BY DATE_TRUNC('month', end_date)
),
active_start AS (
    SELECT 
        generate_series(DATE_TRUNC('month', MIN(start_date)), 
                       DATE_TRUNC('month', MAX(COALESCE(end_date, CURRENT_DATE))), 
                       '1 month'::interval) as month
    FROM subscriptions
)
SELECT 
    asm.month,
    COALESCE(ms.new_subscriptions, 0) as new_subs,
    COALESCE(cs.churned_subscriptions, 0) as churned_subs,
    (SELECT COUNT(*) 
     FROM subscriptions s 
     WHERE s.start_date <= asm.month 
     AND (s.end_date IS NULL OR s.end_date > asm.month)) as active_subs_start,
    CASE 
        WHEN (SELECT COUNT(*) FROM subscriptions s WHERE s.start_date <= asm.month 
              AND (s.end_date IS NULL OR s.end_date > asm.month)) > 0
        THEN ROUND(COALESCE(cs.churned_subscriptions, 0) * 100.0 / 
                  (SELECT COUNT(*) FROM subscriptions s WHERE s.start_date <= asm.month 
                   AND (s.end_date IS NULL OR s.end_date > asm.month)), 2)
        ELSE 0
    END as churn_rate
FROM active_start asm
LEFT JOIN monthly_stats ms ON asm.month = ms.month
LEFT JOIN churn_stats cs ON asm.month = cs.month
ORDER BY asm.month;

-- 문제 8: 고객 세그멘테이션 (RFM 간소화 버전)
WITH customer_metrics AS (
    SELECT 
        customer_id,
        MAX(order_date) as last_order_date,
        SUM(total_amount) as total_spent,
        CURRENT_DATE - MAX(order_date) as recency_days
    FROM orders
    GROUP BY customer_id
),
customer_scores AS (
    SELECT *,
        NTILE(2) OVER (ORDER BY recency_days) as r_score, -- 1=최근, 2=오래됨
        NTILE(2) OVER (ORDER BY total_spent DESC) as m_score -- 1=고액, 2=소액
    FROM customer_metrics
)
SELECT 
    customer_id,
    last_order_date,
    total_spent,
    r_score,
    m_score,
    CASE 
        WHEN r_score = 1 AND m_score = 1 THEN 'Champions'
        WHEN r_score = 1 AND m_score = 2 THEN 'Potential Loyalists'
        WHEN r_score = 2 AND m_score = 1 THEN 'At Risk'
        ELSE 'Others'
    END as customer_grade
FROM customer_scores
ORDER BY total_spent DESC;