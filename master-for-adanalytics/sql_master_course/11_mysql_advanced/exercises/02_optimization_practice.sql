-- Chapter 11: MySQL 최적화 실습

-- 문제 1: 복합 인덱스 설계
-- performance_test 테이블에서 user_id와 action_type으로 자주 검색한다고 가정하고,
-- 최적의 인덱스를 생성하세요. 생성 전후 실행 계획을 비교하세요.



-- 문제 2: 파티션 프루닝 최적화
-- 2023년 데이터만 조회하는 쿼리를 작성하고,
-- 파티션 프루닝이 제대로 작동하는지 실행 계획으로 확인하세요.



-- 문제 3: 쿼리 리팩토링
-- 다음 쿼리를 EXISTS나 JOIN을 사용하여 최적화하세요:
-- SELECT * FROM performance_test 
-- WHERE user_id IN (SELECT user_id FROM performance_test 
--                   WHERE action_type = 'purchase' 
--                   GROUP BY user_id HAVING COUNT(*) > 5);



-- 문제 4: 옵티마이저 힌트 활용
-- performance_test 테이블 조회 시 특정 인덱스를 강제로 사용하도록
-- 힌트를 추가한 쿼리를 작성하세요.



-- 문제 5: 임시 테이블 최적화
-- 대량의 집계 연산을 수행할 때 MEMORY 엔진을 사용한 
-- 임시 테이블로 성능을 개선하는 예제를 작성하세요.



-- 문제 6: 배치 INSERT 최적화
-- 10000개의 레코드를 performance_test에 삽입하는 가장 효율적인 방법을 구현하세요.
-- (힌트: 다중 값 INSERT, 트랜잭션 활용)



-- 문제 7: 인덱스 통계 업데이트
-- 모든 테이블의 인덱스 통계를 업데이트하고,
-- 통계 정보가 얼마나 정확한지 확인하는 쿼리를 작성하세요.



-- 문제 8: 쿼리 캐시 대안 구현
-- MySQL 8.0에서는 쿼리 캐시가 제거되었습니다.
-- cache_data 테이블을 활용하여 자주 사용되는 집계 결과를
-- 캐싱하는 방법을 구현하세요.