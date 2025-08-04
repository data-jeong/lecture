# Chapter 06: 윈도우 함수와 분석 함수

## 학습 목표
- 윈도우 함수의 개념과 동작 원리 완전 이해
- 순위 함수 (ROW_NUMBER, RANK, DENSE_RANK) 활용 마스터
- 값 참조 함수 (LAG, LEAD, FIRST_VALUE, LAST_VALUE) 실무 활용
- 집계 윈도우 함수를 사용한 고급 분석 기법 습득
- PARTITION BY와 ORDER BY의 다양한 조합 패턴 학습
- 실무에서 자주 사용되는 고급 분석 쿼리 작성 능력 배양

## 목차

### 1. 윈도우 함수 기초 개념

윈도우 함수는 현재 행과 관련된 행들의 집합(윈도우)에 대해 계산을 수행하는 함수입니다. GROUP BY와 달리 결과 행 수가 줄어들지 않습니다.

```sql
-- 기본 윈도우 함수 구조
SELECT 
    column1,
    column2,
    WINDOW_FUNCTION() OVER (
        [PARTITION BY column3]
        [ORDER BY column4]
        [ROWS/RANGE BETWEEN ... AND ...]
    )
FROM table_name;
```

### 2. 윈도우 함수의 구성 요소

#### 2.1 PARTITION BY 절
데이터를 그룹으로 나누어 각 그룹 내에서 윈도우 함수를 적용합니다.

```sql
-- 부서별로 분할하여 순번 매기기
SELECT 
    employee_id,
    first_name,
    department,
    salary,
    ROW_NUMBER() OVER (PARTITION BY department ORDER BY salary DESC) as dept_rank
FROM employees;
```

#### 2.2 ORDER BY 절
윈도우 내의 행들을 정렬하는 기준을 정의합니다.

```sql
-- 전체 직원을 급여순으로 정렬하여 순번 매기기
SELECT 
    first_name,
    last_name,
    salary,
    ROW_NUMBER() OVER (ORDER BY salary DESC) as overall_rank
FROM employees;
```

#### 2.3 FRAME 절 (ROWS/RANGE)
윈도우의 범위를 세밀하게 제어합니다.

```sql
-- 현재 행부터 2행 뒤까지의 평균 계산
SELECT 
    employee_id,
    salary,
    AVG(salary) OVER (
        ORDER BY employee_id 
        ROWS BETWEEN CURRENT ROW AND 2 FOLLOWING
    ) as avg_next_3
FROM employees;
```

### 3. 순위 함수 (Ranking Functions)

#### 3.1 ROW_NUMBER()
각 행에 고유한 순번을 부여합니다.

```sql
-- 부서별 급여 순위 (동일 급여도 다른 순번)
SELECT 
    first_name,
    last_name,
    department,
    salary,
    ROW_NUMBER() OVER (PARTITION BY department ORDER BY salary DESC) as row_num
FROM employees;

-- 페이징 구현
SELECT * FROM (
    SELECT 
        product_name,
        price,
        ROW_NUMBER() OVER (ORDER BY price DESC) as rn
    FROM products
) ranked
WHERE rn BETWEEN 11 AND 20;  -- 2페이지 (11-20번째)
```

#### 3.2 RANK()
동일한 값에 대해 같은 순위를 부여하고, 다음 순위는 건너뜁니다.

```sql
-- 급여 기준 순위 (동일 급여는 같은 순위, 다음 순위 건너뜀)
SELECT 
    first_name,
    last_name,
    salary,
    RANK() OVER (ORDER BY salary DESC) as salary_rank
FROM employees;

-- 결과 예시:
-- John, 90000, 1
-- Jane, 90000, 1  
-- Bob,  85000, 3   (2순위는 건너뜀)
```

#### 3.3 DENSE_RANK()
동일한 값에 대해 같은 순위를 부여하지만, 다음 순위는 연속됩니다.

```sql
-- 급여 기준 밀집 순위 (다음 순위 건너뛰지 않음)
SELECT 
    first_name,
    last_name,
    salary,
    DENSE_RANK() OVER (ORDER BY salary DESC) as dense_rank
FROM employees;

-- 결과 예시:
-- John, 90000, 1
-- Jane, 90000, 1  
-- Bob,  85000, 2   (순위 연속)
```

#### 3.4 순위 함수 비교
```sql
-- 세 가지 순위 함수 비교
SELECT 
    first_name,
    salary,
    ROW_NUMBER() OVER (ORDER BY salary DESC) as row_num,
    RANK() OVER (ORDER BY salary DESC) as rank_func,
    DENSE_RANK() OVER (ORDER BY salary DESC) as dense_rank
FROM employees
ORDER BY salary DESC;
```

### 4. 값 참조 함수 (Value Functions)

#### 4.1 LAG() / LEAD()
이전/다음 행의 값을 참조합니다.

```sql
-- 이전 직원과의 급여 비교
SELECT 
    first_name,
    salary,
    LAG(salary) OVER (ORDER BY salary) as prev_salary,
    salary - LAG(salary) OVER (ORDER BY salary) as salary_diff
FROM employees
ORDER BY salary;

-- 다음 달 매출과 비교
SELECT 
    order_month,
    monthly_revenue,
    LEAD(monthly_revenue) OVER (ORDER BY order_month) as next_month_revenue,
    LEAD(monthly_revenue) OVER (ORDER BY order_month) - monthly_revenue as growth
FROM monthly_sales;

-- n개 행 이전/이후 값 참조
SELECT 
    product_name,
    price,
    LAG(price, 2) OVER (ORDER BY price) as price_2_before,
    LEAD(price, 3) OVER (ORDER BY price) as price_3_after
FROM products;
```

#### 4.2 FIRST_VALUE() / LAST_VALUE()
윈도우의 첫 번째/마지막 값을 참조합니다.

```sql
-- 각 부서에서 최고/최저 급여와 비교
SELECT 
    first_name,
    department,
    salary,
    FIRST_VALUE(salary) OVER (
        PARTITION BY department 
        ORDER BY salary DESC
        ROWS UNBOUNDED PRECEDING
    ) as dept_max_salary,
    LAST_VALUE(salary) OVER (
        PARTITION BY department 
        ORDER BY salary DESC
        ROWS BETWEEN UNBOUNDED PRECEDING AND UNBOUNDED FOLLOWING
    ) as dept_min_salary
FROM employees;

-- 월별 누적 최고/최저 매출
SELECT 
    order_date,
    daily_revenue,
    FIRST_VALUE(daily_revenue) OVER (
        ORDER BY order_date
        ROWS UNBOUNDED PRECEDING
    ) as first_day_revenue,
    MAX(daily_revenue) OVER (
        ORDER BY order_date
        ROWS UNBOUNDED PRECEDING
    ) as max_revenue_to_date
FROM daily_sales;
```

#### 4.3 NTH_VALUE()
윈도우에서 n번째 값을 참조합니다.

```sql
-- 각 카테고리에서 3번째로 비싼 상품 가격 참조
SELECT 
    product_name,
    category,
    price,
    NTH_VALUE(price, 3) OVER (
        PARTITION BY category 
        ORDER BY price DESC
        ROWS UNBOUNDED PRECEDING
    ) as third_highest_price
FROM products;
```

### 5. 집계 윈도우 함수

#### 5.1 누적 집계
```sql
-- 누적 매출 계산
SELECT 
    order_date,
    daily_revenue,
    SUM(daily_revenue) OVER (
        ORDER BY order_date
        ROWS UNBOUNDED PRECEDING
    ) as cumulative_revenue
FROM daily_sales;

-- 이동 평균 계산 (7일 이동평균)
SELECT 
    order_date,
    daily_revenue,
    AVG(daily_revenue) OVER (
        ORDER BY order_date
        ROWS BETWEEN 6 PRECEDING AND CURRENT ROW
    ) as moving_avg_7days
FROM daily_sales;
```

#### 5.2 비율 계산
```sql
-- 부서별 급여 비율
SELECT 
    first_name,
    department,
    salary,
    ROUND(
        salary * 100.0 / SUM(salary) OVER (PARTITION BY department), 2
    ) as dept_salary_percentage
FROM employees;

-- 전체 매출 대비 비율
SELECT 
    product_name,
    revenue,
    ROUND(
        revenue * 100.0 / SUM(revenue) OVER (), 2
    ) as revenue_percentage
FROM product_revenue;
```

### 6. 고급 윈도우 함수 활용

#### 6.1 분위수 계산
```sql
-- 급여 사분위수
SELECT 
    first_name,
    salary,
    NTILE(4) OVER (ORDER BY salary) as salary_quartile,
    PERCENT_RANK() OVER (ORDER BY salary) as percentile_rank,
    CUME_DIST() OVER (ORDER BY salary) as cumulative_distribution
FROM employees;
```

#### 6.2 Gap과 Island 문제
연속된 값의 그룹을 찾는 문제입니다.

```sql
-- 연속된 주문 날짜 그룹 찾기
WITH order_groups AS (
    SELECT 
        order_date,
        order_date - INTERVAL (ROW_NUMBER() OVER (ORDER BY order_date)) DAY as group_id
    FROM orders
    WHERE order_date IS NOT NULL
)
SELECT 
    group_id,
    MIN(order_date) as group_start,
    MAX(order_date) as group_end,
    COUNT(*) as consecutive_days
FROM order_groups
GROUP BY group_id
ORDER BY group_start;
```

#### 6.3 Top N per Group
각 그룹에서 상위 N개 항목을 선택합니다.

```sql
-- 각 카테고리별 상위 3개 상품
SELECT 
    category,
    product_name,
    price,
    category_rank
FROM (
    SELECT 
        category,
        product_name,
        price,
        ROW_NUMBER() OVER (PARTITION BY category ORDER BY price DESC) as category_rank
    FROM products
) ranked
WHERE category_rank <= 3;
```

### 7. 실전 분석 예제

#### 7.1 코호트 분석 (Cohort Analysis)
```sql
-- 월별 코호트 분석
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
    WHERE cohort_month = order_month
)
SELECT 
    cd.cohort_month,
    cd.order_month,
    cd.customers,
    cs.cohort_size,
    ROUND(cd.customers * 100.0 / cs.cohort_size, 2) as retention_rate
FROM cohort_data cd
JOIN cohort_sizes cs ON cd.cohort_month = cs.cohort_month
ORDER BY cd.cohort_month, cd.order_month;
```

#### 7.2 매출 성장률 분석
```sql
-- 월별 매출 성장률 분석
WITH monthly_revenue AS (
    SELECT 
        DATE_TRUNC('month', order_date) as month,
        SUM(total_amount) as revenue
    FROM orders
    GROUP BY DATE_TRUNC('month', order_date)
)
SELECT 
    month,
    revenue,
    LAG(revenue) OVER (ORDER BY month) as prev_month_revenue,
    ROUND(
        (revenue - LAG(revenue) OVER (ORDER BY month)) * 100.0 / 
        LAG(revenue) OVER (ORDER BY month), 2
    ) as month_over_month_growth,
    ROUND(
        AVG(revenue) OVER (
            ORDER BY month 
            ROWS BETWEEN 2 PRECEDING AND CURRENT ROW
        ), 2
    ) as moving_avg_3months
FROM monthly_revenue
ORDER BY month;
```

#### 7.3 고객 RFM 분석
```sql
-- RFM 분석 (Recency, Frequency, Monetary)
WITH customer_rfm AS (
    SELECT 
        customer_id,
        MAX(order_date) as last_order_date,
        COUNT(*) as frequency,
        SUM(total_amount) as monetary,
        CURRENT_DATE - MAX(order_date) as recency_days
    FROM orders
    GROUP BY customer_id
),
rfm_quartiles AS (
    SELECT *,
        NTILE(4) OVER (ORDER BY recency_days) as recency_quartile,
        NTILE(4) OVER (ORDER BY frequency DESC) as frequency_quartile,
        NTILE(4) OVER (ORDER BY monetary DESC) as monetary_quartile
    FROM customer_rfm
)
SELECT 
    customer_id,
    recency_days,
    frequency,
    monetary,
    recency_quartile,
    frequency_quartile,
    monetary_quartile,
    CASE 
        WHEN frequency_quartile = 4 AND monetary_quartile = 4 THEN 'Champions'
        WHEN frequency_quartile >= 3 AND monetary_quartile >= 3 THEN 'Loyal Customers'
        WHEN recency_quartile >= 3 THEN 'At Risk'
        ELSE 'Others'
    END as customer_segment
FROM rfm_quartiles
ORDER BY monetary DESC;
```

### 8. 성능 최적화 팁

#### 8.1 인덱스 활용
```sql
-- PARTITION BY와 ORDER BY에 사용되는 컬럼에 인덱스 생성
CREATE INDEX idx_employees_dept_salary ON employees(department, salary DESC);

-- 윈도우 함수 최적화를 위한 복합 인덱스
CREATE INDEX idx_orders_customer_date ON orders(customer_id, order_date);
```

#### 8.2 효율적인 윈도우 함수 사용
```sql
-- 비효율적: 동일한 윈도우를 여러 번 정의
SELECT 
    employee_id,
    ROW_NUMBER() OVER (PARTITION BY department ORDER BY salary DESC),
    RANK() OVER (PARTITION BY department ORDER BY salary DESC),
    salary - AVG(salary) OVER (PARTITION BY department ORDER BY salary DESC)
FROM employees;

-- 효율적: WINDOW 절 사용
SELECT 
    employee_id,
    ROW_NUMBER() OVER dept_salary_window,
    RANK() OVER dept_salary_window,
    salary - AVG(salary) OVER dept_salary_window
FROM employees
WINDOW dept_salary_window AS (PARTITION BY department ORDER BY salary DESC);
```

## 실습 데이터베이스

이번 장에서는 다음과 같은 추가 테이블을 사용합니다:

1. **daily_sales** (일별 매출)
   - sale_date (날짜)
   - daily_revenue (일별 매출)
   - order_count (주문 수)

2. **employee_performance** (직원 성과)
   - employee_id (직원 ID)
   - performance_date (성과 평가일)
   - score (점수)
   - goals_met (목표 달성 여부)

3. **stock_movements** (재고 이동)
   - movement_id (이동 ID)
   - product_id (상품 ID)
   - movement_date (이동 날짜)
   - movement_type (입고/출고)
   - quantity (수량)

## 실습 문제

실습 문제는 `exercises/` 폴더에 있으며, 해답은 `solutions/` 폴더에서 확인할 수 있습니다.

### 기초 문제 (exercises/01_basic_window_functions.sql)
1. 직원들을 급여순으로 순위 매기기 (ROW_NUMBER, RANK, DENSE_RANK)
2. 각 부서별 급여 상위 3명 조회
3. 전월 대비 매출 증감률 계산 (LAG 활용)
4. 각 카테고리에서 가장 비싼/저렴한 상품 가격 조회 (FIRST_VALUE, LAST_VALUE)
5. 누적 매출 계산

### 중급 문제 (exercises/02_advanced_analytics.sql)
1. 이동 평균 계산 (3개월, 6개월)
2. 백분위수 계산 및 분위수 분류
3. 부서별 급여 비율 계산
4. Top N per Group 구현
5. Gap과 Island 문제 해결

### 고급 문제 (exercises/03_real_world_analytics.sql)
1. 코호트 분석 구현
2. RFM 고객 세그멘테이션
3. 상품별 재고 회전율 분석
4. 직원 성과 트렌드 분석
5. 복합 지표를 활용한 대시보드 쿼리

## 다음 단계

Chapter 06을 완료했다면, Chapter 07에서 인덱스와 쿼리 최적화를 학습하여 대용량 데이터에서도 빠른 분석이 가능한 SQL을 작성하는 방법을 익힙니다.