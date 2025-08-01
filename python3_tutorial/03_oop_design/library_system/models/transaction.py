"""
거래(대출/반납) 관련 클래스
"""

from datetime import datetime, timedelta
from enum import Enum
import uuid

class TransactionType(Enum):
    """거래 유형"""
    BORROW = "대출"
    RETURN = "반납"
    RENEW = "연장"
    RESERVE = "예약"
    CANCEL_RESERVE = "예약취소"

class Transaction:
    """거래 클래스"""
    
    def __init__(self, member_id, book_id, transaction_type):
        self.id = str(uuid.uuid4())[:8]  # 고유 ID
        self.member_id = member_id
        self.book_id = book_id
        self.transaction_type = transaction_type
        self.transaction_date = datetime.now()
        self.due_date = None
        self.return_date = None
        self.fine_amount = 0
        self.is_completed = False
        self.notes = ""
        
    def set_due_date(self, days):
        """반납 예정일 설정"""
        self.due_date = self.transaction_date + timedelta(days=days)
    
    def complete_transaction(self):
        """거래 완료 처리"""
        self.is_completed = True
        if self.transaction_type == TransactionType.RETURN:
            self.return_date = datetime.now()
    
    def calculate_overdue_days(self):
        """연체일 계산"""
        if not self.due_date:
            return 0
        
        compare_date = self.return_date or datetime.now()
        
        if compare_date > self.due_date:
            return (compare_date - self.due_date).days
        return 0
    
    def is_overdue(self):
        """연체 여부 확인"""
        return self.calculate_overdue_days() > 0
    
    def get_status(self):
        """거래 상태 반환"""
        if self.is_completed:
            return "완료"
        elif self.is_overdue():
            return f"연체 ({self.calculate_overdue_days()}일)"
        else:
            return "진행중"
    
    def __str__(self):
        status = self.get_status()
        return (f"[{self.id}] {self.transaction_type.value} - "
                f"회원: {self.member_id}, 도서: {self.book_id}, "
                f"날짜: {self.transaction_date.strftime('%Y-%m-%d')}, "
                f"상태: {status}")
    
    def __repr__(self):
        return (f"Transaction('{self.member_id}', '{self.book_id}', "
                f"TransactionType.{self.transaction_type.name})")
    
    def to_dict(self):
        """딕셔너리로 변환 (저장용)"""
        return {
            'id': self.id,
            'member_id': self.member_id,
            'book_id': self.book_id,
            'transaction_type': self.transaction_type.value,
            'transaction_date': self.transaction_date.isoformat(),
            'due_date': self.due_date.isoformat() if self.due_date else None,
            'return_date': self.return_date.isoformat() if self.return_date else None,
            'fine_amount': self.fine_amount,
            'is_completed': self.is_completed,
            'notes': self.notes
        }
    
    @classmethod
    def from_dict(cls, data):
        """딕셔너리에서 객체 생성"""
        # TransactionType 찾기
        transaction_type = None
        for t in TransactionType:
            if t.value == data['transaction_type']:
                transaction_type = t
                break
        
        transaction = cls(
            data['member_id'],
            data['book_id'],
            transaction_type
        )
        
        transaction.id = data['id']
        transaction.transaction_date = datetime.fromisoformat(data['transaction_date'])
        
        if data['due_date']:
            transaction.due_date = datetime.fromisoformat(data['due_date'])
        
        if data['return_date']:
            transaction.return_date = datetime.fromisoformat(data['return_date'])
        
        transaction.fine_amount = data['fine_amount']
        transaction.is_completed = data['is_completed']
        transaction.notes = data['notes']
        
        return transaction


class TransactionHistory:
    """거래 이력 관리"""
    
    def __init__(self):
        self.transactions = []
    
    def add_transaction(self, transaction):
        """거래 추가"""
        self.transactions.append(transaction)
    
    def get_member_transactions(self, member_id):
        """특정 회원의 거래 이력"""
        return [t for t in self.transactions if t.member_id == member_id]
    
    def get_book_transactions(self, book_id):
        """특정 도서의 거래 이력"""
        return [t for t in self.transactions if t.book_id == book_id]
    
    def get_overdue_transactions(self):
        """연체 중인 거래 목록"""
        return [t for t in self.transactions 
                if not t.is_completed and t.is_overdue()]
    
    def get_transactions_by_date(self, start_date, end_date):
        """기간별 거래 조회"""
        return [t for t in self.transactions
                if start_date <= t.transaction_date <= end_date]
    
    def get_statistics(self):
        """거래 통계"""
        total = len(self.transactions)
        if total == 0:
            return {
                'total': 0,
                'borrows': 0,
                'returns': 0,
                'overdue': 0,
                'completed': 0
            }
        
        borrows = sum(1 for t in self.transactions 
                     if t.transaction_type == TransactionType.BORROW)
        returns = sum(1 for t in self.transactions 
                     if t.transaction_type == TransactionType.RETURN)
        overdue = len(self.get_overdue_transactions())
        completed = sum(1 for t in self.transactions if t.is_completed)
        
        return {
            'total': total,
            'borrows': borrows,
            'returns': returns,
            'overdue': overdue,
            'completed': completed,
            'completion_rate': f"{(completed/total)*100:.1f}%" if total > 0 else "0%"
        }