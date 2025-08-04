from typing import List, Optional, Dict, Any
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from sqlalchemy import and_, or_, func

from ..models import Course, Professor, Department, Enrollment, Student


class CourseService:
    """Service class for course-related operations"""
    
    def __init__(self, session: Session):
        self.session = session
        
    def create_course(self, course_data: Dict[str, Any]) -> Course:
        """Create a new course"""
        # Check if course already exists
        existing = self.session.query(Course).filter_by(
            course_code=course_data.get("course_code")
        ).first()
        
        if existing:
            raise ValueError(f"Course with code {course_data['course_code']} already exists")
            
        # Create course
        course = Course(**course_data)
        self.session.add(course)
        
        try:
            self.session.commit()
            self.session.refresh(course)
            return course
        except IntegrityError as e:
            self.session.rollback()
            raise ValueError(f"Failed to create course: {str(e)}")
            
    def get_course(self, course_code: str) -> Optional[Course]:
        """Get course by course code"""
        return self.session.query(Course).filter_by(course_code=course_code).first()
        
    def get_course_by_id(self, id: int) -> Optional[Course]:
        """Get course by database ID"""
        return self.session.get(Course, id)
        
    def update_course(self, course_code: str, update_data: Dict[str, Any]) -> Optional[Course]:
        """Update course information"""
        course = self.get_course(course_code)
        
        if not course:
            return None
            
        # Update fields
        for key, value in update_data.items():
            if hasattr(course, key) and key not in ["id", "course_code", "created_at"]:
                setattr(course, key, value)
                
        try:
            self.session.commit()
            self.session.refresh(course)
            return course
        except IntegrityError as e:
            self.session.rollback()
            raise ValueError(f"Failed to update course: {str(e)}")
            
    def delete_course(self, course_code: str) -> bool:
        """Delete a course"""
        course = self.get_course(course_code)
        
        if not course:
            return False
            
        # Check if course has enrollments
        enrollment_count = self.session.query(Enrollment).filter(
            Enrollment.course_id == course.id
        ).count()
        
        if enrollment_count > 0:
            raise ValueError("Cannot delete course with existing enrollments")
            
        self.session.delete(course)
        self.session.commit()
        return True
        
    def search_courses(self,
                      name: Optional[str] = None,
                      professor_name: Optional[str] = None,
                      department_code: Optional[str] = None,
                      course_type: Optional[str] = None) -> List[Course]:
        """Search courses with filters"""
        query = self.session.query(Course)
        
        if name:
            query = query.filter(Course.name.ilike(f"%{name}%"))
        if course_type:
            query = query.filter(Course.course_type == course_type)
        if professor_name:
            query = query.join(Professor).filter(
                Professor.name.ilike(f"%{professor_name}%")
            )
        if department_code:
            query = query.join(Department).filter(Department.code == department_code)
            
        return query.all()
        
    def get_all_courses(self,
                       limit: Optional[int] = None,
                       offset: Optional[int] = None) -> List[Course]:
        """Get all courses with pagination"""
        query = self.session.query(Course).order_by(Course.course_code)
        
        if offset:
            query = query.offset(offset)
        if limit:
            query = query.limit(limit)
            
        return query.all()
        
    def enroll_student(self, student_id: int, course_id: int,
                      semester: str, year: int) -> Enrollment:
        """Enroll a student in a course"""
        # Check if student exists
        student = self.session.get(Student, student_id)
        if not student:
            raise ValueError(f"Student with ID {student_id} not found")
            
        # Check if course exists
        course = self.session.get(Course, course_id)
        if not course:
            raise ValueError(f"Course with ID {course_id} not found")
            
        # Check if already enrolled
        existing = self.session.query(Enrollment).filter(
            and_(
                Enrollment.student_id == student_id,
                Enrollment.course_id == course_id,
                Enrollment.semester == semester,
                Enrollment.year == year
            )
        ).first()
        
        if existing:
            raise ValueError("Student is already enrolled in this course for this semester")
            
        # Check if course is full
        enrolled_count = self.session.query(Enrollment).filter(
            and_(
                Enrollment.course_id == course_id,
                Enrollment.semester == semester,
                Enrollment.year == year,
                Enrollment.status == "enrolled"
            )
        ).count()
        
        if enrolled_count >= course.max_students:
            raise ValueError("Course is full")
            
        # Create enrollment
        enrollment = Enrollment(
            student_id=student_id,
            course_id=course_id,
            semester=semester,
            year=year,
            status="enrolled"
        )
        
        self.session.add(enrollment)
        
        try:
            self.session.commit()
            self.session.refresh(enrollment)
            return enrollment
        except IntegrityError as e:
            self.session.rollback()
            raise ValueError(f"Failed to enroll student: {str(e)}")
            
    def drop_enrollment(self, student_id: int, course_id: int,
                       semester: str, year: int) -> bool:
        """Drop a student from a course"""
        enrollment = self.session.query(Enrollment).filter(
            and_(
                Enrollment.student_id == student_id,
                Enrollment.course_id == course_id,
                Enrollment.semester == semester,
                Enrollment.year == year
            )
        ).first()
        
        if not enrollment:
            return False
            
        if enrollment.status != "enrolled":
            raise ValueError("Can only drop enrolled courses")
            
        enrollment.status = "dropped"
        self.session.commit()
        return True
        
    def get_course_enrollments(self, course_id: int,
                              semester: str, year: int) -> List[Enrollment]:
        """Get all enrollments for a course"""
        return self.session.query(Enrollment).filter(
            and_(
                Enrollment.course_id == course_id,
                Enrollment.semester == semester,
                Enrollment.year == year
            )
        ).all()
        
    def get_course_students(self, course_id: int,
                          semester: str, year: int) -> List[Student]:
        """Get all students enrolled in a course"""
        enrollments = self.get_course_enrollments(course_id, semester, year)
        return [e.student for e in enrollments if e.status == "enrolled"]
        
    def get_available_courses(self, semester: str, year: int,
                            student_id: Optional[int] = None) -> List[Course]:
        """Get courses available for enrollment"""
        # Get all courses
        query = self.session.query(Course)
        
        # If student specified, exclude already enrolled courses
        if student_id:
            enrolled_course_ids = self.session.query(Enrollment.course_id).filter(
                and_(
                    Enrollment.student_id == student_id,
                    Enrollment.semester == semester,
                    Enrollment.year == year
                )
            ).subquery()
            
            query = query.filter(~Course.id.in_(enrolled_course_ids))
            
        courses = query.all()
        
        # Filter courses that are not full
        available = []
        for course in courses:
            enrolled_count = self.session.query(Enrollment).filter(
                and_(
                    Enrollment.course_id == course.id,
                    Enrollment.semester == semester,
                    Enrollment.year == year,
                    Enrollment.status == "enrolled"
                )
            ).count()
            
            if enrolled_count < course.max_students:
                available.append(course)
                
        return available
        
    def get_course_statistics(self, course_id: int) -> Dict[str, Any]:
        """Get comprehensive course statistics"""
        course = self.session.get(Course, course_id)
        
        if not course:
            return {}
            
        # Get all enrollments
        enrollments = self.session.query(Enrollment).filter(
            Enrollment.course_id == course_id
        ).all()
        
        # Group by semester
        semester_stats = {}
        for enrollment in enrollments:
            key = f"{enrollment.year}-{enrollment.semester}"
            if key not in semester_stats:
                semester_stats[key] = {
                    "enrolled": 0,
                    "completed": 0,
                    "dropped": 0,
                    "failed": 0
                }
            semester_stats[key][enrollment.status] = semester_stats[key].get(enrollment.status, 0) + 1
            
        return {
            "course_code": course.course_code,
            "course_name": course.name,
            "credits": course.credits,
            "professor": course.professor.name if course.professor else None,
            "department": course.department.name if course.department else None,
            "max_students": course.max_students,
            "total_enrollments": len(enrollments),
            "semester_statistics": semester_stats
        }
        
    def assign_professor(self, course_code: str, professor_id: int) -> Course:
        """Assign a professor to a course"""
        course = self.get_course(course_code)
        if not course:
            raise ValueError(f"Course {course_code} not found")
            
        professor = self.session.get(Professor, professor_id)
        if not professor:
            raise ValueError(f"Professor with ID {professor_id} not found")
            
        course.professor_id = professor_id
        self.session.commit()
        self.session.refresh(course)
        
        return course
        
    def get_professor_courses(self, professor_id: int,
                            semester: Optional[str] = None,
                            year: Optional[int] = None) -> List[Course]:
        """Get all courses taught by a professor"""
        query = self.session.query(Course).filter(
            Course.professor_id == professor_id
        )
        
        if semester and year:
            # Filter by courses with enrollments in the specified semester
            query = query.join(Enrollment).filter(
                and_(
                    Enrollment.semester == semester,
                    Enrollment.year == year
                )
            ).distinct()
            
        return query.all()