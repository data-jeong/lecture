-- Chapter 10: PostgreSQL 고급 기능 실습용 데이터베이스
-- 주의: 이 스크립트는 PostgreSQL 전용입니다.

-- ===========================
-- 1. JSON/JSONB 데이터 타입
-- ===========================

-- 이벤트 로그 테이블 (JSONB 사용)
DROP TABLE IF EXISTS event_logs CASCADE;
CREATE TABLE event_logs (
    event_id SERIAL PRIMARY KEY,
    event_type VARCHAR(50),
    event_data JSONB NOT NULL,
    user_id INT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- API 응답 캐시 테이블
DROP TABLE IF EXISTS api_responses CASCADE;
CREATE TABLE api_responses (
    api_endpoint VARCHAR(200) PRIMARY KEY,
    response_data JSONB,
    headers JSONB,
    cached_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    expires_at TIMESTAMP
);

-- 사용자 설정 테이블
DROP TABLE IF EXISTS user_preferences CASCADE;
CREATE TABLE user_preferences (
    user_id INT PRIMARY KEY,
    preferences JSONB DEFAULT '{}',
    last_updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- ===========================
-- 2. 배열 데이터 타입
-- ===========================

-- 제품 태그 테이블
DROP TABLE IF EXISTS product_tags CASCADE;
CREATE TABLE product_tags (
    product_id SERIAL PRIMARY KEY,
    product_name VARCHAR(200),
    tags TEXT[] DEFAULT '{}',
    prices DECIMAL[] DEFAULT '{}',
    available_sizes VARCHAR[] DEFAULT '{}'
);

-- 사용자 권한 테이블
DROP TABLE IF EXISTS user_permissions CASCADE;
CREATE TABLE user_permissions (
    user_id INT PRIMARY KEY,
    username VARCHAR(50) UNIQUE,
    roles TEXT[] DEFAULT '{}',
    allowed_actions TEXT[] DEFAULT '{}',
    restricted_resources INT[] DEFAULT '{}'
);

-- ===========================
-- 3. Range 데이터 타입
-- ===========================

-- 호텔 예약 테이블
DROP TABLE IF EXISTS hotel_reservations CASCADE;
CREATE TABLE hotel_reservations (
    reservation_id SERIAL PRIMARY KEY,
    room_number INT,
    guest_name VARCHAR(100),
    stay_period DATERANGE,
    price_per_night DECIMAL(10, 2),
    EXCLUDE USING GIST (room_number WITH =, stay_period WITH &&)
);

-- 근무 시간 테이블
DROP TABLE IF EXISTS work_schedules CASCADE;
CREATE TABLE work_schedules (
    schedule_id SERIAL PRIMARY KEY,
    employee_id INT,
    work_date DATE,
    work_hours TSTZRANGE,
    break_periods TSTZRANGE[]
);

-- ===========================
-- 4. 고급 데이터 타입
-- ===========================

-- 지리 정보 테이블 (PostGIS 없이 기본 기능만)
DROP TABLE IF EXISTS locations CASCADE;
CREATE TABLE locations (
    location_id SERIAL PRIMARY KEY,
    location_name VARCHAR(200),
    coordinates POINT,
    service_area CIRCLE,
    metadata JSONB
);

-- UUID 테이블
DROP TABLE IF EXISTS uuid_example CASCADE;
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE TABLE uuid_example (
    id UUID DEFAULT uuid_generate_v4() PRIMARY KEY,
    name VARCHAR(100),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- ENUM 타입 생성
DROP TYPE IF EXISTS order_status CASCADE;
CREATE TYPE order_status AS ENUM ('pending', 'processing', 'shipped', 'delivered', 'cancelled');

DROP TYPE IF EXISTS user_role CASCADE;
CREATE TYPE user_role AS ENUM ('admin', 'moderator', 'user', 'guest');

-- ENUM을 사용하는 테이블
DROP TABLE IF EXISTS enum_orders CASCADE;
CREATE TABLE enum_orders (
    order_id SERIAL PRIMARY KEY,
    customer_name VARCHAR(100),
    status order_status DEFAULT 'pending',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- ===========================
-- 5. 전문 검색 (Full Text Search)
-- ===========================

-- 문서 테이블
DROP TABLE IF EXISTS documents CASCADE;
CREATE TABLE documents (
    doc_id SERIAL PRIMARY KEY,
    title VARCHAR(500),
    content TEXT,
    author VARCHAR(100),
    tags TEXT[],
    search_vector TSVECTOR,
    published_date DATE
);

-- 검색 벡터 자동 업데이트 트리거
CREATE OR REPLACE FUNCTION update_search_vector() RETURNS TRIGGER AS $$
BEGIN
    NEW.search_vector := 
        setweight(to_tsvector('english', COALESCE(NEW.title, '')), 'A') ||
        setweight(to_tsvector('english', COALESCE(NEW.content, '')), 'B') ||
        setweight(to_tsvector('english', COALESCE(NEW.author, '')), 'C');
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

DROP TRIGGER IF EXISTS update_search_vector_trigger ON documents;
CREATE TRIGGER update_search_vector_trigger
    BEFORE INSERT OR UPDATE ON documents
    FOR EACH ROW
    EXECUTE FUNCTION update_search_vector();

-- ===========================
-- 6. 파티셔닝 (선언적 파티셔닝)
-- ===========================

-- 로그 테이블 (월별 파티션)
DROP TABLE IF EXISTS application_logs CASCADE;
CREATE TABLE application_logs (
    log_id BIGSERIAL,
    log_level VARCHAR(20),
    log_message TEXT,
    log_data JSONB,
    created_at TIMESTAMP NOT NULL
) PARTITION BY RANGE (created_at);

-- 파티션 생성 (최근 3개월)
CREATE TABLE application_logs_2024_01 PARTITION OF application_logs
    FOR VALUES FROM ('2024-01-01') TO ('2024-02-01');

CREATE TABLE application_logs_2024_02 PARTITION OF application_logs
    FOR VALUES FROM ('2024-02-01') TO ('2024-03-01');

CREATE TABLE application_logs_2024_03 PARTITION OF application_logs
    FOR VALUES FROM ('2024-03-01') TO ('2024-04-01');

-- ===========================
-- 7. 샘플 데이터
-- ===========================

-- JSONB 데이터
INSERT INTO event_logs (event_type, event_data, user_id) VALUES
('page_view', '{"page": "/home", "duration": 45, "browser": "Chrome", "device": {"type": "mobile", "os": "iOS"}}', 1),
('purchase', '{"product_id": 123, "quantity": 2, "price": 29.99, "payment": {"method": "credit_card", "last4": "1234"}}', 2),
('error', '{"code": 500, "message": "Internal Server Error", "stack_trace": ["line1", "line2"], "context": {"endpoint": "/api/users"}}', NULL),
('user_action', '{"action": "click", "element": "button#submit", "coordinates": {"x": 150, "y": 300}, "metadata": {"ab_test": "variant_b"}}', 3),
('api_call', '{"endpoint": "/api/data", "method": "GET", "response_time": 234, "status": 200, "params": {"limit": 10, "offset": 0}}', 4);

-- 배열 데이터
INSERT INTO product_tags (product_name, tags, prices, available_sizes) VALUES
('T-Shirt', '{"clothing", "casual", "summer"}', '{19.99, 24.99, 29.99}', '{"S", "M", "L", "XL"}'),
('Laptop', '{"electronics", "computer", "portable"}', '{999.99, 1299.99}', NULL),
('Book', '{"education", "programming", "python"}', '{39.99, 49.99}', NULL),
('Shoes', '{"footwear", "sports", "running"}', '{79.99, 89.99, 99.99}', '{"7", "8", "9", "10", "11"}');

-- 사용자 권한 데이터
INSERT INTO user_permissions (user_id, username, roles, allowed_actions, restricted_resources) VALUES
(1, 'admin', '{"admin", "moderator"}', '{"create", "read", "update", "delete"}', '{}'),
(2, 'john_doe', '{"user"}', '{"read", "update"}', '{100, 101, 102}'),
(3, 'jane_smith', '{"moderator"}', '{"read", "update", "moderate"}', '{200}');

-- Range 데이터
INSERT INTO hotel_reservations (room_number, guest_name, stay_period, price_per_night) VALUES
(101, 'Alice Johnson', '[2024-02-01, 2024-02-05)', 150.00),
(102, 'Bob Smith', '[2024-02-03, 2024-02-07)', 175.00),
(103, 'Carol White', '[2024-02-10, 2024-02-15)', 200.00),
(101, 'David Brown', '[2024-02-06, 2024-02-10)', 150.00);

-- 전문 검색용 문서 데이터
INSERT INTO documents (title, content, author, tags, published_date) VALUES
('Introduction to PostgreSQL', 'PostgreSQL is a powerful, open source object-relational database system...', 'John Doe', '{"database", "postgresql", "tutorial"}', '2024-01-15'),
('Advanced JSON Features', 'PostgreSQL provides robust support for JSON data types...', 'Jane Smith', '{"json", "postgresql", "advanced"}', '2024-01-20'),
('Full Text Search Guide', 'Learn how to implement efficient full text search in PostgreSQL...', 'Bob Johnson', '{"search", "postgresql", "performance"}', '2024-01-25'),
('Array Operations', 'Arrays in PostgreSQL can store multiple values in a single column...', 'Alice Brown', '{"arrays", "postgresql", "data-types"}', '2024-02-01');

-- 사용자 설정 데이터
INSERT INTO user_preferences (user_id, preferences) VALUES
(1, '{"theme": "dark", "language": "en", "notifications": {"email": true, "push": false}, "privacy": {"profile_visible": true}}'),
(2, '{"theme": "light", "language": "es", "notifications": {"email": false, "push": true}, "dashboard": {"widgets": ["weather", "news", "calendar"]}}'),
(3, '{"theme": "auto", "language": "fr", "notifications": {"email": true, "push": true}, "features": {"beta": true, "advanced_mode": false}}');

-- ===========================
-- 8. 고급 인덱스
-- ===========================

-- GIN 인덱스 (JSONB)
CREATE INDEX idx_event_data_gin ON event_logs USING GIN (event_data);

-- GIN 인덱스 (배열)
CREATE INDEX idx_tags_gin ON product_tags USING GIN (tags);

-- GiST 인덱스 (Range)
CREATE INDEX idx_stay_period_gist ON hotel_reservations USING GIST (stay_period);

-- 전문 검색 인덱스
CREATE INDEX idx_search_vector_gin ON documents USING GIN (search_vector);

-- 부분 인덱스
CREATE INDEX idx_pending_orders ON enum_orders (created_at) WHERE status = 'pending';

-- 표현식 인덱스
CREATE INDEX idx_event_type_lower ON event_logs (lower(event_type));

-- ===========================
-- 9. 저장 함수 예제
-- ===========================

-- JSONB 데이터 집계 함수
CREATE OR REPLACE FUNCTION aggregate_event_data(p_event_type VARCHAR)
RETURNS JSONB AS $$
DECLARE
    result JSONB;
BEGIN
    SELECT jsonb_agg(event_data)
    INTO result
    FROM event_logs
    WHERE event_type = p_event_type;
    
    RETURN result;
END;
$$ LANGUAGE plpgsql;

-- 배열 작업 함수
CREATE OR REPLACE FUNCTION find_products_with_tag(p_tag TEXT)
RETURNS TABLE(product_id INT, product_name VARCHAR, all_tags TEXT[]) AS $$
BEGIN
    RETURN QUERY
    SELECT pt.product_id, pt.product_name, pt.tags
    FROM product_tags pt
    WHERE p_tag = ANY(pt.tags);
END;
$$ LANGUAGE plpgsql;

-- Range 중첩 확인 함수
CREATE OR REPLACE FUNCTION check_room_availability(
    p_room_number INT,
    p_check_in DATE,
    p_check_out DATE
)
RETURNS BOOLEAN AS $$
DECLARE
    is_available BOOLEAN;
BEGIN
    SELECT NOT EXISTS (
        SELECT 1
        FROM hotel_reservations
        WHERE room_number = p_room_number
        AND stay_period && daterange(p_check_in, p_check_out, '[)')
    ) INTO is_available;
    
    RETURN is_available;
END;
$$ LANGUAGE plpgsql;