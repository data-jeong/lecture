-- Chapter 02: 트랜잭션 실습 해답

-- 문제 1: 계좌 이체 트랜잭션
BEGIN;

-- 잔액 확인
DO $$
DECLARE
    sender_balance DECIMAL(15,2);
BEGIN
    SELECT balance INTO sender_balance FROM accounts WHERE account_id = 1;
    
    IF sender_balance >= 1000 THEN
        -- 송금자 계좌에서 차감
        UPDATE accounts 
        SET balance = balance - 1000 
        WHERE account_id = 1;
        
        -- 수신자 계좌에 추가
        UPDATE accounts 
        SET balance = balance + 1000 
        WHERE account_id = 2;
        
        RAISE NOTICE '이체 완료: John Doe -> Jane Smith, 금액: $1000';
    ELSE
        RAISE EXCEPTION '잔액 부족: 현재 잔액 $%, 이체 요청 $1000', sender_balance;
    END IF;
END $$;

COMMIT;

-- 문제 2: 주문 처리 트랜잭션
BEGIN;

-- 재고 확인
DO $$
DECLARE
    laptop_stock INT;
    keyboard_stock INT;
    order_total DECIMAL(10,2);
BEGIN
    -- 재고 확인
    SELECT quantity INTO laptop_stock FROM inventory WHERE product_id = 1;
    SELECT quantity INTO keyboard_stock FROM inventory WHERE product_id = 7;
    
    IF laptop_stock >= 2 AND keyboard_stock >= 1 THEN
        -- 주문 총액 계산
        SELECT (p1.price * 2 + p2.price * 1) INTO order_total
        FROM products p1, products p2
        WHERE p1.product_id = 1 AND p2.product_id = 7;
        
        -- 주문 생성
        INSERT INTO orders (order_id, customer_id, order_date, status, total_amount)
        VALUES (12, 1, CURRENT_DATE, 'Processing', order_total);
        
        -- 주문 상세 추가
        INSERT INTO order_items (item_id, order_id, product_id, quantity, unit_price)
        SELECT 
            COALESCE(MAX(item_id), 0) + 1,
            12,
            1,
            2,
            price
        FROM order_items, products WHERE product_id = 1;
        
        INSERT INTO order_items (item_id, order_id, product_id, quantity, unit_price)
        SELECT 
            COALESCE(MAX(item_id), 0) + 1,
            12,
            7,
            1,
            price
        FROM order_items, products WHERE product_id = 7;
        
        -- 재고 차감
        UPDATE inventory SET quantity = quantity - 2 WHERE product_id = 1;
        UPDATE inventory SET quantity = quantity - 1 WHERE product_id = 7;
        
        RAISE NOTICE '주문 처리 완료: Order ID 12';
    ELSE
        RAISE EXCEPTION '재고 부족: Laptop 재고 %, Keyboard 재고 %', laptop_stock, keyboard_stock;
    END IF;
END $$;

COMMIT;

-- 문제 3: SAVEPOINT를 활용한 부분 롤백
BEGIN;

-- 1. 모든 직원 급여 5% 인상
UPDATE employees SET salary = salary * 1.05;

-- 2. SAVEPOINT 생성
SAVEPOINT salary_increase;

-- 3. Sales 부서 고액 급여자 삭제
DELETE FROM employees 
WHERE department = 'Sales' AND salary >= 80000;

-- 4. 삭제된 직원 수 확인 및 조건부 롤백
DO $$
DECLARE
    deleted_count INT;
BEGIN
    GET DIAGNOSTICS deleted_count = ROW_COUNT;
    
    IF deleted_count >= 3 THEN
        ROLLBACK TO salary_increase;
        RAISE NOTICE '삭제된 직원이 %명이므로 급여 인상 이후 상태로 롤백', deleted_count;
    ELSE
        RAISE NOTICE '삭제된 직원 %명, 변경사항 유지', deleted_count;
    END IF;
END $$;

COMMIT;

-- 문제 4: 동시성 제어 시뮬레이션
-- Session 1
BEGIN;
UPDATE accounts SET balance = balance - 500 WHERE account_id = 3;
-- 여기서 잠시 대기 (다른 세션이 작업할 시간 제공)
SELECT pg_sleep(5); -- PostgreSQL의 경우
COMMIT;

-- Session 2 (별도 세션에서 실행)
BEGIN;
UPDATE accounts SET balance = balance + 300 WHERE account_id = 3;
COMMIT;

-- 결과 확인
SELECT account_id, account_holder, balance FROM accounts WHERE account_id = 3;

-- 문제 5: 배치 처리 트랜잭션
BEGIN;

-- order_items_archive 테이블 생성
CREATE TABLE IF NOT EXISTS order_items_archive (
    item_id INT,
    order_id INT,
    product_id INT,
    quantity INT,
    unit_price DECIMAL(10, 2),
    archived_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

DO $$
DECLARE
    affected_orders INT;
    affected_items INT;
BEGIN
    -- 1. 2019년 이전 주문들을 'Archived' 상태로 변경
    UPDATE orders 
    SET status = 'Archived' 
    WHERE order_date < '2019-01-01';
    
    GET DIAGNOSTICS affected_orders = ROW_COUNT;
    RAISE NOTICE '% 건의 주문이 아카이브 상태로 변경됨', affected_orders;
    
    -- 2. 해당 주문들의 상세 정보를 아카이브 테이블로 이동
    INSERT INTO order_items_archive (item_id, order_id, product_id, quantity, unit_price)
    SELECT oi.item_id, oi.order_id, oi.product_id, oi.quantity, oi.unit_price
    FROM order_items oi
    INNER JOIN orders o ON oi.order_id = o.order_id
    WHERE o.order_date < '2019-01-01';
    
    GET DIAGNOSTICS affected_items = ROW_COUNT;
    RAISE NOTICE '% 건의 주문 상세가 아카이브됨', affected_items;
    
    -- 3. 원본에서 삭제
    DELETE FROM order_items 
    WHERE order_id IN (
        SELECT order_id FROM orders WHERE order_date < '2019-01-01'
    );
    
    RAISE NOTICE '배치 처리 완료';
    
EXCEPTION
    WHEN OTHERS THEN
        RAISE NOTICE '오류 발생: %, 모든 변경사항 롤백', SQLERRM;
        ROLLBACK;
END $$;

COMMIT;