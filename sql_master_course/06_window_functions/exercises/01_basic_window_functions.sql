-- Chapter 06: 기초 윈도우 함수 실습 문제
-- 각 문제를 해결하는 SQL 쿼리를 작성하세요.

-- 문제 1: 직원들을 급여순으로 순위를 매기세요.
-- ROW_NUMBER, RANK, DENSE_RANK를 모두 사용하여 차이점을 보여주세요.
-- 결과: 이름, 급여, ROW_NUMBER, RANK, DENSE_RANK
-- 힌트: ORDER BY salary DESC 사용


-- 문제 2: 각 부서별로 급여 상위 3명의 직원을 조회하세요.
-- 결과: 부서, 이름, 급여, 부서내 순위
-- 힌트: ROW_NUMBER() OVER (PARTITION BY department ORDER BY salary DESC)


-- 문제 3: 일별 매출에서 전일 대비 매출 증감률을 계산하세요.
-- 결과: 날짜, 일별 매출, 전일 매출, 증감률(%)
-- 힌트: LAG 함수 사용, daily_sales 테이블


-- 문제 4: 각 카테고리에서 가장 비싼 상품과 가장 저렴한 상품의 가격을 조회하세요.
-- 모든 상품에 대해 해당 카테고리의 최고가와 최저가를 표시하세요.
-- 결과: 상품명, 카테고리, 가격, 카테고리 최고가, 카테고리 최저가
-- 힌트: FIRST_VALUE, LAST_VALUE 사용


-- 문제 5: 일별 매출의 누적 합계를 계산하세요.
-- 결과: 날짜, 일별 매출, 누적 매출
-- 힌트: SUM() OVER (ORDER BY date ROWS UNBOUNDED PRECEDING)


-- 문제 6: 각 직원의 성과 점수에서 다음 분기 성과와 비교하세요.
-- 결과: 직원명, 분기, 성과 점수, 다음 분기 성과, 성과 향상도
-- 힌트: LEAD 함수 사용, employee_performance 테이블


-- 문제 7: 상품별로 재고 이동 내역에서 각 이동의 누적 재고 변화량을 계산하세요.
-- 결과: 상품 ID, 날짜, 이동 유형, 수량, 누적 재고 변화
-- 힌트: SUM() OVER (PARTITION BY product_id ORDER BY movement_date)


-- 문제 8: 각 부서의 월별 목표 대비 달성률을 이전 달과 비교하세요.
-- 결과: 부서, 월, 목표, 달성률, 이전 달 달성률, 달성률 변화
-- 힌트: LAG 함수 사용, 달성률은 가정값 사용


-- 문제 9: 상품 가격의 백분위수를 계산하세요.
-- 각 상품이 전체 상품 중 몇 번째 백분위에 속하는지 표시하세요.
-- 결과: 상품명, 가격, 백분위수(PERCENT_RANK), 누적 분포(CUME_DIST)
-- 힌트: PERCENT_RANK(), CUME_DIST() 함수 사용


-- 문제 10: 일별 매출에서 7일 이동 평균을 계산하세요.
-- 결과: 날짜, 일별 매출, 7일 이동 평균
-- 힌트: AVG() OVER (ORDER BY date ROWS BETWEEN 6 PRECEDING AND CURRENT ROW)


-- 문제 11: 각 고객의 주문 날짜별로 순번을 매기고, 첫 번째 주문과 마지막 주문을 표시하세요.
-- 결과: 고객명, 주문 날짜, 주문 순번, 첫 주문일, 마지막 주문일
-- 힌트: ROW_NUMBER, FIRST_VALUE, LAST_VALUE 사용


-- 문제 12: 직원별 성과 점수를 4분위로 나누세요.
-- 결과: 직원명, 평균 성과 점수, 성과 분위(1-4)
-- 힌트: NTILE(4) 함수 사용


-- 문제 13: 상품별로 가장 최근 재고 이동 날짜와 유형을 조회하세요.
-- 결과: 상품 ID, 상품명, 최근 이동 날짜, 최근 이동 유형, 수량
-- 힌트: ROW_NUMBER() OVER (PARTITION BY product_id ORDER BY movement_date DESC)


-- 문제 14: 일별 매출에서 해당 월의 최고 매출일과 최저 매출일을 표시하세요.
-- 결과: 날짜, 일별 매출, 해당 월 최고 매출, 해당 월 최저 매출
-- 힌트: MAX(), MIN() OVER (PARTITION BY YEAR, MONTH)


-- 문제 15: 각 부서별로 직원들의 급여 누적 분포를 계산하세요.
-- 급여 기준으로 정렬했을 때 각 직원이 해당 부서에서 차지하는 비율을 표시하세요.
-- 결과: 부서, 직원명, 급여, 부서내 급여 누적 비율(%)
-- 힌트: CUME_DIST() OVER (PARTITION BY department ORDER BY salary)