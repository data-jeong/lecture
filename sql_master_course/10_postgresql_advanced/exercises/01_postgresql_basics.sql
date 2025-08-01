-- Chapter 10: PostgreSQL 고급 기능 실습 문제

-- 문제 1: JSON/JSONB 데이터 처리
-- 사용자 프로필 정보를 JSONB로 저장하고 복잡한 쿼리 작성

CREATE TABLE user_profiles (
    user_id SERIAL PRIMARY KEY,
    username VARCHAR(50),
    profile JSONB
);

-- 샘플 데이터 삽입 및 JSON 경로 쿼리 작성

-- 문제 2: 배열 타입 활용
-- 게시글의 태그 시스템을 배열로 구현

CREATE TABLE posts (
    post_id SERIAL PRIMARY KEY,
    title TEXT,
    content TEXT,
    tags TEXT[]
);

-- 배열 검색 및 집계 쿼리 작성

-- 문제 3: Range 타입 사용
-- 회의실 예약 시스템에서 시간 범위 겹침 검사

-- 문제 4: 기본 PL/pgSQL 함수 작성
-- 복리 계산 함수 작성

-- 문제 5: GIN 인덱스 활용
-- 전문 검색을 위한 GIN 인덱스 생성과 활용