-- Chapter 12: 데이터 분석가 인터뷰 대비 실습용 테이블 생성 스크립트
-- 실제 인터뷰에서 자주 사용되는 데이터 구조

-- 웹 분석용 테이블들
DROP TABLE IF EXISTS page_views CASCADE;
CREATE TABLE page_views (
    view_id SERIAL PRIMARY KEY,
    user_id INT NOT NULL,
    session_id VARCHAR(50),
    page_url VARCHAR(200),
    page_type VARCHAR(50), -- 'home', 'product', 'checkout', etc.
    timestamp TIMESTAMP NOT NULL,
    device_type VARCHAR(20),
    referrer VARCHAR(200),
    duration_seconds INT
);

DROP TABLE IF EXISTS user_events CASCADE;
CREATE TABLE user_events (
    event_id SERIAL PRIMARY KEY,
    user_id INT NOT NULL,
    event_type VARCHAR(50), -- 'click', 'purchase', 'signup', etc.
    event_data JSONB,
    timestamp TIMESTAMP NOT NULL,
    page_url VARCHAR(200)
);

-- 구독 서비스 분석용 테이블들
DROP TABLE IF EXISTS subscriptions CASCADE;
CREATE TABLE subscriptions (
    subscription_id SERIAL PRIMARY KEY,
    user_id INT NOT NULL,
    plan_type VARCHAR(50), -- 'basic', 'premium', 'enterprise'
    start_date DATE NOT NULL,
    end_date DATE,
    monthly_fee DECIMAL(8, 2),
    status VARCHAR(20) -- 'active', 'cancelled', 'expired'
);

DROP TABLE IF EXISTS usage_logs CASCADE;
CREATE TABLE usage_logs (
    log_id SERIAL PRIMARY KEY,
    user_id INT NOT NULL,
    feature_used VARCHAR(100),
    usage_date DATE NOT NULL,
    usage_duration_minutes INT,
    session_count INT DEFAULT 1
);

-- A/B 테스트 분석용 테이블들
DROP TABLE IF EXISTS ab_tests CASCADE;
CREATE TABLE ab_tests (
    test_id SERIAL PRIMARY KEY,
    test_name VARCHAR(100),
    start_date DATE,
    end_date DATE,
    description TEXT
);

DROP TABLE IF EXISTS ab_test_participants CASCADE;
CREATE TABLE ab_test_participants (
    participant_id SERIAL PRIMARY KEY,
    test_id INT REFERENCES ab_tests(test_id),
    user_id INT NOT NULL,
    variant VARCHAR(20), -- 'control', 'treatment_a', 'treatment_b'
    assigned_date DATE NOT NULL
);

DROP TABLE IF EXISTS conversion_events CASCADE;
CREATE TABLE conversion_events (
    conversion_id SERIAL PRIMARY KEY,
    user_id INT NOT NULL,
    test_id INT REFERENCES ab_tests(test_id),
    conversion_type VARCHAR(50), -- 'signup', 'purchase', 'upgrade'
    conversion_value DECIMAL(10, 2),
    conversion_date TIMESTAMP NOT NULL
);

-- 전자상거래 심화 분석용 테이블들
DROP TABLE IF EXISTS product_categories CASCADE;
CREATE TABLE product_categories (
    category_id SERIAL PRIMARY KEY,
    category_name VARCHAR(100),
    parent_category_id INT,
    level INT DEFAULT 1
);

DROP TABLE IF EXISTS cart_events CASCADE;  
CREATE TABLE cart_events (
    cart_event_id SERIAL PRIMARY KEY,
    user_id INT NOT NULL,
    product_id INT NOT NULL,
    event_type VARCHAR(20), -- 'add', 'remove', 'update'
    quantity INT,
    timestamp TIMESTAMP NOT NULL,
    session_id VARCHAR(50)
);

-- 마케팅 캠페인 분석용 테이블들
DROP TABLE IF EXISTS campaigns CASCADE;
CREATE TABLE campaigns (
    campaign_id SERIAL PRIMARY KEY,
    campaign_name VARCHAR(100),
    channel VARCHAR(50), -- 'email', 'social', 'search', 'display'
    start_date DATE,
    end_date DATE,
    budget DECIMAL(12, 2),
    target_audience TEXT
);

DROP TABLE IF EXISTS campaign_interactions CASCADE;
CREATE TABLE campaign_interactions (
    interaction_id SERIAL PRIMARY KEY,
    campaign_id INT REFERENCES campaigns(campaign_id),
    user_id INT NOT NULL,
    interaction_type VARCHAR(50), -- 'impression', 'click', 'conversion'
    timestamp TIMESTAMP NOT NULL,
    cost DECIMAL(8, 4) -- cost per interaction
);

-- 샘플 데이터 삽입

-- page_views 데이터
INSERT INTO page_views (user_id, session_id, page_url, page_type, timestamp, device_type, referrer, duration_seconds)
SELECT 
    (random() * 10000 + 1)::int as user_id,
    'sess_' || (random() * 50000 + 1)::int as session_id,
    CASE (random() * 5)::int
        WHEN 0 THEN '/home'
        WHEN 1 THEN '/product/' || (random() * 100 + 1)::int
        WHEN 2 THEN '/category/' || (random() * 20 + 1)::int
        WHEN 3 THEN '/checkout'
        ELSE '/search'
    END as page_url,
    CASE (random() * 5)::int
        WHEN 0 THEN 'home'
        WHEN 1 THEN 'product'
        WHEN 2 THEN 'category'
        WHEN 3 THEN 'checkout'
        ELSE 'search'
    END as page_type,
    CURRENT_TIMESTAMP - (random() * 90)::int * INTERVAL '1 day' - (random() * 24)::int * INTERVAL '1 hour' as timestamp,
    CASE (random() * 3)::int
        WHEN 0 THEN 'desktop'
        WHEN 1 THEN 'mobile'
        ELSE 'tablet'
    END as device_type,
    CASE WHEN random() < 0.3 THEN 'google.com' WHEN random() < 0.6 THEN 'facebook.com' ELSE 'direct' END as referrer,
    (random() * 600 + 10)::int as duration_seconds
FROM generate_series(1, 500000);

-- subscriptions 데이터
INSERT INTO subscriptions (user_id, plan_type, start_date, end_date, monthly_fee, status)
SELECT 
    (random() * 5000 + 1)::int as user_id,
    CASE (random() * 3)::int
        WHEN 0 THEN 'basic'
        WHEN 1 THEN 'premium'
        ELSE 'enterprise'
    END as plan_type,
    CURRENT_DATE - (random() * 365)::int as start_date,
    CASE WHEN random() < 0.2 THEN CURRENT_DATE - (random() * 180)::int ELSE NULL END as end_date,
    CASE (random() * 3)::int
        WHEN 0 THEN 9.99
        WHEN 1 THEN 19.99
        ELSE 49.99
    END as monthly_fee,
    CASE WHEN random() < 0.8 THEN 'active' WHEN random() < 0.9 THEN 'cancelled' ELSE 'expired' END as status
FROM generate_series(1, 20000);

-- A/B 테스트 데이터
INSERT INTO ab_tests (test_name, start_date, end_date, description) VALUES
('Checkout Flow Optimization', '2023-01-01', '2023-02-28', 'Testing new checkout flow design'),
('Email Subject Line Test', '2023-03-01', '2023-03-31', 'Testing different email subject lines'),
('Pricing Page Layout', '2023-04-01', '2023-05-31', 'Testing new pricing page layout'),
('Signup Form Optimization', '2023-06-01', '2023-07-31', 'Testing simplified signup form'),
('Product Recommendation Engine', '2023-08-01', '2023-09-30', 'Testing ML-based recommendations');

-- AB 테스트 참가자 데이터
INSERT INTO ab_test_participants (test_id, user_id, variant, assigned_date)
SELECT 
    (random() * 5 + 1)::int as test_id,
    (random() * 10000 + 1)::int as user_id,
    CASE (random() * 3)::int
        WHEN 0 THEN 'control'
        WHEN 1 THEN 'treatment_a'
        ELSE 'treatment_b'
    END as variant,
    CURRENT_DATE - (random() * 300)::int as assigned_date
FROM generate_series(1, 50000);

-- 캠페인 데이터
INSERT INTO campaigns (campaign_name, channel, start_date, end_date, budget, target_audience) VALUES
('Summer Sale 2023', 'email', '2023-06-01', '2023-08-31', 50000.00, 'Existing customers'),
('New Product Launch', 'social', '2023-07-01', '2023-07-31', 75000.00, 'Tech enthusiasts'),
('Back to School', 'search', '2023-08-01', '2023-09-15', 100000.00, 'Students and parents'),
('Holiday Shopping', 'display', '2023-11-01', '2023-12-31', 200000.00, 'General audience'),
('Black Friday Special', 'email', '2023-11-20', '2023-11-27', 150000.00, 'High-value customers');

-- 통계 정보 업데이트
ANALYZE page_views;
ANALYZE user_events;
ANALYZE subscriptions;
ANALYZE usage_logs;
ANALYZE ab_tests;
ANALYZE ab_test_participants;
ANALYZE conversion_events;
ANALYZE campaigns;
ANALYZE campaign_interactions;