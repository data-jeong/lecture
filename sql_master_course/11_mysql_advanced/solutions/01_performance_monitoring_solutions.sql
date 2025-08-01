-- Chapter 11: MySQL 성능 모니터링 실습 해답

-- 문제 1: 가장 자주 실행되는 쿼리 TOP 5
SELECT 
    query_digest,
    query_text,
    execution_count,
    avg_time_ms,
    total_time_ms,
    execution_count * avg_time_ms AS total_impact
FROM query_performance_log
ORDER BY execution_count DESC
LIMIT 5;

-- 문제 2: InnoDB 버퍼 풀 히트율 계산
SELECT 
    @reads := (SELECT VARIABLE_VALUE 
               FROM performance_schema.global_status 
               WHERE VARIABLE_NAME = 'Innodb_buffer_pool_reads') AS buffer_pool_reads,
    @requests := (SELECT VARIABLE_VALUE 
                  FROM performance_schema.global_status 
                  WHERE VARIABLE_NAME = 'Innodb_buffer_pool_read_requests') AS read_requests,
    @hit_rate := (1 - (@reads / @requests)) * 100 AS hit_rate_pct,
    CASE 
        WHEN @hit_rate >= 95 THEN 'Good'
        WHEN @hit_rate >= 90 THEN 'Fair'
        ELSE 'Poor'
    END AS performance_status;

-- 문제 3: 효율적인 인덱스 찾기
SELECT 
    table_name,
    index_name,
    read_count,
    write_count,
    ROUND(read_count / NULLIF(write_count, 0), 2) AS read_write_ratio
FROM index_usage_stats
WHERE read_count >= write_count * 10
ORDER BY read_write_ratio DESC;

-- 문제 4: 파티션별 데이터 분포
SELECT 
    partition_name,
    table_rows,
    data_length / 1024 / 1024 AS data_size_mb,
    index_length / 1024 / 1024 AS index_size_mb,
    (data_length + index_length) / 1024 / 1024 AS total_size_mb
FROM information_schema.partitions
WHERE table_schema = 'sql_course'
    AND table_name = 'sales_partitioned'
    AND partition_name IS NOT NULL
ORDER BY partition_ordinal_position;

-- 문제 5: 전문 검색으로 'performance' 찾기
SELECT 
    id,
    title,
    author,
    published_date,
    MATCH(title, content) AGAINST('performance' IN NATURAL LANGUAGE MODE) AS relevance_score
FROM articles
WHERE MATCH(title, content) AGAINST('performance' IN NATURAL LANGUAGE MODE)
ORDER BY relevance_score DESC;

-- Boolean 모드로 더 정확한 검색
SELECT 
    id,
    title,
    author,
    MATCH(title, content) AGAINST('+performance +MySQL' IN BOOLEAN MODE) AS relevance
FROM articles
WHERE MATCH(title, content) AGAINST('+performance +MySQL' IN BOOLEAN MODE);

-- 문제 6: 비효율적인 쿼리 식별
SELECT 
    query_digest,
    query_text,
    avg_time_ms,
    rows_examined_avg,
    rows_sent_avg,
    ROUND(rows_examined_avg / NULLIF(rows_sent_avg, 0), 2) AS examine_send_ratio,
    'Consider adding appropriate indexes or rewriting the query' AS recommendation
FROM query_performance_log
WHERE avg_time_ms > 50
    AND rows_examined_avg > rows_sent_avg * 100
ORDER BY avg_time_ms DESC;

-- 문제 7: 프래그멘테이션 확인
SELECT 
    table_schema,
    table_name,
    ROUND(data_length / 1024 / 1024, 2) AS data_size_mb,
    ROUND(data_free / 1024 / 1024, 2) AS free_space_mb,
    ROUND(data_free / (data_length + index_length) * 100, 2) AS fragmentation_pct,
    CONCAT('OPTIMIZE TABLE ', table_schema, '.', table_name, ';') AS optimization_command
FROM information_schema.tables
WHERE table_schema = 'sql_course'
    AND data_free > 0
    AND (data_free / (data_length + index_length)) > 0.2
ORDER BY data_free DESC;

-- 문제 8: 장시간 실행 중인 쿼리 모니터링
-- 방법 1: PROCESSLIST 사용
SELECT 
    id,
    user,
    host,
    db,
    command,
    time AS seconds_running,
    state,
    LEFT(info, 100) AS query_preview
FROM information_schema.processlist
WHERE command != 'Sleep'
    AND time > 5
ORDER BY time DESC;

-- 방법 2: Performance Schema 사용 (더 상세한 정보)
SELECT 
    thread_id,
    event_name,
    sql_text,
    timer_wait / 1000000000 AS seconds_running,
    lock_time / 1000000000 AS lock_time_seconds,
    rows_examined,
    rows_sent
FROM performance_schema.events_statements_current
WHERE timer_wait > 5000000000  -- 5초 이상
ORDER BY timer_wait DESC;