#!/usr/bin/env python3
"""
Grade Management System - Main Entry Point
"""

import click
import sys
from pathlib import Path
from datetime import date
from typing import Optional

from grade_system.database.connection import init_database, session_scope
from grade_system.services import StudentService, CourseService, GradeService, ReportService
from grade_system.models import Student, Course, Department, Professor
from grade_system.utils.validators import validate_student_id, validate_email


@click.group()
@click.option('--db', default='grade_system.db', help='Database file path')
@click.pass_context
def cli(ctx, db):
    """Grade Management System CLI"""
    ctx.ensure_object(dict)
    ctx.obj['db'] = init_database(f"sqlite:///{db}")


@cli.command()
@click.pass_context
def init_db(ctx):
    """Initialize database with tables"""
    db = ctx.obj['db']
    db.create_tables()
    click.echo("Database initialized successfully!")
    
    # Add sample departments
    with session_scope() as session:
        departments = [
            Department(code="CS", name="Computer Science", building="Engineering Building"),
            Department(code="MATH", name="Mathematics", building="Science Building"),
            Department(code="PHYS", name="Physics", building="Science Building"),
            Department(code="ENG", name="English", building="Liberal Arts Building")
        ]
        
        for dept in departments:
            existing = session.query(Department).filter_by(code=dept.code).first()
            if not existing:
                session.add(dept)
                
        click.echo("Sample departments added!")


@cli.command()
@click.option('--student-id', prompt=True, help='Student ID (10 digits)')
@click.option('--name', prompt=True, help='Student name')
@click.option('--email', prompt=True, help='Student email')
@click.option('--major', prompt=True, help='Major')
@click.option('--department', prompt=True, help='Department code')
@click.pass_context
def add_student(ctx, student_id, name, email, major, department):
    """Add a new student"""
    try:
        validate_student_id(student_id)
        validate_email(email)
        
        with session_scope() as session:
            # Get department
            dept = session.query(Department).filter_by(code=department).first()
            if not dept:
                click.echo(f"Department {department} not found!", err=True)
                return
                
            service = StudentService(session)
            student = service.create_student({
                "student_id": student_id,
                "name": name,
                "email": email,
                "major": major,
                "department_id": dept.id,
                "enrollment_date": date.today()
            })
            
            click.echo(f"Student {student.name} (ID: {student.student_id}) added successfully!")
            
    except ValueError as e:
        click.echo(f"Error: {e}", err=True)


@cli.command()
@click.option('--course-code', prompt=True, help='Course code')
@click.option('--name', prompt=True, help='Course name')
@click.option('--credits', prompt=True, type=int, help='Credits')
@click.option('--max-students', default=30, help='Maximum students')
@click.option('--department', prompt=True, help='Department code')
@click.pass_context
def add_course(ctx, course_code, name, credits, max_students, department):
    """Add a new course"""
    try:
        with session_scope() as session:
            # Get department
            dept = session.query(Department).filter_by(code=department).first()
            if not dept:
                click.echo(f"Department {department} not found!", err=True)
                return
                
            service = CourseService(session)
            course = service.create_course({
                "course_code": course_code,
                "name": name,
                "credits": credits,
                "max_students": max_students,
                "department_id": dept.id,
                "course_type": "required"
            })
            
            click.echo(f"Course {course.name} ({course.course_code}) added successfully!")
            
    except ValueError as e:
        click.echo(f"Error: {e}", err=True)


@cli.command()
@click.option('--student-id', prompt=True, help='Student ID')
@click.option('--course-code', prompt=True, help='Course code')
@click.option('--semester', prompt=True, help='Semester (e.g., 2024-1)')
@click.option('--year', prompt=True, type=int, help='Year')
@click.pass_context
def enroll(ctx, student_id, course_code, semester, year):
    """Enroll a student in a course"""
    try:
        with session_scope() as session:
            student_service = StudentService(session)
            course_service = CourseService(session)
            
            student = student_service.get_student(student_id)
            if not student:
                click.echo(f"Student {student_id} not found!", err=True)
                return
                
            course = course_service.get_course(course_code)
            if not course:
                click.echo(f"Course {course_code} not found!", err=True)
                return
                
            enrollment = course_service.enroll_student(
                student.id, course.id, semester, year
            )
            
            click.echo(f"Student {student.name} enrolled in {course.name} successfully!")
            
    except ValueError as e:
        click.echo(f"Error: {e}", err=True)


@cli.command()
@click.option('--student-id', prompt=True, help='Student ID')
@click.option('--course-code', prompt=True, help='Course code')
@click.option('--semester', prompt=True, help='Semester')
@click.option('--year', prompt=True, type=int, help='Year')
@click.option('--midterm', prompt=True, type=float, help='Midterm score')
@click.option('--final', prompt=True, type=float, help='Final score')
@click.option('--assignment', prompt=True, type=float, help='Assignment score')
@click.option('--attendance', prompt=True, type=float, help='Attendance score')
@click.pass_context
def add_grade(ctx, student_id, course_code, semester, year, 
             midterm, final, assignment, attendance):
    """Add grade for a student"""
    try:
        with session_scope() as session:
            student_service = StudentService(session)
            course_service = CourseService(session)
            grade_service = GradeService(session)
            
            student = student_service.get_student(student_id)
            if not student:
                click.echo(f"Student {student_id} not found!", err=True)
                return
                
            course = course_service.get_course(course_code)
            if not course:
                click.echo(f"Course {course_code} not found!", err=True)
                return
                
            # Find enrollment
            from grade_system.models import Enrollment
            enrollment = session.query(Enrollment).filter_by(
                student_id=student.id,
                course_id=course.id,
                semester=semester,
                year=year
            ).first()
            
            if not enrollment:
                click.echo(f"Enrollment not found!", err=True)
                return
                
            grade = grade_service.add_grade(enrollment.id, {
                "midterm_score": midterm,
                "final_score": final,
                "assignment_score": assignment,
                "attendance_score": attendance
            })
            
            click.echo(f"Grade added successfully!")
            click.echo(f"Total Score: {grade.total_score}")
            click.echo(f"Letter Grade: {grade.letter_grade}")
            click.echo(f"Grade Points: {grade.grade_points}")
            
    except ValueError as e:
        click.echo(f"Error: {e}", err=True)


@cli.command()
@click.option('--student-id', prompt=True, help='Student ID')
@click.pass_context
def show_student(ctx, student_id):
    """Show student information"""
    with session_scope() as session:
        service = StudentService(session)
        student = service.get_student(student_id)
        
        if not student:
            click.echo(f"Student {student_id} not found!", err=True)
            return
            
        stats = service.get_student_statistics(student_id)
        
        click.echo("\n" + "="*50)
        click.echo(f"Student ID: {stats['student_id']}")
        click.echo(f"Name: {stats['name']}")
        click.echo(f"Status: {stats['status']}")
        click.echo(f"GPA: {stats['gpa']}")
        click.echo(f"Total Credits: {stats['total_credits']}")
        click.echo(f"Completed Courses: {stats['completed_courses']}")
        click.echo(f"Enrolled Courses: {stats['enrolled_courses']}")
        click.echo(f"Average Score: {stats['average_score']}")
        click.echo("="*50 + "\n")


@cli.command()
@click.option('--student-id', prompt=True, help='Student ID')
@click.option('--format', type=click.Choice(['text', 'json', 'excel']), 
             default='text', help='Output format')
@click.option('--output', help='Output file path')
@click.pass_context
def transcript(ctx, student_id, format, output):
    """Generate student transcript"""
    with session_scope() as session:
        service = ReportService(session)
        
        try:
            if format == 'text':
                transcript_data = service.generate_transcript(student_id, 'dict')
                
                click.echo("\n" + "="*60)
                click.echo("ACADEMIC TRANSCRIPT")
                click.echo("="*60)
                
                student_info = transcript_data['student_info']
                click.echo(f"\nStudent ID: {student_info['student_id']}")
                click.echo(f"Name: {student_info['name']}")
                click.echo(f"Email: {student_info['email']}")
                click.echo(f"Major: {student_info['major']}")
                click.echo(f"Overall GPA: {student_info['overall_gpa']}")
                click.echo(f"Total Credits: {student_info['total_credits']}")
                
                click.echo("\nGrade History:")
                click.echo("-"*60)
                
                for record in transcript_data['grade_history']:
                    click.echo(f"\n{record['year']}-{record['semester']}:")
                    click.echo(f"  {record['course_code']} - {record['course_name']}")
                    click.echo(f"  Credits: {record.get('credits', 'N/A')}")
                    click.echo(f"  Grade: {record.get('letter_grade', 'N/A')}")
                    click.echo(f"  Score: {record.get('total_score', 'N/A')}")
                    
            elif format == 'json':
                transcript_data = service.generate_transcript(student_id, 'json')
                if output:
                    with open(output, 'w') as f:
                        f.write(transcript_data)
                    click.echo(f"Transcript saved to {output}")
                else:
                    click.echo(transcript_data)
                    
            elif format == 'excel':
                transcript_data = service.generate_transcript(student_id, 'dict')
                from grade_system.utils.exporters import ExcelExporter
                
                output_file = output or f"transcript_{student_id}.xlsx"
                ExcelExporter.export_transcript(transcript_data, output_file)
                click.echo(f"Transcript saved to {output_file}")
                
        except ValueError as e:
            click.echo(f"Error: {e}", err=True)


@cli.command()
@click.option('--semester', prompt=True, help='Semester')
@click.option('--year', prompt=True, type=int, help='Year')
@click.option('--output', help='Output file path')
@click.pass_context
def report(ctx, semester, year, output):
    """Generate semester report"""
    with session_scope() as session:
        service = ReportService(session)
        
        stats = service.generate_statistics_report(semester, year)
        
        click.echo("\n" + "="*60)
        click.echo(f"SEMESTER REPORT: {semester} {year}")
        click.echo("="*60)
        
        overall = stats['overall']
        click.echo(f"\nTotal Students: {overall['total_students']}")
        click.echo(f"Total Enrollments: {overall['total_enrollments']}")
        click.echo(f"Completed Enrollments: {overall['completed_enrollments']}")
        click.echo(f"Completion Rate: {overall['completion_rate']}%")
        
        click.echo("\nTop Students:")
        click.echo("-"*40)
        for student in stats['top_students'][:5]:
            click.echo(f"{student['rank']}. {student['name']} - Avg: {student['average_score']}")
            
        if output:
            from grade_system.utils.exporters import ExcelExporter
            ExcelExporter.export_statistics(stats, output)
            click.echo(f"\nFull report saved to {output}")


@cli.command()
@click.pass_context
def list_students(ctx):
    """List all students"""
    with session_scope() as session:
        service = StudentService(session)
        students = service.get_all_students(limit=50)
        
        click.echo("\n" + "="*60)
        click.echo("STUDENT LIST")
        click.echo("="*60)
        click.echo(f"{'ID':<12} {'Name':<25} {'Major':<15} {'GPA':<5}")
        click.echo("-"*60)
        
        for student in students:
            click.echo(f"{student.student_id:<12} {student.name:<25} "
                      f"{student.major or 'N/A':<15} {student.gpa:<5.2f}")


@cli.command()
@click.pass_context
def list_courses(ctx):
    """List all courses"""
    with session_scope() as session:
        service = CourseService(session)
        courses = service.get_all_courses(limit=50)
        
        click.echo("\n" + "="*60)
        click.echo("COURSE LIST")
        click.echo("="*60)
        click.echo(f"{'Code':<10} {'Name':<30} {'Credits':<8} {'Max':<5}")
        click.echo("-"*60)
        
        for course in courses:
            click.echo(f"{course.course_code:<10} {course.name:<30} "
                      f"{course.credits:<8} {course.max_students:<5}")


if __name__ == '__main__':
    cli()