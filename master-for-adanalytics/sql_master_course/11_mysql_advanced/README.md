# Chapter 11: MySQL 심화 - 성능 튜닝과 아키텍처

## 학습 목표
- MySQL 아키텍처와 스토리지 엔진 이해
- 성능 모니터링과 튜닝 기법 마스터
- 복제(Replication)와 고가용성 구성
- MySQL 특화 최적화 기법 습득

## 목차

### 1. MySQL 아키텍처 개요

#### 1.1 MySQL 계층 구조
```sql
-- MySQL 아키텍처 구성요소
-- 1. 연결 계층 (Connection Layer)
-- 2. SQL 계층 (SQL Layer)
-- 3. 스토리지 엔진 계층 (Storage Engine Layer)

-- 현재 스토리지 엔진 확인
SHOW ENGINES;

-- 테이블별 스토리지 엔진 확인
SELECT 
    table_name,
    engine,
    table_rows,
    data_length,
    index_length
FROM information_schema.tables
WHERE table_schema = 'sql_course';
```

### 2. 스토리지 엔진 비교

#### 2.1 InnoDB vs MyISAM
```sql
-- InnoDB 특징
-- - 트랜잭션 지원 (ACID)
-- - 행 수준 잠금
-- - 외래 키 제약조건
-- - 크래시 복구

-- MyISAM 특징
-- - 테이블 수준 잠금
-- - 전문 검색 인덱스 지원
-- - 공간 효율적
-- - 트랜잭션 미지원

-- 테이블 엔진 변경
ALTER TABLE table_name ENGINE = InnoDB;

-- InnoDB 버퍼 풀 상태 확인
SHOW ENGINE INNODB STATUS;
```

### 3. MySQL 성능 모니터링

#### 3.1 Performance Schema
```sql
-- Performance Schema 활성화
UPDATE performance_schema.setup_instruments 
SET ENABLED = 'YES', TIMED = 'YES'
WHERE NAME LIKE '%statement%';

-- 느린 쿼리 확인
SELECT 
    digest_text,
    count_star,
    avg_timer_wait/1000000000 AS avg_time_ms,
    sum_rows_examined,
    sum_rows_sent
FROM performance_schema.events_statements_summary_by_digest
ORDER BY avg_timer_wait DESC
LIMIT 10;

-- 인덱스 사용률 확인
SELECT 
    object_schema,
    object_name,
    index_name,
    count_read,
    count_write
FROM performance_schema.table_io_waits_summary_by_index_usage
WHERE object_schema = 'sql_course'
ORDER BY count_read + count_write DESC;
```

#### 3.2 슬로우 쿼리 로그
```sql
-- 슬로우 쿼리 설정
SET GLOBAL slow_query_log = 'ON';
SET GLOBAL long_query_time = 1;
SET GLOBAL log_queries_not_using_indexes = 'ON';

-- 슬로우 쿼리 로그 위치 확인
SHOW VARIABLES LIKE 'slow_query_log_file';
```

### 4. MySQL 쿼리 최적화

#### 4.1 옵티마이저 힌트
```sql
-- 인덱스 강제 사용
SELECT /*+ INDEX(e idx_department) */ *
FROM employees e
WHERE department = 'Sales';

-- 조인 순서 강제
SELECT /*+ LEADING(o c) */ *
FROM orders o
JOIN customers c ON o.customer_id = c.customer_id;

-- 특정 조인 알고리즘 사용
SELECT /*+ BNL(e d) */ *
FROM employees e
JOIN departments d ON e.department_id = d.id;
```

#### 4.2 파티셔닝
```sql
-- 범위 파티셔닝
CREATE TABLE sales_data (
    id INT,
    sale_date DATE,
    amount DECIMAL(10,2)
) 
PARTITION BY RANGE (YEAR(sale_date)) (
    PARTITION p2020 VALUES LESS THAN (2021),
    PARTITION p2021 VALUES LESS THAN (2022),
    PARTITION p2022 VALUES LESS THAN (2023),
    PARTITION p2023 VALUES LESS THAN (2024),
    PARTITION p_future VALUES LESS THAN MAXVALUE
);

-- 파티션 정보 확인
SELECT 
    partition_name,
    table_rows,
    data_length,
    index_length
FROM information_schema.partitions
WHERE table_name = 'sales_data';

-- 특정 파티션만 쿼리
SELECT * FROM sales_data PARTITION (p2023)
WHERE sale_date >= '2023-01-01';
```

### 5. InnoDB 최적화

#### 5.1 버퍼 풀 설정
```sql
-- 버퍼 풀 크기 확인
SHOW VARIABLES LIKE 'innodb_buffer_pool_size';

-- 버퍼 풀 상태 확인
SELECT 
    pool_id,
    pool_size,
    free_buffers,
    database_pages,
    dirty_pages,
    pages_made_young,
    pages_not_made_young
FROM information_schema.innodb_buffer_pool_stats;

-- 버퍼 풀 히트율 계산
SELECT 
    (1 - (Innodb_buffer_pool_reads / Innodb_buffer_pool_read_requests)) * 100 AS hit_ratio
FROM (
    SELECT 
        variable_value AS Innodb_buffer_pool_reads
    FROM performance_schema.global_status
    WHERE variable_name = 'Innodb_buffer_pool_reads'
) AS reads,
(
    SELECT 
        variable_value AS Innodb_buffer_pool_read_requests
    FROM performance_schema.global_status
    WHERE variable_name = 'Innodb_buffer_pool_read_requests'
) AS requests;
```

#### 5.2 트랜잭션 로그 최적화
```sql
-- 로그 파일 크기 확인
SHOW VARIABLES LIKE 'innodb_log_file_size';
SHOW VARIABLES LIKE 'innodb_log_files_in_group';

-- 체크포인트 성능 확인
SHOW ENGINE INNODB STATUS;
```

### 6. MySQL 복제 (Replication)

#### 6.1 마스터-슬레이브 설정
```sql
-- 마스터 설정
-- my.cnf 파일에 추가
-- [mysqld]
-- server-id = 1
-- log-bin = mysql-bin
-- binlog-format = ROW

-- 복제 사용자 생성 (마스터에서)
CREATE USER 'repl'@'%' IDENTIFIED BY 'password';
GRANT REPLICATION SLAVE ON *.* TO 'repl'@'%';

-- 마스터 상태 확인
SHOW MASTER STATUS;

-- 슬레이브 설정
CHANGE MASTER TO
    MASTER_HOST = 'master_host',
    MASTER_PORT = 3306,
    MASTER_USER = 'repl',
    MASTER_PASSWORD = 'password',
    MASTER_LOG_FILE = 'mysql-bin.000001',
    MASTER_LOG_POS = 154;

START SLAVE;
SHOW SLAVE STATUS\G
```

### 7. 인덱스 최적화

#### 7.1 복합 인덱스 전략
```sql
-- 카디널리티 확인
SELECT 
    column_name,
    cardinality
FROM information_schema.statistics
WHERE table_schema = 'sql_course'
    AND table_name = 'orders'
ORDER BY cardinality DESC;

-- 커버링 인덱스 생성
CREATE INDEX idx_covering 
ON orders(customer_id, order_date, status, total_amount);

-- 인덱스 통계 업데이트
ANALYZE TABLE orders;
```

#### 7.2 인덱스 유지보수
```sql
-- 프래그멘테이션 확인
SELECT 
    table_name,
    data_free,
    (data_length + index_length) AS total_size,
    ROUND(data_free / (data_length + index_length) * 100, 2) AS fragmentation_pct
FROM information_schema.tables
WHERE table_schema = 'sql_course'
    AND data_free > 0
ORDER BY data_free DESC;

-- 테이블 최적화
OPTIMIZE TABLE orders;
```

### 8. 쿼리 캐시와 버퍼

#### 8.1 쿼리 캐시 (MySQL 5.7 이하)
```sql
-- 쿼리 캐시 상태 확인
SHOW VARIABLES LIKE 'query_cache%';

-- 쿼리 캐시 통계
SHOW STATUS LIKE 'Qcache%';

-- 쿼리 캐시 비우기
FLUSH QUERY CACHE;
```

#### 8.2 기타 버퍼 설정
```sql
-- 주요 버퍼 설정 확인
SELECT 
    variable_name,
    variable_value
FROM performance_schema.global_variables
WHERE variable_name IN (
    'join_buffer_size',
    'sort_buffer_size',
    'read_buffer_size',
    'read_rnd_buffer_size'
);
```

### 9. 보안과 권한 관리

#### 9.1 사용자 권한 최적화
```sql
-- 권한 확인
SHOW GRANTS FOR 'user'@'host';

-- 최소 권한 원칙
GRANT SELECT, INSERT, UPDATE ON database.* TO 'app_user'@'localhost';

-- SSL 연결 강제
ALTER USER 'user'@'host' REQUIRE SSL;
```

### 10. 백업과 복구 전략

#### 10.1 논리적 백업
```bash
# mysqldump를 사용한 백업
mysqldump -u root -p --single-transaction --routines --triggers sql_course > backup.sql

# 특정 테이블만 백업
mysqldump -u root -p sql_course orders order_items > orders_backup.sql
```

#### 10.2 바이너리 로그를 이용한 복구
```sql
-- 바이너리 로그 확인
SHOW BINARY LOGS;

-- 특정 시점으로 복구
mysqlbinlog --start-datetime="2024-01-01 00:00:00" \
            --stop-datetime="2024-01-01 12:00:00" \
            mysql-bin.000001 | mysql -u root -p
```

## 실습 환경

이 장의 실습을 위해 MySQL 성능 모니터링과 튜닝을 위한 샘플 데이터베이스를 제공합니다.

## 주요 설정 파일 예제

```ini
# my.cnf 최적화 설정 예제
[mysqld]
# InnoDB 설정
innodb_buffer_pool_size = 1G
innodb_log_file_size = 256M
innodb_flush_log_at_trx_commit = 2
innodb_flush_method = O_DIRECT

# 쿼리 캐시 (MySQL 5.7)
query_cache_type = 1
query_cache_size = 128M

# 연결 설정
max_connections = 500
thread_cache_size = 50

# 로깅
slow_query_log = 1
long_query_time = 2
log_queries_not_using_indexes = 1
```

## 다음 단계

Chapter 12에서는 데이터 분석가 인터뷰를 위한 실전 SQL 문제들을 다룹니다.