-- Chapter 03: DDL and Table Design - Exercise 1: Table Creation
-- 연습문제: 테이블 생성과 제약조건

/*
실습 시나리오: 
온라인 학습 플랫폼을 위한 데이터베이스를 설계해야 합니다.
다음 요구사항에 맞는 테이블들을 생성하세요.
*/

-- ============================================================================
-- Exercise 1-1: 기본 테이블 생성
-- ============================================================================

/*
문제 1: 강사(instructors) 테이블을 생성하세요.
요구사항:
- instructor_id: 자동 증가하는 기본키
- first_name: 이름 (최대 50자, 필수)
- last_name: 성 (최대 50자, 필수)
- email: 이메일 (최대 100자, 유일값, 필수)
- phone: 전화번호 (최대 20자)
- bio: 자기소개 (긴 텍스트)
- hourly_rate: 시간당 강의료 (소수점 2자리, 0보다 큰 값)
- specialization: 전문분야 (최대 100자)
- years_experience: 경력년수 (정수, 0 이상)
- is_active: 활성 상태 (불린, 기본값 true)
- joined_date: 가입일 (날짜, 기본값 현재날짜)
- created_at: 생성시간 (타임스탬프, 기본값 현재시간)
*/

-- 여기에 답안을 작성하세요
-- CREATE TABLE instructors (
--     ...
-- );


/*
문제 2: 학생(students) 테이블을 생성하세요.
요구사항:
- student_id: 자동 증가하는 기본키
- student_number: 학번 (최대 20자, 유일값, 'STU'로 시작)
- first_name: 이름 (최대 50자, 필수)
- last_name: 성 (최대 50자, 필수)
- email: 이메일 (최대 100자, 유일값, 필수)
- phone: 전화번호 (최대 20자)
- date_of_birth: 생년월일 (날짜)
- gender: 성별 ('M' 또는 'F')
- grade_level: 학년 (1부터 4까지)
- major: 전공 (최대 100자)
- enrollment_date: 등록일 (날짜, 기본값 현재날짜)
- graduation_date: 졸업일 (날짜, 선택사항)
- gpa: 평점 (소수점 2자리, 0.0 이상 4.0 이하)
- is_active: 활성 상태 (불린, 기본값 true)
- created_at: 생성시간 (타임스탬프, 기본값 현재시간)
*/

-- 여기에 답안을 작성하세요


/*
문제 3: 코스(courses) 테이블을 생성하세요.
요구사항:
- course_id: 자동 증가하는 기본키
- course_code: 코스코드 (최대 20자, 유일값, 필수)
- course_name: 코스명 (최대 255자, 필수)
- description: 설명 (긴 텍스트)
- instructor_id: 강사 ID (외래키, instructors 테이블 참조)
- credits: 학점 (정수, 1 이상 6 이하)
- max_students: 최대 수강인원 (정수, 1 이상)
- current_students: 현재 수강인원 (정수, 기본값 0, 0 이상)
- price: 수강료 (소수점 2자리, 0 이상)
- difficulty_level: 난이도 ('Beginner', 'Intermediate', 'Advanced' 중 하나)
- duration_weeks: 수업기간(주) (정수, 1 이상)
- start_date: 시작일 (날짜)
- end_date: 종료일 (날짜)
- is_active: 활성 상태 (불린, 기본값 true)
- created_at: 생성시간 (타임스탬프, 기본값 현재시간)
- updated_at: 수정시간 (타임스탬프, 기본값 현재시간)

추가 제약조건:
- 현재 수강인원이 최대 수강인원을 초과할 수 없음
- 종료일이 시작일보다 늦어야 함
*/

-- 여기에 답안을 작성하세요


-- ============================================================================
-- Exercise 1-2: 복합 제약조건과 고급 테이블
-- ============================================================================

/*
문제 4: 수강신청(enrollments) 테이블을 생성하세요.
요구사항:
- enrollment_id: 자동 증가하는 기본키
- student_id: 학생 ID (외래키, students 테이블 참조)
- course_id: 코스 ID (외래키, courses 테이블 참조)
- enrollment_date: 수강신청일 (날짜, 기본값 현재날짜)
- status: 상태 ('enrolled', 'completed', 'dropped', 'failed' 중 하나, 기본값 'enrolled')
- grade: 성적 ('A+', 'A', 'B+', 'B', 'C+', 'C', 'D+', 'D', 'F' 중 하나, 선택사항)
- final_score: 최종점수 (소수점 2자리, 0 이상 100 이하)
- completion_date: 수료일 (날짜, 선택사항)
- payment_status: 결제상태 ('pending', 'paid', 'refunded' 중 하나, 기본값 'pending')
- created_at: 생성시간 (타임스탬프, 기본값 현재시간)

추가 제약조건:
- 같은 학생이 같은 코스에 중복 수강신청할 수 없음
- 수료일이 수강신청일보다 늦어야 함 (수료일이 있는 경우)
*/

-- 여기에 답안을 작성하세요


/*
문제 5: 과제(assignments) 테이블을 생성하세요.
요구사항:
- assignment_id: 자동 증가하는 기본키
- course_id: 코스 ID (외래키, courses 테이블 참조)
- title: 과제 제목 (최대 255자, 필수)
- description: 과제 설명 (긴 텍스트)
- type: 과제 유형 ('homework', 'quiz', 'project', 'exam' 중 하나)
- max_score: 만점 (소수점 2자리, 0보다 큰 값)
- weight: 성적 반영 비율 (소수점 4자리, 0 이상 1 이하)
- due_date: 마감일 (타임스탬프)
- is_group_work: 팀 과제 여부 (불린, 기본값 false)
- submission_format: 제출 형식 ('online', 'offline', 'presentation' 중 하나)
- created_at: 생성시간 (타임스탬프, 기본값 현재시간)
- updated_at: 수정시간 (타임스탬프, 기본값 현재시간)
*/

-- 여기에 답안을 작성하세요


/*
문제 6: 과제 제출(submissions) 테이블을 생성하세요.
요구사항:
- submission_id: 자동 증가하는 기본키
- assignment_id: 과제 ID (외래키, assignments 테이블 참조)
- student_id: 학생 ID (외래키, students 테이블 참조)
- submitted_at: 제출시간 (타임스탬프, 기본값 현재시간)
- content: 제출 내용 (긴 텍스트)
- file_path: 첨부파일 경로 (최대 500자)
- score: 점수 (소수점 2자리, 0 이상)
- feedback: 피드백 (긴 텍스트)
- graded_at: 채점일시 (타임스탬프)
- graded_by: 채점자 ID (외래키, instructors 테이블 참조)
- is_late: 지각 제출 여부 (불린, 기본값 false)
- attempt_number: 시도 횟수 (정수, 기본값 1, 1 이상)

추가 제약조건:
- 같은 학생이 같은 과제에 대해 여러 번 제출할 수 있지만, 각 시도마다 고유해야 함
- 점수는 해당 과제의 만점을 초과할 수 없음 (이는 트리거나 애플리케이션에서 처리)
*/

-- 여기에 답안을 작성하세요


-- ============================================================================
-- Exercise 1-3: 인덱스 생성
-- ============================================================================

/*
문제 7: 성능 최적화를 위한 인덱스를 생성하세요.
다음 쿼리 패턴을 고려하여 적절한 인덱스를 설계하세요:

1. 강사의 이메일로 검색하는 경우가 많음
2. 학생의 학번으로 검색하는 경우가 많음
3. 코스를 강사별로 조회하는 경우가 많음
4. 수강신청을 학생별, 코스별로 조회하는 경우가 많음
5. 과제를 코스별로 조회하는 경우가 많음
6. 과제 제출을 과제별, 학생별로 조회하는 경우가 많음
7. 활성 상태인 강사/학생/코스만 조회하는 경우가 많음
8. 코스를 난이도별로 필터링하는 경우가 많음
*/

-- 인덱스를 생성하세요 (인덱스명은 의미있게 작성)
-- 예: CREATE INDEX idx_instructors_email ON instructors (email);


-- ============================================================================
-- Exercise 1-4: 뷰 생성
-- ============================================================================

/*
문제 8: 자주 사용되는 조인을 위한 뷰를 생성하세요.

1. instructor_courses_view: 강사별 담당 코스 정보
   - 강사 정보 (이름, 이메일, 전문분야)
   - 코스 정보 (코스명, 코스코드, 학점, 수강료)
   - 현재 수강생 수, 최대 수강생 수
*/

-- 여기에 답안을 작성하세요


/*
문제 9: student_progress_view 생성
   - 학생별 수강 현황 정보
   - 학생 정보 (이름, 이메일, 학번)
   - 수강 중인 코스 수
   - 완료한 코스 수
   - 평균 성적 (GPA)
   - 총 취득 학점
*/

-- 여기에 답안을 작성하세요


/*
문제 10: course_statistics_view 생성
   - 코스별 통계 정보
   - 코스 정보 (코스명, 강사명)
   - 총 수강신청자 수
   - 완료자 수
   - 중도포기자 수
   - 평균 점수
   - 완료율 (%)
*/

-- 여기에 답안을 작성하세요


-- ============================================================================
-- Exercise 1-5: 테이블 수정 연습
-- ============================================================================

/*
문제 11: 기존 테이블을 수정하세요.

1. instructors 테이블에 다음 컬럼을 추가:
   - linkedin_url: 링크드인 URL (최대 255자)
   - certification: 자격증 정보 (긴 텍스트)
   - rating: 평점 (소수점 2자리, 1.0 이상 5.0 이하)

2. students 테이블에 다음 컬럼을 추가:
   - emergency_contact: 비상연락처 (최대 100자)
   - address: 주소 (긴 텍스트)
   - scholarship_amount: 장학금 (소수점 2자리, 0 이상)

3. courses 테이블의 difficulty_level 컬럼에 'Expert' 레벨을 추가
*/

-- 여기에 답안을 작성하세요


/*
문제 12: 제약조건 수정
1. students 테이블의 email 컬럼을 NOT NULL로 변경
2. courses 테이블에 새로운 CHECK 제약조건 추가: price는 credits * 50000 이상이어야 함
3. instructors 테이블의 hourly_rate에 상한선 추가: 500000 이하
*/

-- 여기에 답안을 작성하세요


-- ============================================================================
-- 검증 쿼리 (답안 확인용)
-- ============================================================================

-- 생성된 테이블 목록 확인
SELECT tablename 
FROM pg_tables 
WHERE schemaname = 'public' 
  AND tablename IN ('instructors', 'students', 'courses', 'enrollments', 'assignments', 'submissions')
ORDER BY tablename;

-- 제약조건 확인
SELECT 
    tc.table_name, 
    tc.constraint_name, 
    tc.constraint_type,
    kcu.column_name
FROM information_schema.table_constraints tc
JOIN information_schema.key_column_usage kcu 
    ON tc.constraint_name = kcu.constraint_name
WHERE tc.table_schema = 'public'
  AND tc.table_name IN ('instructors', 'students', 'courses', 'enrollments', 'assignments', 'submissions')
ORDER BY tc.table_name, tc.constraint_type, tc.constraint_name;

-- 인덱스 목록 확인
SELECT 
    schemaname, 
    tablename, 
    indexname, 
    indexdef
FROM pg_indexes 
WHERE schemaname = 'public'
  AND tablename IN ('instructors', 'students', 'courses', 'enrollments', 'assignments', 'submissions')
ORDER BY tablename, indexname;

-- 뷰 목록 확인
SELECT viewname, definition 
FROM pg_views 
WHERE schemaname = 'public'
  AND viewname LIKE '%_view'
ORDER BY viewname;