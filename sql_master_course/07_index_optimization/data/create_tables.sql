-- Chapter 07: 인덱스와 쿼리 최적화 실습용 테이블 생성 스크립트
-- 대용량 데이터와 성능 테스트를 위한 테이블들

-- 대용량 주문 테이블 (성능 테스트용)
DROP TABLE IF EXISTS large_orders;
CREATE TABLE large_orders (
    order_id SERIAL PRIMARY KEY,
    customer_id INT NOT NULL,
    product_id INT NOT NULL,
    order_date DATE NOT NULL,
    quantity INT NOT NULL,
    unit_price DECIMAL(10, 2) NOT NULL,
    total_amount DECIMAL(12, 2) NOT NULL,
    status VARCHAR(20) DEFAULT 'pending',
    region VARCHAR(50),
    sales_rep_id INT
);

-- 성능 테스트용 테이블
DROP TABLE IF EXISTS performance_test;
CREATE TABLE performance_test (
    id SERIAL PRIMARY KEY,
    category_id INT NOT NULL,
    subcategory_id INT,
    name VARCHAR(200) NOT NULL,
    description TEXT,
    price DECIMAL(10, 2),
    created_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    status CHAR(1) DEFAULT 'A',
    tags TEXT[],
    metadata JSONB
);

-- 인덱스 효과 테스트용 테이블
DROP TABLE IF EXISTS index_test;
CREATE TABLE index_test (
    id SERIAL PRIMARY KEY,
    code VARCHAR(20) NOT NULL,
    category VARCHAR(50),
    value DECIMAL(15, 2),
    date_field DATE,
    timestamp_field TIMESTAMP,
    text_field TEXT,
    flag BOOLEAN DEFAULT false
);

-- 대용량 데이터 생성 (실제 환경에서는 더 큰 데이터셋 사용)
-- 100,000건의 주문 데이터 생성
INSERT INTO large_orders (customer_id, product_id, order_date, quantity, unit_price, total_amount, status, region, sales_rep_id)
SELECT 
    (random() * 1000 + 1)::int as customer_id,
    (random() * 20 + 1)::int as product_id,
    CURRENT_DATE - (random() * 365)::int as order_date,
    (random() * 10 + 1)::int as quantity,
    (random() * 1000 + 10)::decimal(10,2) as unit_price,
    ((random() * 10 + 1) * (random() * 1000 + 10))::decimal(12,2) as total_amount,
    CASE 
        WHEN random() < 0.7 THEN 'completed'
        WHEN random() < 0.9 THEN 'shipped'
        ELSE 'pending'
    END as status,
    CASE 
        WHEN random() < 0.3 THEN 'North'
        WHEN random() < 0.6 THEN 'South'
        WHEN random() < 0.8 THEN 'East'
        ELSE 'West'
    END as region,
    (random() * 50 + 1)::int as sales_rep_id
FROM generate_series(1, 100000);

-- 성능 테스트 데이터 생성
INSERT INTO performance_test (category_id, subcategory_id, name, description, price, status, tags, metadata)
SELECT 
    (random() * 50 + 1)::int as category_id,
    (random() * 200 + 1)::int as subcategory_id,
    'Product ' || i as name,
    'Description for product ' || i as description,
    (random() * 5000)::decimal(10,2) as price,
    CASE WHEN random() < 0.8 THEN 'A' ELSE 'I' END as status,
    ARRAY['tag' || (random() * 10 + 1)::int, 'category' || (random() * 5 + 1)::int] as tags,
    ('{"rating": ' || (random() * 5 + 1)::int || ', "views": ' || (random() * 10000)::int || '}')::jsonb as metadata
FROM generate_series(1, 50000) i;

-- 인덱스 테스트 데이터 생성
INSERT INTO index_test (code, category, value, date_field, timestamp_field, text_field, flag)
SELECT 
    'CODE' || LPAD(i::text, 6, '0') as code,
    'Category' || (i % 100 + 1) as category,
    random() * 100000 as value,
    CURRENT_DATE - (random() * 1000)::int as date_field,
    CURRENT_TIMESTAMP - (random() * 1000)::int * INTERVAL '1 day' as timestamp_field,
    'Text content for record ' || i as text_field,
    random() < 0.3 as flag
FROM generate_series(1, 200000) i;

-- 통계 정보 업데이트
ANALYZE large_orders;
ANALYZE performance_test;
ANALYZE index_test;