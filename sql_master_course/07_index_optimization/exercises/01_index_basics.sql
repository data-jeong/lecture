-- Chapter 07: 인덱스 기초 실습 문제

-- 문제 1: 기본 단일 컬럼 인덱스를 생성하고 성능을 비교하세요.
-- large_orders 테이블의 customer_id에 인덱스를 생성하기 전과 후의 쿼리 성능을 측정하세요.
-- 힌트: EXPLAIN ANALYZE 사용


-- 문제 2: 복합 인덱스를 생성하여 다중 조건 쿼리를 최적화하세요.
-- order_date와 status를 함께 검색하는 쿼리에 적합한 복합 인덱스를 설계하세요.
-- 힌트: 컬럼 순서의 중요성 고려


-- 문제 3: 부분 인덱스를 활용하여 저장 공간을 절약하세요.
-- 'completed' 상태의 주문만을 대상으로 하는 부분 인덱스를 생성하세요.
-- 힌트: WHERE 조건을 인덱스 정의에 포함


-- 문제 4: 인덱스의 선택도(Selectivity)를 계산하고 분석하세요.
-- 각 컬럼별 고유값의 비율을 계산하여 인덱스 효과를 예측하세요.
-- 힌트: DISTINCT COUNT / TOTAL COUNT


-- 문제 5: 커버링 인덱스를 설계하여 인덱스만으로 쿼리를 처리하세요.
-- 자주 사용되는 SELECT 쿼리가 인덱스만으로 처리되도록 INCLUDE 컬럼을 추가하세요.
-- 힌트: 인덱스에 추가 컬럼 포함