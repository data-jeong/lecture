-- Chapter 05: 고급 서브쿼리 실습 문제
-- 더 복잡한 비즈니스 로직을 서브쿼리로 구현하세요.

-- 문제 1: 각 부서에서 급여 순위 TOP 2인 직원을 조회하세요.
-- 부서, 이름, 급여, 부서내 순위를 표시하세요.
-- 힌트: 윈도우 함수 대신 서브쿼리로 구현


-- 문제 2: 고객별 총 주문 금액과 평균 주문 금액을 조회하되,
-- 평균 주문 금액이 전체 고객 평균보다 높은 고객만 표시하세요.
-- 힌트: 인라인 뷰와 서브쿼리 조합


-- 문제 3: 재고가 해당 카테고리 평균보다 적으면서, 동시에 
-- 평균 평점이 4.0 이상인 상품의 카테고리별 통계를 조회하세요.
-- 카테고리, 해당 상품 수, 평균 가격을 표시하세요.
-- 힌트: 복합 조건의 서브쿼리


-- 문제 4: 2023년 각 월 대비 다음 달 주문 증가율을 계산하세요.
-- 월, 해당월 주문수, 다음월 주문수, 증가율(%)을 표시하세요.
-- 힌트: 자기 참조 서브쿼리 활용


-- 문제 5: 연속으로 3번 이상 주문한 고객을 찾으세요.
-- (주문 날짜가 연속 3개월 이내에 있는 경우)
-- 고객명, 연속 주문 횟수를 표시하세요.
-- 힌트: 상관 서브쿼리로 날짜 범위 계산


-- 문제 6: 각 상품에 대해 "대체 상품" 추천 로직을 구현하세요.
-- 같은 카테고리, 비슷한 가격대(±20%), 더 높은 평점인 상품을 찾으세요.
-- 원본 상품명, 대체 상품명, 가격 차이, 평점 차이를 표시하세요.
-- 힌트: 복잡한 조건의 상관 서브쿼리


-- 문제 7: 부서별 "스타 직원"을 찾으세요.
-- (해당 부서에서 급여 TOP 25%이면서 입사 후 2년 이상된 직원)
-- 부서, 직원명, 급여, 부서내 급여 순위를 표시하세요.
-- 힌트: PERCENTILE 계산을 서브쿼리로 구현


-- 문제 8: 계절별 베스트셀러 상품을 찾으세요.
-- (분기별로 가장 많이 판매된 상품)
-- 분기, 상품명, 판매량, 매출액을 표시하세요.
-- 힌트: CASE문과 서브쿼리로 분기 구분


-- 문제 9: 고객 이탈 위험도를 계산하세요.
-- 마지막 주문으로부터 90일 이상 지났고, 과거 평균 주문 주기보다 길게 주문하지 않은 고객
-- 고객명, 마지막 주문일, 평균 주문 주기, 이탈 위험 점수를 표시하세요.
-- 힌트: 복잡한 날짜 계산 서브쿼리


-- 문제 10: 상품 재주문률을 계산하세요.
-- (동일 고객이 같은 상품을 2번 이상 주문한 비율)
-- 상품명, 총 주문 고객수, 재주문 고객수, 재주문률(%)을 표시하세요.
-- 힌트: EXISTS와 GROUP BY 조합


-- 문제 11: ABC 분석을 구현하세요.
-- 매출 기준으로 상품을 A(상위 70%), B(71-90%), C(91-100%) 그룹으로 분류
-- 상품명, 매출액, 누적 매출 비율, ABC 등급을 표시하세요.
-- 힌트: 서브쿼리로 누적 비율 계산


-- 문제 12: 부서간 급여 형평성을 분석하세요.
-- 각 부서의 급여 분포(Q1, Q2, Q3)와 다른 부서와의 격차를 계산하세요.
-- 부서명, Q1, Q2(중앙값), Q3, 전체 중앙값 대비 차이를 표시하세요.
-- 힌트: 서브쿼리로 사분위수 계산


-- 문제 13: 상품 생명주기 분석을 수행하세요.
-- 각 상품의 출시 후 월별 매출 추이를 분석하여 성장/성숙/쇠퇴 단계를 판단하세요.
-- 상품명, 출시 후 개월수, 최근 3개월 평균 매출, 이전 3개월 평균 매출, 생명주기 단계를 표시하세요.
-- 힌트: 복잡한 날짜 기반 서브쿼리


-- 문제 14: 크로스셀링 기회를 찾으세요.
-- 함께 자주 구매되는 상품 조합 중, 한 상품만 구매한 고객을 찾으세요.
-- 고객명, 구매한 상품, 추천 상품, 함께 구매 확률을 표시하세요.
-- 힌트: 복잡한 JOIN과 서브쿼리 조합


-- 문제 15: 동적 가격 최적화 분석을 수행하세요.
-- 각 상품에 대해 가격을 10% 인하했을 때 예상 매출 증가량을 계산하세요.
-- (과거 유사 상품의 가격 탄력성 기반으로 추정)
-- 상품명, 현재 가격, 추천 가격, 예상 매출 증가율을 표시하세요.
-- 힌트: 매우 복잡한 비즈니스 로직을 서브쿼리로 구현