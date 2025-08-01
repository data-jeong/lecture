-- Chapter 06: 고급 분석 윈도우 함수 실습 문제 해답

-- 문제 1: 3개월과 6개월 이동 평균을 동시에 계산하세요.
WITH monthly_revenue AS (
    SELECT 
        EXTRACT(YEAR FROM sale_date) as year,
        EXTRACT(MONTH FROM sale_date) as month,
        SUM(daily_revenue) as monthly_revenue
    FROM daily_sales
    GROUP BY EXTRACT(YEAR FROM sale_date), EXTRACT(MONTH FROM sale_date)
)
SELECT 
    year || '-' || LPAD(month::TEXT, 2, '0') as year_month,
    monthly_revenue,
    ROUND(AVG(monthly_revenue) OVER (
        ORDER BY year, month 
        ROWS BETWEEN 2 PRECEDING AND CURRENT ROW
    ), 2) as moving_avg_3months,
    ROUND(AVG(monthly_revenue) OVER (
        ORDER BY year, month 
        ROWS BETWEEN 5 PRECEDING AND CURRENT ROW
    ), 2) as moving_avg_6months
FROM monthly_revenue
ORDER BY year, month;

-- 문제 2: 직원들을 성과 점수 기준으로 백분위수를 계산하고 등급을 부여하세요.
WITH employee_avg_performance AS (
    SELECT 
        e.employee_id,
        e.first_name,
        e.last_name,
        e.department,
        AVG(ep.score) as avg_score
    FROM employees e
    JOIN employee_performance ep ON e.employee_id = ep.employee_id
    GROUP BY e.employee_id, e.first_name, e.last_name, e.department
)
SELECT 
    first_name,
    last_name,
    department,
    ROUND(avg_score, 2) as avg_performance,
    ROUND(PERCENT_RANK() OVER (ORDER BY avg_score DESC) * 100, 2) as percentile,
    CASE 
        WHEN PERCENT_RANK() OVER (ORDER BY avg_score DESC) <= 0.10 THEN 'A'
        WHEN PERCENT_RANK() OVER (ORDER BY avg_score DESC) <= 0.30 THEN 'B'
        WHEN PERCENT_RANK() OVER (ORDER BY avg_score DESC) <= 0.70 THEN 'C'
        ELSE 'D'
    END as grade
FROM employee_avg_performance
ORDER BY avg_score DESC;

-- 문제 3: 각 부서별로 급여 비율과 누적 급여 비율을 계산하세요.
SELECT 
    department,
    first_name,
    last_name,
    salary,
    ROUND(salary * 100.0 / SUM(salary) OVER (PARTITION BY department), 2) as dept_salary_ratio,
    ROUND(
        SUM(salary) OVER (
            PARTITION BY department 
            ORDER BY salary DESC
            ROWS UNBOUNDED PRECEDING
        ) * 100.0 / SUM(salary) OVER (PARTITION BY department), 2
    ) as cumulative_salary_ratio
FROM employees
ORDER BY department, salary DESC;

-- 문제 5: Gap과 Island 문제를 해결하세요.
WITH date_groups AS (
    SELECT 
        sale_date,
        daily_revenue,
        sale_date - INTERVAL (ROW_NUMBER() OVER (ORDER BY sale_date)) DAY as group_id
    FROM daily_sales
),
consecutive_periods AS (
    SELECT 
        group_id,
        MIN(sale_date) as period_start,
        MAX(sale_date) as period_end,
        COUNT(*) as consecutive_days,
        SUM(daily_revenue) as total_revenue
    FROM date_groups
    GROUP BY group_id
)
SELECT 
    ROW_NUMBER() OVER (ORDER BY period_start) as group_number,
    period_start,
    period_end,
    consecutive_days,
    ROUND(total_revenue, 2) as period_total_revenue
FROM consecutive_periods
WHERE consecutive_days > 1
ORDER BY period_start;

-- 문제 9: 고객 이탈 예측을 위한 RFM 스코어링을 구현하세요.
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
        NTILE(5) OVER (ORDER BY recency_days) as r_score,
        NTILE(5) OVER (ORDER BY frequency DESC) as f_score,
        NTILE(5) OVER (ORDER BY monetary DESC) as m_score
    FROM customer_rfm
    WHERE last_order_date IS NOT NULL
)
SELECT 
    company_name,
    r_score,
    f_score,
    m_score,
    r_score + f_score + m_score as total_score,
    CASE 
        WHEN r_score >= 4 AND f_score >= 4 AND m_score >= 4 THEN 'Champions'
        WHEN r_score >= 3 AND f_score >= 3 AND m_score >= 3 THEN 'Loyal Customers'
        WHEN r_score >= 3 AND f_score <= 2 THEN 'Potential Loyalists'
        WHEN r_score <= 2 AND f_score >= 3 THEN 'At Risk'
        WHEN r_score <= 2 AND f_score <= 2 THEN 'Lost Customers'
        ELSE 'New Customers'
    END as customer_segment
FROM rfm_scores
ORDER BY total_score DESC;