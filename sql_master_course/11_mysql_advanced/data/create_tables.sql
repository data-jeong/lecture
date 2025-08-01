-- Chapter 11: MySQL 성능 테스트용 데이터베이스

-- 대용량 데이터 테스트를 위한 테이블
DROP TABLE IF EXISTS performance_test;
CREATE TABLE performance_test (
    id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT NOT NULL,
    action_type VARCHAR(50),
    action_timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    data JSON,
    ip_address VARCHAR(45),
    INDEX idx_user_id (user_id),
    INDEX idx_timestamp (action_timestamp),
    INDEX idx_user_timestamp (user_id, action_timestamp)
) ENGINE=InnoDB;

-- 파티션 테이블 예제
DROP TABLE IF EXISTS sales_partitioned;
CREATE TABLE sales_partitioned (
    id INT NOT NULL,
    sale_date DATE NOT NULL,
    store_id INT,
    product_id INT,
    quantity INT,
    amount DECIMAL(10,2),
    PRIMARY KEY (id, sale_date)
) ENGINE=InnoDB
PARTITION BY RANGE (YEAR(sale_date)) (
    PARTITION p2020 VALUES LESS THAN (2021),
    PARTITION p2021 VALUES LESS THAN (2022),
    PARTITION p2022 VALUES LESS THAN (2023),
    PARTITION p2023 VALUES LESS THAN (2024),
    PARTITION p2024 VALUES LESS THAN (2025)
);

-- 메모리 테이블 예제
DROP TABLE IF EXISTS cache_data;
CREATE TABLE cache_data (
    cache_key VARCHAR(255) PRIMARY KEY,
    cache_value TEXT,
    expiry_time TIMESTAMP,
    INDEX idx_expiry (expiry_time)
) ENGINE=MEMORY;

-- MyISAM 테이블 (전문 검색용)
DROP TABLE IF EXISTS articles;
CREATE TABLE articles (
    id INT AUTO_INCREMENT PRIMARY KEY,
    title VARCHAR(255),
    content TEXT,
    author VARCHAR(100),
    published_date DATE,
    FULLTEXT idx_fulltext (title, content)
) ENGINE=MyISAM;

-- 복제 모니터링 테이블
DROP TABLE IF EXISTS replication_monitor;
CREATE TABLE replication_monitor (
    check_id INT AUTO_INCREMENT PRIMARY KEY,
    check_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    master_position VARCHAR(255),
    slave_lag_seconds INT,
    status VARCHAR(50)
) ENGINE=InnoDB;

-- 쿼리 성능 로그 테이블
DROP TABLE IF EXISTS query_performance_log;
CREATE TABLE query_performance_log (
    log_id INT AUTO_INCREMENT PRIMARY KEY,
    query_digest VARCHAR(64),
    query_text TEXT,
    execution_count INT DEFAULT 0,
    total_time_ms DECIMAL(15,3),
    avg_time_ms DECIMAL(15,3),
    max_time_ms DECIMAL(15,3),
    rows_examined_avg INT,
    rows_sent_avg INT,
    last_seen TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    INDEX idx_digest (query_digest),
    INDEX idx_avg_time (avg_time_ms DESC)
) ENGINE=InnoDB;

-- 인덱스 사용 통계 테이블
DROP TABLE IF EXISTS index_usage_stats;
CREATE TABLE index_usage_stats (
    table_name VARCHAR(64),
    index_name VARCHAR(64),
    read_count BIGINT DEFAULT 0,
    write_count BIGINT DEFAULT 0,
    last_accessed TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY (table_name, index_name)
) ENGINE=InnoDB;

-- 대용량 데이터 생성을 위한 프로시저
DELIMITER $$

CREATE PROCEDURE generate_performance_data(IN num_records INT)
BEGIN
    DECLARE i INT DEFAULT 0;
    DECLARE batch_size INT DEFAULT 1000;
    
    -- 트랜잭션 시작
    START TRANSACTION;
    
    WHILE i < num_records DO
        INSERT INTO performance_test (user_id, action_type, action_timestamp, data, ip_address)
        VALUES (
            FLOOR(1 + RAND() * 10000),
            ELT(FLOOR(1 + RAND() * 5), 'login', 'logout', 'purchase', 'view', 'click'),
            DATE_SUB(NOW(), INTERVAL FLOOR(RAND() * 365) DAY),
            JSON_OBJECT('page', CONCAT('page', FLOOR(RAND() * 100)), 'duration', FLOOR(RAND() * 3600)),
            CONCAT(
                FLOOR(RAND() * 256), '.',
                FLOOR(RAND() * 256), '.',
                FLOOR(RAND() * 256), '.',
                FLOOR(RAND() * 256)
            )
        );
        
        SET i = i + 1;
        
        -- 배치 커밋
        IF i % batch_size = 0 THEN
            COMMIT;
            START TRANSACTION;
        END IF;
    END WHILE;
    
    COMMIT;
END$$

-- 파티션 데이터 생성 프로시저
CREATE PROCEDURE generate_sales_data()
BEGIN
    DECLARE i INT DEFAULT 0;
    DECLARE sale_date DATE;
    
    WHILE i < 10000 DO
        SET sale_date = DATE_SUB(CURDATE(), INTERVAL FLOOR(RAND() * 1460) DAY);
        
        INSERT INTO sales_partitioned (id, sale_date, store_id, product_id, quantity, amount)
        VALUES (
            i + 1,
            sale_date,
            FLOOR(1 + RAND() * 100),
            FLOOR(1 + RAND() * 1000),
            FLOOR(1 + RAND() * 10),
            ROUND(10 + RAND() * 990, 2)
        );
        
        SET i = i + 1;
    END WHILE;
END$$

DELIMITER ;

-- 샘플 데이터 생성
-- 성능 테스트 데이터 (10만 건)
CALL generate_performance_data(100000);

-- 파티션 테이블 데이터
CALL generate_sales_data();

-- 전문 검색용 샘플 데이터
INSERT INTO articles (title, content, author, published_date) VALUES
('MySQL Performance Tuning Guide', 'This comprehensive guide covers all aspects of MySQL performance tuning including query optimization, indexing strategies, and server configuration.', 'John Doe', '2024-01-15'),
('Understanding InnoDB Buffer Pool', 'The InnoDB buffer pool is a critical component for MySQL performance. Learn how to configure and monitor it effectively.', 'Jane Smith', '2024-01-10'),
('MySQL Replication Best Practices', 'Master-slave replication is essential for high availability. This article covers setup, monitoring, and troubleshooting.', 'Bob Johnson', '2024-01-05'),
('Query Cache Optimization', 'Although deprecated in MySQL 8.0, understanding query cache can help with older versions and migration strategies.', 'Alice Brown', '2023-12-20'),
('Partitioning Strategies in MySQL', 'Table partitioning can significantly improve query performance for large datasets. Learn when and how to implement it.', 'Charlie Wilson', '2023-12-15'),
('MySQL Security Hardening', 'Security is crucial for database systems. This guide covers user privileges, SSL connections, and audit logging.', 'Diana Davis', '2023-12-10'),
('Backup and Recovery Strategies', 'Comprehensive backup strategies including mysqldump, binary logs, and point-in-time recovery techniques.', 'Eve Miller', '2023-12-05'),
('MySQL 8.0 New Features', 'Explore the latest features in MySQL 8.0 including window functions, CTEs, and JSON enhancements.', 'Frank Thomas', '2023-11-30'),
('Index Design Patterns', 'Effective indexing is key to query performance. Learn about covering indexes, composite indexes, and index hints.', 'Grace Lee', '2023-11-25'),
('Monitoring MySQL with Performance Schema', 'Performance Schema provides detailed insights into MySQL operations. Learn how to use it effectively.', 'Henry Wang', '2023-11-20');

-- 쿼리 성능 로그 샘플 데이터
INSERT INTO query_performance_log (query_digest, query_text, execution_count, total_time_ms, avg_time_ms, max_time_ms, rows_examined_avg, rows_sent_avg) VALUES
('a1b2c3d4e5f6', 'SELECT * FROM users WHERE status = ?', 15000, 45000, 3, 150, 100, 50),
('b2c3d4e5f6g7', 'SELECT COUNT(*) FROM orders WHERE date > ?', 8000, 120000, 15, 500, 50000, 1),
('c3d4e5f6g7h8', 'UPDATE products SET stock = stock - ? WHERE id = ?', 25000, 75000, 3, 50, 1, 0),
('d4e5f6g7h8i9', 'SELECT u.*, o.* FROM users u JOIN orders o ON u.id = o.user_id WHERE u.country = ?', 3000, 180000, 60, 2000, 150000, 1000),
('e5f6g7h8i9j0', 'INSERT INTO logs (user_id, action, timestamp) VALUES (?, ?, ?)', 50000, 100000, 2, 30, 0, 0);

-- 인덱스 사용 통계 샘플 데이터
INSERT INTO index_usage_stats (table_name, index_name, read_count, write_count) VALUES
('users', 'PRIMARY', 150000, 5000),
('users', 'idx_email', 75000, 5000),
('users', 'idx_status', 25000, 5000),
('orders', 'PRIMARY', 200000, 15000),
('orders', 'idx_user_id', 180000, 15000),
('orders', 'idx_date', 95000, 15000),
('products', 'PRIMARY', 300000, 2000),
('products', 'idx_category', 150000, 2000);

-- 성능 모니터링을 위한 뷰
CREATE OR REPLACE VIEW v_slow_queries AS
SELECT 
    query_digest,
    query_text,
    execution_count,
    avg_time_ms,
    max_time_ms,
    rows_examined_avg,
    execution_count * avg_time_ms AS total_impact
FROM query_performance_log
WHERE avg_time_ms > 10
ORDER BY total_impact DESC;

CREATE OR REPLACE VIEW v_index_efficiency AS
SELECT 
    table_name,
    index_name,
    read_count,
    write_count,
    ROUND(read_count / NULLIF(write_count, 0), 2) AS read_write_ratio,
    last_accessed
FROM index_usage_stats
ORDER BY read_count DESC;