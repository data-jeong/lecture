-- Chapter 03: DDL and Table Design - Exercise 2: Advanced DDL Operations
-- 연습문제: 고급 DDL 작업과 데이터베이스 설계

/*
실습 시나리오: 
기존의 온라인 학습 플랫폼에 새로운 기능들을 추가하고,
성능 최적화 및 데이터 관리 개선을 위한 고급 DDL 작업을 수행합니다.
*/

-- ============================================================================
-- Exercise 2-1: 파티셔닝 (PostgreSQL)
-- ============================================================================

/*
문제 1: logs 테이블을 생성하고 날짜별로 파티셔닝하세요.
로그 데이터는 시간이 지날수록 대용량이 되므로 효율적인 관리가 필요합니다.

요구사항:
- log_id: 자동 증가하는 기본키
- user_id: 사용자 ID (정수)
- user_type: 사용자 유형 ('student', 'instructor', 'admin')
- action: 수행한 작업 (최대 100자)
- resource_type: 리소스 유형 (최대 50자)
- resource_id: 리소스 ID (정수)
- ip_address: IP 주소 (최대 45자, IPv6 지원)
- user_agent: 사용자 에이전트 (최대 500자)
- session_id: 세션 ID (최대 100자)
- created_at: 생성시간 (타임스탬프, 기본값 현재시간)
- additional_data: 추가 데이터 (JSONB)

파티셔닝:
- created_at 컬럼을 기준으로 월별 파티셔닝
- 2024년 1월부터 12월까지의 파티션 생성
*/

-- 파티션 테이블 생성
-- CREATE TABLE logs (
--     ...
-- ) PARTITION BY RANGE (created_at);

-- 월별 파티션 생성
-- CREATE TABLE logs_2024_01 PARTITION OF logs
--     FOR VALUES FROM ('2024-01-01') TO ('2024-02-01');


/*
문제 2: 사용자별 해시 파티셔닝 테이블 생성
대용량 사용자 활동 데이터를 효율적으로 분산 저장하기 위한 테이블을 생성하세요.

user_activities 테이블:
- activity_id: 자동 증가 기본키
- user_id: 사용자 ID (정수, 파티셔닝 키)
- activity_type: 활동 유형 (최대 50자)
- course_id: 관련 코스 ID (정수, 선택사항)
- duration_seconds: 활동 지속시간 (정수)
- score: 점수/성과 (소수점 2자리)
- metadata: 메타데이터 (JSONB)
- created_at: 생성시간 (타임스탬프)

4개의 해시 파티션으로 분할
*/

-- 여기에 답안을 작성하세요


-- ============================================================================
-- Exercise 2-2: 머티리얼라이즈드 뷰
-- ============================================================================

/*
문제 3: 성능 최적화를 위한 머티리얼라이즈드 뷰 생성
자주 조회되는 복잡한 집계 쿼리를 위한 머티리얼라이즈드 뷰를 생성하세요.

daily_course_stats 머티리얼라이즈드 뷰:
- 날짜별, 코스별 통계 정보
- 포함 데이터:
  * 날짜
  * 코스 ID, 코스명
  * 새로운 수강신청 수
  * 과제 제출 수
  * 평균 점수
  * 활성 학생 수
  * 총 학습 시간 (user_activities의 duration_seconds 합계)
*/

-- 여기에 답안을 작성하세요


/*
문제 4: 월별 수익 분석 머티리얼라이즈드 뷰
monthly_revenue_analysis 머티리얼라이즈드 뷰:
- 월별 수익 분석 데이터
- 포함 데이터:
  * 년월
  * 총 수강료 수입
  * 신규 학생 수
  * 활성 코스 수
  * 평균 코스당 수강생 수
  * 전월 대비 성장률 (LAG 함수 사용)
*/

-- 여기에 답안을 작성하세요


-- ============================================================================
-- Exercise 2-3: 트리거와 저장 프로시저
-- ============================================================================

/*
문제 5: 자동 업데이트 트리거 생성
다음 시나리오에 대한 트리거를 작성하세요:

1. courses 테이블의 current_students 자동 업데이트
   - enrollments 테이블에 새로운 수강신청이 추가될 때
   - 기존 수강신청의 상태가 변경될 때
   
2. students 테이블의 gpa 자동 계산
   - enrollments 테이블에서 성적이 업데이트될 때
   - 성적을 숫자로 변환하여 GPA 계산 (A+ = 4.5, A = 4.0, ..., F = 0.0)
*/

-- 트리거 함수 생성
-- CREATE OR REPLACE FUNCTION update_course_student_count()
-- RETURNS TRIGGER AS $$
-- BEGIN
--     ...
-- END;
-- $$ LANGUAGE plpgsql;

-- 트리거 생성
-- CREATE TRIGGER trigger_update_course_student_count
--     AFTER INSERT OR UPDATE OR DELETE ON enrollments
--     FOR EACH ROW
--     EXECUTE FUNCTION update_course_student_count();


/*
문제 6: 데이터 검증 트리거
enrollment_validation 트리거:
- 수강신청 시 다음 조건들을 검증:
  * 코스의 최대 인원을 초과하지 않는지
  * 학생이 이미 해당 코스에 수강신청했는지
  * 코스가 활성 상태인지
  * 수강신청일이 코스 시작일 이전인지
*/

-- 여기에 답안을 작성하세요


-- ============================================================================
-- Exercise 2-4: 시퀀스와 사용자 정의 타입
-- ============================================================================

/*
문제 7: 커스텀 시퀀스 생성
다음 시퀀스들을 생성하세요:

1. course_code_seq: 코스 코드용 (CS1000부터 시작, 1씩 증가)
2. student_number_seq: 학번용 (20240001부터 시작, 1씩 증가)
3. invoice_number_seq: 청구서 번호용 (INV100000부터 시작, 1씩 증가)
*/

-- 여기에 답안을 작성하세요


/*
문제 8: 사용자 정의 데이터 타입 생성 (PostgreSQL)
다음 사용자 정의 타입들을 생성하세요:

1. grade_enum: 성적 타입 ('A+', 'A', 'B+', 'B', 'C+', 'C', 'D+', 'D', 'F')
2. user_role_enum: 사용자 역할 ('student', 'instructor', 'admin', 'guest')
3. course_status_enum: 코스 상태 ('draft', 'published', 'archived', 'cancelled')
*/

-- 여기에 답안을 작성하세요


-- ============================================================================
-- Exercise 2-5: 복합 인덱스와 부분 인덱스
-- ============================================================================

/*
문제 9: 고급 인덱스 전략
다음 쿼리 패턴을 분석하고 최적의 인덱스를 생성하세요:

1. 특정 기간 내의 특정 코스 로그 조회:
   WHERE course_id = ? AND created_at BETWEEN ? AND ?

2. 활성 상태인 학생의 최근 활동 조회:
   WHERE user_type = 'student' AND is_active = true ORDER BY created_at DESC

3. 특정 강사의 특정 난이도 코스 조회:
   WHERE instructor_id = ? AND difficulty_level = ? AND is_active = true

4. 미완료 과제가 있는 수강생 조회:
   WHERE status = 'enrolled' AND completion_date IS NULL

5. JSON 데이터 내의 특정 키 검색 (additional_data에서 'page' 키 검색)
*/

-- 복합 인덱스와 부분 인덱스를 생성하세요


/*
문제 10: 함수 기반 인덱스
다음 검색 패턴을 위한 함수 기반 인덱스를 생성하세요:

1. 대소문자 구분 없는 강사 이름 검색
2. 전체 이름(first_name + last_name) 검색
3. 이메일의 도메인 부분 검색
4. 과제 제출일의 연월 기준 검색
*/

-- 여기에 답안을 작성하세요


-- ============================================================================
-- Exercise 2-6: 테이블 상속 (PostgreSQL)
-- ============================================================================

/*
문제 11: 테이블 상속을 활용한 사용자 관리
base_users 부모 테이블을 생성하고, 이를 상속받는 students와 instructors 테이블을 생성하세요.

base_users:
- user_id: 기본키
- first_name, last_name: 이름 정보
- email: 이메일 (유일값)
- phone: 전화번호
- created_at, updated_at: 시간 정보
- is_active: 활성 상태

students (base_users 상속):
- student_number: 학번
- major: 전공
- enrollment_date: 등록일
- gpa: 평점

instructors (base_users 상속):
- employee_id: 직원 ID
- department: 부서
- hourly_rate: 시간당 급여
- specialization: 전문분야
*/

-- 여기에 답안을 작성하세요


-- ============================================================================
-- Exercise 2-7: 외래 테이블과 확장 기능
-- ============================================================================

/*
문제 12: PostgreSQL 확장 기능 활용
다음 확장 기능들을 활용한 테이블을 생성하세요:

1. uuid-ossp 확장을 사용한 UUID 기본키
2. hstore 확장을 사용한 키-값 쌍 저장
3. 전문 검색을 위한 tsvector 컬럼

sessions 테이블:
- session_id: UUID 기본키
- user_id: 사용자 ID
- login_time: 로그인 시간
- logout_time: 로그아웃 시간
- ip_address: IP 주소
- browser_info: 브라우저 정보 (hstore)
- search_vector: 검색용 벡터 (tsvector)
*/

-- 확장 기능 활성화 (필요한 경우)
-- CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
-- CREATE EXTENSION IF NOT EXISTS hstore;

-- 여기에 답안을 작성하세요


-- ============================================================================
-- Exercise 2-8: 성능 최적화와 모니터링
-- ============================================================================

/*
문제 13: 통계 정보 업데이트 전략
대용량 테이블의 성능 최적화를 위한 설정과 모니터링 쿼리를 작성하세요:

1. 테이블별 통계 정보 수동 업데이트
2. 인덱스 사용률 모니터링 쿼리
3. 테이블 크기와 인덱스 크기 조회 쿼리
4. 느린 쿼리 식별을 위한 모니터링 쿼리
*/

-- 통계 정보 업데이트
-- ANALYZE table_name;

-- 인덱스 사용률 모니터링 쿼리 작성


/*
문제 14: 파티션 관리 자동화
월별 파티션을 자동으로 생성하고 오래된 파티션을 삭제하는 함수를 작성하세요:

1. create_monthly_partition(): 다음 달 파티션 생성
2. drop_old_partitions(): 6개월 이전 파티션 삭제
3. 이를 스케줄링하기 위한 pg_cron 설정 (의사코드)
*/

-- 여기에 답안을 작성하세요


-- ============================================================================
-- 검증 및 테스트 쿼리
-- ============================================================================

-- 생성된 파티션 테이블 확인
SELECT 
    schemaname,
    tablename,
    tableowner
FROM pg_tables 
WHERE tablename LIKE 'logs%' OR tablename LIKE 'user_activities%'
ORDER BY tablename;

-- 머티리얼라이즈드 뷰 확인
SELECT 
    matviewname,
    definition
FROM pg_matviews 
WHERE schemaname = 'public'
ORDER BY matviewname;

-- 트리거 목록 확인
SELECT 
    trigger_name,
    event_manipulation,
    event_object_table,
    action_statement
FROM information_schema.triggers
WHERE trigger_schema = 'public'
ORDER BY event_object_table, trigger_name;

-- 시퀀스 목록 확인
SELECT 
    sequencename,
    start_value,
    increment_by,
    max_value,
    min_value
FROM pg_sequences
WHERE schemaname = 'public'
ORDER BY sequencename;

-- 사용자 정의 타입 확인
SELECT 
    typname,
    typtype,
    typcategory
FROM pg_type 
WHERE typnamespace = (SELECT oid FROM pg_namespace WHERE nspname = 'public')
  AND typtype = 'e'  -- enum types
ORDER BY typname;

-- 확장 기능 목록 확인
SELECT 
    extname,
    extversion
FROM pg_extension
ORDER BY extname;