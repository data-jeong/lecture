-- Chapter 03: DDL and Table Design - Solutions for Exercise 1
-- 답안: 테이블 생성과 제약조건

-- ============================================================================
-- Exercise 1-1: 기본 테이블 생성 - 답안
-- ============================================================================

-- 문제 1: 강사(instructors) 테이블 생성
CREATE TABLE instructors (
    instructor_id SERIAL PRIMARY KEY,
    first_name VARCHAR(50) NOT NULL,
    last_name VARCHAR(50) NOT NULL,
    email VARCHAR(100) UNIQUE NOT NULL,
    phone VARCHAR(20),
    bio TEXT,
    hourly_rate DECIMAL(10,2) CHECK (hourly_rate > 0),
    specialization VARCHAR(100),
    years_experience INTEGER CHECK (years_experience >= 0),
    is_active BOOLEAN DEFAULT TRUE,
    joined_date DATE DEFAULT CURRENT_DATE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 문제 2: 학생(students) 테이블 생성
CREATE TABLE students (
    student_id SERIAL PRIMARY KEY,
    student_number VARCHAR(20) UNIQUE CHECK (student_number LIKE 'STU%'),
    first_name VARCHAR(50) NOT NULL,
    last_name VARCHAR(50) NOT NULL,
    email VARCHAR(100) UNIQUE NOT NULL,
    phone VARCHAR(20),
    date_of_birth DATE,
    gender CHAR(1) CHECK (gender IN ('M', 'F')),
    grade_level INTEGER CHECK (grade_level BETWEEN 1 AND 4),
    major VARCHAR(100),
    enrollment_date DATE DEFAULT CURRENT_DATE,
    graduation_date DATE,
    gpa DECIMAL(3,2) CHECK (gpa >= 0.0 AND gpa <= 4.0),
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    -- 졸업일이 등록일보다 늦어야 함
    CONSTRAINT check_graduation_after_enrollment 
        CHECK (graduation_date IS NULL OR graduation_date > enrollment_date)
);

-- 문제 3: 코스(courses) 테이블 생성
CREATE TABLE courses (
    course_id SERIAL PRIMARY KEY,
    course_code VARCHAR(20) UNIQUE NOT NULL,
    course_name VARCHAR(255) NOT NULL,
    description TEXT,
    instructor_id INTEGER,
    credits INTEGER CHECK (credits BETWEEN 1 AND 6),
    max_students INTEGER CHECK (max_students >= 1),
    current_students INTEGER DEFAULT 0 CHECK (current_students >= 0),
    price DECIMAL(10,2) CHECK (price >= 0),
    difficulty_level VARCHAR(20) CHECK (difficulty_level IN ('Beginner', 'Intermediate', 'Advanced')),
    duration_weeks INTEGER CHECK (duration_weeks >= 1),
    start_date DATE,
    end_date DATE,
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    -- 외래키 제약조건
    CONSTRAINT fk_courses_instructor 
        FOREIGN KEY (instructor_id) REFERENCES instructors(instructor_id),
    
    -- 현재 수강인원이 최대 수강인원을 초과할 수 없음
    CONSTRAINT check_student_capacity 
        CHECK (current_students <= max_students),
    
    -- 종료일이 시작일보다 늦어야 함
    CONSTRAINT check_end_after_start 
        CHECK (end_date IS NULL OR end_date > start_date)
);

-- ============================================================================
-- Exercise 1-2: 복합 제약조건과 고급 테이블 - 답안
-- ============================================================================

-- 문제 4: 수강신청(enrollments) 테이블 생성
CREATE TABLE enrollments (
    enrollment_id SERIAL PRIMARY KEY,
    student_id INTEGER NOT NULL,
    course_id INTEGER NOT NULL,
    enrollment_date DATE DEFAULT CURRENT_DATE,
    status VARCHAR(20) DEFAULT 'enrolled' CHECK (
        status IN ('enrolled', 'completed', 'dropped', 'failed')
    ),
    grade VARCHAR(2) CHECK (
        grade IN ('A+', 'A', 'B+', 'B', 'C+', 'C', 'D+', 'D', 'F')
    ),
    final_score DECIMAL(5,2) CHECK (final_score >= 0 AND final_score <= 100),
    completion_date DATE,
    payment_status VARCHAR(20) DEFAULT 'pending' CHECK (
        payment_status IN ('pending', 'paid', 'refunded')
    ),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    -- 외래키 제약조건
    CONSTRAINT fk_enrollments_student 
        FOREIGN KEY (student_id) REFERENCES students(student_id),
    CONSTRAINT fk_enrollments_course 
        FOREIGN KEY (course_id) REFERENCES courses(course_id),
    
    -- 같은 학생이 같은 코스에 중복 수강신청할 수 없음
    CONSTRAINT uq_student_course UNIQUE (student_id, course_id),
    
    -- 수료일이 수강신청일보다 늦어야 함
    CONSTRAINT check_completion_after_enrollment 
        CHECK (completion_date IS NULL OR completion_date >= enrollment_date)
);

-- 문제 5: 과제(assignments) 테이블 생성
CREATE TABLE assignments (
    assignment_id SERIAL PRIMARY KEY,
    course_id INTEGER NOT NULL,
    title VARCHAR(255) NOT NULL,
    description TEXT,
    type VARCHAR(20) CHECK (type IN ('homework', 'quiz', 'project', 'exam')),
    max_score DECIMAL(5,2) CHECK (max_score > 0),
    weight DECIMAL(5,4) CHECK (weight >= 0 AND weight <= 1),
    due_date TIMESTAMP,
    is_group_work BOOLEAN DEFAULT FALSE,
    submission_format VARCHAR(20) CHECK (
        submission_format IN ('online', 'offline', 'presentation')
    ),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    -- 외래키 제약조건
    CONSTRAINT fk_assignments_course 
        FOREIGN KEY (course_id) REFERENCES courses(course_id)
);

-- 문제 6: 과제 제출(submissions) 테이블 생성
CREATE TABLE submissions (
    submission_id SERIAL PRIMARY KEY,
    assignment_id INTEGER NOT NULL,
    student_id INTEGER NOT NULL,
    submitted_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    content TEXT,
    file_path VARCHAR(500),
    score DECIMAL(5,2) CHECK (score >= 0),
    feedback TEXT,
    graded_at TIMESTAMP,
    graded_by INTEGER,
    is_late BOOLEAN DEFAULT FALSE,
    attempt_number INTEGER DEFAULT 1 CHECK (attempt_number >= 1),
    
    -- 외래키 제약조건
    CONSTRAINT fk_submissions_assignment 
        FOREIGN KEY (assignment_id) REFERENCES assignments(assignment_id),
    CONSTRAINT fk_submissions_student 
        FOREIGN KEY (student_id) REFERENCES students(student_id),
    CONSTRAINT fk_submissions_grader 
        FOREIGN KEY (graded_by) REFERENCES instructors(instructor_id),
    
    -- 같은 학생이 같은 과제에 대해 시도 번호가 고유해야 함
    CONSTRAINT uq_student_assignment_attempt 
        UNIQUE (student_id, assignment_id, attempt_number)
);

-- ============================================================================
-- Exercise 1-3: 인덱스 생성 - 답안
-- ============================================================================

-- 강사 관련 인덱스
CREATE INDEX idx_instructors_email ON instructors (email);
CREATE INDEX idx_instructors_active ON instructors (is_active);
CREATE INDEX idx_instructors_specialization ON instructors (specialization);

-- 학생 관련 인덱스
CREATE INDEX idx_students_student_number ON students (student_number);
CREATE INDEX idx_students_email ON students (email);
CREATE INDEX idx_students_active ON students (is_active);
CREATE INDEX idx_students_major ON students (major);
CREATE INDEX idx_students_grade_level ON students (grade_level);

-- 코스 관련 인덱스
CREATE INDEX idx_courses_instructor ON courses (instructor_id);
CREATE INDEX idx_courses_active ON courses (is_active);
CREATE INDEX idx_courses_difficulty ON courses (difficulty_level);
CREATE INDEX idx_courses_start_date ON courses (start_date);
CREATE INDEX idx_courses_code ON courses (course_code);

-- 수강신청 관련 인덱스
CREATE INDEX idx_enrollments_student ON enrollments (student_id);
CREATE INDEX idx_enrollments_course ON enrollments (course_id);
CREATE INDEX idx_enrollments_status ON enrollments (status);
CREATE INDEX idx_enrollments_student_status ON enrollments (student_id, status);
CREATE INDEX idx_enrollments_course_status ON enrollments (course_id, status);

-- 과제 관련 인덱스
CREATE INDEX idx_assignments_course ON assignments (course_id);
CREATE INDEX idx_assignments_type ON assignments (type);
CREATE INDEX idx_assignments_due_date ON assignments (due_date);

-- 과제 제출 관련 인덱스
CREATE INDEX idx_submissions_assignment ON submissions (assignment_id);
CREATE INDEX idx_submissions_student ON submissions (student_id);
CREATE INDEX idx_submissions_graded_by ON submissions (graded_by);
CREATE INDEX idx_submissions_submitted_at ON submissions (submitted_at);

-- 복합 인덱스 (자주 함께 사용되는 컬럼들)
CREATE INDEX idx_enrollments_student_course ON enrollments (student_id, course_id);
CREATE INDEX idx_submissions_assignment_student ON submissions (assignment_id, student_id);

-- ============================================================================
-- Exercise 1-4: 뷰 생성 - 답안
-- ============================================================================

-- 문제 8: instructor_courses_view
CREATE VIEW instructor_courses_view AS
SELECT 
    i.instructor_id,
    i.first_name || ' ' || i.last_name AS instructor_name,
    i.email AS instructor_email,
    i.specialization,
    c.course_id,
    c.course_code,
    c.course_name,
    c.credits,
    c.price,
    c.current_students,
    c.max_students,
    c.difficulty_level,
    c.start_date,
    c.end_date,
    c.is_active AS course_active,
    ROUND((c.current_students::DECIMAL / c.max_students) * 100, 2) AS enrollment_percentage
FROM instructors i
JOIN courses c ON i.instructor_id = c.instructor_id
WHERE i.is_active = TRUE;

-- 문제 9: student_progress_view
CREATE VIEW student_progress_view AS
SELECT 
    s.student_id,
    s.student_number,
    s.first_name || ' ' || s.last_name AS student_name,
    s.email,
    s.major,
    COUNT(CASE WHEN e.status = 'enrolled' THEN 1 END) AS courses_in_progress,
    COUNT(CASE WHEN e.status = 'completed' THEN 1 END) AS courses_completed,
    COUNT(CASE WHEN e.status = 'dropped' THEN 1 END) AS courses_dropped,
    COUNT(CASE WHEN e.status = 'failed' THEN 1 END) AS courses_failed,
    -- GPA 계산 (A+ = 4.5, A = 4.0, B+ = 3.5, ..., F = 0.0)
    ROUND(AVG(
        CASE e.grade
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
    ), 2) AS calculated_gpa,
    SUM(CASE WHEN e.status = 'completed' THEN c.credits ELSE 0 END) AS total_credits_earned
FROM students s
LEFT JOIN enrollments e ON s.student_id = e.student_id
LEFT JOIN courses c ON e.course_id = c.course_id
WHERE s.is_active = TRUE
GROUP BY s.student_id, s.student_number, s.first_name, s.last_name, s.email, s.major;

-- 문제 10: course_statistics_view
CREATE VIEW course_statistics_view AS
SELECT 
    c.course_id,
    c.course_code,
    c.course_name,
    i.first_name || ' ' || i.last_name AS instructor_name,
    COUNT(e.enrollment_id) AS total_enrollments,
    COUNT(CASE WHEN e.status = 'completed' THEN 1 END) AS completed_count,
    COUNT(CASE WHEN e.status = 'dropped' THEN 1 END) AS dropped_count,
    COUNT(CASE WHEN e.status = 'failed' THEN 1 END) AS failed_count,
    ROUND(AVG(e.final_score), 2) AS average_score,
    ROUND(
        (COUNT(CASE WHEN e.status = 'completed' THEN 1 END)::DECIMAL / 
         NULLIF(COUNT(e.enrollment_id), 0)) * 100, 2
    ) AS completion_rate_percentage,
    c.price,
    c.credits,
    c.difficulty_level
FROM courses c
LEFT JOIN instructors i ON c.instructor_id = i.instructor_id
LEFT JOIN enrollments e ON c.course_id = e.course_id
WHERE c.is_active = TRUE
GROUP BY c.course_id, c.course_code, c.course_name, 
         i.first_name, i.last_name, c.price, c.credits, c.difficulty_level;

-- ============================================================================
-- Exercise 1-5: 테이블 수정 연습 - 답안
-- ============================================================================

-- 문제 11: 컬럼 추가
-- instructors 테이블에 컬럼 추가
ALTER TABLE instructors 
ADD COLUMN linkedin_url VARCHAR(255),
ADD COLUMN certification TEXT,
ADD COLUMN rating DECIMAL(3,2) CHECK (rating >= 1.0 AND rating <= 5.0);

-- students 테이블에 컬럼 추가
ALTER TABLE students 
ADD COLUMN emergency_contact VARCHAR(100),
ADD COLUMN address TEXT,
ADD COLUMN scholarship_amount DECIMAL(10,2) CHECK (scholarship_amount >= 0);

-- courses 테이블의 difficulty_level 제약조건 수정
ALTER TABLE courses 
DROP CONSTRAINT IF EXISTS courses_difficulty_level_check;

ALTER TABLE courses 
ADD CONSTRAINT courses_difficulty_level_check 
    CHECK (difficulty_level IN ('Beginner', 'Intermediate', 'Advanced', 'Expert'));

-- 문제 12: 제약조건 수정
-- students 테이블의 email 컬럼을 NOT NULL로 변경 (이미 NOT NULL이므로 확인)
-- 이미 NOT NULL 제약조건이 있으므로 생략

-- courses 테이블에 새로운 CHECK 제약조건 추가
ALTER TABLE courses 
ADD CONSTRAINT check_price_vs_credits 
    CHECK (price >= credits * 50000);

-- instructors 테이블의 hourly_rate 제약조건 수정
ALTER TABLE instructors 
DROP CONSTRAINT IF EXISTS instructors_hourly_rate_check;

ALTER TABLE instructors 
ADD CONSTRAINT instructors_hourly_rate_check 
    CHECK (hourly_rate > 0 AND hourly_rate <= 500000);

-- ============================================================================
-- 추가 유용한 기능들
-- ============================================================================

-- 자동 업데이트 트리거 함수
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ language 'plpgsql';

-- courses 테이블의 updated_at 자동 업데이트 트리거
CREATE TRIGGER update_courses_updated_at 
    BEFORE UPDATE ON courses 
    FOR EACH ROW 
    EXECUTE FUNCTION update_updated_at_column();

-- assignments 테이블의 updated_at 자동 업데이트 트리거
CREATE TRIGGER update_assignments_updated_at 
    BEFORE UPDATE ON assignments 
    FOR EACH ROW 
    EXECUTE FUNCTION update_updated_at_column();

-- 학번 자동 생성을 위한 시퀀스와 함수
CREATE SEQUENCE student_number_seq START WITH 1 INCREMENT BY 1;

CREATE OR REPLACE FUNCTION generate_student_number()
RETURNS TRIGGER AS $$
BEGIN
    IF NEW.student_number IS NULL THEN
        NEW.student_number := 'STU' || LPAD(nextval('student_number_seq')::TEXT, 6, '0');
    END IF;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- 학생 테이블에 학번 자동 생성 트리거
CREATE TRIGGER generate_student_number_trigger
    BEFORE INSERT ON students
    FOR EACH ROW
    EXECUTE FUNCTION generate_student_number();

-- 샘플 데이터 삽입 (테스트용)
INSERT INTO instructors (first_name, last_name, email, specialization, hourly_rate, years_experience) VALUES
('김', '교수', 'kim.prof@university.edu', 'Computer Science', 80000, 10),
('이', '박사', 'lee.dr@university.edu', 'Mathematics', 75000, 8),
('박', '강사', 'park.instructor@university.edu', 'Physics', 60000, 5);

INSERT INTO students (first_name, last_name, email, major, grade_level) VALUES
('홍', '길동', 'hong.gd@student.edu', 'Computer Science', 2),
('김', '영희', 'kim.yh@student.edu', 'Mathematics', 3),
('이', '철수', 'lee.cs@student.edu', 'Physics', 1);

INSERT INTO courses (course_code, course_name, instructor_id, credits, max_students, price, difficulty_level, duration_weeks, start_date, end_date) VALUES
('CS101', 'Introduction to Programming', 1, 3, 30, 300000, 'Beginner', 16, '2024-03-01', '2024-06-15'),
('MATH201', 'Calculus II', 2, 4, 25, 400000, 'Intermediate', 16, '2024-03-01', '2024-06-15'),
('PHYS101', 'General Physics', 3, 3, 35, 300000, 'Beginner', 16, '2024-03-01', '2024-06-15');

-- 검증을 위한 최종 쿼리
SELECT 'Tables, indexes, views, and constraints created successfully!' AS status;