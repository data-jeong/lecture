"""Input validation utilities"""

import re
from typing import Optional, Tuple
from datetime import datetime
from urllib.parse import urlparse


def validate_email(email: str) -> bool:
    """Validate email address"""
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return bool(re.match(pattern, email))


def validate_url(url: str) -> bool:
    """Validate URL"""
    try:
        result = urlparse(url)
        return all([result.scheme, result.netloc])
    except:
        return False


def validate_phone(phone: str) -> bool:
    """Validate phone number (basic international format)"""
    pattern = r'^\+?1?\d{9,15}$'
    phone_clean = re.sub(r'[\s\-\(\)]', '', phone)
    return bool(re.match(pattern, phone_clean))


def validate_date_range(start_date: datetime, end_date: datetime) -> Tuple[bool, Optional[str]]:
    """Validate date range"""
    if start_date > end_date:
        return False, "Start date must be before end date"
    
    if (end_date - start_date).days > 365:
        return False, "Date range cannot exceed 365 days"
    
    if end_date > datetime.now():
        return False, "End date cannot be in the future"
    
    return True, None


def validate_password(password: str) -> Tuple[bool, Optional[str]]:
    """Validate password strength"""
    if len(password) < 8:
        return False, "Password must be at least 8 characters long"
    
    if not re.search(r'[A-Z]', password):
        return False, "Password must contain at least one uppercase letter"
    
    if not re.search(r'[a-z]', password):
        return False, "Password must contain at least one lowercase letter"
    
    if not re.search(r'\d', password):
        return False, "Password must contain at least one number"
    
    if not re.search(r'[!@#$%^&*(),.?":{}|<>]', password):
        return False, "Password must contain at least one special character"
    
    return True, None


def validate_username(username: str) -> Tuple[bool, Optional[str]]:
    """Validate username"""
    if len(username) < 3:
        return False, "Username must be at least 3 characters long"
    
    if len(username) > 20:
        return False, "Username must be less than 20 characters"
    
    if not re.match(r'^[a-zA-Z0-9_]+$', username):
        return False, "Username can only contain letters, numbers, and underscores"
    
    if username[0].isdigit():
        return False, "Username cannot start with a number"
    
    return True, None


def validate_file_type(filename: str, allowed_types: list) -> bool:
    """Validate file type"""
    extension = filename.split('.')[-1].lower()
    return extension in allowed_types


def validate_json(json_str: str) -> Tuple[bool, Optional[str]]:
    """Validate JSON string"""
    import json
    
    try:
        json.loads(json_str)
        return True, None
    except json.JSONDecodeError as e:
        return False, str(e)


def validate_sql_injection(input_str: str) -> bool:
    """Basic SQL injection validation"""
    dangerous_patterns = [
        r';\s*DROP',
        r';\s*DELETE',
        r';\s*UPDATE',
        r';\s*INSERT',
        r'UNION\s+SELECT',
        r'OR\s+1\s*=\s*1',
        r'--',
        r'/\*.*\*/'
    ]
    
    input_upper = input_str.upper()
    for pattern in dangerous_patterns:
        if re.search(pattern, input_upper):
            return False
    
    return True


def validate_number_range(value: float, min_val: Optional[float] = None, 
                         max_val: Optional[float] = None) -> Tuple[bool, Optional[str]]:
    """Validate number is within range"""
    if min_val is not None and value < min_val:
        return False, f"Value must be at least {min_val}"
    
    if max_val is not None and value > max_val:
        return False, f"Value must be at most {max_val}"
    
    return True, None


def sanitize_input(input_str: str) -> str:
    """Sanitize user input"""
    # Remove potential HTML/JS
    input_str = re.sub(r'<[^>]*>', '', input_str)
    
    # Remove potential SQL injection attempts
    input_str = re.sub(r'[;\'"]', '', input_str)
    
    # Trim whitespace
    input_str = input_str.strip()
    
    return input_str