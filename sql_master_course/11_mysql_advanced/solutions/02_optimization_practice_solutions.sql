-- Chapter 11: MySQL 최적화 실습 해답

-- 문제 1: 복합 인덱스 설계
-- 실행 계획 확인 (인덱스 생성 전)
EXPLAIN SELECT * FROM performance_test 
WHERE user_id = 1234 AND action_type = 'purchase';

-- 복합 인덱스 생성
CREATE INDEX idx_user_action ON performance_test(user_id, action_type);

-- 추가로 시간 범위 검색이 많다면
CREATE INDEX idx_user_action_time ON performance_test(user_id, action_type, action_timestamp);

-- 실행 계획 확인 (인덱스 생성 후)
EXPLAIN SELECT * FROM performance_test 
WHERE user_id = 1234 AND action_type = 'purchase';

-- 인덱스 사용 통계 확인
SHOW INDEX FROM performance_test;

-- 문제 2: 파티션 프루닝 최적화
-- 파티션 프루닝이 작동하는 쿼리
EXPLAIN SELECT * FROM sales_partitioned 
WHERE sale_date >= '2023-01-01' AND sale_date < '2024-01-01';

-- EXPLAIN PARTITIONS로 더 자세히 확인 (MySQL 5.7)
EXPLAIN PARTITIONS SELECT COUNT(*), SUM(amount) 
FROM sales_partitioned 
WHERE sale_date BETWEEN '2023-01-01' AND '2023-12-31';

-- 특정 파티션만 직접 조회
SELECT COUNT(*) AS record_count, SUM(amount) AS total_sales
FROM sales_partitioned PARTITION (p2023);

-- 문제 3: 쿼리 리팩토링
-- 원본 쿼리 (IN 서브쿼리 사용)
EXPLAIN SELECT * FROM performance_test 
WHERE user_id IN (
    SELECT user_id FROM performance_test 
    WHERE action_type = 'purchase' 
    GROUP BY user_id HAVING COUNT(*) > 5
);

-- 최적화 1: EXISTS 사용
EXPLAIN SELECT DISTINCT p1.* 
FROM performance_test p1
WHERE EXISTS (
    SELECT 1 
    FROM performance_test p2 
    WHERE p2.user_id = p1.user_id 
        AND p2.action_type = 'purchase'
    GROUP BY p2.user_id 
    HAVING COUNT(*) > 5
);

-- 최적화 2: JOIN 사용
EXPLAIN SELECT DISTINCT p1.*
FROM performance_test p1
INNER JOIN (
    SELECT user_id
    FROM performance_test
    WHERE action_type = 'purchase'
    GROUP BY user_id
    HAVING COUNT(*) > 5
) frequent_buyers ON p1.user_id = frequent_buyers.user_id;

-- 문제 4: 옵티마이저 힌트 활용
-- 인덱스 힌트
SELECT /*+ INDEX(performance_test idx_user_id) */ *
FROM performance_test
WHERE user_id = 1234;

-- 조인 순서 힌트
SELECT /*+ LEADING(p1 p2) */ *
FROM performance_test p1
JOIN performance_test p2 ON p1.user_id = p2.user_id
WHERE p1.action_type = 'login';

-- 조인 알고리즘 힌트
SELECT /*+ NO_BNL(p1, p2) */ *
FROM performance_test p1
JOIN performance_test p2 ON p1.user_id = p2.user_id;

-- 문제 5: 임시 테이블 최적화
-- MEMORY 엔진 임시 테이블 생성
CREATE TEMPORARY TABLE temp_user_summary (
    user_id INT PRIMARY KEY,
    total_actions INT,
    last_action TIMESTAMP
) ENGINE=MEMORY;

-- 데이터 집계 및 저장
INSERT INTO temp_user_summary
SELECT 
    user_id,
    COUNT(*) as total_actions,
    MAX(action_timestamp) as last_action
FROM performance_test
WHERE action_timestamp >= DATE_SUB(NOW(), INTERVAL 30 DAY)
GROUP BY user_id;

-- 임시 테이블 활용
SELECT * FROM temp_user_summary 
WHERE total_actions > 100
ORDER BY total_actions DESC;

DROP TEMPORARY TABLE temp_user_summary;

-- 문제 6: 배치 INSERT 최적화
-- 방법 1: 다중 값 INSERT
DELIMITER $$
CREATE PROCEDURE batch_insert_optimized()
BEGIN
    DECLARE i INT DEFAULT 0;
    DECLARE batch_size INT DEFAULT 1000;
    DECLARE sql_values TEXT DEFAULT '';
    
    -- 자동 커밋 비활성화
    SET autocommit = 0;
    START TRANSACTION;
    
    WHILE i < 10000 DO
        -- 배치 값 생성
        IF i % batch_size = 0 THEN
            IF i > 0 THEN
                -- 배치 INSERT 실행
                SET @sql = CONCAT('INSERT INTO performance_test (user_id, action_type, data, ip_address) VALUES ', 
                                SUBSTRING(sql_values, 2));
                PREPARE stmt FROM @sql;
                EXECUTE stmt;
                DEALLOCATE PREPARE stmt;
                
                -- 값 초기화
                SET sql_values = '';
            END IF;
        END IF;
        
        -- 값 추가
        SET sql_values = CONCAT(sql_values, ',(',
            FLOOR(1 + RAND() * 10000), ',',
            '"', ELT(FLOOR(1 + RAND() * 5), 'login', 'logout', 'purchase', 'view', 'click'), '",',
            '\'{"test": "data"}\',',
            '"192.168.1.', FLOOR(RAND() * 255), '")'
        );
        
        SET i = i + 1;
    END WHILE;
    
    -- 마지막 배치 처리
    IF sql_values != '' THEN
        SET @sql = CONCAT('INSERT INTO performance_test (user_id, action_type, data, ip_address) VALUES ', 
                        SUBSTRING(sql_values, 2));
        PREPARE stmt FROM @sql;
        EXECUTE stmt;
        DEALLOCATE PREPARE stmt;
    END IF;
    
    COMMIT;
    SET autocommit = 1;
END$$
DELIMITER ;

-- 방법 2: LOAD DATA INFILE (가장 빠름)
-- CSV 파일 생성 후
-- LOAD DATA INFILE '/tmp/performance_data.csv'
-- INTO TABLE performance_test
-- FIELDS TERMINATED BY ',' 
-- LINES TERMINATED BY '\n'
-- (user_id, action_type, @json_data, ip_address)
-- SET data = @json_data;

-- 문제 7: 인덱스 통계 업데이트
-- 모든 테이블 통계 업데이트
ANALYZE TABLE performance_test, sales_partitioned, articles, cache_data;

-- 통계 정확도 확인
SELECT 
    s.table_name,
    s.index_name,
    s.column_name,
    s.cardinality,
    t.table_rows,
    ROUND(s.cardinality / NULLIF(t.table_rows, 0) * 100, 2) AS selectivity_pct
FROM information_schema.statistics s
JOIN information_schema.tables t 
    ON s.table_schema = t.table_schema 
    AND s.table_name = t.table_name
WHERE s.table_schema = 'sql_course'
    AND s.cardinality IS NOT NULL
ORDER BY s.table_name, s.index_name, s.seq_in_index;

-- 문제 8: 쿼리 캐시 대안 구현
-- 캐시 테이블에 집계 결과 저장
DELIMITER $$
CREATE PROCEDURE cache_daily_stats(IN target_date DATE)
BEGIN
    DECLARE cache_key VARCHAR(255);
    DECLARE cache_value TEXT;
    
    SET cache_key = CONCAT('daily_stats_', target_date);
    
    -- 집계 수행
    SELECT JSON_OBJECT(
        'date', target_date,
        'total_users', COUNT(DISTINCT user_id),
        'total_actions', COUNT(*),
        'action_breakdown', JSON_OBJECTAGG(action_type, action_count)
    ) INTO cache_value
    FROM (
        SELECT 
            action_type,
            COUNT(*) as action_count
        FROM performance_test
        WHERE DATE(action_timestamp) = target_date
        GROUP BY action_type
    ) summary
    CROSS JOIN (
        SELECT COUNT(DISTINCT user_id) as total_users, COUNT(*) as total_actions
        FROM performance_test
        WHERE DATE(action_timestamp) = target_date
    ) totals;
    
    -- 캐시에 저장 (UPSERT)
    INSERT INTO cache_data (cache_key, cache_value, expiry_time)
    VALUES (cache_key, cache_value, DATE_ADD(NOW(), INTERVAL 1 DAY))
    ON DUPLICATE KEY UPDATE 
        cache_value = VALUES(cache_value),
        expiry_time = VALUES(expiry_time);
END$$

-- 캐시 조회 함수
CREATE FUNCTION get_cached_stats(target_date DATE) 
RETURNS JSON
READS SQL DATA
BEGIN
    DECLARE result TEXT;
    
    SELECT cache_value INTO result
    FROM cache_data
    WHERE cache_key = CONCAT('daily_stats_', target_date)
        AND expiry_time > NOW()
    LIMIT 1;
    
    IF result IS NULL THEN
        -- 캐시 미스 시 재생성
        CALL cache_daily_stats(target_date);
        
        SELECT cache_value INTO result
        FROM cache_data
        WHERE cache_key = CONCAT('daily_stats_', target_date)
        LIMIT 1;
    END IF;
    
    RETURN result;
END$$
DELIMITER ;

-- 사용 예
SELECT get_cached_stats('2024-01-01');