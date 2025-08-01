# Chapter 04: 조인(JOIN) 마스터하기

## 학습 목표
- 모든 JOIN 유형의 완전한 이해와 활용
- 복잡한 다중 테이블 조인 설계
- JOIN 성능 최적화 기법
- 실전 비즈니스 시나리오에서의 JOIN 활용

## 목차

### 1. JOIN의 기본 개념과 원리

#### 1.1 관계형 데이터베이스에서의 JOIN
```sql
-- JOIN이 필요한 이유: 정규화된 테이블들의 연결
-- 예시: 고객 주문 정보 조회

-- 잘못된 접근 (데이터 중복)
-- 모든 정보를 하나의 테이블에 저장하면 중복이 발생

-- 올바른 접근 (정규화 + JOIN)
SELECT 
    c.customer_name,
    o.order_date,
    p.product_name,
    oi.quantity
FROM customers c
JOIN orders o ON c.customer_id = o.customer_id
JOIN order_items oi ON o.order_id = oi.order_id
JOIN products p ON oi.product_id = p.product_id;
```

#### 1.2 JOIN의 종류 개요
- **INNER JOIN**: 두 테이블에 모두 존재하는 데이터만
- **LEFT JOIN**: 왼쪽 테이블의 모든 데이터 + 매칭되는 오른쪽 데이터
- **RIGHT JOIN**: 오른쪽 테이블의 모든 데이터 + 매칭되는 왼쪽 데이터
- **FULL OUTER JOIN**: 양쪽 테이블의 모든 데이터
- **CROSS JOIN**: 카테시안 곱 (모든 조합)
- **SELF JOIN**: 같은 테이블끼리의 조인

### 2. INNER JOIN 완벽 마스터

#### 2.1 기본 INNER JOIN
```sql
-- 가장 기본적인 INNER JOIN
SELECT 
    e.first_name,
    e.last_name,
    d.dept_name
FROM employees e
INNER JOIN departments d ON e.department_id = d.dept_id;

-- INNER는 생략 가능
SELECT 
    e.first_name,
    e.last_name,
    d.dept_name
FROM employees e
JOIN departments d ON e.department_id = d.dept_id;
```

#### 2.2 복합 조건 INNER JOIN
```sql
-- 다중 조건으로 조인
SELECT *
FROM orders o
JOIN order_items oi ON o.order_id = oi.order_id
    AND o.order_date >= '2024-01-01'
    AND oi.quantity > 1;

-- 범위 조건으로 조인
SELECT 
    s.student_name,
    g.grade_letter,
    g.min_score,
    g.max_score
FROM student_scores s
JOIN grade_ranges g ON s.score BETWEEN g.min_score AND g.max_score;
```

#### 2.3 다중 테이블 INNER JOIN
```sql
-- 4개 테이블 조인: 고객별 주문 상세 정보
SELECT 
    c.customer_name,
    c.email,
    o.order_number,
    o.order_date,
    p.product_name,
    p.category,
    oi.quantity,
    oi.unit_price,
    (oi.quantity * oi.unit_price) AS line_total
FROM customers c
JOIN orders o ON c.customer_id = o.customer_id
JOIN order_items oi ON o.order_id = oi.order_id
JOIN products p ON oi.product_id = p.product_id
WHERE o.order_date >= '2024-01-01'
ORDER BY c.customer_name, o.order_date;
```

### 3. LEFT JOIN 활용법

#### 3.1 기본 LEFT JOIN
```sql
-- 모든 고객과 그들의 주문 정보 (주문이 없는 고객도 포함)
SELECT 
    c.customer_id,
    c.customer_name,
    o.order_id,
    o.order_date,
    o.total_amount
FROM customers c
LEFT JOIN orders o ON c.customer_id = o.customer_id
ORDER BY c.customer_name;
```

#### 3.2 NULL 값 활용
```sql
-- 주문하지 않은 고객 찾기
SELECT 
    c.customer_id,
    c.customer_name,
    c.email
FROM customers c
LEFT JOIN orders o ON c.customer_id = o.customer_id
WHERE o.customer_id IS NULL;

-- 특정 기간에 주문하지 않은 고객
SELECT 
    c.customer_id,
    c.customer_name
FROM customers c
LEFT JOIN orders o ON c.customer_id = o.customer_id 
    AND o.order_date >= '2024-01-01'
WHERE o.customer_id IS NULL;
```

#### 3.3 집계와 함께 사용하는 LEFT JOIN
```sql
-- 고객별 주문 통계 (주문이 없는 고객은 0으로 표시)
SELECT 
    c.customer_id,
    c.customer_name,
    COALESCE(COUNT(o.order_id), 0) AS total_orders,
    COALESCE(SUM(o.total_amount), 0) AS total_spent,
    COALESCE(AVG(o.total_amount), 0) AS avg_order_value,
    MAX(o.order_date) AS last_order_date
FROM customers c
LEFT JOIN orders o ON c.customer_id = o.customer_id
GROUP BY c.customer_id, c.customer_name
ORDER BY total_spent DESC;
```

### 4. RIGHT JOIN과 FULL OUTER JOIN

#### 4.1 RIGHT JOIN
```sql
-- RIGHT JOIN (잘 사용되지 않음 - LEFT JOIN으로 대체 가능)
SELECT 
    c.customer_name,
    o.order_number,
    o.order_date
FROM customers c
RIGHT JOIN orders o ON c.customer_id = o.customer_id;

-- 동일한 결과를 LEFT JOIN으로
SELECT 
    c.customer_name,
    o.order_number,
    o.order_date
FROM orders o
LEFT JOIN customers c ON o.customer_id = c.customer_id;
```

#### 4.2 FULL OUTER JOIN
```sql
-- 모든 고객과 모든 주문 정보 (매칭되지 않는 것도 포함)
SELECT 
    c.customer_id,
    c.customer_name,
    o.order_id,
    o.order_date,
    CASE 
        WHEN c.customer_id IS NULL THEN '고객 정보 없음'
        WHEN o.order_id IS NULL THEN '주문 없음'
        ELSE '정상 매칭'
    END AS match_status
FROM customers c
FULL OUTER JOIN orders o ON c.customer_id = o.customer_id;

-- 데이터 품질 검사: 참조 무결성 위반 찾기
SELECT 
    COALESCE(c.customer_id, o.customer_id) AS customer_id,
    c.customer_name,
    o.order_id,
    CASE 
        WHEN c.customer_id IS NULL THEN 'Missing Customer'
        WHEN o.order_id IS NULL THEN 'No Orders'
        ELSE 'Valid'
    END AS status
FROM customers c
FULL OUTER JOIN orders o ON c.customer_id = o.customer_id
WHERE c.customer_id IS NULL OR o.order_id IS NULL;
```

### 5. CROSS JOIN과 특별한 활용

#### 5.1 기본 CROSS JOIN
```sql
-- 카테시안 곱: 모든 조합 생성
SELECT 
    c.category_name,
    s.size_name,
    cl.color_name
FROM categories c
CROSS JOIN sizes s
CROSS JOIN colors cl
ORDER BY c.category_name, s.size_name, cl.color_name;

-- 날짜 시리즈와 카테고리의 조합 (리포팅용)
SELECT 
    d.date_value,
    c.category_name,
    COALESCE(s.sales_amount, 0) AS sales_amount
FROM (
    SELECT DATE '2024-01-01' + (n || ' days')::INTERVAL AS date_value
    FROM generate_series(0, 30) AS n
) d
CROSS JOIN categories c
LEFT JOIN daily_sales s ON d.date_value = s.sale_date 
    AND c.category_id = s.category_id;
```

#### 5.2 실전 CROSS JOIN 활용
```sql
-- 학생별 과목별 성적표 템플릿 생성
SELECT 
    s.student_id,
    s.student_name,
    sub.subject_id,
    sub.subject_name,
    COALESCE(g.grade, 'Not Taken') AS grade,
    COALESCE(g.score, 0) AS score
FROM students s
CROSS JOIN subjects sub
LEFT JOIN grades g ON s.student_id = g.student_id 
    AND sub.subject_id = g.subject_id
WHERE s.is_active = TRUE
ORDER BY s.student_name, sub.subject_name;
```

### 6. SELF JOIN 마스터하기

#### 6.1 계층 구조 조회
```sql
-- 직원과 상사 관계 조회
SELECT 
    e.employee_id,
    e.first_name || ' ' || e.last_name AS employee_name,
    e.job_title,
    m.first_name || ' ' || m.last_name AS manager_name,
    m.job_title AS manager_title
FROM employees e
LEFT JOIN employees m ON e.manager_id = m.employee_id
ORDER BY e.department_id, e.employee_id;

-- 상사가 있는 직원 vs 상사가 없는 직원 구분
SELECT 
    CASE 
        WHEN e.manager_id IS NULL THEN 'Top Level'
        ELSE 'Has Manager'
    END AS hierarchy_level,
    e.first_name || ' ' || e.last_name AS employee_name,
    COALESCE(m.first_name || ' ' || m.last_name, 'No Manager') AS manager_name
FROM employees e
LEFT JOIN employees m ON e.manager_id = m.employee_id
ORDER BY hierarchy_level, e.employee_id;
```

#### 6.2 순위와 비교
```sql
-- 같은 부서 내에서 급여 비교
SELECT 
    e1.employee_id,
    e1.first_name || ' ' || e1.last_name AS employee_name,
    e1.salary,
    e1.department_id,
    COUNT(e2.employee_id) + 1 AS salary_rank
FROM employees e1
LEFT JOIN employees e2 ON e1.department_id = e2.department_id 
    AND e1.salary < e2.salary
GROUP BY e1.employee_id, e1.first_name, e1.last_name, e1.salary, e1.department_id
ORDER BY e1.department_id, salary_rank;

-- 연속된 날짜 찾기 (로그 분석 등에 유용)
SELECT 
    l1.log_date,
    l1.user_id,
    l1.action_count,
    l2.log_date AS next_date,
    l2.action_count AS next_count
FROM daily_user_logs l1
JOIN daily_user_logs l2 ON l1.user_id = l2.user_id 
    AND l2.log_date = l1.log_date + 1
WHERE l1.action_count > 10 AND l2.action_count > 10;
```

### 7. 조건부 JOIN과 고급 기법

#### 7.1 조건부 JOIN
```sql
-- 조건에 따라 다른 테이블과 조인
SELECT 
    o.order_id,
    o.customer_type,
    CASE o.customer_type
        WHEN 'individual' THEN ic.first_name || ' ' || ic.last_name
        WHEN 'business' THEN bc.company_name
    END AS customer_name,
    o.order_date,
    o.total_amount
FROM orders o
LEFT JOIN individual_customers ic ON o.customer_id = ic.customer_id 
    AND o.customer_type = 'individual'  
LEFT JOIN business_customers bc ON o.customer_id = bc.customer_id 
    AND o.customer_type = 'business'
ORDER BY o.order_date DESC;
```

#### 7.2 집계 결과와 JOIN
```sql
-- 각 고객의 평균 주문액과 개별 주문 비교
WITH customer_averages AS (
    SELECT 
        customer_id,
        AVG(total_amount) AS avg_order_amount,
        COUNT(*) AS total_orders
    FROM orders
    GROUP BY customer_id
)
SELECT 
    o.order_id,
    c.customer_name,
    o.total_amount,
    ca.avg_order_amount,
    ROUND((o.total_amount / ca.avg_order_amount - 1) * 100, 2) AS variance_percent,
    CASE 
        WHEN o.total_amount > ca.avg_order_amount * 1.5 THEN 'High Value'
        WHEN o.total_amount < ca.avg_order_amount * 0.5 THEN 'Low Value'
        ELSE 'Normal'
    END AS order_category
FROM orders o
JOIN customers c ON o.customer_id = c.customer_id
JOIN customer_averages ca ON o.customer_id = ca.customer_id
WHERE ca.total_orders >= 3
ORDER BY variance_percent DESC;
```

### 8. UNION과 JOIN의 조합

#### 8.1 서로 다른 소스 통합
```sql
-- 개인고객과 기업고객 통합 뷰
SELECT 
    'individual' AS customer_type,
    ic.customer_id,
    ic.first_name || ' ' || ic.last_name AS customer_name,
    ic.email,
    ic.phone,
    ic.date_of_birth AS reference_date
FROM individual_customers ic

UNION ALL

SELECT 
    'business' AS customer_type,
    bc.customer_id,
    bc.company_name AS customer_name,
    bc.contact_email AS email,
    bc.phone,
    bc.established_date AS reference_date
FROM business_customers bc;

-- 통합된 고객 정보로 주문 분석
WITH unified_customers AS (
    SELECT 'individual' AS customer_type, customer_id, 
           first_name || ' ' || last_name AS customer_name
    FROM individual_customers
    UNION ALL
    SELECT 'business' AS customer_type, customer_id, company_name
    FROM business_customers
)
SELECT 
    uc.customer_type,
    uc.customer_name,
    COUNT(o.order_id) AS total_orders,
    SUM(o.total_amount) AS total_spent,
    AVG(o.total_amount) AS avg_order_value
FROM unified_customers uc
LEFT JOIN orders o ON uc.customer_id = o.customer_id
GROUP BY uc.customer_type, uc.customer_id, uc.customer_name
ORDER BY total_spent DESC NULLS LAST;
```

### 9. JOIN 성능 최적화

#### 9.1 인덱스 최적화
```sql
-- JOIN 조건에 맞는 인덱스 생성
CREATE INDEX idx_orders_customer_date ON orders (customer_id, order_date);
CREATE INDEX idx_order_items_order_product ON order_items (order_id, product_id);

-- 복합 인덱스로 JOIN + WHERE 조건 최적화
CREATE INDEX idx_products_category_price ON products (category_id, price)
WHERE is_active = TRUE;

-- 부분 인덱스로 자주 사용되는 조건 최적화
CREATE INDEX idx_orders_recent_customer ON orders (customer_id)
WHERE order_date >= '2024-01-01';
```

#### 9.2 실행 계획 분석
```sql
-- 실행 계획 확인
EXPLAIN (ANALYZE, BUFFERS) 
SELECT 
    c.customer_name,
    COUNT(o.order_id) AS order_count,
    SUM(o.total_amount) AS total_spent
FROM customers c
LEFT JOIN orders o ON c.customer_id = o.customer_id
WHERE c.is_active = TRUE
GROUP BY c.customer_id, c.customer_name
ORDER BY total_spent DESC;

-- 비효율적인 JOIN 패턴 개선 전
SELECT *
FROM orders o
JOIN customers c ON o.customer_id = c.customer_id
WHERE o.order_date >= '2024-01-01'
  AND c.customer_status = 'active';

-- 개선 후: 조건을 JOIN에 포함
SELECT *
FROM orders o
JOIN customers c ON o.customer_id = c.customer_id 
    AND c.customer_status = 'active'
WHERE o.order_date >= '2024-01-01';
```

### 10. 실전 비즈니스 시나리오

#### 10.1 고객 생애 가치 분석
```sql
-- 고객별 생애 가치 (CLV) 계산
WITH customer_metrics AS (
    SELECT 
        c.customer_id,
        c.customer_name,
        c.acquisition_date,
        COUNT(o.order_id) AS total_orders,
        SUM(o.total_amount) AS total_revenue,
        AVG(o.total_amount) AS avg_order_value,
        MAX(o.order_date) AS last_order_date,
        MIN(o.order_date) AS first_order_date,
        EXTRACT(DAYS FROM MAX(o.order_date) - MIN(o.order_date)) AS customer_lifespan_days
    FROM customers c
    LEFT JOIN orders o ON c.customer_id = o.customer_id
    WHERE c.is_active = TRUE
    GROUP BY c.customer_id, c.customer_name, c.acquisition_date
),
customer_segments AS (
    SELECT 
        *,
        CASE 
            WHEN total_orders = 0 THEN 'No Purchase'
            WHEN total_orders = 1 THEN 'One-time Buyer'
            WHEN total_orders BETWEEN 2 AND 5 THEN 'Occasional Buyer'
            WHEN total_orders BETWEEN 6 AND 15 THEN 'Regular Customer'
            ELSE 'VIP Customer'
        END AS customer_segment,
        CASE 
            WHEN last_order_date >= CURRENT_DATE - INTERVAL '30 days' THEN 'Active'
            WHEN last_order_date >= CURRENT_DATE - INTERVAL '90 days' THEN 'At Risk'
            WHEN last_order_date >= CURRENT_DATE - INTERVAL '365 days' THEN 'Inactive'
            ELSE 'Lost'
        END AS activity_status
    FROM customer_metrics
)
SELECT 
    customer_segment,
    activity_status,
    COUNT(*) AS customer_count,
    ROUND(AVG(total_revenue), 2) AS avg_revenue,
    ROUND(AVG(avg_order_value), 2) AS avg_order_value,
    ROUND(AVG(customer_lifespan_days), 0) AS avg_lifespan_days
FROM customer_segments
GROUP BY customer_segment, activity_status
ORDER BY 
    CASE customer_segment
        WHEN 'VIP Customer' THEN 1
        WHEN 'Regular Customer' THEN 2
        WHEN 'Occasional Buyer' THEN 3
        WHEN 'One-time Buyer' THEN 4
        ELSE 5
    END,
    CASE activity_status
        WHEN 'Active' THEN 1
        WHEN 'At Risk' THEN 2
        WHEN 'Inactive' THEN 3
        ELSE 4
    END;
```

#### 10.2 재고 관리와 공급업체 분석
```sql
-- 재고 부족 예상 및 공급업체 성과 분석
WITH inventory_analysis AS (
    SELECT 
        p.product_id,
        p.product_name,
        p.current_stock,
        p.reorder_level,
        p.lead_time_days,
        s.supplier_name,
        s.reliability_score,
        
        -- 최근 30일 판매량
        COALESCE(SUM(oi.quantity), 0) AS sales_last_30days,
        
        -- 일평균 판매량
        ROUND(COALESCE(SUM(oi.quantity), 0) / 30.0, 2) AS daily_avg_sales,
        
        -- 예상 재고 소진일
        CASE 
            WHEN COALESCE(SUM(oi.quantity), 0) = 0 THEN NULL
            ELSE ROUND(p.current_stock / (COALESCE(SUM(oi.quantity), 0) / 30.0), 0)
        END AS days_until_stockout
        
    FROM products p
    LEFT JOIN suppliers s ON p.supplier_id = s.supplier_id
    LEFT JOIN order_items oi ON p.product_id = oi.product_id
    LEFT JOIN orders o ON oi.order_id = o.order_id 
        AND o.order_date >= CURRENT_DATE - INTERVAL '30 days'
    WHERE p.is_active = TRUE
    GROUP BY p.product_id, p.product_name, p.current_stock, p.reorder_level, 
             p.lead_time_days, s.supplier_name, s.reliability_score
),
reorder_recommendations AS (
    SELECT 
        *,
        CASE 
            WHEN current_stock <= reorder_level THEN 'Immediate Reorder'
            WHEN days_until_stockout <= lead_time_days THEN 'Urgent Reorder'
            WHEN days_until_stockout <= lead_time_days * 1.5 THEN 'Plan Reorder'
            ELSE 'No Action Needed'
        END AS reorder_status,
        
        -- 추천 주문량 (리드타임 + 안전재고 고려)
        GREATEST(
            reorder_level * 2,
            ROUND(daily_avg_sales * (lead_time_days + 7), 0)
        ) AS recommended_order_qty
        
    FROM inventory_analysis
)
SELECT 
    reorder_status,
    product_name,
    supplier_name,
    current_stock,
    reorder_level,
    daily_avg_sales,
    days_until_stockout,
    recommended_order_qty,
    reliability_score,
    CASE 
        WHEN reliability_score >= 95 THEN 'Preferred'
        WHEN reliability_score >= 85 THEN 'Good'
        WHEN reliability_score >= 70 THEN 'Average'
        ELSE 'Review Required'
    END AS supplier_grade
FROM reorder_recommendations
WHERE reorder_status != 'No Action Needed'
ORDER BY 
    CASE reorder_status
        WHEN 'Immediate Reorder' THEN 1
        WHEN 'Urgent Reorder' THEN 2
        WHEN 'Plan Reorder' THEN 3
    END,
    days_until_stockout NULLS LAST;
```

## 성능 최적화 가이드

### JOIN 최적화 체크리스트
1. **인덱스 확인**: JOIN 조건의 모든 컬럼에 적절한 인덱스
2. **통계 정보**: `ANALYZE` 명령으로 최신 통계 유지
3. **JOIN 순서**: 가장 선택적인 조건부터 처리
4. **조건 배치**: WHERE 조건을 적절한 위치에 배치
5. **데이터 타입**: JOIN 컬럼의 데이터 타입 일치

### 일반적인 성능 문제와 해결법
```sql
-- 문제: 대용량 테이블의 비효율적 JOIN
-- 해결: 먼저 필터링 후 JOIN
WITH filtered_orders AS (
    SELECT customer_id, order_id, total_amount
    FROM orders 
    WHERE order_date >= '2024-01-01'
)
SELECT c.customer_name, f.total_amount
FROM filtered_orders f
JOIN customers c ON f.customer_id = c.customer_id;

-- 문제: 불필요한 컬럼 조회
-- 해결: 필요한 컬럼만 SELECT
SELECT c.customer_name, o.order_date  -- 필요한 컬럼만
FROM customers c
JOIN orders o ON c.customer_id = o.customer_id;
```

## 다음 단계

Chapter 05에서는 서브쿼리와 CTE(Common Table Expression)를 활용한 고급 쿼리 기법을 학습합니다.