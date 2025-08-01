-- Chapter 08: 트랜잭션과 동시성 제어 실습용 데이터베이스

-- 은행 계좌 테이블
DROP TABLE IF EXISTS bank_accounts;
CREATE TABLE bank_accounts (
    account_id INT PRIMARY KEY,
    account_number VARCHAR(20) UNIQUE NOT NULL,
    account_holder VARCHAR(100) NOT NULL,
    balance DECIMAL(15, 2) DEFAULT 0,
    account_type VARCHAR(20) DEFAULT 'CHECKING',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    last_modified TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 거래 내역 테이블
DROP TABLE IF EXISTS transactions;
CREATE TABLE transactions (
    transaction_id INT PRIMARY KEY AUTO_INCREMENT,
    from_account INT,
    to_account INT,
    amount DECIMAL(15, 2),
    transaction_type VARCHAR(20), -- DEPOSIT, WITHDRAWAL, TRANSFER
    status VARCHAR(20) DEFAULT 'PENDING', -- PENDING, COMPLETED, FAILED, CANCELLED
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    completed_at TIMESTAMP NULL,
    FOREIGN KEY (from_account) REFERENCES bank_accounts(account_id),
    FOREIGN KEY (to_account) REFERENCES bank_accounts(account_id)
);

-- 재고 관리 테이블 (동시성 테스트용)
DROP TABLE IF EXISTS inventory_items;
CREATE TABLE inventory_items (
    item_id INT PRIMARY KEY,
    item_name VARCHAR(200) NOT NULL,
    quantity INT DEFAULT 0,
    reserved_quantity INT DEFAULT 0,
    unit_price DECIMAL(10, 2),
    last_restocked TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    version INT DEFAULT 0 -- 낙관적 잠금용
);

-- 주문 테이블
DROP TABLE IF EXISTS concurrent_orders;
CREATE TABLE concurrent_orders (
    order_id INT PRIMARY KEY AUTO_INCREMENT,
    customer_id INT,
    order_status VARCHAR(20) DEFAULT 'PENDING',
    total_amount DECIMAL(15, 2),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 주문 상세 테이블
DROP TABLE IF EXISTS concurrent_order_items;
CREATE TABLE concurrent_order_items (
    order_item_id INT PRIMARY KEY AUTO_INCREMENT,
    order_id INT,
    item_id INT,
    quantity INT,
    unit_price DECIMAL(10, 2),
    FOREIGN KEY (order_id) REFERENCES concurrent_orders(order_id),
    FOREIGN KEY (item_id) REFERENCES inventory_items(item_id)
);

-- 잠금 테스트용 테이블
DROP TABLE IF EXISTS lock_test;
CREATE TABLE lock_test (
    id INT PRIMARY KEY,
    value VARCHAR(100),
    counter INT DEFAULT 0,
    locked_by VARCHAR(100),
    locked_at TIMESTAMP NULL
);

-- 데드락 시뮬레이션용 테이블
DROP TABLE IF EXISTS deadlock_table_a;
CREATE TABLE deadlock_table_a (
    id INT PRIMARY KEY,
    value INT DEFAULT 0,
    last_updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

DROP TABLE IF EXISTS deadlock_table_b;
CREATE TABLE deadlock_table_b (
    id INT PRIMARY KEY,
    value INT DEFAULT 0,
    last_updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 격리 수준 테스트용 테이블
DROP TABLE IF EXISTS isolation_test;
CREATE TABLE isolation_test (
    id INT PRIMARY KEY,
    name VARCHAR(100),
    value INT DEFAULT 0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 트랜잭션 로그 테이블
DROP TABLE IF EXISTS transaction_log;
CREATE TABLE transaction_log (
    log_id INT PRIMARY KEY AUTO_INCREMENT,
    transaction_type VARCHAR(50),
    table_name VARCHAR(50),
    action VARCHAR(20),
    user_id VARCHAR(50),
    before_value TEXT,
    after_value TEXT,
    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 샘플 데이터 삽입
-- 은행 계좌
INSERT INTO bank_accounts (account_id, account_number, account_holder, balance, account_type) VALUES
(1, 'ACC001', 'John Doe', 10000.00, 'CHECKING'),
(2, 'ACC002', 'Jane Smith', 15000.00, 'SAVINGS'),
(3, 'ACC003', 'Bob Johnson', 5000.00, 'CHECKING'),
(4, 'ACC004', 'Alice Brown', 20000.00, 'SAVINGS'),
(5, 'ACC005', 'Charlie Wilson', 7500.00, 'CHECKING'),
(6, 'ACC006', 'Diana Davis', 30000.00, 'BUSINESS'),
(7, 'ACC007', 'Eve Miller', 12000.00, 'SAVINGS'),
(8, 'ACC008', 'Frank Thomas', 8000.00, 'CHECKING'),
(9, 'ACC009', 'Grace Lee', 25000.00, 'BUSINESS'),
(10, 'ACC010', 'Henry Wang', 9000.00, 'CHECKING');

-- 재고 아이템
INSERT INTO inventory_items (item_id, item_name, quantity, unit_price) VALUES
(1, 'Laptop Pro', 50, 1299.99),
(2, 'Wireless Mouse', 200, 29.99),
(3, 'USB-C Cable', 500, 19.99),
(4, 'Mechanical Keyboard', 75, 149.99),
(5, 'Monitor 27"', 30, 399.99),
(6, 'Webcam HD', 100, 89.99),
(7, 'Desk Lamp', 150, 49.99),
(8, 'Phone Stand', 300, 24.99),
(9, 'Laptop Bag', 80, 79.99),
(10, 'Power Bank', 120, 59.99);

-- 잠금 테스트 데이터
INSERT INTO lock_test (id, value, counter) VALUES
(1, 'Test Row 1', 0),
(2, 'Test Row 2', 0),
(3, 'Test Row 3', 0),
(4, 'Test Row 4', 0),
(5, 'Test Row 5', 0);

-- 데드락 테스트 데이터
INSERT INTO deadlock_table_a (id, value) VALUES
(1, 100),
(2, 200),
(3, 300);

INSERT INTO deadlock_table_b (id, value) VALUES
(1, 1000),
(2, 2000),
(3, 3000);

-- 격리 수준 테스트 데이터
INSERT INTO isolation_test (id, name, value) VALUES
(1, 'Read Uncommitted Test', 100),
(2, 'Read Committed Test', 200),
(3, 'Repeatable Read Test', 300),
(4, 'Serializable Test', 400),
(5, 'Phantom Read Test', 500);

-- 저장 프로시저: 계좌 이체
DELIMITER $$

CREATE PROCEDURE transfer_money(
    IN p_from_account INT,
    IN p_to_account INT,
    IN p_amount DECIMAL(15, 2),
    OUT p_status VARCHAR(20)
)
BEGIN
    DECLARE v_from_balance DECIMAL(15, 2);
    DECLARE EXIT HANDLER FOR SQLEXCEPTION
    BEGIN
        ROLLBACK;
        SET p_status = 'FAILED';
    END;
    
    START TRANSACTION;
    
    -- 송금 계좌 잔액 확인 (잠금)
    SELECT balance INTO v_from_balance 
    FROM bank_accounts 
    WHERE account_id = p_from_account 
    FOR UPDATE;
    
    IF v_from_balance >= p_amount THEN
        -- 송금 계좌에서 차감
        UPDATE bank_accounts 
        SET balance = balance - p_amount 
        WHERE account_id = p_from_account;
        
        -- 수신 계좌에 추가
        UPDATE bank_accounts 
        SET balance = balance + p_amount 
        WHERE account_id = p_to_account;
        
        -- 거래 기록
        INSERT INTO transactions (from_account, to_account, amount, transaction_type, status)
        VALUES (p_from_account, p_to_account, p_amount, 'TRANSFER', 'COMPLETED');
        
        COMMIT;
        SET p_status = 'SUCCESS';
    ELSE
        ROLLBACK;
        SET p_status = 'INSUFFICIENT_FUNDS';
    END IF;
END$$

-- 저장 프로시저: 재고 예약
CREATE PROCEDURE reserve_inventory(
    IN p_item_id INT,
    IN p_quantity INT,
    OUT p_status VARCHAR(20)
)
BEGIN
    DECLARE v_available_quantity INT;
    DECLARE EXIT HANDLER FOR SQLEXCEPTION
    BEGIN
        ROLLBACK;
        SET p_status = 'FAILED';
    END;
    
    START TRANSACTION;
    
    -- 재고 확인 (잠금)
    SELECT quantity - reserved_quantity INTO v_available_quantity
    FROM inventory_items
    WHERE item_id = p_item_id
    FOR UPDATE;
    
    IF v_available_quantity >= p_quantity THEN
        -- 재고 예약
        UPDATE inventory_items
        SET reserved_quantity = reserved_quantity + p_quantity
        WHERE item_id = p_item_id;
        
        COMMIT;
        SET p_status = 'SUCCESS';
    ELSE
        ROLLBACK;
        SET p_status = 'INSUFFICIENT_STOCK';
    END IF;
END$$

DELIMITER ;