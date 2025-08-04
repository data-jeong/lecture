-- PostgreSQL 초기화 스크립트
-- 확장 모듈 설치 및 기본 설정

-- UUID 확장 설치
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- 전문 검색 확장 설치
CREATE EXTENSION IF NOT EXISTS "pg_trgm";

-- JSON 확장 함수들
CREATE EXTENSION IF NOT EXISTS "btree_gin";

-- 시간대 설정
SET timezone = 'UTC';

-- 기본 사용자 권한 설정
GRANT ALL PRIVILEGES ON DATABASE sql_course TO student;
GRANT ALL PRIVILEGES ON SCHEMA public TO student;

-- 기본 함수들 생성
CREATE OR REPLACE FUNCTION update_modified_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.last_modified = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ language 'plpgsql';

-- 로깅을 위한 기본 설정
ALTER SYSTEM SET log_statement = 'all';
ALTER SYSTEM SET log_duration = 'on';
SELECT pg_reload_conf();

COMMIT;