-- Chapter 01: 중급 실습 문제 해답

-- 문제 1: 가장 비싼 상품 TOP 5를 조회하세요.
SELECT 
    product_name,
    category,
    price
FROM products
ORDER BY price DESC
LIMIT 5;

-- 문제 2: 재고가 10개 미만인 Electronics 카테고리 상품을 조회하세요.
SELECT *
FROM products
WHERE category = 'Electronics' 
  AND stock_quantity < 10
ORDER BY stock_quantity;

-- 문제 3: 국가별 고객 수를 조회하되, 고객이 5명 이상인 국가만 표시하세요.
SELECT 
    country,
    COUNT(*) as customer_count
FROM customers
GROUP BY country
HAVING COUNT(*) >= 5
ORDER BY customer_count DESC;

-- 문제 4: 부서별 최고 급여와 최저 급여, 그리고 급여 차이를 계산하세요.
SELECT 
    department,
    MAX(salary) as max_salary,
    MIN(salary) as min_salary,
    MAX(salary) - MIN(salary) as salary_difference
FROM employees
GROUP BY department
ORDER BY salary_difference DESC;

-- 문제 5: 각 카테고리에서 가장 비싼 상품의 정보를 조회하세요.
-- 방법 1: 서브쿼리 사용
SELECT p.*
FROM products p
WHERE (category, price) IN (
    SELECT category, MAX(price)
    FROM products
    GROUP BY category
);

-- 방법 2: JOIN 사용
SELECT p.*
FROM products p
INNER JOIN (
    SELECT category, MAX(price) as max_price
    FROM products
    GROUP BY category
) max_prices
ON p.category = max_prices.category 
AND p.price = max_prices.max_price;

-- 문제 6: 평균 급여보다 높은 급여를 받는 직원들의 정보를 조회하세요.
SELECT 
    first_name,
    last_name,
    department,
    salary
FROM employees
WHERE salary > (SELECT AVG(salary) FROM employees)
ORDER BY salary DESC;

-- 문제 7: 각 도시별 고객 수를 구하고, 2개 이상의 고객이 있는 도시만 표시하세요.
SELECT 
    country,
    city,
    COUNT(*) as customer_count
FROM customers
GROUP BY country, city
HAVING COUNT(*) >= 2
ORDER BY country, customer_count DESC;

-- 문제 8: 직원 수가 가장 많은 부서 TOP 3를 조회하세요.
SELECT 
    department,
    COUNT(*) as employee_count,
    AVG(salary) as avg_salary
FROM employees
GROUP BY department
ORDER BY employee_count DESC
LIMIT 3;

-- 문제 9: 재고 금액이 가장 높은 상품 10개를 조회하세요.
SELECT 
    product_name,
    stock_quantity,
    price as unit_price,
    price * stock_quantity as total_inventory_value
FROM products
ORDER BY total_inventory_value DESC
LIMIT 10;

-- 문제 10: 2019년도와 2020년 이후 입사 직원들의 평균 급여 비교
-- 방법 1: CASE WHEN 사용
SELECT 
    CASE 
        WHEN EXTRACT(YEAR FROM hire_date) = 2019 THEN '2019년 입사'
        WHEN hire_date >= '2020-01-01' THEN '2020년 이후 입사'
    END as hire_period,
    AVG(salary) as avg_salary,
    COUNT(*) as employee_count
FROM employees
WHERE hire_date >= '2019-01-01'
GROUP BY 
    CASE 
        WHEN EXTRACT(YEAR FROM hire_date) = 2019 THEN '2019년 입사'
        WHEN hire_date >= '2020-01-01' THEN '2020년 이후 입사'
    END;

-- 방법 2: 개별 쿼리로 비교
-- 2019년 입사자 평균 급여
SELECT 
    '2019년 입사' as period,
    AVG(salary) as avg_salary
FROM employees
WHERE EXTRACT(YEAR FROM hire_date) = 2019

UNION ALL

-- 2020년 이후 입사자 평균 급여
SELECT 
    '2020년 이후 입사' as period,
    AVG(salary) as avg_salary
FROM employees
WHERE hire_date >= '2020-01-01';