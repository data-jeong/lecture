-- Chapter 06: 기초 윈도우 함수 실습 문제 해답

-- 문제 1: 직원들을 급여순으로 순위를 매기세요.
SELECT 
    first_name,
    last_name,
    salary,
    ROW_NUMBER() OVER (ORDER BY salary DESC) as row_number,
    RANK() OVER (ORDER BY salary DESC) as rank_func,
    DENSE_RANK() OVER (ORDER BY salary DESC) as dense_rank
FROM employees
ORDER BY salary DESC;

-- 문제 2: 각 부서별로 급여 상위 3명의 직원을 조회하세요.
SELECT 
    department,
    first_name,
    last_name,
    salary,
    dept_rank
FROM (
    SELECT 
        department,
        first_name,
        last_name,
        salary,
        ROW_NUMBER() OVER (PARTITION BY department ORDER BY salary DESC) as dept_rank
    FROM employees
) ranked
WHERE dept_rank <= 3
ORDER BY department, dept_rank;

-- 문제 3: 일별 매출에서 전일 대비 매출 증감률을 계산하세요.
SELECT 
    sale_date,
    daily_revenue,
    LAG(daily_revenue) OVER (ORDER BY sale_date) as prev_day_revenue,
    ROUND(
        (daily_revenue - LAG(daily_revenue) OVER (ORDER BY sale_date)) * 100.0 / 
        LAG(daily_revenue) OVER (ORDER BY sale_date), 2
    ) as growth_rate_percent
FROM daily_sales
ORDER BY sale_date;

-- 문제 4: 각 카테고리에서 가장 비싼 상품과 가장 저렴한 상품의 가격을 조회하세요.
SELECT 
    product_name,
    category,
    price,
    FIRST_VALUE(price) OVER (
        PARTITION BY category 
        ORDER BY price DESC
        ROWS UNBOUNDED PRECEDING
    ) as category_max_price,
    LAST_VALUE(price) OVER (
        PARTITION BY category 
        ORDER BY price DESC
        ROWS BETWEEN UNBOUNDED PRECEDING AND UNBOUNDED FOLLOWING
    ) as category_min_price
FROM products
ORDER BY category, price DESC;

-- 문제 5: 일별 매출의 누적 합계를 계산하세요.
SELECT 
    sale_date,
    daily_revenue,
    SUM(daily_revenue) OVER (
        ORDER BY sale_date 
        ROWS UNBOUNDED PRECEDING
    ) as cumulative_revenue
FROM daily_sales
ORDER BY sale_date;

-- 문제 6: 각 직원의 성과 점수에서 다음 분기 성과와 비교하세요.
SELECT 
    e.first_name,
    ep.quarter,
    ep.score,
    LEAD(ep.score) OVER (
        PARTITION BY ep.employee_id 
        ORDER BY ep.performance_date
    ) as next_quarter_score,
    LEAD(ep.score) OVER (
        PARTITION BY ep.employee_id 
        ORDER BY ep.performance_date
    ) - ep.score as performance_improvement
FROM employees e
JOIN employee_performance ep ON e.employee_id = ep.employee_id
ORDER BY e.first_name, ep.performance_date;

-- 문제 7: 상품별로 재고 이동 내역에서 각 이동의 누적 재고 변화량을 계산하세요.
SELECT 
    product_id,
    movement_date,
    movement_type,
    CASE 
        WHEN movement_type = 'IN' THEN quantity
        ELSE -quantity
    END as quantity_change,
    SUM(
        CASE 
            WHEN movement_type = 'IN' THEN quantity
            ELSE -quantity
        END
    ) OVER (
        PARTITION BY product_id 
        ORDER BY movement_date
        ROWS UNBOUNDED PRECEDING
    ) as cumulative_stock_change
FROM stock_movements
ORDER BY product_id, movement_date;

-- 문제 8: 각 부서의 월별 목표 대비 달성률을 이전 달과 비교하세요.
SELECT 
    department,
    target_month,
    revenue_target,
    revenue_target * 0.85 as assumed_actual, -- 가정 달성률 85%
    ROUND((revenue_target * 0.85 / revenue_target) * 100, 2) as achievement_rate,
    LAG(ROUND((revenue_target * 0.85 / revenue_target) * 100, 2)) OVER (
        PARTITION BY department 
        ORDER BY target_month
    ) as prev_month_achievement,
    ROUND((revenue_target * 0.85 / revenue_target) * 100, 2) - 
    LAG(ROUND((revenue_target * 0.85 / revenue_target) * 100, 2)) OVER (
        PARTITION BY department 
        ORDER BY target_month
    ) as achievement_change
FROM monthly_targets
ORDER BY department, target_month;

-- 문제 9: 상품 가격의 백분위수를 계산하세요.
SELECT 
    product_name,
    price,
    ROUND(PERCENT_RANK() OVER (ORDER BY price) * 100, 2) as price_percentile,
    ROUND(CUME_DIST() OVER (ORDER BY price) * 100, 2) as cumulative_distribution
FROM products
ORDER BY price DESC;

-- 문제 10: 일별 매출에서 7일 이동 평균을 계산하세요.
SELECT 
    sale_date,
    daily_revenue,
    ROUND(
        AVG(daily_revenue) OVER (
            ORDER BY sale_date 
            ROWS BETWEEN 6 PRECEDING AND CURRENT ROW
        ), 2
    ) as moving_avg_7days
FROM daily_sales
ORDER BY sale_date;

-- 문제 11: 각 고객의 주문 날짜별로 순번을 매기고, 첫 번째 주문과 마지막 주문을 표시하세요.
SELECT 
    c.company_name,
    o.order_date,
    ROW_NUMBER() OVER (
        PARTITION BY o.customer_id 
        ORDER BY o.order_date
    ) as order_sequence,
    FIRST_VALUE(o.order_date) OVER (
        PARTITION BY o.customer_id 
        ORDER BY o.order_date
        ROWS UNBOUNDED PRECEDING
    ) as first_order_date,
    LAST_VALUE(o.order_date) OVER (
        PARTITION BY o.customer_id 
        ORDER BY o.order_date
        ROWS BETWEEN UNBOUNDED PRECEDING AND UNBOUNDED FOLLOWING
    ) as last_order_date
FROM customers c
JOIN orders o ON c.customer_id = o.customer_id
ORDER BY c.company_name, o.order_date;

-- 문제 12: 직원별 성과 점수를 4분위로 나누세요.
SELECT 
    e.first_name,
    e.last_name,
    AVG(ep.score) as avg_performance_score,
    NTILE(4) OVER (ORDER BY AVG(ep.score)) as performance_quartile
FROM employees e
JOIN employee_performance ep ON e.employee_id = ep.employee_id
GROUP BY e.employee_id, e.first_name, e.last_name
ORDER BY avg_performance_score DESC;

-- 문제 13: 상품별로 가장 최근 재고 이동 날짜와 유형을 조회하세요.
SELECT 
    sm.product_id,
    p.product_name,
    sm.movement_date as latest_movement_date,
    sm.movement_type as latest_movement_type,
    sm.quantity
FROM (
    SELECT 
        product_id,
        movement_date,
        movement_type,
        quantity,
        ROW_NUMBER() OVER (
            PARTITION BY product_id 
            ORDER BY movement_date DESC
        ) as rn
    FROM stock_movements
) sm
JOIN products p ON sm.product_id = p.product_id
WHERE sm.rn = 1
ORDER BY sm.product_id;

-- 문제 14: 일별 매출에서 해당 월의 최고 매출일과 최저 매출일을 표시하세요.
SELECT 
    sale_date,
    daily_revenue,
    MAX(daily_revenue) OVER (
        PARTITION BY EXTRACT(YEAR FROM sale_date), EXTRACT(MONTH FROM sale_date)
    ) as month_max_revenue,
    MIN(daily_revenue) OVER (
        PARTITION BY EXTRACT(YEAR FROM sale_date), EXTRACT(MONTH FROM sale_date)
    ) as month_min_revenue
FROM daily_sales
ORDER BY sale_date;

-- 문제 15: 각 부서별로 직원들의 급여 누적 분포를 계산하세요.
SELECT 
    department,
    first_name,
    last_name,
    salary,
    ROUND(CUME_DIST() OVER (PARTITION BY department ORDER BY salary) * 100, 2) as dept_salary_percentile
FROM employees
ORDER BY department, salary DESC;