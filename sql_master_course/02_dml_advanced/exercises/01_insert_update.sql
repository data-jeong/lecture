-- Chapter 02: INSERT와 UPDATE 실습 문제

-- 문제 1: employees_backup 테이블에 IT 부서 직원들의 데이터를 복사하세요.
-- SELECT를 이용한 INSERT를 사용하세요.



-- 문제 2: 새로운 주문 3건을 orders 테이블에 한 번에 삽입하세요.
-- 다중 행 INSERT를 사용하세요.
-- order_id: 9, 10, 11
-- customer_id: 8, 9, 10
-- order_date: 오늘 날짜
-- status: 'Pending'
-- total_amount: 500.00, 750.00, 1000.00



-- 문제 3: 모든 Electronics 카테고리 상품의 가격을 10% 인상하세요.
-- 동시에 last_modified 컬럼도 현재 시간으로 업데이트하세요.
-- (products 테이블에 last_modified 컬럼이 없다면 먼저 추가하세요)



-- 문제 4: 직원들의 급여를 성과 평가에 따라 인상하세요.
-- A등급: 15% 인상, B등급: 10% 인상, C등급: 5% 인상, D등급: 인상 없음
-- CASE 문을 사용하세요.



-- 문제 5: 재고가 10개 미만인 상품의 재고를 50개 추가하세요.
-- inventory 테이블을 업데이트하고, last_updated 시간도 갱신하세요.



-- 문제 6: product_changes 테이블을 활용한 가격 변경 추적
-- Electronics 카테고리 상품의 가격을 5% 인하하면서,
-- 변경 전후 가격을 product_changes 테이블에 기록하세요.
-- (힌트: INSERT와 UPDATE를 함께 사용)



-- 문제 7: 부서별 평균 급여보다 낮은 급여를 받는 직원들의 급여를
-- 해당 부서 평균 급여의 90%로 조정하세요.
-- (힌트: 서브쿼리를 활용한 UPDATE)



-- 문제 8: UPSERT를 사용하여 inventory 테이블을 업데이트하세요.
-- product_id가 21, 22, 23인 상품의 재고를 100개로 설정하세요.
-- 이미 존재하는 경우 기존 재고에 100을 추가하세요.
-- (PostgreSQL과 MySQL 각각의 문법으로 작성)