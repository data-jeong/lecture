from typing import List, Optional, Dict, Any
from datetime import date, datetime
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from sqlalchemy import and_, or_, func

from ..models import Student, Department, Enrollment, Grade
from ..utils.validators import validate_email, validate_student_id


class StudentService:
    """Service class for student-related operations"""
    
    def __init__(self, session: Session):
        self.session = session
        
    def create_student(self, student_data: Dict[str, Any]) -> Student:
        """Create a new student"""
        # Validate input
        if "email" in student_data:
            validate_email(student_data["email"])
        if "student_id" in student_data:
            validate_student_id(student_data["student_id"])
            
        # Check if student already exists
        existing = self.session.query(Student).filter_by(
            student_id=student_data.get("student_id")
        ).first()
        
        if existing:
            raise ValueError(f"Student with ID {student_data['student_id']} already exists")
            
        # Create student
        student = Student(**student_data)
        self.session.add(student)
        
        try:
            self.session.commit()
            self.session.refresh(student)
            return student
        except IntegrityError as e:
            self.session.rollback()
            raise ValueError(f"Failed to create student: {str(e)}")
            
    def get_student(self, student_id: str) -> Optional[Student]:
        """Get student by student ID"""
        return self.session.query(Student).filter_by(student_id=student_id).first()
        
    def get_student_by_id(self, id: int) -> Optional[Student]:
        """Get student by database ID"""
        return self.session.query(Student).get(id)
        
    def update_student(self, student_id: str, update_data: Dict[str, Any]) -> Optional[Student]:
        """Update student information"""
        student = self.get_student(student_id)
        
        if not student:
            return None
            
        # Validate email if being updated
        if "email" in update_data:
            validate_email(update_data["email"])
            
        # Update fields
        for key, value in update_data.items():
            if hasattr(student, key) and key not in ["id", "student_id", "created_at"]:
                setattr(student, key, value)
                
        try:
            self.session.commit()
            self.session.refresh(student)
            return student
        except IntegrityError as e:
            self.session.rollback()
            raise ValueError(f"Failed to update student: {str(e)}")
            
    def delete_student(self, student_id: str) -> bool:
        """Delete a student (soft delete by changing status)"""
        student = self.get_student(student_id)
        
        if not student:
            return False
            
        student.status = "expelled"
        self.session.commit()
        return True
        
    def hard_delete_student(self, student_id: str) -> bool:
        """Permanently delete a student from database"""
        student = self.get_student(student_id)
        
        if not student:
            return False
            
        self.session.delete(student)
        self.session.commit()
        return True
        
    def search_students(self, 
                       name: Optional[str] = None,
                       major: Optional[str] = None,
                       status: Optional[str] = None,
                       department_code: Optional[str] = None) -> List[Student]:
        """Search students with filters"""
        query = self.session.query(Student)
        
        if name:
            query = query.filter(Student.name.ilike(f"%{name}%"))
        if major:
            query = query.filter(Student.major.ilike(f"%{major}%"))
        if status:
            query = query.filter(Student.status == status)
        if department_code:
            query = query.join(Department).filter(Department.code == department_code)
            
        return query.all()
        
    def get_all_students(self, 
                         limit: Optional[int] = None,
                         offset: Optional[int] = None,
                         order_by: str = "name") -> List[Student]:
        """Get all students with pagination"""
        query = self.session.query(Student)
        
        # Apply ordering
        if order_by == "name":
            query = query.order_by(Student.name)
        elif order_by == "student_id":
            query = query.order_by(Student.student_id)
        elif order_by == "gpa":
            query = query.order_by(Student.gpa.desc())
        elif order_by == "enrollment_date":
            query = query.order_by(Student.enrollment_date.desc())
            
        # Apply pagination
        if offset:
            query = query.offset(offset)
        if limit:
            query = query.limit(limit)
            
        return query.all()
        
    def get_student_enrollments(self, student_id: str, 
                               semester: Optional[str] = None,
                               year: Optional[int] = None) -> List[Enrollment]:
        """Get student's enrollments"""
        student = self.get_student(student_id)
        
        if not student:
            return []
            
        query = self.session.query(Enrollment).filter(Enrollment.student_id == student.id)
        
        if semester:
            query = query.filter(Enrollment.semester == semester)
        if year:
            query = query.filter(Enrollment.year == year)
            
        return query.all()
        
    def get_student_grades(self, student_id: str,
                          semester: Optional[str] = None,
                          year: Optional[int] = None) -> List[Grade]:
        """Get student's grades"""
        student = self.get_student(student_id)
        
        if not student:
            return []
            
        query = self.session.query(Grade).join(Enrollment).filter(
            Enrollment.student_id == student.id
        )
        
        if semester:
            query = query.filter(Enrollment.semester == semester)
        if year:
            query = query.filter(Enrollment.year == year)
            
        return query.all()
        
    def calculate_gpa(self, student_id: str) -> float:
        """Calculate student's GPA"""
        student = self.get_student(student_id)
        
        if not student:
            return 0.0
            
        gpa = student.calculate_gpa()
        
        # Update student's GPA in database
        student.gpa = gpa
        student.total_credits = sum(
            e.course.credits for e in student.enrollments 
            if e.status == "completed"
        )
        self.session.commit()
        
        return gpa
        
    def get_student_statistics(self, student_id: str) -> Dict[str, Any]:
        """Get comprehensive student statistics"""
        student = self.get_student(student_id)
        
        if not student:
            return {}
            
        completed_courses = [e for e in student.enrollments if e.status == "completed"]
        enrolled_courses = [e for e in student.enrollments if e.status == "enrolled"]
        
        # Calculate average scores
        grades = [e.grade for e in completed_courses if e.grade]
        avg_score = 0
        if grades:
            scores = [g.total_score for g in grades if g.total_score is not None]
            avg_score = sum(scores) / len(scores) if scores else 0
            
        return {
            "student_id": student.student_id,
            "name": student.name,
            "status": student.status,
            "gpa": student.gpa,
            "total_credits": student.total_credits,
            "completed_courses": len(completed_courses),
            "enrolled_courses": len(enrolled_courses),
            "average_score": round(avg_score, 2),
            "enrollment_date": student.enrollment_date,
            "expected_graduation": student.graduation_date,
        }
        
    def get_top_students(self, limit: int = 10, 
                        department_code: Optional[str] = None) -> List[Student]:
        """Get top students by GPA"""
        query = self.session.query(Student).filter(
            Student.status == "active"
        ).order_by(Student.gpa.desc())
        
        if department_code:
            query = query.join(Department).filter(Department.code == department_code)
            
        return query.limit(limit).all()
        
    def update_student_status(self, student_id: str, new_status: str) -> bool:
        """Update student status"""
        valid_statuses = ["active", "graduated", "on_leave", "expelled"]
        
        if new_status not in valid_statuses:
            raise ValueError(f"Invalid status. Must be one of: {valid_statuses}")
            
        student = self.get_student(student_id)
        
        if not student:
            return False
            
        student.status = new_status
        
        if new_status == "graduated":
            student.graduation_date = date.today()
            
        self.session.commit()
        return True