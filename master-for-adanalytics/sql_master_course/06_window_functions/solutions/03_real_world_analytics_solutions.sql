-- Chapter 06: 실무 분석 윈도우 함수 실습 문제 해답

-- 문제 1: 완전한 코호트 분석을 구현하세요.
WITH customer_cohorts AS (
    SELECT 
        customer_id,
        DATE_TRUNC('month', MIN(order_date)) as cohort_month
    FROM orders
    GROUP BY customer_id
),
cohort_data AS (
    SELECT 
        cc.cohort_month,
        DATE_TRUNC('month', o.order_date) as order_month,
        EXTRACT(EPOCH FROM (DATE_TRUNC('month', o.order_date) - cc.cohort_month))/(60*60*24*30) as period_number,
        COUNT(DISTINCT o.customer_id) as customers
    FROM customer_cohorts cc
    JOIN orders o ON cc.customer_id = o.customer_id
    GROUP BY cc.cohort_month, DATE_TRUNC('month', o.order_date)
),
cohort_sizes AS (
    SELECT 
        cohort_month,
        customers as cohort_size
    FROM cohort_data
    WHERE period_number = 0
)
SELECT 
    cd.cohort_month,
    cd.period_number,
    cd.customers,
    cs.cohort_size,
    ROUND(cd.customers * 100.0 / cs.cohort_size, 2) as retention_rate
FROM cohort_data cd
JOIN cohort_sizes cs ON cd.cohort_month = cs.cohort_month
WHERE cd.period_number <= 12  -- 12개월까지만
ORDER BY cd.cohort_month, cd.period_number;

-- 문제 2: 고급 RFM 고객 세그멘테이션을 구현하세요.
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
        END as r_score,
        CASE 
            WHEN frequency >= 10 THEN 5
            WHEN frequency >= 6 THEN 4
            WHEN frequency >= 4 THEN 3
            WHEN frequency >= 2 THEN 2
            ELSE 1
        END as f_score,
        CASE 
            WHEN monetary >= 5000 THEN 5
            WHEN monetary >= 2000 THEN 4
            WHEN monetary >= 1000 THEN 3
            WHEN monetary >= 500 THEN 2
            ELSE 1
        END as m_score
    FROM customer_rfm
    WHERE last_order_date IS NOT NULL
),
customer_segments AS (
    SELECT *,
        CASE 
            WHEN r_score = 5 AND f_score >= 4 AND m_score >= 4 THEN 'Champions'
            WHEN r_score >= 4 AND f_score >= 3 AND m_score >= 3 THEN 'Loyal Customers'
            WHEN r_score >= 3 AND f_score >= 2 AND m_score >= 2 THEN 'Potential Loyalists'
            WHEN r_score >= 4 AND f_score <= 2 AND m_score <= 2 THEN 'New Customers'
            WHEN r_score >= 3 AND f_score <= 3 AND m_score <= 3 THEN 'Promising'
            WHEN r_score = 3 AND f_score >= 3 AND m_score >= 3 THEN 'Need Attention'
            WHEN r_score = 2 AND f_score >= 2 AND m_score >= 2 THEN 'About to Sleep'
            WHEN r_score <= 2 AND f_score >= 4 AND m_score >= 4 THEN 'Cannot Lose Them'
            WHEN r_score <= 2 AND f_score >= 2 AND m_score >= 2 THEN 'At Risk'
            WHEN r_score <= 2 AND f_score <= 2 AND m_score >= 4 THEN 'Hibernating'
            ELSE 'Lost'
        END as segment,
        monetary * 2.5 as estimated_clv  -- 간단한 CLV 추정
    FROM rfm_scores
)
SELECT 
    company_name,
    CONCAT(r_score, f_score, m_score) as rfm_score,
    segment,
    ROUND(estimated_clv, 2) as estimated_clv,
    CASE segment
        WHEN 'Champions' THEN 'VIP 프로그램 초대'
        WHEN 'Loyal Customers' THEN '로열티 보상 제공'
        WHEN 'Potential Loyalists' THEN '개인화된 할인 제공'
        WHEN 'At Risk' THEN '재구매 인센티브 제공'
        WHEN 'Lost' THEN '윈백 캠페인 실행'
        ELSE '일반 마케팅'
    END as recommended_action
FROM customer_segments
ORDER BY estimated_clv DESC;

-- 문제 4: 직원 성과 트렌드 종합 분석을 수행하세요.
WITH performance_trends AS (
    SELECT 
        e.employee_id,
        e.first_name,
        e.last_name,
        e.department,
        ep.performance_date,
        ep.score,
        ROW_NUMBER() OVER (PARTITION BY e.employee_id ORDER BY ep.performance_date) as period_num,
        AVG(ep.score) OVER (PARTITION BY e.department) as dept_avg_score
    FROM employees e
    JOIN employee_performance ep ON e.employee_id = ep.employee_id
),
trend_analysis AS (
    SELECT *,
        -- 선형 회귀를 위한 기본 계산
        AVG(score) OVER (PARTITION BY employee_id) as avg_score,
        score - LAG(score) OVER (PARTITION BY employee_id ORDER BY performance_date) as score_change,
        score - AVG(score) OVER (PARTITION BY department) as dept_relative_performance
    FROM performance_trends
)
SELECT 
    first_name,
    last_name,
    department,
    ROUND(avg_score, 2) as avg_performance,
    CASE 
        WHEN AVG(score_change) OVER (PARTITION BY employee_id) > 2 THEN 'Improving'
        WHEN AVG(score_change) OVER (PARTITION BY employee_id) < -2 THEN 'Declining'
        ELSE 'Stable'
    END as trend,
    ROUND(AVG(dept_relative_performance) OVER (PARTITION BY employee_id), 2) as relative_position,
    CASE 
        WHEN avg_score < 80 THEN 'High'
        WHEN avg_score < 90 THEN 'Medium'
        ELSE 'Low'
    END as development_need
FROM trend_analysis
GROUP BY employee_id, first_name, last_name, department, avg_score
ORDER BY department, avg_score DESC;