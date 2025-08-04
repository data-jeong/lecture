import pytest
import tempfile
from pathlib import Path
from datetime import date, datetime
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from grade_system.database.connection import DatabaseConnection, init_database
from grade_system.database.models import Base, Student, Course, Enrollment, Grade, Department
from grade_system.services import StudentService, CourseService, GradeService
from grade_system.utils.calculators import GradeCalculator


@pytest.fixture
def test_db():
    """Create a test database"""
    # Use in-memory database for tests
    db = DatabaseConnection("sqlite:///:memory:")
    db.create_tables()
    
    # Add test data
    with db.session_scope() as session:
        # Add departments
        dept_cs = Department(code="CS", name="Computer Science", building="Engineering")
        dept_math = Department(code="MATH", name="Mathematics", building="Science")
        session.add_all([dept_cs, dept_math])
        session.commit()
        
    yield db
    
    # Cleanup
    db.close()


@pytest.fixture
def session(test_db):
    """Get a test session"""
    with test_db.session_scope() as session:
        yield session


class TestModels:
    def test_student_creation(self, session):
        """Test creating a student"""
        dept = session.query(Department).filter_by(code="CS").first()
        
        student = Student(
            student_id="2024000001",
            name="John Doe",
            email="john@example.com",
            enrollment_date=date.today(),
            major="Computer Science",
            department_id=dept.id
        )
        
        session.add(student)
        session.commit()
        
        # Verify
        saved_student = session.query(Student).filter_by(student_id="2024000001").first()
        assert saved_student is not None
        assert saved_student.name == "John Doe"
        assert saved_student.email == "john@example.com"
        
    def test_course_creation(self, session):
        """Test creating a course"""
        dept = session.query(Department).filter_by(code="CS").first()
        
        course = Course(
            course_code="CS101",
            name="Introduction to Programming",
            credits=3,
            department_id=dept.id,
            max_students=30
        )
        
        session.add(course)
        session.commit()
        
        # Verify
        saved_course = session.query(Course).filter_by(course_code="CS101").first()
        assert saved_course is not None
        assert saved_course.name == "Introduction to Programming"
        assert saved_course.credits == 3
        
    def test_enrollment(self, session):
        """Test enrollment relationship"""
        dept = session.query(Department).filter_by(code="CS").first()
        
        # Create student and course
        student = Student(
            student_id="2024000002",
            name="Jane Smith",
            email="jane@example.com",
            enrollment_date=date.today(),
            department_id=dept.id
        )
        
        course = Course(
            course_code="CS102",
            name="Data Structures",
            credits=4,
            department_id=dept.id
        )
        
        session.add_all([student, course])
        session.commit()
        
        # Create enrollment
        enrollment = Enrollment(
            student_id=student.id,
            course_id=course.id,
            semester="2024-1",
            year=2024
        )
        
        session.add(enrollment)
        session.commit()
        
        # Verify relationships
        assert len(student.enrollments) == 1
        assert student.enrollments[0].course == course
        assert len(course.enrollments) == 1
        assert course.enrollments[0].student == student
        
    def test_grade_calculation(self, session):
        """Test grade calculation"""
        grade = Grade(
            enrollment_id=1,
            midterm_score=85,
            final_score=90,
            assignment_score=88,
            attendance_score=95
        )
        
        total_score = grade.calculate_total_score()
        assert total_score == 88.5  # (85*0.3 + 90*0.4 + 88*0.2 + 95*0.1)
        
        letter_grade, grade_points = Grade.score_to_letter_grade(total_score)
        assert letter_grade == "A-"
        assert grade_points == 3.5


class TestStudentService:
    def test_create_student(self, session):
        """Test creating student through service"""
        service = StudentService(session)
        dept = session.query(Department).filter_by(code="CS").first()
        
        student_data = {
            "student_id": "2024000003",
            "name": "Bob Johnson",
            "email": "bob@example.com",
            "enrollment_date": date.today(),
            "major": "Computer Science",
            "department_id": dept.id
        }
        
        student = service.create_student(student_data)
        
        assert student is not None
        assert student.student_id == "2024000003"
        assert student.name == "Bob Johnson"
        
    def test_update_student(self, session):
        """Test updating student"""
        service = StudentService(session)
        dept = session.query(Department).filter_by(code="CS").first()
        
        # Create student
        student_data = {
            "student_id": "2024000004",
            "name": "Alice Brown",
            "email": "alice@example.com",
            "enrollment_date": date.today(),
            "department_id": dept.id
        }
        
        student = service.create_student(student_data)
        
        # Update student
        updated = service.update_student("2024000004", {
            "major": "Mathematics",
            "email": "alice.brown@example.com"
        })
        
        assert updated.major == "Mathematics"
        assert updated.email == "alice.brown@example.com"
        
    def test_search_students(self, session):
        """Test searching students"""
        service = StudentService(session)
        dept = session.query(Department).filter_by(code="CS").first()
        
        # Create multiple students
        for i in range(3):
            service.create_student({
                "student_id": f"202400010{i}",
                "name": f"Student {i}",
                "email": f"student{i}@example.com",
                "enrollment_date": date.today(),
                "major": "Computer Science" if i < 2 else "Mathematics",
                "department_id": dept.id
            })
            
        # Search by major
        cs_students = service.search_students(major="Computer Science")
        assert len(cs_students) == 2
        
        # Search by name
        student_1 = service.search_students(name="Student 1")
        assert len(student_1) == 1
        assert student_1[0].name == "Student 1"


class TestCourseService:
    def test_enroll_student(self, session):
        """Test enrolling student in course"""
        student_service = StudentService(session)
        course_service = CourseService(session)
        dept = session.query(Department).filter_by(code="CS").first()
        
        # Create student
        student = student_service.create_student({
            "student_id": "2024000200",
            "name": "Test Student",
            "email": "test@example.com",
            "enrollment_date": date.today(),
            "department_id": dept.id
        })
        
        # Create course
        course = course_service.create_course({
            "course_code": "CS201",
            "name": "Algorithms",
            "credits": 3,
            "department_id": dept.id,
            "max_students": 2
        })
        
        # Enroll student
        enrollment = course_service.enroll_student(
            student.id, course.id, "2024-1", 2024
        )
        
        assert enrollment is not None
        assert enrollment.student_id == student.id
        assert enrollment.course_id == course.id
        assert enrollment.status == "enrolled"
        
    def test_course_capacity(self, session):
        """Test course capacity limit"""
        student_service = StudentService(session)
        course_service = CourseService(session)
        dept = session.query(Department).filter_by(code="CS").first()
        
        # Create course with max 2 students
        course = course_service.create_course({
            "course_code": "CS202",
            "name": "Limited Course",
            "credits": 3,
            "department_id": dept.id,
            "max_students": 2
        })
        
        # Create and enroll 2 students
        for i in range(2):
            student = student_service.create_student({
                "student_id": f"202400030{i}",
                "name": f"Student {i}",
                "email": f"s{i}@example.com",
                "enrollment_date": date.today(),
                "department_id": dept.id
            })
            
            course_service.enroll_student(
                student.id, course.id, "2024-1", 2024
            )
            
        # Try to enroll third student - should fail
        student3 = student_service.create_student({
            "student_id": "2024000302",
            "name": "Student 3",
            "email": "s3@example.com",
            "enrollment_date": date.today(),
            "department_id": dept.id
        })
        
        with pytest.raises(ValueError, match="Course is full"):
            course_service.enroll_student(
                student3.id, course.id, "2024-1", 2024
            )


class TestGradeService:
    def test_add_grade(self, session):
        """Test adding grades"""
        student_service = StudentService(session)
        course_service = CourseService(session)
        grade_service = GradeService(session)
        dept = session.query(Department).filter_by(code="CS").first()
        
        # Setup student and course
        student = student_service.create_student({
            "student_id": "2024000400",
            "name": "Grade Test",
            "email": "grade@example.com",
            "enrollment_date": date.today(),
            "department_id": dept.id
        })
        
        course = course_service.create_course({
            "course_code": "CS301",
            "name": "Test Course",
            "credits": 3,
            "department_id": dept.id
        })
        
        enrollment = course_service.enroll_student(
            student.id, course.id, "2024-1", 2024
        )
        
        # Add grade
        grade = grade_service.add_grade(enrollment.id, {
            "midterm_score": 85,
            "final_score": 90,
            "assignment_score": 88,
            "attendance_score": 95
        })
        
        assert grade is not None
        assert grade.total_score == 88.5
        assert grade.letter_grade == "A-"
        assert grade.grade_points == 3.5
        assert grade.is_pass is True
        
    def test_grade_statistics(self, session):
        """Test calculating grade statistics"""
        # Setup is similar to previous test
        # ... (setup code)
        
        grade_service = GradeService(session)
        
        # Test would add multiple grades and calculate statistics
        # This is a placeholder for the actual implementation


class TestCalculators:
    def test_grade_calculator(self):
        """Test grade calculation utilities"""
        calc = GradeCalculator()
        
        # Test total score calculation
        total = calc.calculate_total_score(
            midterm=80,
            final=85,
            assignment=90,
            attendance=100
        )
        assert total == 86.0  # (80*0.3 + 85*0.4 + 90*0.2 + 100*0.1)
        
        # Test letter grade conversion
        letter, points = calc.score_to_letter_grade(86.0)
        assert letter == "A-"
        assert points == 3.5
        
        # Test GPA calculation
        grades = [(4.0, 3), (3.5, 4), (3.0, 3)]  # (grade_points, credits)
        gpa = calc.calculate_gpa(grades)
        assert gpa == 3.5  # (4.0*3 + 3.5*4 + 3.0*3) / 10
        
    def test_grade_distribution(self):
        """Test grade distribution calculation"""
        calc = GradeCalculator()
        
        scores = [95, 88, 76, 82, 91, 67, 58, 73, 85, 90]
        distribution = calc.calculate_grade_distribution(scores)
        
        assert distribution["A+"] == 1  # 95
        assert distribution["A0"] == 2  # 91, 90
        assert distribution["B+"] == 1  # 82
        assert distribution["B0"] == 1  # 76
        assert distribution["C+"] == 1  # 67
        assert distribution["C-"] == 1  # 58


if __name__ == "__main__":
    pytest.main([__file__, "-v"])