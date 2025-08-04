from typing import List, Optional, Dict, Any, Tuple
from datetime import datetime
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from sqlalchemy import and_, func

from ..models import Grade, Enrollment, Student, Course, Professor
from ..utils.calculators import GradeCalculator


class GradeService:
    """Service class for grade-related operations"""
    
    def __init__(self, session: Session):
        self.session = session
        self.calculator = GradeCalculator()
        
    def add_grade(self, enrollment_id: int, grade_data: Dict[str, Any],
                 professor_id: Optional[int] = None) -> Grade:
        """Add or update grade for an enrollment"""
        # Check if enrollment exists
        enrollment = self.session.get(Enrollment, enrollment_id)
        if not enrollment:
            raise ValueError(f"Enrollment with ID {enrollment_id} not found")
            
        # Check if grade already exists
        existing_grade = self.session.query(Grade).filter_by(
            enrollment_id=enrollment_id
        ).first()
        
        if existing_grade:
            # Update existing grade
            for key, value in grade_data.items():
                if hasattr(existing_grade, key):
                    setattr(existing_grade, key, value)
            grade = existing_grade
        else:
            # Create new grade
            grade = Grade(enrollment_id=enrollment_id, **grade_data)
            self.session.add(grade)
            
        # Calculate total score and letter grade
        if any(k in grade_data for k in ["midterm_score", "final_score", 
                                         "assignment_score", "attendance_score"]):
            grade.total_score = grade.calculate_total_score()
            grade.letter_grade, grade.grade_points = Grade.score_to_letter_grade(
                grade.total_score
            )
            grade.is_pass = grade.grade_points > 0
            
        # Set grading info
        if professor_id:
            grade.graded_by = professor_id
        grade.graded_at = datetime.now()
        
        # Update enrollment status if grade is finalized
        if grade.letter_grade:
            enrollment.status = "completed" if grade.is_pass else "failed"
            
        try:
            self.session.commit()
            self.session.refresh(grade)
            
            # Update student's GPA
            self._update_student_gpa(enrollment.student_id)
            
            return grade
        except IntegrityError as e:
            self.session.rollback()
            raise ValueError(f"Failed to add grade: {str(e)}")
            
    def get_grade(self, enrollment_id: int) -> Optional[Grade]:
        """Get grade by enrollment ID"""
        return self.session.query(Grade).filter_by(enrollment_id=enrollment_id).first()
        
    def update_grade_component(self, enrollment_id: int, 
                              component: str, score: float) -> Optional[Grade]:
        """Update a specific component of a grade"""
        valid_components = ["midterm_score", "final_score", 
                          "assignment_score", "attendance_score"]
        
        if component not in valid_components:
            raise ValueError(f"Invalid component. Must be one of: {valid_components}")
            
        if not 0 <= score <= 100:
            raise ValueError("Score must be between 0 and 100")
            
        grade = self.get_grade(enrollment_id)
        if not grade:
            # Create new grade with this component
            return self.add_grade(enrollment_id, {component: score})
            
        setattr(grade, component, score)
        
        # Recalculate total score and letter grade
        grade.total_score = grade.calculate_total_score()
        grade.letter_grade, grade.grade_points = Grade.score_to_letter_grade(
            grade.total_score
        )
        grade.is_pass = grade.grade_points > 0
        
        self.session.commit()
        self.session.refresh(grade)
        
        # Update student's GPA
        enrollment = self.session.get(Enrollment, enrollment_id)
        if enrollment:
            self._update_student_gpa(enrollment.student_id)
            
        return grade
        
    def batch_grade_update(self, grades_data: List[Dict[str, Any]]) -> List[Grade]:
        """Update multiple grades at once"""
        updated_grades = []
        
        for grade_info in grades_data:
            enrollment_id = grade_info.pop("enrollment_id")
            professor_id = grade_info.pop("professor_id", None)
            
            try:
                grade = self.add_grade(enrollment_id, grade_info, professor_id)
                updated_grades.append(grade)
            except ValueError as e:
                print(f"Failed to update grade for enrollment {enrollment_id}: {e}")
                
        return updated_grades
        
    def get_course_grades(self, course_id: int, 
                         semester: str, year: int) -> List[Grade]:
        """Get all grades for a course in a specific semester"""
        grades = self.session.query(Grade).join(Enrollment).filter(
            and_(
                Enrollment.course_id == course_id,
                Enrollment.semester == semester,
                Enrollment.year == year
            )
        ).all()
        
        return grades
        
    def get_student_grades(self, student_id: int,
                          semester: Optional[str] = None,
                          year: Optional[int] = None) -> List[Grade]:
        """Get all grades for a student"""
        query = self.session.query(Grade).join(Enrollment).filter(
            Enrollment.student_id == student_id
        )
        
        if semester:
            query = query.filter(Enrollment.semester == semester)
        if year:
            query = query.filter(Enrollment.year == year)
            
        return query.all()
        
    def calculate_course_statistics(self, course_id: int,
                                  semester: str, year: int) -> Dict[str, Any]:
        """Calculate statistics for a course"""
        grades = self.get_course_grades(course_id, semester, year)
        
        if not grades:
            return {
                "enrolled_count": 0,
                "graded_count": 0,
                "average_score": 0,
                "median_score": 0,
                "max_score": 0,
                "min_score": 0,
                "pass_rate": 0,
                "grade_distribution": {}
            }
            
        scores = [g.total_score for g in grades if g.total_score is not None]
        letter_grades = [g.letter_grade for g in grades if g.letter_grade]
        
        # Calculate grade distribution
        grade_distribution = {}
        for grade in letter_grades:
            grade_distribution[grade] = grade_distribution.get(grade, 0) + 1
            
        # Calculate pass rate
        pass_count = sum(1 for g in grades if g.is_pass)
        pass_rate = (pass_count / len(grades) * 100) if grades else 0
        
        return {
            "enrolled_count": len(grades),
            "graded_count": len(scores),
            "average_score": round(sum(scores) / len(scores), 2) if scores else 0,
            "median_score": sorted(scores)[len(scores) // 2] if scores else 0,
            "max_score": max(scores) if scores else 0,
            "min_score": min(scores) if scores else 0,
            "pass_rate": round(pass_rate, 2),
            "grade_distribution": grade_distribution
        }
        
    def get_student_ranking(self, semester: str, year: int,
                          department_id: Optional[int] = None) -> List[Dict[str, Any]]:
        """Get student rankings for a semester"""
        query = self.session.query(
            Student.student_id,
            Student.name,
            func.avg(Grade.total_score).label("avg_score"),
            func.count(Grade.id).label("course_count")
        ).join(
            Enrollment, Student.id == Enrollment.student_id
        ).join(
            Grade, Enrollment.id == Grade.enrollment_id
        ).filter(
            and_(
                Enrollment.semester == semester,
                Enrollment.year == year,
                Enrollment.status == "completed"
            )
        ).group_by(Student.id)
        
        if department_id:
            query = query.filter(Student.department_id == department_id)
            
        results = query.order_by(func.avg(Grade.total_score).desc()).all()
        
        rankings = []
        for rank, (student_id, name, avg_score, course_count) in enumerate(results, 1):
            rankings.append({
                "rank": rank,
                "student_id": student_id,
                "name": name,
                "average_score": round(avg_score, 2) if avg_score else 0,
                "completed_courses": course_count
            })
            
        return rankings
        
    def finalize_semester_grades(self, semester: str, year: int) -> int:
        """Finalize all grades for a semester"""
        enrollments = self.session.query(Enrollment).filter(
            and_(
                Enrollment.semester == semester,
                Enrollment.year == year,
                Enrollment.status == "enrolled"
            )
        ).all()
        
        finalized_count = 0
        
        for enrollment in enrollments:
            grade = self.get_grade(enrollment.id)
            
            if grade and grade.total_score is not None:
                # Mark enrollment as completed or failed
                enrollment.status = "completed" if grade.is_pass else "failed"
                finalized_count += 1
            else:
                # No grade recorded, mark as incomplete
                enrollment.status = "dropped"
                
        self.session.commit()
        
        # Update all students' GPAs
        student_ids = set(e.student_id for e in enrollments)
        for student_id in student_ids:
            self._update_student_gpa(student_id)
            
        return finalized_count
        
    def _update_student_gpa(self, student_id: int):
        """Update student's GPA after grade changes"""
        student = self.session.get(Student, student_id)
        if student:
            student.gpa = student.calculate_gpa()
            student.total_credits = sum(
                e.course.credits for e in student.enrollments 
                if e.status == "completed"
            )
            self.session.commit()
            
    def get_grade_history(self, student_id: int) -> List[Dict[str, Any]]:
        """Get complete grade history for a student"""
        enrollments = self.session.query(Enrollment).filter(
            Enrollment.student_id == student_id
        ).order_by(Enrollment.year.desc(), Enrollment.semester.desc()).all()
        
        history = []
        for enrollment in enrollments:
            course = enrollment.course
            grade = enrollment.grade
            
            history_entry = {
                "semester": enrollment.semester,
                "year": enrollment.year,
                "course_code": course.course_code,
                "course_name": course.name,
                "credits": course.credits,
                "status": enrollment.status,
                "professor": course.professor.name if course.professor else None,
            }
            
            if grade:
                history_entry.update({
                    "midterm_score": grade.midterm_score,
                    "final_score": grade.final_score,
                    "assignment_score": grade.assignment_score,
                    "attendance_score": grade.attendance_score,
                    "total_score": grade.total_score,
                    "letter_grade": grade.letter_grade,
                    "grade_points": grade.grade_points,
                })
            
            history.append(history_entry)
            
        return history