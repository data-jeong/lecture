-- Chapter 03: DDL and Table Design - Solutions for Exercise 2
-- 답안: 고급 DDL 작업과 데이터베이스 설계

-- ============================================================================
-- Exercise 2-1: 파티셔닝 (PostgreSQL) - 답안
-- ============================================================================

-- 문제 1: logs 테이블 월별 파티셔닝
CREATE TABLE logs (
    log_id BIGSERIAL,
    user_id INTEGER,
    user_type VARCHAR(20) CHECK (user_type IN ('student', 'instructor', 'admin')),
    action VARCHAR(100) NOT NULL,
    resource_type VARCHAR(50),
    resource_id INTEGER,
    ip_address VARCHAR(45),  -- IPv6 지원
    user_agent VARCHAR(500),
    session_id VARCHAR(100),
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    additional_data JSONB,
    
    PRIMARY KEY (log_id, created_at)  -- 파티셔닝 키 포함
) PARTITION BY RANGE (created_at);

-- 2024년 월별 파티션 생성
CREATE TABLE logs_2024_01 PARTITION OF logs
    FOR VALUES FROM ('2024-01-01') TO ('2024-02-01');

CREATE TABLE logs_2024_02 PARTITION OF logs
    FOR VALUES FROM ('2024-02-01') TO ('2024-03-01');

CREATE TABLE logs_2024_03 PARTITION OF logs
    FOR VALUES FROM ('2024-03-01') TO ('2024-04-01');

CREATE TABLE logs_2024_04 PARTITION OF logs
    FOR VALUES FROM ('2024-04-01') TO ('2024-05-01');

CREATE TABLE logs_2024_05 PARTITION OF logs
    FOR VALUES FROM ('2024-05-01') TO ('2024-06-01');

CREATE TABLE logs_2024_06 PARTITION OF logs
    FOR VALUES FROM ('2024-06-01') TO ('2024-07-01');

CREATE TABLE logs_2024_07 PARTITION OF logs
    FOR VALUES FROM ('2024-07-01') TO ('2024-08-01');

CREATE TABLE logs_2024_08 PARTITION OF logs
    FOR VALUES FROM ('2024-08-01') TO ('2024-09-01');

CREATE TABLE logs_2024_09 PARTITION OF logs
    FOR VALUES FROM ('2024-09-01') TO ('2024-10-01');

CREATE TABLE logs_2024_10 PARTITION OF logs
    FOR VALUES FROM ('2024-10-01') TO ('2024-11-01');

CREATE TABLE logs_2024_11 PARTITION OF logs
    FOR VALUES FROM ('2024-11-01') TO ('2024-12-01');

CREATE TABLE logs_2024_12 PARTITION OF logs
    FOR VALUES FROM ('2024-12-01') TO ('2025-01-01');

-- 파티션별 인덱스 생성
CREATE INDEX idx_logs_user_id ON logs (user_id);
CREATE INDEX idx_logs_user_type ON logs (user_type);
CREATE INDEX idx_logs_action ON logs (action);
CREATE INDEX idx_logs_resource ON logs (resource_type, resource_id);
CREATE INDEX idx_logs_session ON logs (session_id);
CREATE INDEX idx_logs_additional_data ON logs USING GIN (additional_data);

-- 문제 2: user_activities 해시 파티셔닝
CREATE TABLE user_activities (
    activity_id BIGSERIAL,
    user_id INTEGER NOT NULL,
    activity_type VARCHAR(50) NOT NULL,
    course_id INTEGER,
    duration_seconds INTEGER CHECK (duration_seconds >= 0),
    score DECIMAL(10,2),
    metadata JSONB,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    PRIMARY KEY (activity_id, user_id)  -- 파티셔닝 키 포함
) PARTITION BY HASH (user_id);

-- 4개의 해시 파티션 생성
CREATE TABLE user_activities_0 PARTITION OF user_activities
    FOR VALUES WITH (MODULUS 4, REMAINDER 0);

CREATE TABLE user_activities_1 PARTITION OF user_activities
    FOR VALUES WITH (MODULUS 4, REMAINDER 1);

CREATE TABLE user_activities_2 PARTITION OF user_activities
    FOR VALUES WITH (MODULUS 4, REMAINDER 2);

CREATE TABLE user_activities_3 PARTITION OF user_activities
    FOR VALUES WITH (MODULUS 4, REMAINDER 3);

-- 파티션별 인덱스
CREATE INDEX idx_user_activities_type ON user_activities (activity_type);
CREATE INDEX idx_user_activities_course ON user_activities (course_id);
CREATE INDEX idx_user_activities_created ON user_activities (created_at);
CREATE INDEX idx_user_activities_metadata ON user_activities USING GIN (metadata);

-- ============================================================================
-- Exercise 2-2: 머티리얼라이즈드 뷰 - 답안
-- ============================================================================

-- 문제 3: daily_course_stats 머티리얼라이즈드 뷰
CREATE MATERIALIZED VIEW daily_course_stats AS
SELECT 
    DATE(COALESCE(e.enrollment_date, s.submitted_at, ua.created_at)) AS stat_date,
    c.course_id,
    c.course_name,
    c.course_code,
    i.first_name || ' ' || i.last_name AS instructor_name,
    
    -- 새로운 수강신청 수
    COUNT(DISTINCT CASE WHEN DATE(e.enrollment_date) = DATE(COALESCE(e.enrollment_date, s.submitted_at, ua.created_at)) 
                        THEN e.enrollment_id END) AS new_enrollments,
    
    -- 과제 제출 수
    COUNT(DISTINCT CASE WHEN DATE(s.submitted_at) = DATE(COALESCE(e.enrollment_date, s.submitted_at, ua.created_at))
                        THEN s.submission_id END) AS assignment_submissions,
    
    -- 평균 점수
    ROUND(AVG(s.score), 2) AS avg_assignment_score,
    
    -- 활성 학생 수 (해당 날짜에 활동이 있는 학생)
    COUNT(DISTINCT CASE WHEN DATE(ua.created_at) = DATE(COALESCE(e.enrollment_date, s.submitted_at, ua.created_at))
                        THEN ua.user_id END) AS active_students,
    
    -- 총 학습 시간
    COALESCE(SUM(CASE WHEN DATE(ua.created_at) = DATE(COALESCE(e.enrollment_date, s.submitted_at, ua.created_at))
                      THEN ua.duration_seconds END), 0) AS total_study_seconds,
    
    -- 데이터 마지막 업데이트 시간
    CURRENT_TIMESTAMP AS last_updated

FROM courses c
LEFT JOIN instructors i ON c.instructor_id = i.instructor_id
LEFT JOIN enrollments e ON c.course_id = e.course_id
LEFT JOIN assignments a ON c.course_id = a.course_id
LEFT JOIN submissions s ON a.assignment_id = s.assignment_id
LEFT JOIN user_activities ua ON c.course_id = ua.course_id

WHERE c.is_active = TRUE
  AND (e.enrollment_date IS NOT NULL OR s.submitted_at IS NOT NULL OR ua.created_at IS NOT NULL)

GROUP BY 
    DATE(COALESCE(e.enrollment_date, s.submitted_at, ua.created_at)),
    c.course_id, c.course_name, c.course_code,
    i.first_name, i.last_name

ORDER BY stat_date DESC, c.course_name;

-- 인덱스 생성
CREATE UNIQUE INDEX idx_daily_course_stats_unique 
    ON daily_course_stats (stat_date, course_id);
CREATE INDEX idx_daily_course_stats_date 
    ON daily_course_stats (stat_date);
CREATE INDEX idx_daily_course_stats_course 
    ON daily_course_stats (course_id);

-- 문제 4: monthly_revenue_analysis 머티리얼라이즈드 뷰
CREATE MATERIALIZED VIEW monthly_revenue_analysis AS
WITH monthly_data AS (
    SELECT 
        DATE_TRUNC('month', e.enrollment_date) AS month_year,
        SUM(c.price) AS total_revenue,
        COUNT(DISTINCT e.student_id) AS new_students,
        COUNT(DISTINCT c.course_id) AS active_courses,
        COUNT(e.enrollment_id) AS total_enrollments,
        ROUND(AVG(c.current_students), 2) AS avg_students_per_course
    FROM enrollments e
    JOIN courses c ON e.course_id = c.course_id
    WHERE e.payment_status = 'paid'
      AND e.enrollment_date >= '2023-01-01'
    GROUP BY DATE_TRUNC('month', e.enrollment_date)
)
SELECT 
    month_year,
    total_revenue,
    new_students,
    active_courses,
    total_enrollments,
    avg_students_per_course,
    
    -- 전월 대비 성장률
    ROUND(
        ((total_revenue - LAG(total_revenue) OVER (ORDER BY month_year)) / 
         NULLIF(LAG(total_revenue) OVER (ORDER BY month_year), 0)) * 100, 2
    ) AS revenue_growth_rate,
    
    ROUND(
        ((new_students - LAG(new_students) OVER (ORDER BY month_year)) / 
         NULLIF(LAG(new_students) OVER (ORDER BY month_year), 0)) * 100, 2
    ) AS student_growth_rate,
    
    -- 누적 수익
    SUM(total_revenue) OVER (ORDER BY month_year) AS cumulative_revenue,
    
    -- 업데이트 시간
    CURRENT_TIMESTAMP AS last_updated

FROM monthly_data
ORDER BY month_year;

-- 인덱스 생성
CREATE UNIQUE INDEX idx_monthly_revenue_month 
    ON monthly_revenue_analysis (month_year);

-- ============================================================================
-- Exercise 2-3: 트리거와 저장 프로시저 - 답안
-- ============================================================================

-- 문제 5: courses 테이블의 current_students 자동 업데이트 트리거
CREATE OR REPLACE FUNCTION update_course_student_count()
RETURNS TRIGGER AS $$
BEGIN
    -- INSERT나 UPDATE의 경우
    IF TG_OP = 'INSERT' OR TG_OP = 'UPDATE' THEN
        -- 새로운 수강신청이 'enrolled' 상태인 경우
        IF NEW.status = 'enrolled' THEN
            UPDATE courses 
            SET current_students = (
                SELECT COUNT(*) 
                FROM enrollments 
                WHERE course_id = NEW.course_id AND status = 'enrolled'
            )
            WHERE course_id = NEW.course_id;
        END IF;
        
        -- UPDATE에서 상태가 변경된 경우
        IF TG_OP = 'UPDATE' AND OLD.status != NEW.status THEN
            UPDATE courses 
            SET current_students = (
                SELECT COUNT(*) 
                FROM enrollments 
                WHERE course_id = NEW.course_id AND status = 'enrolled'
            )
            WHERE course_id = NEW.course_id;
        END IF;
        
        RETURN NEW;
    END IF;
    
    -- DELETE의 경우
    IF TG_OP = 'DELETE' THEN
        UPDATE courses 
        SET current_students = (
            SELECT COUNT(*) 
            FROM enrollments 
            WHERE course_id = OLD.course_id AND status = 'enrolled'
        )
        WHERE course_id = OLD.course_id;
        
        RETURN OLD;
    END IF;
    
    RETURN NULL;
END;
$$ LANGUAGE plpgsql;

-- 트리거 생성
CREATE TRIGGER trigger_update_course_student_count
    AFTER INSERT OR UPDATE OR DELETE ON enrollments
    FOR EACH ROW
    EXECUTE FUNCTION update_course_student_count();

-- GPA 자동 계산 함수
CREATE OR REPLACE FUNCTION update_student_gpa()
RETURNS TRIGGER AS $$
BEGIN
    -- 성적이 있는 경우에만 GPA 계산
    IF NEW.grade IS NOT NULL THEN
        UPDATE students 
        SET gpa = (
            SELECT ROUND(AVG(
                CASE grade
                    WHEN 'A+' THEN 4.5
                    WHEN 'A' THEN 4.0
                    WHEN 'B+' THEN 3.5
                    WHEN 'B' THEN 3.0
                    WHEN 'C+' THEN 2.5
                    WHEN 'C' THEN 2.0
                    WHEN 'D+' THEN 1.5
                    WHEN 'D' THEN 1.0
                    WHEN 'F' THEN 0.0
                END
            ), 2)
            FROM enrollments 
            WHERE student_id = NEW.student_id 
              AND grade IS NOT NULL
              AND status IN ('completed', 'failed')
        )
        WHERE student_id = NEW.student_id;
    END IF;
    
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- GPA 업데이트 트리거
CREATE TRIGGER trigger_update_student_gpa
    AFTER UPDATE ON enrollments
    FOR EACH ROW
    WHEN (OLD.grade IS DISTINCT FROM NEW.grade)
    EXECUTE FUNCTION update_student_gpa();

-- 문제 6: 수강신청 검증 트리거
CREATE OR REPLACE FUNCTION validate_enrollment()
RETURNS TRIGGER AS $$
DECLARE
    course_record RECORD;
    existing_enrollment INTEGER;
BEGIN
    -- 코스 정보 조회
    SELECT c.max_students, c.current_students, c.is_active, c.start_date
    INTO course_record
    FROM courses c
    WHERE c.course_id = NEW.course_id;
    
    -- 코스가 활성 상태인지 확인
    IF NOT course_record.is_active THEN
        RAISE EXCEPTION '비활성 코스에는 수강신청할 수 없습니다. (Course ID: %)', NEW.course_id;
    END IF;
    
    -- 최대 인원 확인
    IF course_record.current_students >= course_record.max_students THEN
        RAISE EXCEPTION '코스 정원이 초과되었습니다. (최대: %, 현재: %)', 
            course_record.max_students, course_record.current_students;
    END IF;
    
    -- 중복 수강신청 확인
    SELECT COUNT(*)
    INTO existing_enrollment
    FROM enrollments
    WHERE student_id = NEW.student_id 
      AND course_id = NEW.course_id
      AND status IN ('enrolled', 'completed');
    
    IF existing_enrollment > 0 THEN
        RAISE EXCEPTION '이미 수강신청한 코스입니다. (Student: %, Course: %)', 
            NEW.student_id, NEW.course_id;
    END IF;
    
    -- 수강신청일이 코스 시작일 이전인지 확인
    IF NEW.enrollment_date > course_record.start_date THEN
        RAISE EXCEPTION '코스 시작일 이후에는 수강신청할 수 없습니다. (시작일: %)', 
            course_record.start_date;
    END IF;
    
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- 수강신청 검증 트리거
CREATE TRIGGER trigger_validate_enrollment
    BEFORE INSERT ON enrollments
    FOR EACH ROW
    EXECUTE FUNCTION validate_enrollment();

-- ============================================================================
-- Exercise 2-4: 시퀀스와 사용자 정의 타입 - 답안
-- ============================================================================

-- 문제 7: 커스텀 시퀀스 생성
-- 코스 코드용 시퀀스
CREATE SEQUENCE course_code_seq
    START WITH 1000
    INCREMENT BY 1
    MINVALUE 1000
    MAXVALUE 9999
    CACHE 1;

-- 학번용 시퀀스
CREATE SEQUENCE student_number_seq
    START WITH 20240001
    INCREMENT BY 1
    MINVALUE 20240001
    MAXVALUE 99999999
    CACHE 1;

-- 청구서 번호용 시퀀스
CREATE SEQUENCE invoice_number_seq
    START WITH 100000
    INCREMENT BY 1
    MINVALUE 100000
    MAXVALUE 999999999
    CACHE 1;

-- 시퀀스 사용 함수들
CREATE OR REPLACE FUNCTION generate_course_code(prefix TEXT DEFAULT 'CS')
RETURNS TEXT AS $$
BEGIN
    RETURN prefix || nextval('course_code_seq');
END;
$$ LANGUAGE plpgsql;

CREATE OR REPLACE FUNCTION generate_invoice_number()
RETURNS TEXT AS $$
BEGIN
    RETURN 'INV' || nextval('invoice_number_seq');
END;
$$ LANGUAGE plpgsql;

-- 문제 8: 사용자 정의 데이터 타입 생성
-- 성적 열거형
CREATE TYPE grade_enum AS ENUM (
    'A+', 'A', 'B+', 'B', 'C+', 'C', 'D+', 'D', 'F'
);

-- 사용자 역할 열거형
CREATE TYPE user_role_enum AS ENUM (
    'student', 'instructor', 'admin', 'guest'
);

-- 코스 상태 열거형
CREATE TYPE course_status_enum AS ENUM (
    'draft', 'published', 'archived', 'cancelled'
);

-- 추가 열거형들
CREATE TYPE payment_status_enum AS ENUM (
    'pending', 'paid', 'failed', 'refunded', 'partial'
);

CREATE TYPE enrollment_status_enum AS ENUM (
    'enrolled', 'completed', 'dropped', 'failed', 'suspended'
);

-- 열거형 사용 예제 테이블 수정
ALTER TABLE enrollments 
    ALTER COLUMN grade TYPE grade_enum USING grade::grade_enum;

-- ============================================================================
-- Exercise 2-5: 복합 인덱스와 부분 인덱스 - 답안
-- ============================================================================

-- 문제 9: 고급 인덱스 전략

-- 1. 특정 기간 내의 특정 코스 로그 조회
CREATE INDEX idx_logs_course_time ON logs (course_id, created_at) 
WHERE course_id IS NOT NULL;

-- 2. 활성 상태인 학생의 최근 활동 조회
CREATE INDEX idx_user_activities_active_recent 
ON user_activities (user_type, created_at DESC) 
WHERE user_type = 'student';

-- 3. 특정 강사의 특정 난이도 코스 조회
CREATE INDEX idx_courses_instructor_difficulty 
ON courses (instructor_id, difficulty_level, is_active)
WHERE is_active = TRUE;

-- 4. 미완료 과제가 있는 수강생 조회
CREATE INDEX idx_enrollments_incomplete 
ON enrollments (status, completion_date)
WHERE status = 'enrolled' AND completion_date IS NULL;

-- 5. JSON 데이터 검색을 위한 GIN 인덱스
CREATE INDEX idx_logs_additional_data_page 
ON logs USING GIN ((additional_data->'page'));

CREATE INDEX idx_user_activities_metadata_gin 
ON user_activities USING GIN (metadata);

-- 추가 성능 최적화 인덱스들
CREATE INDEX idx_submissions_assignment_student_attempt 
ON submissions (assignment_id, student_id, attempt_number);

CREATE INDEX idx_courses_active_start_date 
ON courses (is_active, start_date) 
WHERE is_active = TRUE;

CREATE INDEX idx_enrollments_student_status_date 
ON enrollments (student_id, status, enrollment_date);

-- 문제 10: 함수 기반 인덱스

-- 1. 대소문자 구분 없는 강사 이름 검색
CREATE INDEX idx_instructors_lower_first_name 
ON instructors (LOWER(first_name));

CREATE INDEX idx_instructors_lower_last_name 
ON instructors (LOWER(last_name));

-- 2. 전체 이름 검색
CREATE INDEX idx_instructors_full_name 
ON instructors ((first_name || ' ' || last_name));

CREATE INDEX idx_students_full_name 
ON students ((first_name || ' ' || last_name));

-- 3. 이메일 도메인 검색
CREATE INDEX idx_instructors_email_domain 
ON instructors ((SPLIT_PART(email, '@', 2)));

CREATE INDEX idx_students_email_domain 
ON students ((SPLIT_PART(email, '@', 2)));

-- 4. 과제 제출일의 연월 기준 검색
CREATE INDEX idx_submissions_year_month 
ON submissions ((DATE_TRUNC('month', submitted_at)));

-- 전문 검색을 위한 텍스트 검색 인덱스
CREATE INDEX idx_courses_name_search 
ON courses USING GIN (to_tsvector('english', course_name));

CREATE INDEX idx_assignments_title_search 
ON assignments USING GIN (to_tsvector('english', title || ' ' || COALESCE(description, '')));

-- ============================================================================
-- Exercise 2-6: 테이블 상속 (PostgreSQL) - 답안
-- ============================================================================

-- 문제 11: 테이블 상속을 활용한 사용자 관리

-- 부모 테이블 생성
CREATE TABLE base_users (
    user_id SERIAL PRIMARY KEY,
    first_name VARCHAR(50) NOT NULL,
    last_name VARCHAR(50) NOT NULL,
    email VARCHAR(100) UNIQUE NOT NULL,
    phone VARCHAR(20),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    is_active BOOLEAN DEFAULT TRUE
);

-- 학생 테이블 (상속)
CREATE TABLE students_inherited (
    student_number VARCHAR(20) UNIQUE,
    major VARCHAR(100),
    enrollment_date DATE DEFAULT CURRENT_DATE,
    gpa DECIMAL(3,2) CHECK (gpa >= 0.0 AND gpa <= 4.0),
    
    CONSTRAINT check_student_email CHECK (email LIKE '%@student.%')
) INHERITS (base_users);

-- 강사 테이블 (상속)
CREATE TABLE instructors_inherited (
    employee_id VARCHAR(20) UNIQUE,
    department VARCHAR(100),
    hourly_rate DECIMAL(10,2) CHECK (hourly_rate > 0),
    specialization VARCHAR(100),
    years_experience INTEGER CHECK (years_experience >= 0),
    
    CONSTRAINT check_instructor_email CHECK (email LIKE '%@faculty.%' OR email LIKE '%@staff.%')
) INHERITS (base_users);

-- 상속 테이블을 위한 인덱스
CREATE INDEX idx_students_inherited_student_number ON students_inherited (student_number);
CREATE INDEX idx_students_inherited_major ON students_inherited (major);
CREATE INDEX idx_instructors_inherited_employee_id ON instructors_inherited (employee_id);
CREATE INDEX idx_instructors_inherited_department ON instructors_inherited (department);

-- 상속 테이블용 트리거
CREATE TRIGGER update_students_inherited_updated_at 
    BEFORE UPDATE ON students_inherited 
    FOR EACH ROW 
    EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_instructors_inherited_updated_at 
    BEFORE UPDATE ON instructors_inherited 
    FOR EACH ROW 
    EXECUTE FUNCTION update_updated_at_column();

-- ============================================================================
-- Exercise 2-7: 외래 테이블과 확장 기능 - 답안
-- ============================================================================

-- 문제 12: PostgreSQL 확장 기능 활용

-- 확장 기능 활성화
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE EXTENSION IF NOT EXISTS hstore;
CREATE EXTENSION IF NOT EXISTS pg_trgm;  -- 텍스트 유사성 검색용

-- sessions 테이블 생성
CREATE TABLE sessions (
    session_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id INTEGER NOT NULL,
    user_type user_role_enum NOT NULL,
    login_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    logout_time TIMESTAMP,
    ip_address INET,  -- IP 주소 전용 타입
    browser_info HSTORE,  -- 키-값 쌍으로 브라우저 정보 저장
    search_vector TSVECTOR,  -- 전문 검색용
    session_data JSONB,  -- 세션 데이터
    is_active BOOLEAN DEFAULT TRUE,
    last_activity TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    -- 제약조건
    CONSTRAINT check_logout_after_login 
        CHECK (logout_time IS NULL OR logout_time >= login_time)
);

-- hstore를 활용한 인덱스
CREATE INDEX idx_sessions_browser_info ON sessions USING GIN (browser_info);
CREATE INDEX idx_sessions_search_vector ON sessions USING GIN (search_vector);
CREATE INDEX idx_sessions_session_data ON sessions USING GIN (session_data);

-- IP 주소 검색을 위한 인덱스
CREATE INDEX idx_sessions_ip_address ON sessions USING GIST (ip_address inet_ops);

-- 유사성 검색을 위한 인덱스 (pg_trgm 확장 사용)
CREATE INDEX idx_sessions_similarity ON sessions USING GIN (session_id::text gin_trgm_ops);

-- search_vector 자동 업데이트 함수
CREATE OR REPLACE FUNCTION update_session_search_vector()
RETURNS TRIGGER AS $$
BEGIN
    NEW.search_vector := to_tsvector('english', 
        COALESCE(NEW.session_id::text, '') || ' ' ||
        COALESCE(NEW.ip_address::text, '') || ' ' ||
        COALESCE(NEW.browser_info::text, '')
    );
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- search_vector 업데이트 트리거
CREATE TRIGGER trigger_update_session_search_vector
    BEFORE INSERT OR UPDATE ON sessions
    FOR EACH ROW
    EXECUTE FUNCTION update_session_search_vector();

-- ============================================================================
-- Exercise 2-8: 성능 최적화와 모니터링 - 답안
-- ============================================================================

-- 문제 13: 통계 정보 업데이트 전략

-- 모든 테이블의 통계 정보 업데이트
DO $$
DECLARE
    table_name TEXT;
BEGIN
    FOR table_name IN 
        SELECT tablename FROM pg_tables WHERE schemaname = 'public'
    LOOP
        EXECUTE 'ANALYZE ' || quote_ident(table_name);
    END LOOP;
END $$;

-- 인덱스 사용률 모니터링 쿼리
CREATE VIEW index_usage_stats AS
SELECT 
    schemaname,
    tablename,
    indexname,
    idx_tup_read,
    idx_tup_fetch,
    CASE 
        WHEN idx_tup_read = 0 THEN 0
        ELSE (idx_tup_fetch * 100.0 / idx_tup_read)
    END AS hit_ratio,
    pg_size_pretty(pg_relation_size(indexrelid)) AS index_size
FROM pg_stat_user_indexes
ORDER BY idx_tup_read DESC;

-- 테이블 크기와 인덱스 크기 조회
CREATE VIEW table_sizes AS
SELECT 
    schemaname,
    tablename,
    pg_size_pretty(pg_total_relation_size(schemaname||'.'||tablename)) AS total_size,
    pg_size_pretty(pg_relation_size(schemaname||'.'||tablename)) AS table_size,
    pg_size_pretty(pg_total_relation_size(schemaname||'.'||tablename) - 
                   pg_relation_size(schemaname||'.'||tablename)) AS index_size,
    pg_stat_get_live_tuples(c.oid) AS live_tuples,
    pg_stat_get_dead_tuples(c.oid) AS dead_tuples
FROM pg_tables pt
JOIN pg_class c ON c.relname = pt.tablename
WHERE pt.schemaname = 'public'
ORDER BY pg_total_relation_size(schemaname||'.'||tablename) DESC;

-- 느린 쿼리 식별 뷰 (pg_stat_statements 확장 필요)
CREATE VIEW slow_queries AS
SELECT 
    query,
    calls,
    total_time,
    mean_time,
    rows,
    100.0 * shared_blks_hit / nullif(shared_blks_hit + shared_blks_read, 0) AS hit_percent
FROM pg_stat_statements
WHERE calls > 10
ORDER BY mean_time DESC
LIMIT 20;

-- 문제 14: 파티션 관리 자동화

-- 다음 달 파티션 생성 함수
CREATE OR REPLACE FUNCTION create_monthly_partition(
    table_name TEXT,
    partition_date DATE DEFAULT DATE_TRUNC('month', CURRENT_DATE + INTERVAL '1 month')
)
RETURNS TEXT AS $$
DECLARE
    partition_name TEXT;
    start_date DATE;
    end_date DATE;
    sql_cmd TEXT;
BEGIN
    start_date := DATE_TRUNC('month', partition_date);
    end_date := start_date + INTERVAL '1 month';
    partition_name := table_name || '_' || TO_CHAR(start_date, 'YYYY_MM');
    
    sql_cmd := format(
        'CREATE TABLE %I PARTITION OF %I FOR VALUES FROM (%L) TO (%L)',
        partition_name, table_name, start_date, end_date
    );
    
    EXECUTE sql_cmd;
    
    -- 파티션별 인덱스 생성 (logs 테이블의 경우)
    IF table_name = 'logs' THEN
        EXECUTE format('CREATE INDEX %I ON %I (user_id)', 
                      'idx_' || partition_name || '_user_id', partition_name);
        EXECUTE format('CREATE INDEX %I ON %I (action)', 
                      'idx_' || partition_name || '_action', partition_name);
    END IF;
    
    RETURN '파티션 생성 완료: ' || partition_name;
END;
$$ LANGUAGE plpgsql;

-- 오래된 파티션 삭제 함수 (6개월 이전)
CREATE OR REPLACE FUNCTION drop_old_partitions(
    table_name TEXT,
    months_to_keep INTEGER DEFAULT 6
)
RETURNS TEXT[] AS $$
DECLARE
    partition_record RECORD;
    cutoff_date DATE;
    dropped_partitions TEXT[] := '{}';
BEGIN
    cutoff_date := DATE_TRUNC('month', CURRENT_DATE - (months_to_keep || ' months')::INTERVAL);
    
    FOR partition_record IN
        SELECT schemaname, tablename 
        FROM pg_tables 
        WHERE tablename LIKE table_name || '_%'
          AND tablename ~ '\d{4}_\d{2}$'
          AND TO_DATE(RIGHT(tablename, 7), 'YYYY_MM') < cutoff_date
    LOOP
        EXECUTE 'DROP TABLE IF EXISTS ' || quote_ident(partition_record.tablename) || ' CASCADE';
        dropped_partitions := array_append(dropped_partitions, partition_record.tablename);
    END LOOP;
    
    RETURN dropped_partitions;
END;
$$ LANGUAGE plpgsql;

-- 파티션 관리를 위한 메인 함수
CREATE OR REPLACE FUNCTION maintain_partitions()
RETURNS TEXT AS $$
DECLARE
    result TEXT := '';
    dropped_list TEXT[];
BEGIN
    -- 새 파티션 생성
    result := result || create_monthly_partition('logs') || E'\n';
    
    -- 오래된 파티션 삭제
    dropped_list := drop_old_partitions('logs', 6);
    
    IF array_length(dropped_list, 1) > 0 THEN
        result := result || '삭제된 파티션: ' || array_to_string(dropped_list, ', ');
    ELSE
        result := result || '삭제된 파티션 없음';
    END IF;
    
    -- 통계 정보 업데이트
    ANALYZE logs;
    
    RETURN result;
END;
$$ LANGUAGE plpgsql;

-- pg_cron을 사용한 스케줄링 (의사코드 - 실제로는 슈퍼유저 권한 필요)
/*
-- 매월 1일 자정에 파티션 관리 실행
SELECT cron.schedule('maintain-partitions', '0 0 1 * *', 'SELECT maintain_partitions();');

-- 매일 자정에 통계 정보 업데이트
SELECT cron.schedule('update-stats', '0 0 * * *', 'ANALYZE;');
*/

-- 머티리얼라이즈드 뷰 새로고침 함수
CREATE OR REPLACE FUNCTION refresh_all_materialized_views()
RETURNS TEXT AS $$
DECLARE
    view_record RECORD;
    result TEXT := '';
BEGIN
    FOR view_record IN
        SELECT matviewname
        FROM pg_matviews
        WHERE schemaname = 'public'
    LOOP
        EXECUTE 'REFRESH MATERIALIZED VIEW ' || quote_ident(view_record.matviewname);
        result := result || '새로고침 완료: ' || view_record.matviewname || E'\n';
    END LOOP;
    
    RETURN result;
END;
$$ LANGUAGE plpgsql;

-- 성능 모니터링을 위한 대시보드 뷰
CREATE VIEW performance_dashboard AS
SELECT 
    'Database Size' AS metric,
    pg_size_pretty(pg_database_size(current_database())) AS value,
    'Total database size' AS description

UNION ALL

SELECT 
    'Active Connections',
    COUNT(*)::TEXT,
    'Current active connections'
FROM pg_stat_activity
WHERE state = 'active'

UNION ALL

SELECT 
    'Cache Hit Ratio',
    ROUND((sum(blks_hit) * 100.0 / sum(blks_hit + blks_read)), 2)::TEXT || '%',
    'Buffer cache efficiency'
FROM pg_stat_database
WHERE datname = current_database()

UNION ALL

SELECT 
    'Largest Table',
    (SELECT tablename FROM table_sizes LIMIT 1),
    'Table with most storage usage'

UNION ALL

SELECT 
    'Total Partitions',
    COUNT(*)::TEXT,
    'Number of partition tables'
FROM pg_tables 
WHERE tablename LIKE '%_202%';

-- 최종 검증 쿼리
SELECT 'Advanced DDL setup completed successfully!' AS status;