"""
도서 관련 클래스
"""

from abc import ABC, abstractmethod
from datetime import datetime
import random
import string

class Book(ABC):
    """도서 추상 클래스"""
    
    # 클래스 변수
    _id_counter = 1000
    
    def __init__(self, title, author, isbn=None, genre="일반", publication_year=None):
        self.id = Book._id_counter
        Book._id_counter += 1
        
        self.title = title
        self.author = author
        self.isbn = isbn or self._generate_isbn()
        self.genre = genre
        self.publication_year = publication_year or datetime.now().year
        self.is_available = True
        self.borrowed_by = None
        self.borrowed_date = None
        self.return_date = None
        self.reservation_queue = []  # 예약 대기열
        
    def _generate_isbn(self):
        """ISBN 자동 생성"""
        # 실제 ISBN은 더 복잡하지만, 여기서는 간단히 구현
        prefix = "978"
        group = "89"  # 한국
        publisher = ''.join(random.choices(string.digits, k=4))
        title_code = ''.join(random.choices(string.digits, k=4))
        check = random.choice(string.digits)
        return f"{prefix}-{group}-{publisher}-{title_code}-{check}"
    
    @abstractmethod
    def get_type(self):
        """도서 타입 반환"""
        pass
    
    @abstractmethod
    def get_loan_period(self):
        """대출 기간 반환 (일 단위)"""
        pass
    
    def __str__(self):
        status = "대출 가능" if self.is_available else f"대출 중 ({self.borrowed_by})"
        return f"[{self.id}] {self.title} - {self.author} ({self.get_type()}) - {status}"
    
    def __repr__(self):
        return f"{self.__class__.__name__}('{self.title}', '{self.author}', '{self.isbn}')"
    
    def __eq__(self, other):
        if not isinstance(other, Book):
            return False
        return self.isbn == other.isbn
    
    def is_overdue(self):
        """연체 여부 확인"""
        if not self.return_date:
            return False
        return datetime.now() > self.return_date
    
    def add_reservation(self, member_id):
        """예약 추가"""
        if member_id not in self.reservation_queue:
            self.reservation_queue.append(member_id)
            return True
        return False
    
    def remove_reservation(self, member_id):
        """예약 취소"""
        if member_id in self.reservation_queue:
            self.reservation_queue.remove(member_id)
            return True
        return False
    
    def get_next_reserver(self):
        """다음 예약자 반환"""
        if self.reservation_queue:
            return self.reservation_queue[0]
        return None


class PhysicalBook(Book):
    """실물 도서"""
    
    def __init__(self, title, author, isbn=None, genre="일반", 
                 publication_year=None, pages=0, location=""):
        super().__init__(title, author, isbn, genre, publication_year)
        self.pages = pages
        self.location = location  # 도서관 내 위치
        self.condition = "양호"   # 상태: 양호, 보통, 불량
    
    def get_type(self):
        return "일반도서"
    
    def get_loan_period(self):
        return 14  # 14일
    
    def update_condition(self, condition):
        """도서 상태 업데이트"""
        valid_conditions = ["양호", "보통", "불량"]
        if condition in valid_conditions:
            self.condition = condition
            return True
        return False


class EBook(Book):
    """전자책"""
    
    def __init__(self, title, author, isbn=None, genre="일반", 
                 publication_year=None, file_size=0, file_format="PDF"):
        super().__init__(title, author, isbn, genre, publication_year)
        self.file_size = file_size  # MB 단위
        self.file_format = file_format
        self.download_count = 0
        self.drm_enabled = True
    
    def get_type(self):
        return "전자책"
    
    def get_loan_period(self):
        return 7  # 7일
    
    def download(self):
        """다운로드 처리"""
        self.download_count += 1
        return f"{self.title}.{self.file_format.lower()}"
    
    def get_file_size_mb(self):
        """파일 크기 반환"""
        return f"{self.file_size} MB"


class AudioBook(Book):
    """오디오북"""
    
    def __init__(self, title, author, isbn=None, genre="일반", 
                 publication_year=None, duration=0, narrator=""):
        super().__init__(title, author, isbn, genre, publication_year)
        self.duration = duration  # 분 단위
        self.narrator = narrator  # 낭독자
        self.play_count = 0
    
    def get_type(self):
        return "오디오북"
    
    def get_loan_period(self):
        return 10  # 10일
    
    def get_duration_formatted(self):
        """재생 시간을 시:분 형식으로 반환"""
        hours = self.duration // 60
        minutes = self.duration % 60
        return f"{hours}시간 {minutes}분"
    
    def play(self):
        """재생 처리"""
        self.play_count += 1
        return f"'{self.title}' 오디오북을 재생합니다. (낭독: {self.narrator})"