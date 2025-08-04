import re
from typing import Any, Optional
from datetime import date, datetime


def validate_email(email: str) -> bool:
    """Validate email format"""
    if not email:
        raise ValueError("Email cannot be empty")
        
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    
    if not re.match(pattern, email):
        raise ValueError(f"Invalid email format: {email}")
        
    return True


def validate_student_id(student_id: str) -> bool:
    """Validate student ID format (e.g., 2024001234)"""
    if not student_id:
        raise ValueError("Student ID cannot be empty")
        
    # Example format: year(4) + sequence(6)
    if not re.match(r'^\d{10}$', student_id):
        raise ValueError(f"Invalid student ID format: {student_id}. Expected 10 digits.")
        
    return True


def validate_professor_id(professor_id: str) -> bool:
    """Validate professor ID format"""
    if not professor_id:
        raise ValueError("Professor ID cannot be empty")
        
    # Example format: P + 3 digits
    if not re.match(r'^P\d{3}$', professor_id):
        raise ValueError(f"Invalid professor ID format: {professor_id}. Expected P followed by 3 digits.")
        
    return True


def validate_course_code(course_code: str) -> bool:
    """Validate course code format"""
    if not course_code:
        raise ValueError("Course code cannot be empty")
        
    # Example format: DEPT101, CS201, etc.
    if not re.match(r'^[A-Z]{2,4}\d{3}$', course_code):
        raise ValueError(f"Invalid course code format: {course_code}")
        
    return True


def validate_score(score: float, min_val: float = 0, max_val: float = 100) -> bool:
    """Validate score is within range"""
    if score is None:
        return True  # Allow None for ungraded
        
    if not isinstance(score, (int, float)):
        raise ValueError(f"Score must be a number, got {type(score)}")
        
    if not min_val <= score <= max_val:
        raise ValueError(f"Score must be between {min_val} and {max_val}, got {score}")
        
    return True


def validate_semester(semester: str) -> bool:
    """Validate semester format (e.g., 2024-1, 2024-2, 2024-S for summer)"""
    if not semester:
        raise ValueError("Semester cannot be empty")
        
    if not re.match(r'^\d{4}-[12S]$', semester):
        raise ValueError(f"Invalid semester format: {semester}. Expected YYYY-1, YYYY-2, or YYYY-S")
        
    return True


def validate_year(year: int) -> bool:
    """Validate academic year"""
    current_year = date.today().year
    
    if not isinstance(year, int):
        raise ValueError(f"Year must be an integer, got {type(year)}")
        
    if year < 1900 or year > current_year + 1:
        raise ValueError(f"Invalid year: {year}")
        
    return True


def validate_phone(phone: str) -> bool:
    """Validate phone number format"""
    if not phone:
        return True  # Phone is optional
        
    # Remove common separators
    cleaned = re.sub(r'[\s\-\(\)]', '', phone)
    
    # Check if it's a valid phone number (10-11 digits)
    if not re.match(r'^\d{10,11}$', cleaned):
        raise ValueError(f"Invalid phone number: {phone}")
        
    return True


def validate_grade_letter(letter_grade: str) -> bool:
    """Validate letter grade"""
    valid_grades = ["A+", "A0", "A-", "B+", "B0", "B-", 
                   "C+", "C0", "C-", "D+", "D0", "D-", "F"]
    
    if letter_grade not in valid_grades:
        raise ValueError(f"Invalid letter grade: {letter_grade}. Must be one of {valid_grades}")
        
    return True


def validate_enrollment_status(status: str) -> bool:
    """Validate enrollment status"""
    valid_statuses = ["enrolled", "completed", "dropped", "failed"]
    
    if status not in valid_statuses:
        raise ValueError(f"Invalid enrollment status: {status}. Must be one of {valid_statuses}")
        
    return True


def validate_student_status(status: str) -> bool:
    """Validate student status"""
    valid_statuses = ["active", "graduated", "on_leave", "expelled"]
    
    if status not in valid_statuses:
        raise ValueError(f"Invalid student status: {status}. Must be one of {valid_statuses}")
        
    return True


def validate_credits(credits: int) -> bool:
    """Validate course credits"""
    if not isinstance(credits, int):
        raise ValueError(f"Credits must be an integer, got {type(credits)}")
        
    if credits < 1 or credits > 6:
        raise ValueError(f"Credits must be between 1 and 6, got {credits}")
        
    return True


def validate_date_range(start_date: date, end_date: date) -> bool:
    """Validate date range"""
    if start_date > end_date:
        raise ValueError(f"Start date {start_date} cannot be after end date {end_date}")
        
    return True


def validate_gpa(gpa: float) -> bool:
    """Validate GPA value"""
    if not isinstance(gpa, (int, float)):
        raise ValueError(f"GPA must be a number, got {type(gpa)}")
        
    if not 0.0 <= gpa <= 4.5:
        raise ValueError(f"GPA must be between 0.0 and 4.5, got {gpa}")
        
    return True


def validate_attendance_rate(rate: float) -> bool:
    """Validate attendance rate"""
    if not isinstance(rate, (int, float)):
        raise ValueError(f"Attendance rate must be a number, got {type(rate)}")
        
    if not 0.0 <= rate <= 100.0:
        raise ValueError(f"Attendance rate must be between 0 and 100, got {rate}")
        
    return True