-- Chapter 04: 조인(JOIN) 마스터하기 - SELF JOIN 특화 연습 해답
-- 난이도: 중급-고급

-- =============================================================================
-- 1. 계층 구조 분석 (Hierarchical Data)
-- =============================================================================

-- 1-1. 조직도 기본 조회
SELECT 
    e.employee_id,
    e.first_name || ' ' || e.last_name AS employee_name,
    e.job_title,
    e.manager_id,
    COALESCE(m.first_name || ' ' || m.last_name, 'No Manager') AS manager_name,
    m.job_title AS manager_title
FROM employees e
LEFT JOIN employees m ON e.manager_id = m.employee_id
ORDER BY COALESCE(e.manager_id, 0), e.employee_id;

-- 1-2. 최고 경영진 조회
SELECT 
    employee_id,
    first_name || ' ' || last_name AS executive_name,
    job_title,
    hire_date,
    salary
FROM employees
WHERE manager_id IS NULL
ORDER BY salary DESC;

-- 1-3. 특정 매니저의 직속 부하직원 조회
SELECT 
    e.employee_id,
    e.first_name || ' ' || e.last_name AS employee_name,
    e.job_title,
    e.salary,
    e.hire_date
FROM employees e
WHERE e.manager_id = 5
ORDER BY e.salary DESC;

-- 1-4. 조직 레벨별 직원 수 조회
WITH RECURSIVE org_levels AS (
    -- Level 1: Top executives (no manager)
    SELECT 
        employee_id,
        first_name || ' ' || last_name AS employee_name,
        1 AS org_level
    FROM employees
    WHERE manager_id IS NULL
    
    UNION ALL
    
    -- Recursive case: each subsequent level
    SELECT 
        e.employee_id,
        e.first_name || ' ' || e.last_name,
        ol.org_level + 1
    FROM employees e
    JOIN org_levels ol ON e.manager_id = ol.employee_id
)
SELECT 
    org_level,
    COUNT(*) AS employee_count,
    ROUND(AVG(e.salary), 2) AS avg_salary_at_level
FROM org_levels ol
JOIN employees e ON ol.employee_id = e.employee_id
GROUP BY org_level
ORDER BY org_level;

-- =============================================================================
-- 2. 재귀적 계층 구조 (Recursive Hierarchy)
-- =============================================================================

-- 2-1. 특정 매니저 하위의 모든 직원 조회 (재귀 CTE 사용)
WITH RECURSIVE subordinates AS (
    -- Base case: direct reports of manager ID 3
    SELECT 
        employee_id,
        first_name || ' ' || last_name AS employee_name,
        job_title,
        salary,
        1 AS level,
        manager_id,
        ARRAY[employee_id] AS path
    FROM employees
    WHERE manager_id = 3
    
    UNION ALL
    
    -- Recursive case: employees reporting to subordinates
    SELECT 
        e.employee_id,
        e.first_name || ' ' || e.last_name,
        e.job_title,
        e.salary,
        s.level + 1,
        e.manager_id,
        s.path || e.employee_id
    FROM employees e
    JOIN subordinates s ON e.manager_id = s.employee_id
)
SELECT 
    level,
    REPEAT('  ', level - 1) || employee_name AS hierarchical_display,
    job_title,
    salary
FROM subordinates
ORDER BY path;

-- 2-2. 조직 경로 추적
WITH RECURSIVE employee_path AS (
    -- Base case: top-level employees
    SELECT 
        employee_id,
        first_name || ' ' || last_name AS employee_name,
        manager_id,
        1 AS level,
        first_name || ' ' || last_name AS path_to_top
    FROM employees
    WHERE manager_id IS NULL
    
    UNION ALL
    
    -- Recursive case: build path from employee to top
    SELECT 
        e.employee_id,
        e.first_name || ' ' || e.last_name,
        e.manager_id,
        ep.level + 1,
        e.first_name || ' ' || e.last_name || ' -> ' || ep.path_to_top
    FROM employees e
    JOIN employee_path ep ON e.manager_id = ep.employee_id
)
SELECT 
    employee_name,
    level,
    path_to_top
FROM employee_path
ORDER BY level, employee_name;

-- 2-3. 팀별 총 인원 수 계산
WITH RECURSIVE team_sizes AS (
    -- Base case: individual employees
    SELECT 
        employee_id,
        first_name || ' ' || last_name AS manager_name,
        1 AS team_size
    FROM employees
    
    UNION ALL
    
    -- Recursive case: accumulate team sizes
    SELECT 
        m.employee_id,
        m.first_name || ' ' || m.last_name,
        ts.team_size + 1
    FROM employees e
    JOIN employees m ON e.manager_id = m.employee_id
    JOIN team_sizes ts ON e.employee_id = ts.employee_id
)
SELECT 
    manager_name,
    MAX(team_size) AS total_team_size,
    (SELECT COUNT(*) FROM employees WHERE manager_id = ts.employee_id) AS direct_reports
FROM team_sizes ts
WHERE (SELECT COUNT(*) FROM employees WHERE manager_id = ts.employee_id) > 0
GROUP BY ts.employee_id, manager_name
ORDER BY total_team_size DESC;

-- =============================================================================
-- 3. 급여 및 성과 비교 분석
-- =============================================================================

-- 3-1. 동일 부서 내 급여 순위
SELECT 
    e1.first_name || ' ' || e1.last_name AS employee_name,
    d.dept_name,
    e1.salary,
    COUNT(e2.employee_id) + 1 AS dept_salary_rank
FROM employees e1
JOIN departments d ON e1.department_id = d.dept_id
LEFT JOIN employees e2 ON e1.department_id = e2.department_id 
    AND e1.salary < e2.salary
GROUP BY e1.employee_id, e1.first_name, e1.last_name, d.dept_name, e1.salary
ORDER BY d.dept_name, dept_salary_rank;

-- 3-2. 급여 분포 분석
SELECT 
    e1.first_name || ' ' || e1.last_name AS employee_name,
    e1.salary,
    COUNT(e2.employee_id) AS higher_paid_count,
    COUNT(e3.employee_id) AS lower_paid_count,
    (SELECT COUNT(*) FROM employees) - COUNT(e2.employee_id) - COUNT(e3.employee_id) - 1 AS same_salary_count
FROM employees e1
LEFT JOIN employees e2 ON e1.salary < e2.salary
LEFT JOIN employees e3 ON e1.salary > e3.salary
GROUP BY e1.employee_id, e1.first_name, e1.last_name, e1.salary
ORDER BY e1.salary DESC;

-- 3-3. 상사와 부하직원 급여 비교
SELECT 
    e.first_name || ' ' || e.last_name AS employee_name,
    e.salary AS employee_salary,
    m.first_name || ' ' || m.last_name AS manager_name,
    m.salary AS manager_salary,
    e.salary - m.salary AS salary_difference
FROM employees e
JOIN employees m ON e.manager_id = m.employee_id
WHERE e.salary > m.salary
ORDER BY salary_difference DESC;

-- 3-4. 팀 내 급여 격차 분석
SELECT 
    m.first_name || ' ' || m.last_name AS team_manager,
    COUNT(e.employee_id) AS team_size,
    MAX(e.salary) AS max_team_salary,
    MIN(e.salary) AS min_team_salary,
    MAX(e.salary) - MIN(e.salary) AS salary_gap,
    ROUND(AVG(e.salary), 2) AS avg_team_salary
FROM employees m
JOIN employees e ON m.employee_id = e.manager_id
GROUP BY m.employee_id, m.first_name, m.last_name
HAVING COUNT(e.employee_id) > 1
ORDER BY salary_gap DESC;

-- =============================================================================
-- 4. 시간 기반 SELF JOIN
-- =============================================================================

-- 4-1. 연속 주문 고객 분석
SELECT 
    c.customer_name,
    o1.order_date AS first_order_date,
    o2.order_date AS second_order_date,
    EXTRACT(EPOCH FROM (o2.order_date - o1.order_date))/3600 AS hours_between_orders
FROM orders o1
JOIN orders o2 ON o1.customer_id = o2.customer_id 
    AND o2.order_date > o1.order_date
    AND o2.order_date <= o1.order_date + INTERVAL '2 days'
JOIN customers c ON o1.customer_id = c.customer_id
WHERE o1.order_id != o2.order_id
ORDER BY c.customer_name, o1.order_date;

-- 4-2. 매출 성장률 계산
WITH monthly_sales AS (
    SELECT 
        EXTRACT(YEAR FROM order_date) AS year,
        EXTRACT(MONTH FROM order_date) AS month,
        SUM(total_amount) AS monthly_revenue
    FROM orders
    GROUP BY EXTRACT(YEAR FROM order_date), EXTRACT(MONTH FROM order_date)
)
SELECT 
    ms1.year,
    ms1.month,
    ms1.monthly_revenue AS current_month,
    ms2.monthly_revenue AS previous_month,
    ROUND(
        ((ms1.monthly_revenue - ms2.monthly_revenue) * 100.0 / 
         NULLIF(ms2.monthly_revenue, 0)), 2
    ) AS growth_rate_percent
FROM monthly_sales ms1
LEFT JOIN monthly_sales ms2 ON (
    (ms1.year = ms2.year AND ms1.month = ms2.month + 1) OR
    (ms1.year = ms2.year + 1 AND ms1.month = 1 AND ms2.month = 12)
)
ORDER BY ms1.year, ms1.month;

-- 4-3. 재주문 패턴 분석
SELECT 
    c.customer_name,
    p.product_name,
    o1.order_date AS first_order_date,
    o2.order_date AS reorder_date,
    o2.order_date - o1.order_date AS reorder_interval_days
FROM orders o1
JOIN orders o2 ON o1.customer_id = o2.customer_id AND o1.order_date < o2.order_date
JOIN order_items oi1 ON o1.order_id = oi1.order_id
JOIN order_items oi2 ON o2.order_id = oi2.order_id AND oi1.product_id = oi2.product_id
JOIN customers c ON o1.customer_id = c.customer_id
JOIN products p ON oi1.product_id = p.product_id
WHERE NOT EXISTS (
    SELECT 1 FROM orders o3
    JOIN order_items oi3 ON o3.order_id = oi3.order_id
    WHERE o3.customer_id = o1.customer_id
    AND oi3.product_id = oi1.product_id
    AND o3.order_date > o1.order_date
    AND o3.order_date < o2.order_date
)
ORDER BY c.customer_name, p.product_name, o1.order_date;

-- 4-4. 계절별 매출 비교
WITH seasonal_sales AS (
    SELECT 
        EXTRACT(YEAR FROM order_date) AS year,
        CASE 
            WHEN EXTRACT(MONTH FROM order_date) IN (12, 1, 2) THEN 'Winter'
            WHEN EXTRACT(MONTH FROM order_date) IN (3, 4, 5) THEN 'Spring'
            WHEN EXTRACT(MONTH FROM order_date) IN (6, 7, 8) THEN 'Summer'
            ELSE 'Fall'
        END AS season,
        SUM(total_amount) AS seasonal_revenue
    FROM orders
    GROUP BY EXTRACT(YEAR FROM order_date), 
        CASE 
            WHEN EXTRACT(MONTH FROM order_date) IN (12, 1, 2) THEN 'Winter'
            WHEN EXTRACT(MONTH FROM order_date) IN (3, 4, 5) THEN 'Spring'
            WHEN EXTRACT(MONTH FROM order_date) IN (6, 7, 8) THEN 'Summer'
            ELSE 'Fall'
        END
)
SELECT 
    ss1.year,
    ss1.season,
    ss1.seasonal_revenue AS current_year,
    ss2.seasonal_revenue AS previous_year,
    ROUND(
        ((ss1.seasonal_revenue - ss2.seasonal_revenue) * 100.0 / 
         NULLIF(ss2.seasonal_revenue, 0)), 2
    ) AS yoy_growth_percent
FROM seasonal_sales ss1
LEFT JOIN seasonal_sales ss2 ON ss1.season = ss2.season 
    AND ss1.year = ss2.year + 1
ORDER BY ss1.year, 
    CASE ss1.season 
        WHEN 'Spring' THEN 1 
        WHEN 'Summer' THEN 2 
        WHEN 'Fall' THEN 3 
        WHEN 'Winter' THEN 4 
    END;

-- =============================================================================
-- 5. 순위 및 랭킹 시스템
-- =============================================================================

-- 5-1. 부서별 TOP 3 직원
SELECT 
    d.dept_name,
    e1.first_name || ' ' || e1.last_name AS employee_name,
    e1.salary,
    COUNT(e2.employee_id) + 1 AS dept_rank
FROM employees e1
JOIN departments d ON e1.department_id = d.dept_id
LEFT JOIN employees e2 ON e1.department_id = e2.department_id 
    AND e1.salary < e2.salary
GROUP BY d.dept_name, e1.employee_id, e1.first_name, e1.last_name, e1.salary
HAVING COUNT(e2.employee_id) < 3
ORDER BY d.dept_name, dept_rank;

-- 5-2. 매출 실적 순위
WITH quarterly_sales AS (
    SELECT 
        e.employee_id,
        e.first_name || ' ' || e.last_name AS employee_name,
        EXTRACT(YEAR FROM o.order_date) AS year,
        EXTRACT(QUARTER FROM o.order_date) AS quarter,
        SUM(o.total_amount) AS quarterly_revenue
    FROM employees e
    LEFT JOIN orders o ON e.employee_id = o.sales_rep_id
    GROUP BY e.employee_id, e.first_name, e.last_name, 
             EXTRACT(YEAR FROM o.order_date), EXTRACT(QUARTER FROM o.order_date)
)
SELECT 
    qs1.employee_name,
    qs1.year,
    qs1.quarter,
    COALESCE(qs1.quarterly_revenue, 0) AS revenue,
    COUNT(qs2.employee_id) + 1 AS quarterly_rank
FROM quarterly_sales qs1
LEFT JOIN quarterly_sales qs2 ON qs1.year = qs2.year 
    AND qs1.quarter = qs2.quarter
    AND qs1.quarterly_revenue < qs2.quarterly_revenue
WHERE qs1.year IS NOT NULL AND qs1.quarter IS NOT NULL
GROUP BY qs1.employee_name, qs1.year, qs1.quarter, qs1.quarterly_revenue
ORDER BY qs1.year, qs1.quarter, quarterly_rank;

-- 5-3. 고객 충성도 순위
WITH customer_spending AS (
    SELECT 
        c.customer_id,
        c.customer_name,
        SUM(o.total_amount) AS total_spent
    FROM customers c
    LEFT JOIN orders o ON c.customer_id = o.customer_id
    GROUP BY c.customer_id, c.customer_name
),
customer_ranks AS (
    SELECT 
        cs1.customer_name,
        cs1.total_spent,
        COUNT(cs2.customer_id) + 1 AS spending_rank,
        (SELECT COUNT(*) FROM customer_spending) AS total_customers
    FROM customer_spending cs1
    LEFT JOIN customer_spending cs2 ON cs1.total_spent < cs2.total_spent
    GROUP BY cs1.customer_id, cs1.customer_name, cs1.total_spent
)
SELECT 
    customer_name,
    COALESCE(total_spent, 0) AS total_spent,
    spending_rank,
    CASE 
        WHEN spending_rank <= total_customers * 0.1 THEN 'VIP'
        WHEN spending_rank <= total_customers * 0.3 THEN 'Premium'
        ELSE 'Regular'
    END AS customer_tier
FROM customer_ranks
ORDER BY spending_rank;

-- =============================================================================
-- 6. 네트워크 분석
-- =============================================================================

-- 6-1. 친구 관계 분석 (소셜 네트워크)
-- 가정: friends 테이블 구조 (user_id, friend_id)
SELECT 
    u1.user_name AS user_a,
    u2.user_name AS user_b,
    COUNT(f1.friend_id) AS mutual_friends
FROM users u1
JOIN users u2 ON u1.user_id < u2.user_id
JOIN friends f1 ON u1.user_id = f1.user_id
JOIN friends f2 ON u2.user_id = f2.user_id AND f1.friend_id = f2.friend_id
GROUP BY u1.user_id, u1.user_name, u2.user_id, u2.user_name
HAVING COUNT(f1.friend_id) > 0
ORDER BY mutual_friends DESC;

-- 6-2. 추천 시스템
WITH customer_products AS (
    SELECT DISTINCT 
        o.customer_id,
        oi.product_id
    FROM orders o
    JOIN order_items oi ON o.order_id = oi.order_id
)
SELECT 
    c1.customer_name AS customer_a,
    c2.customer_name AS customer_b,
    COUNT(cp1.product_id) AS common_products,
    ROUND(
        COUNT(cp1.product_id)::DECIMAL / 
        (SELECT COUNT(DISTINCT product_id) 
         FROM customer_products 
         WHERE customer_id IN (cp1.customer_id, cp2.customer_id)), 3
    ) AS similarity_score
FROM customer_products cp1
JOIN customer_products cp2 ON cp1.product_id = cp2.product_id 
    AND cp1.customer_id < cp2.customer_id
JOIN customers c1 ON cp1.customer_id = c1.customer_id
JOIN customers c2 ON cp2.customer_id = c2.customer_id
GROUP BY cp1.customer_id, cp2.customer_id, c1.customer_name, c2.customer_name
HAVING COUNT(cp1.product_id) >= 2
ORDER BY similarity_score DESC, common_products DESC
LIMIT 20;

-- 6-3. 영향력 분석
WITH RECURSIVE influence_tree AS (
    SELECT 
        employee_id,
        first_name || ' ' || last_name AS manager_name,
        1 AS direct_reports,
        1 AS total_influence
    FROM employees
    WHERE employee_id IN (SELECT DISTINCT manager_id FROM employees WHERE manager_id IS NOT NULL)
    
    UNION ALL
    
    SELECT 
        m.employee_id,
        m.first_name || ' ' || m.last_name,
        COUNT(e.employee_id),
        it.total_influence + COUNT(e.employee_id)
    FROM employees m
    JOIN employees e ON m.employee_id = e.manager_id
    JOIN influence_tree it ON m.employee_id = it.employee_id
    GROUP BY m.employee_id, m.first_name, m.last_name, it.total_influence
)
SELECT 
    manager_name,
    (SELECT COUNT(*) FROM employees WHERE manager_id = it.employee_id) AS direct_reports,
    MAX(total_influence) AS total_influence_score
FROM influence_tree it
GROUP BY it.employee_id, manager_name
ORDER BY total_influence_score DESC;

-- =============================================================================
-- 7. 데이터 품질 및 이상 탐지
-- =============================================================================

-- 7-1. 순환 참조 탐지
WITH RECURSIVE cycle_check AS (
    SELECT 
        employee_id,
        manager_id,
        ARRAY[employee_id] AS path,
        false AS cycle_detected
    FROM employees
    WHERE manager_id IS NOT NULL
    
    UNION ALL
    
    SELECT 
        e.employee_id,
        e.manager_id,
        cc.path || e.manager_id,
        e.manager_id = ANY(cc.path)
    FROM employees e
    JOIN cycle_check cc ON e.employee_id = cc.manager_id
    WHERE NOT cc.cycle_detected AND e.manager_id IS NOT NULL
)
SELECT DISTINCT
    employee_id,
    manager_id,
    path
FROM cycle_check
WHERE cycle_detected = true;

-- 7-2. 고아 노드 탐지
SELECT 
    e1.employee_id,
    e1.first_name || ' ' || e1.last_name AS employee_name,
    e1.manager_id AS referenced_manager_id
FROM employees e1
LEFT JOIN employees e2 ON e1.manager_id = e2.employee_id
WHERE e1.manager_id IS NOT NULL AND e2.employee_id IS NULL;

-- 7-3. 깊이 이상 탐지
WITH RECURSIVE depth_check AS (
    SELECT 
        employee_id,
        first_name || ' ' || last_name AS employee_name,
        manager_id,
        1 AS depth,
        ARRAY[employee_id] AS path
    FROM employees
    WHERE manager_id IS NULL
    
    UNION ALL
    
    SELECT 
        e.employee_id,
        e.first_name || ' ' || e.last_name,
        e.manager_id,
        dc.depth + 1,
        dc.path || e.employee_id
    FROM employees e
    JOIN depth_check dc ON e.manager_id = dc.employee_id
    WHERE dc.depth < 10  -- Prevent infinite recursion
)
SELECT 
    employee_name,
    depth,
    array_to_string(path, ' -> ') AS hierarchy_path
FROM depth_check
WHERE depth >= 7
ORDER BY depth DESC;

-- 7-4. 중복 데이터 탐지
SELECT 
    first_name,
    last_name,
    department_id,
    COUNT(*) AS duplicate_count,
    array_agg(employee_id) AS employee_ids
FROM employees
GROUP BY first_name, last_name, department_id
HAVING COUNT(*) > 1
ORDER BY duplicate_count DESC;