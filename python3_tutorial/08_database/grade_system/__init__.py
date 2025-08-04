"""
Grade Management System Package
"""

__version__ = "1.0.0"
__author__ = "Grade System Team"

from .database.connection import get_session, init_database
from .models import Student, Course, Enrollment, Grade, Professor, Department

__all__ = [
    "get_session",
    "init_database",
    "Student",
    "Course",
    "Enrollment",
    "Grade",
    "Professor",
    "Department",
]