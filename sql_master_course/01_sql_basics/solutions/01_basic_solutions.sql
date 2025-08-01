-- Chapter 01: 기초 실습 문제 해답

-- 문제 1: employees 테이블에서 모든 직원 정보를 조회하세요.
SELECT * 
FROM employees;

-- 문제 2: 급여(salary)가 70000 이상인 직원의 이름(first_name, last_name)과 급여를 조회하세요.
SELECT first_name, last_name, salary
FROM employees
WHERE salary >= 70000;

-- 문제 3: Sales 부서의 직원 수를 계산하세요.
SELECT COUNT(*) as sales_employee_count
FROM employees
WHERE department = 'Sales';

-- 문제 4: 각 부서별 직원 수와 평균 급여를 조회하세요.
SELECT 
    department,
    COUNT(*) as employee_count,
    AVG(salary) as avg_salary
FROM employees
GROUP BY department
ORDER BY avg_salary DESC;

-- 문제 5: products 테이블에서 가격이 100달러 이상 500달러 이하인 상품을 조회하세요.
-- 방법 1: AND 사용
SELECT *
FROM products
WHERE price >= 100 AND price <= 500;

-- 방법 2: BETWEEN 사용
SELECT *
FROM products
WHERE price BETWEEN 100 AND 500;

-- 문제 6: 'Electronics' 또는 'Books' 카테고리에 속하는 상품의 이름과 가격을 조회하세요.
-- 방법 1: OR 사용
SELECT product_name, price
FROM products
WHERE category = 'Electronics' OR category = 'Books'
ORDER BY price;

-- 방법 2: IN 사용
SELECT product_name, price
FROM products
WHERE category IN ('Electronics', 'Books')
ORDER BY price;

-- 문제 7: 각 카테고리별 상품 수와 평균 가격을 조회하세요.
SELECT 
    category,
    COUNT(*) as product_count,
    AVG(price) as avg_price
FROM products
GROUP BY category
HAVING COUNT(*) >= 3;

-- 문제 8: customers 테이블에서 미국(USA)에 있지 않은 고객들을 조회하세요.
-- 방법 1: NOT 사용
SELECT *
FROM customers
WHERE NOT country = 'USA';

-- 방법 2: <> 또는 != 사용
SELECT *
FROM customers
WHERE country <> 'USA';

-- 문제 9: 2020년 이후에 입사한 직원들의 정보를 조회하세요.
SELECT *
FROM employees
WHERE hire_date >= '2020-01-01'
ORDER BY hire_date DESC;

-- 문제 10: 가장 높은 급여를 받는 직원 3명의 정보를 조회하세요.
SELECT *
FROM employees
ORDER BY salary DESC
LIMIT 3;