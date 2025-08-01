-- Chapter 05: 기초 서브쿼리 실습 문제
-- 각 문제를 해결하는 SQL 쿼리를 작성하세요.

-- 문제 1: 평균 급여보다 높은 급여를 받는 직원의 이름, 부서, 급여를 조회하세요.
-- 결과는 급여가 높은 순으로 정렬하세요.
-- 힌트: WHERE 절에 서브쿼리 사용, AVG 함수


-- 문제 2: 가장 비싼 상품과 같은 카테고리에 속하는 모든 상품을 조회하세요.
-- 상품명, 카테고리, 가격을 표시하고 가격순으로 정렬하세요.
-- 힌트: WHERE 절에 서브쿼리 사용, MAX 함수


-- 문제 3: 각 부서에서 가장 높은 급여를 받는 직원의 정보를 조회하세요.
-- 이름, 부서, 급여를 표시하세요.
-- 힌트: 상관 서브쿼리 사용


-- 문제 4: 주문이 한 번이라도 있는 고객의 정보를 조회하세요.
-- EXISTS 연산자를 사용하세요.
-- 힌트: WHERE EXISTS (SELECT...)


-- 문제 5: 'Electronics' 카테고리의 평균 가격보다 비싼 모든 상품을 조회하세요.
-- 상품명, 카테고리, 가격을 표시하세요.
-- 힌트: WHERE 절에 서브쿼리로 평균 계산


-- 문제 6: 2023년에 주문한 적이 없는 고객을 조회하세요.
-- NOT EXISTS를 사용하세요.
-- 힌트: WHERE NOT EXISTS와 YEAR 함수 활용


-- 문제 7: 재고량이 해당 카테고리 평균 재고량보다 적은 상품을 조회하세요.
-- 상품명, 카테고리, 재고량, 카테고리 평균 재고량을 표시하세요.
-- 힌트: 상관 서브쿼리와 스칼라 서브쿼리 조합


-- 문제 8: 가장 많은 주문을 한 고객의 정보와 주문 횟수를 조회하세요.
-- 힌트: 서브쿼리에서 COUNT와 GROUP BY 사용


-- 문제 9: 평균 주문 금액보다 큰 주문들의 정보를 조회하세요.
-- 주문 ID, 고객명, 주문 날짜, 총 금액을 표시하세요.
-- 힌트: JOIN과 서브쿼리 조합


-- 문제 10: 각 상품에 대한 평점이 4.0 이상인 상품만 조회하세요.
-- 상품명, 카테고리, 평균 평점을 표시하세요.
-- 힌트: product_reviews 테이블 활용, HAVING 절 사용


-- 문제 11: 어떤 IT 부서 직원보다 급여가 높은 다른 부서 직원을 조회하세요.
-- ANY 연산자를 사용하세요.
-- 힌트: WHERE salary > ANY (SELECT...)


-- 문제 12: 모든 Marketing 부서 직원보다 급여가 높은 직원을 조회하세요.
-- ALL 연산자를 사용하세요.
-- 힌트: WHERE salary > ALL (SELECT...)


-- 문제 13: 2023년 각 월별로 가장 많은 매출을 올린 상품을 조회하세요.
-- 월, 상품명, 매출액을 표시하세요.
-- 힌트: 복잡한 서브쿼리와 GROUP BY 활용


-- 문제 14: 자신의 부서 평균 급여보다 높은 급여를 받는 직원 수를 부서별로 조회하세요.
-- 부서명, 해당 직원 수를 표시하세요.
-- 힌트: 상관 서브쿼리와 중첩 서브쿼리


-- 문제 15: 가장 인기있는 카테고리(주문된 상품 수 기준)의 모든 상품을 조회하세요.
-- 상품명, 가격, 재고량을 표시하세요.
-- 힌트: 서브쿼리에서 JOIN과 GROUP BY 사용