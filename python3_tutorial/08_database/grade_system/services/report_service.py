import os
from typing import List, Dict, Any, Optional
from datetime import datetime
import json
import pandas as pd
from pathlib import Path
from jinja2 import Environment, FileSystemLoader
from sqlalchemy.orm import Session

from ..models import Student, Course, Enrollment, Grade, Department
from .student_service import StudentService
from .grade_service import GradeService


class ReportService:
    """Service class for generating various reports"""
    
    def __init__(self, session: Session):
        self.session = session
        self.student_service = StudentService(session)
        self.grade_service = GradeService(session)
        
        # Setup Jinja2 for HTML templates
        template_dir = Path(__file__).parent.parent / "templates"
        if template_dir.exists():
            self.env = Environment(loader=FileSystemLoader(str(template_dir)))
        else:
            self.env = None
            
    def generate_transcript(self, student_id: str, 
                          output_format: str = "dict") -> Any:
        """Generate student transcript"""
        student = self.student_service.get_student(student_id)
        
        if not student:
            raise ValueError(f"Student {student_id} not found")
            
        # Get grade history
        grade_history = self.grade_service.get_grade_history(student.id)
        
        # Calculate semester GPAs
        semester_gpas = self._calculate_semester_gpas(student.id)
        
        transcript_data = {
            "student_info": {
                "student_id": student.student_id,
                "name": student.name,
                "email": student.email,
                "major": student.major,
                "enrollment_date": student.enrollment_date.isoformat() if student.enrollment_date else None,
                "graduation_date": student.graduation_date.isoformat() if student.graduation_date else None,
                "status": student.status,
                "overall_gpa": student.gpa,
                "total_credits": student.total_credits
            },
            "grade_history": grade_history,
            "semester_gpas": semester_gpas,
            "generated_at": datetime.now().isoformat()
        }
        
        if output_format == "dict":
            return transcript_data
        elif output_format == "json":
            return json.dumps(transcript_data, indent=2, default=str)
        elif output_format == "html":
            return self._render_html_transcript(transcript_data)
        elif output_format == "pdf":
            return self._generate_pdf_transcript(transcript_data)
        else:
            raise ValueError(f"Unsupported output format: {output_format}")
            
    def generate_grade_report(self, semester: str, year: int,
                            course_code: Optional[str] = None,
                            department_code: Optional[str] = None) -> pd.DataFrame:
        """Generate grade report for a semester"""
        query = self.session.query(
            Student.student_id,
            Student.name.label("student_name"),
            Course.course_code,
            Course.name.label("course_name"),
            Course.credits,
            Grade.midterm_score,
            Grade.final_score,
            Grade.assignment_score,
            Grade.attendance_score,
            Grade.total_score,
            Grade.letter_grade,
            Grade.grade_points
        ).join(
            Enrollment, Student.id == Enrollment.student_id
        ).join(
            Course, Enrollment.course_id == Course.id
        ).outerjoin(
            Grade, Enrollment.id == Grade.enrollment_id
        ).filter(
            Enrollment.semester == semester,
            Enrollment.year == year
        )
        
        if course_code:
            query = query.filter(Course.course_code == course_code)
            
        if department_code:
            query = query.join(Department, Course.department_id == Department.id)
            query = query.filter(Department.code == department_code)
            
        results = query.all()
        
        # Convert to DataFrame
        df = pd.DataFrame(results, columns=[
            "student_id", "student_name", "course_code", "course_name",
            "credits", "midterm_score", "final_score", "assignment_score",
            "attendance_score", "total_score", "letter_grade", "grade_points"
        ])
        
        return df
        
    def generate_statistics_report(self, semester: str, year: int) -> Dict[str, Any]:
        """Generate comprehensive statistics report for a semester"""
        # Overall statistics
        total_students = self.session.query(Student).filter(
            Student.status == "active"
        ).count()
        
        total_enrollments = self.session.query(Enrollment).filter(
            Enrollment.semester == semester,
            Enrollment.year == year
        ).count()
        
        completed_enrollments = self.session.query(Enrollment).filter(
            Enrollment.semester == semester,
            Enrollment.year == year,
            Enrollment.status == "completed"
        ).count()
        
        # Department statistics
        dept_stats = []
        departments = self.session.query(Department).all()
        
        for dept in departments:
            dept_enrollments = self.session.query(Enrollment).join(
                Student
            ).filter(
                Student.department_id == dept.id,
                Enrollment.semester == semester,
                Enrollment.year == year
            ).count()
            
            dept_stats.append({
                "department": dept.name,
                "code": dept.code,
                "enrollments": dept_enrollments
            })
            
        # Course statistics
        courses = self.session.query(Course).all()
        course_stats = []
        
        for course in courses:
            stats = self.grade_service.calculate_course_statistics(
                course.id, semester, year
            )
            if stats["enrolled_count"] > 0:
                course_stats.append({
                    "course_code": course.course_code,
                    "course_name": course.name,
                    **stats
                })
                
        # Top students
        rankings = self.grade_service.get_student_ranking(semester, year)[:10]
        
        return {
            "semester": semester,
            "year": year,
            "overall": {
                "total_students": total_students,
                "total_enrollments": total_enrollments,
                "completed_enrollments": completed_enrollments,
                "completion_rate": round(completed_enrollments / total_enrollments * 100, 2) 
                    if total_enrollments > 0 else 0
            },
            "department_statistics": dept_stats,
            "course_statistics": course_stats,
            "top_students": rankings,
            "generated_at": datetime.now().isoformat()
        }
        
    def export_to_excel(self, data: Any, filename: str):
        """Export data to Excel file"""
        output_path = Path(filename)
        
        if isinstance(data, pd.DataFrame):
            data.to_excel(output_path, index=False)
        elif isinstance(data, dict):
            with pd.ExcelWriter(output_path) as writer:
                for sheet_name, sheet_data in data.items():
                    if isinstance(sheet_data, list):
                        df = pd.DataFrame(sheet_data)
                    elif isinstance(sheet_data, dict):
                        df = pd.DataFrame([sheet_data])
                    else:
                        continue
                    df.to_excel(writer, sheet_name=sheet_name[:31], index=False)
        else:
            raise ValueError("Data must be DataFrame or dict")
            
    def generate_graduation_checklist(self, student_id: str) -> Dict[str, Any]:
        """Generate graduation requirements checklist for a student"""
        student = self.student_service.get_student(student_id)
        
        if not student:
            raise ValueError(f"Student {student_id} not found")
            
        # Get completed courses
        completed_enrollments = self.session.query(Enrollment).filter(
            Enrollment.student_id == student.id,
            Enrollment.status == "completed"
        ).all()
        
        completed_credits = sum(e.course.credits for e in completed_enrollments)
        
        # Check requirements (example requirements)
        requirements = {
            "total_credits": {
                "required": 120,
                "completed": completed_credits,
                "remaining": max(0, 120 - completed_credits),
                "satisfied": completed_credits >= 120
            },
            "gpa_requirement": {
                "required": 2.0,
                "current": student.gpa,
                "satisfied": student.gpa >= 2.0
            },
            "major_courses": {
                "required": 60,
                "completed": sum(
                    e.course.credits for e in completed_enrollments
                    if e.course.course_type == "required"
                ),
                "satisfied": False  # Simplified
            },
            "general_education": {
                "required": 30,
                "completed": sum(
                    e.course.credits for e in completed_enrollments
                    if e.course.course_type == "general"
                ),
                "satisfied": False  # Simplified
            }
        }
        
        can_graduate = all(req["satisfied"] for req in requirements.values())
        
        return {
            "student_id": student.student_id,
            "name": student.name,
            "major": student.major,
            "requirements": requirements,
            "can_graduate": can_graduate,
            "generated_at": datetime.now().isoformat()
        }
        
    def _calculate_semester_gpas(self, student_id: int) -> List[Dict[str, Any]]:
        """Calculate GPA for each semester"""
        enrollments = self.session.query(Enrollment).filter(
            Enrollment.student_id == student_id,
            Enrollment.status == "completed"
        ).order_by(Enrollment.year, Enrollment.semester).all()
        
        semester_data = {}
        
        for enrollment in enrollments:
            key = f"{enrollment.year}-{enrollment.semester}"
            if key not in semester_data:
                semester_data[key] = {
                    "year": enrollment.year,
                    "semester": enrollment.semester,
                    "total_points": 0,
                    "total_credits": 0
                }
                
            if enrollment.grade and enrollment.grade.grade_points is not None:
                credits = enrollment.course.credits
                semester_data[key]["total_points"] += enrollment.grade.grade_points * credits
                semester_data[key]["total_credits"] += credits
                
        # Calculate GPAs
        result = []
        for key, data in semester_data.items():
            if data["total_credits"] > 0:
                gpa = round(data["total_points"] / data["total_credits"], 2)
            else:
                gpa = 0.0
                
            result.append({
                "year": data["year"],
                "semester": data["semester"],
                "gpa": gpa,
                "credits": data["total_credits"]
            })
            
        return result
        
    def _render_html_transcript(self, data: Dict[str, Any]) -> str:
        """Render transcript as HTML"""
        if not self.env:
            return "<html><body>Template not available</body></html>"
            
        template = self.env.get_template("transcript.html")
        return template.render(**data)
        
    def _generate_pdf_transcript(self, data: Dict[str, Any]) -> bytes:
        """Generate PDF transcript (placeholder)"""
        # This would require a PDF library like reportlab or weasyprint
        # For now, return a placeholder
        return b"PDF generation not implemented"