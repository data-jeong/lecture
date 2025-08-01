"""
입력 검증 클래스
"""

import re
from datetime import datetime

class Validator:
    """입력 검증기"""
    
    @staticmethod
    def validate_email(email):
        """이메일 유효성 검사"""
        pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        return bool(re.match(pattern, email))
    
    @staticmethod
    def validate_phone(phone):
        """전화번호 유효성 검사"""
        # 하이픈 제거
        phone = phone.replace("-", "").replace(" ", "")
        
        # 한국 전화번호 패턴
        patterns = [
            r'^01[0-9]{8,9}$',  # 휴대폰
            r'^0[2-9][0-9]{7,8}$'  # 일반 전화
        ]
        
        return any(re.match(pattern, phone) for pattern in patterns)
    
    @staticmethod
    def validate_isbn(isbn):
        """ISBN 유효성 검사"""
        # 하이픈 제거
        isbn = isbn.replace("-", "")
        
        # ISBN-10 또는 ISBN-13
        if len(isbn) == 10:
            return Validator._validate_isbn10(isbn)
        elif len(isbn) == 13:
            return Validator._validate_isbn13(isbn)
        
        return False
    
    @staticmethod
    def _validate_isbn10(isbn):
        """ISBN-10 검증"""
        if not re.match(r'^\d{9}[\dXx]$', isbn):
            return False
        
        # 체크섬 계산
        total = 0
        for i in range(9):
            total += int(isbn[i]) * (10 - i)
        
        check = isbn[9].upper()
        if check == 'X':
            total += 10
        else:
            total += int(check)
        
        return total % 11 == 0
    
    @staticmethod
    def _validate_isbn13(isbn):
        """ISBN-13 검증"""
        if not re.match(r'^\d{13}$', isbn):
            return False
        
        # 체크섬 계산
        total = 0
        for i in range(12):
            if i % 2 == 0:
                total += int(isbn[i])
            else:
                total += int(isbn[i]) * 3
        
        check = (10 - (total % 10)) % 10
        return check == int(isbn[12])
    
    @staticmethod
    def validate_year(year):
        """연도 유효성 검사"""
        try:
            year = int(year)
            current_year = datetime.now().year
            return 1000 <= year <= current_year
        except ValueError:
            return False
    
    @staticmethod
    def validate_positive_integer(value):
        """양의 정수 검사"""
        try:
            value = int(value)
            return value > 0
        except ValueError:
            return False
    
    @staticmethod
    def validate_genre(genre):
        """장르 유효성 검사"""
        valid_genres = [
            "일반", "소설", "시", "에세이", "자기계발",
            "경제경영", "인문", "역사", "과학", "예술",
            "종교", "사회", "어린이", "청소년", "만화",
            "요리", "건강", "여행", "외국어", "컴퓨터"
        ]
        return genre in valid_genres
    
    @staticmethod
    def validate_book_condition(condition):
        """도서 상태 유효성 검사"""
        valid_conditions = ["양호", "보통", "불량"]
        return condition in valid_conditions
    
    @staticmethod
    def validate_file_format(format):
        """파일 형식 유효성 검사"""
        valid_formats = ["PDF", "EPUB", "MOBI", "AZW", "TXT"]
        return format.upper() in valid_formats
    
    @staticmethod
    def sanitize_input(text):
        """입력값 정제"""
        if not isinstance(text, str):
            return str(text)
        
        # 앞뒤 공백 제거
        text = text.strip()
        
        # 연속된 공백을 하나로
        text = re.sub(r'\s+', ' ', text)
        
        # 특수문자 제거 (필요시)
        # text = re.sub(r'[<>]', '', text)
        
        return text
    
    @staticmethod
    def validate_member_name(name):
        """회원 이름 유효성 검사"""
        if not name or len(name) < 2:
            return False
        
        # 한글, 영문, 공백만 허용
        pattern = r'^[가-힣a-zA-Z\s]+$'
        return bool(re.match(pattern, name))
    
    @staticmethod
    def validate_password(password):
        """비밀번호 유효성 검사 (향후 사용)"""
        if len(password) < 8:
            return False, "비밀번호는 8자 이상이어야 합니다."
        
        if not re.search(r'[A-Z]', password):
            return False, "대문자를 포함해야 합니다."
        
        if not re.search(r'[a-z]', password):
            return False, "소문자를 포함해야 합니다."
        
        if not re.search(r'\d', password):
            return False, "숫자를 포함해야 합니다."
        
        if not re.search(r'[!@#$%^&*(),.?":{}|<>]', password):
            return False, "특수문자를 포함해야 합니다."
        
        return True, "유효한 비밀번호입니다."