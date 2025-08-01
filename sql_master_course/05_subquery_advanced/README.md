# Chapter 05: 서브쿼리와 고급 쿼리 기법

## 학습 목표
- 서브쿼리의 종류와 활용법 완전 마스터
- 상관 서브쿼리와 비상관 서브쿼리 구분 및 활용
- CTE(Common Table Expression)를 활용한 복잡한 쿼리 작성
- EXISTS, IN, ANY, ALL 연산자의 효율적 사용
- 복잡한 비즈니스 로직을 SQL로 구현하는 능력 배양

## 목차

### 1. 서브쿼리 기초 개념
서브쿼리(Subquery)는 다른 SQL 문 안에 포함된 SELECT 문입니다. 주 쿼리(Main Query)의 결과를 얻기 위해 보조적인 역할을 수행합니다.

```sql
-- 기본 서브쿼리 구조
SELECT column1, column2
FROM table1
WHERE column1 = (SELECT column1 FROM table2 WHERE condition);
```

### 2. 서브쿼리의 종류

#### 2.1 위치에 따른 분류
- **SELECT 절 서브쿼리 (스칼라 서브쿼리)**
- **FROM 절 서브쿼리 (인라인 뷰)**
- **WHERE 절 서브쿼리**
- **HAVING 절 서브쿼리**

#### 2.2 반환 결과에 따른 분류
- **단일 행 서브쿼리**: 하나의 행만 반환
- **다중 행 서브쿼리**: 여러 행을 반환
- **다중 열 서브쿼리**: 여러 컬럼을 반환

#### 2.3 실행 방식에 따른 분류
- **비상관 서브쿼리**: 주 쿼리와 독립적으로 실행
- **상관 서브쿼리**: 주 쿼리의 각 행에 대해 실행

### 3. 스칼라 서브쿼리 (SELECT 절)

```sql
-- 각 직원의 정보와 해당 부서의 평균 급여 조회
SELECT 
    employee_id,
    first_name,
    last_name,
    salary,
    (SELECT AVG(salary) 
     FROM employees e2 
     WHERE e2.department = e1.department) as dept_avg_salary
FROM employees e1;

-- 각 상품과 해당 카테고리의 총 상품 수 조회
SELECT 
    product_name,
    category,
    price,
    (SELECT COUNT(*) 
     FROM products p2 
     WHERE p2.category = p1.category) as category_product_count
FROM products p1;
```

### 4. 인라인 뷰 (FROM 절 서브쿼리)

```sql
-- 부서별 평균 급여를 구하고, 전체 평균보다 높은 부서만 조회
SELECT dept_stats.department, dept_stats.avg_salary
FROM (
    SELECT department, AVG(salary) as avg_salary
    FROM employees
    GROUP BY department
) dept_stats
WHERE dept_stats.avg_salary > (
    SELECT AVG(salary) FROM employees
);

-- 월별 주문 통계 (가상의 orders 테이블 사용)
SELECT 
    monthly_sales.order_month,
    monthly_sales.total_amount,
    monthly_sales.order_count
FROM (
    SELECT 
        EXTRACT(YEAR_MONTH FROM order_date) as order_month,
        SUM(total_amount) as total_amount,
        COUNT(*) as order_count
    FROM orders
    GROUP BY EXTRACT(YEAR_MONTH FROM order_date)
) monthly_sales
ORDER BY monthly_sales.order_month;
```

### 5. WHERE 절 서브쿼리

#### 5.1 단일 행 서브쿼리
```sql
-- 평균 급여보다 높은 급여를 받는 직원 조회
SELECT first_name, last_name, salary
FROM employees
WHERE salary > (SELECT AVG(salary) FROM employees);

-- 가장 비싼 상품과 같은 카테고리의 상품들 조회
SELECT product_name, category, price
FROM products
WHERE category = (
    SELECT category 
    FROM products 
    ORDER BY price DESC 
    LIMIT 1
);
```

#### 5.2 다중 행 서브쿼리 - IN 연산자
```sql
-- 'Sales' 또는 'Marketing' 부서에 속한 직원 조회
SELECT first_name, last_name, department
FROM employees
WHERE department IN ('Sales', 'Marketing');

-- 재고가 10개 미만인 상품의 카테고리에 속한 모든 상품 조회
SELECT product_name, category, stock_quantity
FROM products
WHERE category IN (
    SELECT DISTINCT category
    FROM products
    WHERE stock_quantity < 10
);
```

#### 5.3 다중 행 서브쿼리 - ANY/ALL 연산자
```sql
-- 어떤 'Sales' 직원보다 급여가 높은 다른 부서 직원 조회
SELECT first_name, last_name, department, salary
FROM employees
WHERE salary > ANY (
    SELECT salary 
    FROM employees 
    WHERE department = 'Sales'
) AND department != 'Sales';

-- 모든 'IT' 직원보다 급여가 높은 직원 조회
SELECT first_name, last_name, department, salary
FROM employees
WHERE salary > ALL (
    SELECT salary 
    FROM employees 
    WHERE department = 'IT'
);
```

### 6. EXISTS 연산자

EXISTS는 서브쿼리가 하나 이상의 행을 반환하면 TRUE, 그렇지 않으면 FALSE를 반환합니다.

```sql
-- 주문이 있는 고객만 조회 (가상의 orders 테이블)
SELECT customer_id, company_name, contact_name
FROM customers c
WHERE EXISTS (
    SELECT 1 
    FROM orders o 
    WHERE o.customer_id = c.customer_id
);

-- 2022년에 입사한 직원이 있는 부서 조회
SELECT DISTINCT department
FROM employees e1
WHERE EXISTS (
    SELECT 1
    FROM employees e2
    WHERE e2.department = e1.department
    AND EXTRACT(YEAR FROM e2.hire_date) = 2022
);

-- NOT EXISTS: 주문이 없는 고객 조회
SELECT customer_id, company_name, contact_name
FROM customers c
WHERE NOT EXISTS (
    SELECT 1 
    FROM orders o 
    WHERE o.customer_id = c.customer_id
);
```

### 7. 상관 서브쿼리 (Correlated Subquery)

상관 서브쿼리는 외부 쿼리의 각 행에 대해 서브쿼리가 실행됩니다.

```sql
-- 각 부서에서 가장 높은 급여를 받는 직원 조회
SELECT first_name, last_name, department, salary
FROM employees e1
WHERE salary = (
    SELECT MAX(salary)
    FROM employees e2
    WHERE e2.department = e1.department
);

-- 평균보다 높은 가격의 상품을 카테고리별로 조회
SELECT product_name, category, price
FROM products p1
WHERE price > (
    SELECT AVG(price)
    FROM products p2
    WHERE p2.category = p1.category
);

-- 각 고객의 첫 번째 주문 정보 조회
SELECT c.company_name, o.order_date, o.total_amount
FROM customers c
JOIN orders o ON c.customer_id = o.customer_id
WHERE o.order_date = (
    SELECT MIN(order_date)
    FROM orders o2
    WHERE o2.customer_id = c.customer_id
);
```

### 8. CTE (Common Table Expression)

CTE는 임시 결과 집합을 정의하여 쿼리의 가독성과 재사용성을 높입니다.

#### 8.1 기본 CTE
```sql
-- 부서별 통계를 CTE로 계산 후 활용
WITH department_stats AS (
    SELECT 
        department,
        COUNT(*) as employee_count,
        AVG(salary) as avg_salary,
        MAX(salary) as max_salary
    FROM employees
    GROUP BY department
)
SELECT 
    ds.department,
    ds.employee_count,
    ds.avg_salary,
    e.first_name,
    e.last_name
FROM department_stats ds
JOIN employees e ON ds.department = e.department
WHERE e.salary = ds.max_salary;
```

#### 8.2 다중 CTE
```sql
-- 여러 CTE를 연결하여 복잡한 분석 수행
WITH 
high_earners AS (
    SELECT employee_id, first_name, last_name, department, salary
    FROM employees
    WHERE salary > 70000
),
department_averages AS (
    SELECT department, AVG(salary) as avg_salary
    FROM employees
    GROUP BY department
),
final_analysis AS (
    SELECT 
        he.*,
        da.avg_salary as dept_avg,
        he.salary - da.avg_salary as salary_diff
    FROM high_earners he
    JOIN department_averages da ON he.department = da.department
)
SELECT * FROM final_analysis
WHERE salary_diff > 10000
ORDER BY salary_diff DESC;
```

#### 8.3 재귀 CTE
```sql
-- 재귀 CTE를 사용한 계층 구조 조회 (가상의 employees_hierarchy 테이블)
WITH RECURSIVE employee_hierarchy AS (
    -- Anchor: 최상위 관리자
    SELECT employee_id, first_name, last_name, manager_id, 1 as level
    FROM employees_hierarchy
    WHERE manager_id IS NULL
    
    UNION ALL
    
    -- Recursive: 하위 직원들
    SELECT e.employee_id, e.first_name, e.last_name, e.manager_id, eh.level + 1
    FROM employees_hierarchy e
    INNER JOIN employee_hierarchy eh ON e.manager_id = eh.employee_id
)
SELECT * FROM employee_hierarchy
ORDER BY level, employee_id;
```

### 9. 실전 예제: 복잡한 비즈니스 로직

#### 9.1 고객 분석
```sql
-- 고객별 구매 패턴 분석
WITH customer_stats AS (
    SELECT 
        c.customer_id,
        c.company_name,
        COUNT(o.order_id) as total_orders,
        SUM(o.total_amount) as total_spent,
        AVG(o.total_amount) as avg_order_value,
        MIN(o.order_date) as first_order,
        MAX(o.order_date) as last_order
    FROM customers c
    LEFT JOIN orders o ON c.customer_id = o.customer_id
    GROUP BY c.customer_id, c.company_name
),
customer_segments AS (
    SELECT *,
        CASE 
            WHEN total_spent > 10000 THEN 'Premium'
            WHEN total_spent > 5000 THEN 'Gold'
            WHEN total_spent > 1000 THEN 'Silver'
            ELSE 'Bronze'
        END as customer_segment
    FROM customer_stats
)
SELECT 
    customer_segment,
    COUNT(*) as customer_count,
    AVG(total_spent) as avg_total_spent,
    AVG(avg_order_value) as avg_order_value
FROM customer_segments
GROUP BY customer_segment
ORDER BY avg_total_spent DESC;
```

#### 9.2 제품 성과 분석
```sql
-- 제품별 성과와 재고 최적화 분석
WITH product_performance AS (
    SELECT 
        p.product_id,
        p.product_name,
        p.category,
        p.price,
        p.stock_quantity,
        COALESCE(SUM(oi.quantity), 0) as total_sold,
        COALESCE(SUM(oi.quantity * oi.unit_price), 0) as total_revenue
    FROM products p
    LEFT JOIN order_items oi ON p.product_id = oi.product_id
    GROUP BY p.product_id, p.product_name, p.category, p.price, p.stock_quantity
),
category_stats AS (
    SELECT 
        category,
        AVG(total_sold) as avg_sold_per_category,
        AVG(total_revenue) as avg_revenue_per_category
    FROM product_performance
    GROUP BY category
)
SELECT 
    pp.*,
    cs.avg_sold_per_category,
    CASE 
        WHEN pp.total_sold > cs.avg_sold_per_category * 1.5 THEN 'High Performer'
        WHEN pp.total_sold > cs.avg_sold_per_category * 0.5 THEN 'Average'
        ELSE 'Low Performer'
    END as performance_category,
    CASE 
        WHEN pp.stock_quantity > pp.total_sold * 2 THEN 'Overstocked'
        WHEN pp.stock_quantity < pp.total_sold * 0.1 THEN 'Understocked'
        ELSE 'Optimal'
    END as stock_status
FROM product_performance pp
JOIN category_stats cs ON pp.category = cs.category
ORDER BY pp.total_revenue DESC;
```

### 10. 성능 최적화 팁

#### 10.1 서브쿼리 vs JOIN
```sql
-- 비효율적: 상관 서브쿼리
SELECT e1.first_name, e1.last_name, e1.salary
FROM employees e1
WHERE e1.salary > (
    SELECT AVG(e2.salary)
    FROM employees e2
    WHERE e2.department = e1.department
);

-- 효율적: JOIN 사용
SELECT e.first_name, e.last_name, e.salary
FROM employees e
JOIN (
    SELECT department, AVG(salary) as avg_salary
    FROM employees
    GROUP BY department
) dept_avg ON e.department = dept_avg.department
WHERE e.salary > dept_avg.avg_salary;
```

#### 10.2 EXISTS vs IN
```sql
-- 큰 데이터셋에서는 EXISTS가 더 효율적
-- EXISTS 사용 (권장)
SELECT c.company_name
FROM customers c
WHERE EXISTS (
    SELECT 1 FROM orders o WHERE o.customer_id = c.customer_id
);

-- IN 사용 (작은 데이터셋에서만)
SELECT c.company_name
FROM customers c
WHERE c.customer_id IN (
    SELECT DISTINCT customer_id FROM orders
);
```

## 실습 데이터베이스

이번 장에서는 기존 테이블에 추가로 다음 테이블들을 사용합니다:

1. **orders** (주문)
   - order_id (주문 ID)
   - customer_id (고객 ID)
   - order_date (주문 날짜)
   - total_amount (총 금액)
   - status (주문 상태)

2. **order_items** (주문 상품)
   - order_item_id (주문 상품 ID)
   - order_id (주문 ID)
   - product_id (상품 ID)
   - quantity (수량)
   - unit_price (단가)

3. **employees_hierarchy** (직원 계층)
   - employee_id (직원 ID)
   - first_name (이름)
   - last_name (성)
   - manager_id (상급자 ID)
   - position_level (직급 레벨)

## 실습 문제

실습 문제는 `exercises/` 폴더에 있으며, 해답은 `solutions/` 폴더에서 확인할 수 있습니다.

### 기초 문제 (exercises/01_basic_subqueries.sql)
1. 평균 급여보다 높은 급여를 받는 직원 조회
2. 가장 비싼 상품과 같은 카테고리의 모든 상품 조회
3. 각 부서의 최고 급여를 받는 직원 정보 조회
4. 주문이 있는 고객만 조회 (EXISTS 사용)
5. 'Electronics' 카테고리 평균 가격보다 비싼 상품 조회

### 중급 문제 (exercises/02_advanced_subqueries.sql)
1. 부서별 급여 순위 TOP 2 직원 조회
2. 고객별 총 주문 금액과 평균 주문 금액 조회
3. 재고가 평균보다 적은 상품의 카테고리별 통계
4. 각 월별 주문 증가율 계산
5. 상관 서브쿼리를 사용한 연속 주문 고객 분석

### 고급 문제 (exercises/03_cte_complex.sql)
1. CTE를 사용한 고객 세그멘테이션 분석
2. 재귀 CTE를 사용한 조직도 조회
3. 다중 CTE를 사용한 제품 성과 분석
4. 이동 평균을 계산하는 CTE
5. 복잡한 비즈니스 로직을 CTE로 구현

## 다음 단계

Chapter 05를 완료했다면, Chapter 06에서 윈도우 함수와 분석 함수를 학습하여 더욱 고급 데이터 분석 기법을 익힙니다.