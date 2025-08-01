-- Chapter 05: 기초 서브쿼리 실습 문제 해답

-- 문제 1: 평균 급여보다 높은 급여를 받는 직원의 이름, 부서, 급여를 조회하세요.
SELECT first_name, last_name, department, salary
FROM employees
WHERE salary > (SELECT AVG(salary) FROM employees)
ORDER BY salary DESC;

-- 문제 2: 가장 비싼 상품과 같은 카테고리에 속하는 모든 상품을 조회하세요.
SELECT product_name, category, price
FROM products
WHERE category = (
    SELECT category 
    FROM products 
    ORDER BY price DESC 
    LIMIT 1
)
ORDER BY price DESC;

-- 문제 3: 각 부서에서 가장 높은 급여를 받는 직원의 정보를 조회하세요.
SELECT first_name, last_name, department, salary
FROM employees e1
WHERE salary = (
    SELECT MAX(salary)
    FROM employees e2
    WHERE e2.department = e1.department
);

-- 문제 4: 주문이 한 번이라도 있는 고객의 정보를 조회하세요.
SELECT customer_id, company_name, contact_name, country
FROM customers c
WHERE EXISTS (
    SELECT 1 
    FROM orders o 
    WHERE o.customer_id = c.customer_id
);

-- 문제 5: 'Electronics' 카테고리의 평균 가격보다 비싼 모든 상품을 조회하세요.
SELECT product_name, category, price
FROM products
WHERE price > (
    SELECT AVG(price) 
    FROM products 
    WHERE category = 'Electronics'
)
ORDER BY price DESC;

-- 문제 6: 2023년에 주문한 적이 없는 고객을 조회하세요.
SELECT customer_id, company_name, contact_name
FROM customers c
WHERE NOT EXISTS (
    SELECT 1 
    FROM orders o 
    WHERE o.customer_id = c.customer_id 
    AND EXTRACT(YEAR FROM o.order_date) = 2023
);

-- 문제 7: 재고량이 해당 카테고리 평균 재고량보다 적은 상품을 조회하세요.
SELECT 
    product_name, 
    category, 
    stock_quantity,
    (SELECT AVG(stock_quantity) 
     FROM products p2 
     WHERE p2.category = p1.category) as category_avg_stock
FROM products p1
WHERE stock_quantity < (
    SELECT AVG(stock_quantity) 
    FROM products p2 
    WHERE p2.category = p1.category
);

-- 문제 8: 가장 많은 주문을 한 고객의 정보와 주문 횟수를 조회하세요.
SELECT 
    c.customer_id,
    c.company_name,
    c.contact_name,
    (SELECT COUNT(*) FROM orders o WHERE o.customer_id = c.customer_id) as order_count
FROM customers c
WHERE (SELECT COUNT(*) FROM orders o WHERE o.customer_id = c.customer_id) = (
    SELECT MAX(order_count)
    FROM (
        SELECT COUNT(*) as order_count
        FROM orders
        GROUP BY customer_id
    ) sub
);

-- 문제 9: 평균 주문 금액보다 큰 주문들의 정보를 조회하세요.
SELECT 
    o.order_id,
    c.company_name,
    o.order_date,
    o.total_amount
FROM orders o
JOIN customers c ON o.customer_id = c.customer_id
WHERE o.total_amount > (SELECT AVG(total_amount) FROM orders)
ORDER BY o.total_amount DESC;

-- 문제 10: 각 상품에 대한 평점이 4.0 이상인 상품만 조회하세요.
SELECT 
    p.product_name,
    p.category,
    AVG(pr.rating) as avg_rating
FROM products p
JOIN product_reviews pr ON p.product_id = pr.product_id
GROUP BY p.product_id, p.product_name, p.category
HAVING AVG(pr.rating) >= 4.0
ORDER BY avg_rating DESC;

-- 문제 11: 어떤 IT 부서 직원보다 급여가 높은 다른 부서 직원을 조회하세요.
SELECT first_name, last_name, department, salary
FROM employees
WHERE salary > ANY (
    SELECT salary 
    FROM employees 
    WHERE department = 'IT'
) AND department != 'IT'
ORDER BY salary DESC;

-- 문제 12: 모든 Marketing 부서 직원보다 급여가 높은 직원을 조회하세요.
SELECT first_name, last_name, department, salary
FROM employees
WHERE salary > ALL (
    SELECT salary 
    FROM employees 
    WHERE department = 'Marketing'
)
ORDER BY salary DESC;

-- 문제 13: 2023년 각 월별로 가장 많은 매출을 올린 상품을 조회하세요.
SELECT 
    monthly_sales.order_month,
    p.product_name,
    monthly_sales.total_revenue
FROM (
    SELECT 
        EXTRACT(MONTH FROM o.order_date) as order_month,
        oi.product_id,
        SUM(oi.quantity * oi.unit_price) as total_revenue,
        ROW_NUMBER() OVER (PARTITION BY EXTRACT(MONTH FROM o.order_date) ORDER BY SUM(oi.quantity * oi.unit_price) DESC) as rn
    FROM orders o
    JOIN order_items oi ON o.order_id = oi.order_id
    WHERE EXTRACT(YEAR FROM o.order_date) = 2023
    GROUP BY EXTRACT(MONTH FROM o.order_date), oi.product_id
) monthly_sales
JOIN products p ON monthly_sales.product_id = p.product_id
WHERE monthly_sales.rn = 1
ORDER BY monthly_sales.order_month;

-- 문제 14: 자신의 부서 평균 급여보다 높은 급여를 받는 직원 수를 부서별로 조회하세요.
SELECT 
    department,
    COUNT(*) as high_earner_count
FROM employees e1
WHERE salary > (
    SELECT AVG(salary)
    FROM employees e2
    WHERE e2.department = e1.department
)
GROUP BY department
ORDER BY high_earner_count DESC;

-- 문제 15: 가장 인기있는 카테고리(주문된 상품 수 기준)의 모든 상품을 조회하세요.
SELECT 
    p.product_name,
    p.price,
    p.stock_quantity
FROM products p
WHERE p.category = (
    SELECT p2.category
    FROM products p2
    JOIN order_items oi ON p2.product_id = oi.product_id
    GROUP BY p2.category
    ORDER BY SUM(oi.quantity) DESC
    LIMIT 1
)
ORDER BY p.price DESC;