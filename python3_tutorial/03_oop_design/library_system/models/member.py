"""
회원 관련 클래스
"""

from abc import ABC, abstractmethod
from datetime import datetime, timedelta
import re

class Member(ABC):
    """회원 추상 클래스"""
    
    # 클래스 변수
    _id_counter = 1
    
    def __init__(self, name, email, phone):
        self.id = f"M{Member._id_counter:04d}"
        Member._id_counter += 1
        
        self.name = name
        self.email = self._validate_email(email)
        self.phone = self._validate_phone(phone)
        self.registration_date = datetime.now()
        self.is_active = True
        self.borrowed_books = []  # 현재 대출 중인 도서
        self.borrow_history = []  # 대출 이력
        self.fines = 0  # 연체료
        
    def _validate_email(self, email):
        """이메일 유효성 검사"""
        pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        if re.match(pattern, email):
            return email
        raise ValueError("유효하지 않은 이메일 형식입니다.")
    
    def _validate_phone(self, phone):
        """전화번호 유효성 검사"""
        # 하이픈 제거
        phone = phone.replace("-", "")
        if len(phone) in [10, 11] and phone.isdigit():
            return phone
        raise ValueError("유효하지 않은 전화번호 형식입니다.")
    
    @abstractmethod
    def get_max_borrow_count(self):
        """최대 대출 가능 권수"""
        pass
    
    @abstractmethod
    def get_late_fee_per_day(self):
        """일일 연체료"""
        pass
    
    @abstractmethod
    def get_member_type(self):
        """회원 타입"""
        pass
    
    def can_borrow(self):
        """대출 가능 여부 확인"""
        if not self.is_active:
            return False, "비활성 회원입니다."
        
        if self.fines > 0:
            return False, f"미납 연체료가 있습니다. (₩{self.fines:,})"
        
        if len(self.borrowed_books) >= self.get_max_borrow_count():
            return False, f"대출 한도를 초과했습니다. (최대 {self.get_max_borrow_count()}권)"
        
        return True, "대출 가능"
    
    def add_borrowed_book(self, book_id):
        """대출 도서 추가"""
        if book_id not in self.borrowed_books:
            self.borrowed_books.append(book_id)
            self.borrow_history.append({
                'book_id': book_id,
                'borrow_date': datetime.now(),
                'return_date': None
            })
            return True
        return False
    
    def remove_borrowed_book(self, book_id):
        """대출 도서 반납"""
        if book_id in self.borrowed_books:
            self.borrowed_books.remove(book_id)
            # 대출 이력 업데이트
            for record in reversed(self.borrow_history):
                if record['book_id'] == book_id and record['return_date'] is None:
                    record['return_date'] = datetime.now()
                    break
            return True
        return False
    
    def calculate_fine(self, overdue_days):
        """연체료 계산"""
        return overdue_days * self.get_late_fee_per_day()
    
    def pay_fine(self, amount):
        """연체료 납부"""
        if amount <= 0:
            return False, "납부 금액은 0보다 커야 합니다."
        
        if amount > self.fines:
            return False, f"납부 금액이 연체료보다 큽니다. (연체료: ₩{self.fines:,})"
        
        self.fines -= amount
        return True, f"₩{amount:,} 납부 완료. 남은 연체료: ₩{self.fines:,}"
    
    def get_borrow_count(self):
        """현재 대출 권수"""
        return len(self.borrowed_books)
    
    def __str__(self):
        return f"[{self.id}] {self.name} ({self.get_member_type()}) - 대출: {self.get_borrow_count()}권"
    
    def __repr__(self):
        return f"{self.__class__.__name__}('{self.name}', '{self.email}', '{self.phone}')"


class RegularMember(Member):
    """일반 회원"""
    
    def get_max_borrow_count(self):
        return 3  # 최대 3권
    
    def get_late_fee_per_day(self):
        return 200  # 일일 200원
    
    def get_member_type(self):
        return "일반회원"


class PremiumMember(Member):
    """프리미엄 회원"""
    
    def __init__(self, name, email, phone, membership_fee=50000):
        super().__init__(name, email, phone)
        self.membership_fee = membership_fee
        self.membership_expiry = datetime.now() + timedelta(days=365)
        self.priority_reservation = True  # 우선 예약 권한
    
    def get_max_borrow_count(self):
        return 5  # 최대 5권
    
    def get_late_fee_per_day(self):
        return 100  # 일일 100원 (50% 할인)
    
    def get_member_type(self):
        return "프리미엄회원"
    
    def is_membership_valid(self):
        """멤버십 유효성 확인"""
        return datetime.now() < self.membership_expiry
    
    def renew_membership(self, months=12):
        """멤버십 갱신"""
        if months < 1:
            return False, "갱신 기간은 1개월 이상이어야 합니다."
        
        # 현재 시점이나 만료일 중 더 늦은 날짜부터 연장
        base_date = max(datetime.now(), self.membership_expiry)
        self.membership_expiry = base_date + timedelta(days=30 * months)
        
        fee = self.membership_fee * (months / 12)
        return True, f"멤버십이 {months}개월 연장되었습니다. 요금: ₩{fee:,.0f}"
    
    def get_discount_rate(self):
        """할인율 반환"""
        if self.is_membership_valid():
            return 0.5  # 50% 할인
        return 0  # 할인 없음