from datetime import datetime
from typing import Optional, List

from sqlalchemy import (
    Column, Integer, String, Float, Boolean, DateTime, Date, Text,
    ForeignKey, UniqueConstraint, CheckConstraint, Index
)
from sqlalchemy.orm import relationship, declarative_base
from sqlalchemy.sql import func

Base = declarative_base()


class Department(Base):
    __tablename__ = "departments"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    code = Column(String(10), unique=True, nullable=False)
    name = Column(String(100), nullable=False)
    building = Column(String(50))
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())
    
    # Relationships
    professors = relationship("Professor", back_populates="department")
    students = relationship("Student", back_populates="department")
    courses = relationship("Course", back_populates="department")
    
    def __repr__(self):
        return f"<Department(code='{self.code}', name='{self.name}')>"


class Professor(Base):
    __tablename__ = "professors"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    professor_id = Column(String(20), unique=True, nullable=False)
    name = Column(String(100), nullable=False)
    email = Column(String(100), unique=True)
    department_id = Column(Integer, ForeignKey("departments.id"))
    office = Column(String(50))
    phone = Column(String(20))
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())
    
    # Relationships
    department = relationship("Department", back_populates="professors")
    courses = relationship("Course", back_populates="professor")
    graded_grades = relationship("Grade", back_populates="graded_by_professor")
    
    def __repr__(self):
        return f"<Professor(professor_id='{self.professor_id}', name='{self.name}')>"


class Student(Base):
    __tablename__ = "students"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    student_id = Column(String(20), unique=True, nullable=False, index=True)
    name = Column(String(100), nullable=False)
    email = Column(String(100), unique=True, index=True)
    phone = Column(String(20))
    enrollment_date = Column(Date, nullable=False)
    graduation_date = Column(Date)
    major = Column(String(50))
    department_id = Column(Integer, ForeignKey("departments.id"), index=True)
    gpa = Column(Float, default=0.0)
    total_credits = Column(Integer, default=0)
    status = Column(String(20), default="active")  # active, graduated, on_leave, expelled
    photo_path = Column(String(255))
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())
    
    # Relationships
    department = relationship("Department", back_populates="students")
    enrollments = relationship("Enrollment", back_populates="student", cascade="all, delete-orphan")
    
    def __repr__(self):
        return f"<Student(student_id='{self.student_id}', name='{self.name}')>"
    
    def calculate_gpa(self) -> float:
        """Calculate student's GPA based on completed courses"""
        completed_enrollments = [e for e in self.enrollments if e.status == "completed"]
        
        if not completed_enrollments:
            return 0.0
            
        total_points = 0
        total_credits = 0
        
        for enrollment in completed_enrollments:
            if enrollment.grade and enrollment.grade.grade_points is not None:
                credits = enrollment.course.credits
                total_points += enrollment.grade.grade_points * credits
                total_credits += credits
                
        if total_credits == 0:
            return 0.0
            
        return round(total_points / total_credits, 2)


class Course(Base):
    __tablename__ = "courses"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    course_code = Column(String(20), unique=True, nullable=False, index=True)
    name = Column(String(100), nullable=False)
    credits = Column(Integer, nullable=False)
    professor_id = Column(Integer, ForeignKey("professors.id"), index=True)
    department_id = Column(Integer, ForeignKey("departments.id"))
    max_students = Column(Integer, default=30)
    course_type = Column(String(20))  # required, elective, general
    description = Column(Text)
    syllabus_path = Column(String(255))
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())
    
    # Constraints
    __table_args__ = (
        CheckConstraint("credits > 0", name="check_credits_positive"),
    )
    
    # Relationships
    professor = relationship("Professor", back_populates="courses")
    department = relationship("Department", back_populates="courses")
    enrollments = relationship("Enrollment", back_populates="course", cascade="all, delete-orphan")
    
    def __repr__(self):
        return f"<Course(course_code='{self.course_code}', name='{self.name}')>"
    
    def get_enrolled_count(self, semester: str, year: int) -> int:
        """Get number of enrolled students for a specific semester"""
        return len([e for e in self.enrollments 
                   if e.semester == semester and e.year == year and e.status == "enrolled"])


class Enrollment(Base):
    __tablename__ = "enrollments"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    student_id = Column(Integer, ForeignKey("students.id", ondelete="CASCADE"), 
                       nullable=False, index=True)
    course_id = Column(Integer, ForeignKey("courses.id", ondelete="CASCADE"), 
                      nullable=False, index=True)
    semester = Column(String(20), nullable=False)  # e.g., "2024-1", "2024-2"
    year = Column(Integer, nullable=False)
    enrollment_date = Column(Date, default=func.current_date())
    status = Column(String(20), default="enrolled")  # enrolled, completed, dropped, failed
    attendance_rate = Column(Float, default=100.0)
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())
    
    # Constraints
    __table_args__ = (
        UniqueConstraint("student_id", "course_id", "semester", "year", 
                        name="unique_enrollment"),
        Index("idx_enrollments_semester", "semester", "year"),
    )
    
    # Relationships
    student = relationship("Student", back_populates="enrollments")
    course = relationship("Course", back_populates="enrollments")
    grade = relationship("Grade", back_populates="enrollment", uselist=False, 
                        cascade="all, delete-orphan")
    
    def __repr__(self):
        return f"<Enrollment(student_id={self.student_id}, course_id={self.course_id}, semester='{self.semester}')>"


class Grade(Base):
    __tablename__ = "grades"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    enrollment_id = Column(Integer, ForeignKey("enrollments.id", ondelete="CASCADE"), 
                          unique=True, nullable=False, index=True)
    midterm_score = Column(Float)
    final_score = Column(Float)
    assignment_score = Column(Float)
    attendance_score = Column(Float)
    total_score = Column(Float)
    letter_grade = Column(String(2))  # A+, A0, A-, B+, B0, B-, C+, C0, C-, D+, D0, D-, F
    grade_points = Column(Float)  # 4.5, 4.0, 3.5, etc.
    is_pass = Column(Boolean, default=False)
    remarks = Column(Text)
    graded_at = Column(DateTime)
    graded_by = Column(Integer, ForeignKey("professors.id"))
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())
    
    # Constraints
    __table_args__ = (
        CheckConstraint("midterm_score >= 0 AND midterm_score <= 100", 
                       name="check_midterm_score"),
        CheckConstraint("final_score >= 0 AND final_score <= 100", 
                       name="check_final_score"),
        CheckConstraint("assignment_score >= 0 AND assignment_score <= 100", 
                       name="check_assignment_score"),
        CheckConstraint("attendance_score >= 0 AND attendance_score <= 100", 
                       name="check_attendance_score"),
        CheckConstraint("total_score >= 0 AND total_score <= 100", 
                       name="check_total_score"),
    )
    
    # Relationships
    enrollment = relationship("Enrollment", back_populates="grade")
    graded_by_professor = relationship("Professor", back_populates="graded_grades")
    
    def __repr__(self):
        return f"<Grade(enrollment_id={self.enrollment_id}, letter_grade='{self.letter_grade}', total_score={self.total_score})>"
    
    def calculate_total_score(self, weights: dict = None) -> float:
        """Calculate total score based on component scores and weights"""
        if weights is None:
            weights = {
                "midterm": 0.3,
                "final": 0.4,
                "assignment": 0.2,
                "attendance": 0.1
            }
            
        total = 0
        if self.midterm_score is not None:
            total += self.midterm_score * weights.get("midterm", 0)
        if self.final_score is not None:
            total += self.final_score * weights.get("final", 0)
        if self.assignment_score is not None:
            total += self.assignment_score * weights.get("assignment", 0)
        if self.attendance_score is not None:
            total += self.attendance_score * weights.get("attendance", 0)
            
        return round(total, 2)
    
    @staticmethod
    def score_to_letter_grade(score: float) -> tuple[str, float]:
        """Convert numerical score to letter grade and grade points"""
        if score >= 95:
            return "A+", 4.5
        elif score >= 90:
            return "A0", 4.0
        elif score >= 85:
            return "A-", 3.5
        elif score >= 80:
            return "B+", 3.0
        elif score >= 75:
            return "B0", 2.5
        elif score >= 70:
            return "B-", 2.0
        elif score >= 65:
            return "C+", 1.5
        elif score >= 60:
            return "C0", 1.0
        elif score >= 55:
            return "C-", 0.5
        else:
            return "F", 0.0