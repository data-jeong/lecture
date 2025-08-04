"""
도서관 시스템 메인 클래스
"""

from datetime import datetime, timedelta
from ..models import (
    Book, PhysicalBook, EBook, AudioBook,
    Member, RegularMember, PremiumMember,
    Transaction, TransactionType, TransactionHistory
)
from ..utils.storage import Storage

class Library:
    """도서관 관리 시스템"""
    
    def __init__(self, name="중앙도서관"):
        self.name = name
        self.books = {}  # {book_id: Book}
        self.members = {}  # {member_id: Member}
        self.transaction_history = TransactionHistory()
        self.storage = Storage()
        
        # 설정
        self.max_renew_count = 1  # 최대 연장 횟수
        self.reservation_hold_days = 3  # 예약 도서 보관 기간
        
    def add_book(self, book):
        """도서 추가"""
        if book.id in self.books:
            return False, "이미 등록된 도서 ID입니다."
        
        self.books[book.id] = book
        return True, f"도서 '{book.title}'이(가) 등록되었습니다."
    
    def remove_book(self, book_id):
        """도서 삭제"""
        if book_id not in self.books:
            return False, "존재하지 않는 도서입니다."
        
        book = self.books[book_id]
        if not book.is_available:
            return False, "대출 중인 도서는 삭제할 수 없습니다."
        
        del self.books[book_id]
        return True, f"도서 '{book.title}'이(가) 삭제되었습니다."
    
    def add_member(self, member):
        """회원 등록"""
        if member.id in self.members:
            return False, "이미 등록된 회원 ID입니다."
        
        self.members[member.id] = member
        return True, f"회원 '{member.name}'님이 등록되었습니다."
    
    def remove_member(self, member_id):
        """회원 탈퇴"""
        if member_id not in self.members:
            return False, "존재하지 않는 회원입니다."
        
        member = self.members[member_id]
        if member.borrowed_books:
            return False, "대출 중인 도서가 있는 회원은 탈퇴할 수 없습니다."
        
        if member.fines > 0:
            return False, f"미납 연체료가 있습니다. (₩{member.fines:,})"
        
        member.is_active = False
        return True, f"회원 '{member.name}'님이 탈퇴 처리되었습니다."
    
    def borrow_book(self, member_id, book_id):
        """도서 대출"""
        # 유효성 검사
        if member_id not in self.members:
            return False, "존재하지 않는 회원입니다."
        
        if book_id not in self.books:
            return False, "존재하지 않는 도서입니다."
        
        member = self.members[member_id]
        book = self.books[book_id]
        
        # 회원 대출 가능 여부 확인
        can_borrow, message = member.can_borrow()
        if not can_borrow:
            return False, message
        
        # 도서 대출 가능 여부 확인
        if not book.is_available:
            return False, f"이미 대출 중인 도서입니다. (대출자: {book.borrowed_by})"
        
        # 대출 처리
        book.is_available = False
        book.borrowed_by = member_id
        book.borrowed_date = datetime.now()
        book.return_date = datetime.now() + timedelta(days=book.get_loan_period())
        
        member.add_borrowed_book(book_id)
        
        # 거래 기록
        transaction = Transaction(member_id, book_id, TransactionType.BORROW)
        transaction.set_due_date(book.get_loan_period())
        self.transaction_history.add_transaction(transaction)
        
        return True, (f"도서 '{book.title}'이(가) 대출되었습니다.\n"
                     f"반납 예정일: {book.return_date.strftime('%Y-%m-%d')}")
    
    def return_book(self, member_id, book_id):
        """도서 반납"""
        if member_id not in self.members:
            return False, "존재하지 않는 회원입니다."
        
        if book_id not in self.books:
            return False, "존재하지 않는 도서입니다."
        
        member = self.members[member_id]
        book = self.books[book_id]
        
        if book.borrowed_by != member_id:
            return False, "해당 회원이 대출한 도서가 아닙니다."
        
        # 연체료 계산
        overdue_days = 0
        fine = 0
        if book.return_date and datetime.now() > book.return_date:
            overdue_days = (datetime.now() - book.return_date).days
            fine = member.calculate_fine(overdue_days)
            member.fines += fine
        
        # 반납 처리
        book.is_available = True
        book.borrowed_by = None
        book.borrowed_date = None
        book.return_date = None
        
        member.remove_borrowed_book(book_id)
        
        # 거래 기록
        transaction = Transaction(member_id, book_id, TransactionType.RETURN)
        transaction.fine_amount = fine
        transaction.complete_transaction()
        self.transaction_history.add_transaction(transaction)
        
        # 예약자 확인
        next_reserver = book.get_next_reserver()
        if next_reserver:
            book.remove_reservation(next_reserver)
            reservation_msg = f"\n다음 예약자({next_reserver})에게 알림이 전송되었습니다."
        else:
            reservation_msg = ""
        
        if fine > 0:
            return True, (f"도서 '{book.title}'이(가) 반납되었습니다.\n"
                         f"연체일: {overdue_days}일, 연체료: ₩{fine:,}{reservation_msg}")
        else:
            return True, f"도서 '{book.title}'이(가) 반납되었습니다.{reservation_msg}"
    
    def renew_book(self, member_id, book_id):
        """도서 대출 연장"""
        if member_id not in self.members:
            return False, "존재하지 않는 회원입니다."
        
        if book_id not in self.books:
            return False, "존재하지 않는 도서입니다."
        
        book = self.books[book_id]
        
        if book.borrowed_by != member_id:
            return False, "해당 회원이 대출한 도서가 아닙니다."
        
        # 연체 확인
        if book.is_overdue():
            return False, "연체된 도서는 연장할 수 없습니다."
        
        # 예약 확인
        if book.reservation_queue:
            return False, "예약자가 있는 도서는 연장할 수 없습니다."
        
        # 연장 처리
        book.return_date += timedelta(days=7)  # 7일 연장
        
        # 거래 기록
        transaction = Transaction(member_id, book_id, TransactionType.RENEW)
        self.transaction_history.add_transaction(transaction)
        
        return True, f"도서 '{book.title}'의 반납일이 {book.return_date.strftime('%Y-%m-%d')}로 연장되었습니다."
    
    def reserve_book(self, member_id, book_id):
        """도서 예약"""
        if member_id not in self.members:
            return False, "존재하지 않는 회원입니다."
        
        if book_id not in self.books:
            return False, "존재하지 않는 도서입니다."
        
        book = self.books[book_id]
        member = self.members[member_id]
        
        if book.is_available:
            return False, "대출 가능한 도서는 예약할 수 없습니다."
        
        if book.borrowed_by == member_id:
            return False, "본인이 대출한 도서는 예약할 수 없습니다."
        
        # 예약 추가
        if book.add_reservation(member_id):
            position = len(book.reservation_queue)
            
            # 거래 기록
            transaction = Transaction(member_id, book_id, TransactionType.RESERVE)
            self.transaction_history.add_transaction(transaction)
            
            return True, f"도서 '{book.title}'이(가) 예약되었습니다. (대기 순번: {position}번)"
        else:
            return False, "이미 예약한 도서입니다."
    
    def search_books(self, keyword=None, author=None, genre=None, available_only=False):
        """도서 검색"""
        results = []
        
        for book in self.books.values():
            # 대출 가능 도서만 검색
            if available_only and not book.is_available:
                continue
            
            # 키워드 검색 (제목)
            if keyword and keyword.lower() not in book.title.lower():
                continue
            
            # 저자 검색
            if author and author.lower() not in book.author.lower():
                continue
            
            # 장르 검색
            if genre and genre != book.genre:
                continue
            
            results.append(book)
        
        # 제목 순 정렬
        results.sort(key=lambda x: x.title)
        return results
    
    def get_member_info(self, member_id):
        """회원 정보 조회"""
        if member_id not in self.members:
            return None
        
        member = self.members[member_id]
        borrowed_books = [self.books[book_id] for book_id in member.borrowed_books
                         if book_id in self.books]
        
        return {
            'member': member,
            'borrowed_books': borrowed_books,
            'transactions': self.transaction_history.get_member_transactions(member_id)
        }
    
    def get_overdue_books(self):
        """연체 도서 목록"""
        overdue_list = []
        
        for book in self.books.values():
            if not book.is_available and book.is_overdue():
                member = self.members.get(book.borrowed_by)
                if member:
                    overdue_days = (datetime.now() - book.return_date).days
                    fine = member.calculate_fine(overdue_days)
                    
                    overdue_list.append({
                        'book': book,
                        'member': member,
                        'overdue_days': overdue_days,
                        'fine': fine
                    })
        
        # 연체일 순으로 정렬
        overdue_list.sort(key=lambda x: x['overdue_days'], reverse=True)
        return overdue_list
    
    def get_statistics(self):
        """도서관 통계"""
        total_books = len(self.books)
        available_books = sum(1 for book in self.books.values() if book.is_available)
        
        book_types = {}
        for book in self.books.values():
            book_type = book.get_type()
            book_types[book_type] = book_types.get(book_type, 0) + 1
        
        total_members = len(self.members)
        active_members = sum(1 for member in self.members.values() if member.is_active)
        
        member_types = {}
        for member in self.members.values():
            if member.is_active:
                member_type = member.get_member_type()
                member_types[member_type] = member_types.get(member_type, 0) + 1
        
        transaction_stats = self.transaction_history.get_statistics()
        
        return {
            'books': {
                'total': total_books,
                'available': available_books,
                'borrowed': total_books - available_books,
                'types': book_types
            },
            'members': {
                'total': total_members,
                'active': active_members,
                'types': member_types
            },
            'transactions': transaction_stats
        }
    
    def save_data(self, filename="library_data.json"):
        """데이터 저장"""
        data = {
            'name': self.name,
            'books': {book_id: self._book_to_dict(book) 
                     for book_id, book in self.books.items()},
            'members': {member_id: self._member_to_dict(member)
                       for member_id, member in self.members.items()},
            'transactions': [t.to_dict() for t in self.transaction_history.transactions]
        }
        return self.storage.save(data, filename)
    
    def _book_to_dict(self, book):
        """도서 객체를 딕셔너리로 변환"""
        data = {
            'type': book.__class__.__name__,
            'id': book.id,
            'title': book.title,
            'author': book.author,
            'isbn': book.isbn,
            'genre': book.genre,
            'publication_year': book.publication_year,
            'is_available': book.is_available,
            'borrowed_by': book.borrowed_by,
            'borrowed_date': book.borrowed_date.isoformat() if book.borrowed_date else None,
            'return_date': book.return_date.isoformat() if book.return_date else None,
            'reservation_queue': book.reservation_queue
        }
        
        # 타입별 추가 정보
        if isinstance(book, PhysicalBook):
            data.update({
                'pages': book.pages,
                'location': book.location,
                'condition': book.condition
            })
        elif isinstance(book, EBook):
            data.update({
                'file_size': book.file_size,
                'file_format': book.file_format,
                'download_count': book.download_count
            })
        elif isinstance(book, AudioBook):
            data.update({
                'duration': book.duration,
                'narrator': book.narrator,
                'play_count': book.play_count
            })
        
        return data
    
    def _member_to_dict(self, member):
        """회원 객체를 딕셔너리로 변환"""
        data = {
            'type': member.__class__.__name__,
            'id': member.id,
            'name': member.name,
            'email': member.email,
            'phone': member.phone,
            'registration_date': member.registration_date.isoformat(),
            'is_active': member.is_active,
            'borrowed_books': member.borrowed_books,
            'fines': member.fines
        }
        
        if isinstance(member, PremiumMember):
            data.update({
                'membership_fee': member.membership_fee,
                'membership_expiry': member.membership_expiry.isoformat()
            })
        
        return data