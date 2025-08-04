-- Grade Management System Database Schema

-- Drop existing tables if they exist
DROP TABLE IF EXISTS grades;
DROP TABLE IF EXISTS enrollments;
DROP TABLE IF EXISTS courses;
DROP TABLE IF EXISTS students;
DROP TABLE IF EXISTS professors;
DROP TABLE IF EXISTS departments;

-- Departments table
CREATE TABLE departments (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    code VARCHAR(10) UNIQUE NOT NULL,
    name VARCHAR(100) NOT NULL,
    building VARCHAR(50),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Professors table
CREATE TABLE professors (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    professor_id VARCHAR(20) UNIQUE NOT NULL,
    name VARCHAR(100) NOT NULL,
    email VARCHAR(100) UNIQUE,
    department_id INTEGER,
    office VARCHAR(50),
    phone VARCHAR(20),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (department_id) REFERENCES departments(id)
);

-- Students table
CREATE TABLE students (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    student_id VARCHAR(20) UNIQUE NOT NULL,
    name VARCHAR(100) NOT NULL,
    email VARCHAR(100) UNIQUE,
    phone VARCHAR(20),
    enrollment_date DATE NOT NULL,
    graduation_date DATE,
    major VARCHAR(50),
    department_id INTEGER,
    gpa FLOAT DEFAULT 0.0,
    total_credits INTEGER DEFAULT 0,
    status VARCHAR(20) DEFAULT 'active', -- active, graduated, on_leave, expelled
    photo_path VARCHAR(255),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (department_id) REFERENCES departments(id)
);

-- Courses table
CREATE TABLE courses (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    course_code VARCHAR(20) UNIQUE NOT NULL,
    name VARCHAR(100) NOT NULL,
    credits INTEGER NOT NULL CHECK (credits > 0),
    professor_id INTEGER,
    department_id INTEGER,
    max_students INTEGER DEFAULT 30,
    course_type VARCHAR(20), -- required, elective, general
    description TEXT,
    syllabus_path VARCHAR(255),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (professor_id) REFERENCES professors(id),
    FOREIGN KEY (department_id) REFERENCES departments(id)
);

-- Enrollments table (student-course relationship)
CREATE TABLE enrollments (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    student_id INTEGER NOT NULL,
    course_id INTEGER NOT NULL,
    semester VARCHAR(20) NOT NULL, -- e.g., "2024-1", "2024-2"
    year INTEGER NOT NULL,
    enrollment_date DATE DEFAULT CURRENT_DATE,
    status VARCHAR(20) DEFAULT 'enrolled', -- enrolled, completed, dropped, failed
    attendance_rate FLOAT DEFAULT 100.0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (student_id) REFERENCES students(id) ON DELETE CASCADE,
    FOREIGN KEY (course_id) REFERENCES courses(id) ON DELETE CASCADE,
    UNIQUE(student_id, course_id, semester, year)
);

-- Grades table
CREATE TABLE grades (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    enrollment_id INTEGER NOT NULL UNIQUE,
    midterm_score FLOAT CHECK (midterm_score >= 0 AND midterm_score <= 100),
    final_score FLOAT CHECK (final_score >= 0 AND final_score <= 100),
    assignment_score FLOAT CHECK (assignment_score >= 0 AND assignment_score <= 100),
    attendance_score FLOAT CHECK (attendance_score >= 0 AND attendance_score <= 100),
    total_score FLOAT CHECK (total_score >= 0 AND total_score <= 100),
    letter_grade VARCHAR(2), -- A+, A0, A-, B+, B0, B-, C+, C0, C-, D+, D0, D-, F
    grade_points FLOAT, -- 4.5, 4.0, 3.5, etc.
    is_pass BOOLEAN DEFAULT FALSE,
    remarks TEXT,
    graded_at TIMESTAMP,
    graded_by INTEGER,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (enrollment_id) REFERENCES enrollments(id) ON DELETE CASCADE,
    FOREIGN KEY (graded_by) REFERENCES professors(id)
);

-- Create indexes for better performance
CREATE INDEX idx_students_student_id ON students(student_id);
CREATE INDEX idx_students_email ON students(email);
CREATE INDEX idx_students_department ON students(department_id);
CREATE INDEX idx_courses_course_code ON courses(course_code);
CREATE INDEX idx_courses_professor ON courses(professor_id);
CREATE INDEX idx_enrollments_student ON enrollments(student_id);
CREATE INDEX idx_enrollments_course ON enrollments(course_id);
CREATE INDEX idx_enrollments_semester ON enrollments(semester, year);
CREATE INDEX idx_grades_enrollment ON grades(enrollment_id);

-- Create triggers for updated_at
CREATE TRIGGER update_students_timestamp 
AFTER UPDATE ON students
BEGIN
    UPDATE students SET updated_at = CURRENT_TIMESTAMP WHERE id = NEW.id;
END;

CREATE TRIGGER update_courses_timestamp 
AFTER UPDATE ON courses
BEGIN
    UPDATE courses SET updated_at = CURRENT_TIMESTAMP WHERE id = NEW.id;
END;

CREATE TRIGGER update_enrollments_timestamp 
AFTER UPDATE ON enrollments
BEGIN
    UPDATE enrollments SET updated_at = CURRENT_TIMESTAMP WHERE id = NEW.id;
END;

CREATE TRIGGER update_grades_timestamp 
AFTER UPDATE ON grades
BEGIN
    UPDATE grades SET updated_at = CURRENT_TIMESTAMP WHERE id = NEW.id;
END;

-- Sample data insertion
INSERT INTO departments (code, name, building) VALUES 
    ('CS', 'Computer Science', 'Engineering Building'),
    ('MATH', 'Mathematics', 'Science Building'),
    ('PHYS', 'Physics', 'Science Building'),
    ('ENG', 'English', 'Liberal Arts Building');

INSERT INTO professors (professor_id, name, email, department_id, office) VALUES
    ('P001', 'Dr. Kim Jung-ho', 'kim@university.edu', 1, 'E301'),
    ('P002', 'Dr. Lee Mi-young', 'lee@university.edu', 2, 'S205'),
    ('P003', 'Dr. Park Sung-woo', 'park@university.edu', 1, 'E302');

-- Create views for common queries
CREATE VIEW student_transcript AS
SELECT 
    s.student_id,
    s.name AS student_name,
    c.course_code,
    c.name AS course_name,
    c.credits,
    e.semester,
    e.year,
    g.letter_grade,
    g.grade_points,
    g.total_score
FROM students s
JOIN enrollments e ON s.id = e.student_id
JOIN courses c ON e.course_id = c.id
LEFT JOIN grades g ON e.id = g.enrollment_id
WHERE e.status = 'completed'
ORDER BY s.student_id, e.year, e.semester;

CREATE VIEW course_statistics AS
SELECT 
    c.course_code,
    c.name AS course_name,
    e.semester,
    e.year,
    COUNT(DISTINCT e.student_id) AS enrolled_students,
    AVG(g.total_score) AS avg_score,
    MAX(g.total_score) AS max_score,
    MIN(g.total_score) AS min_score
FROM courses c
JOIN enrollments e ON c.id = e.course_id
LEFT JOIN grades g ON e.id = g.enrollment_id
GROUP BY c.id, e.semester, e.year;