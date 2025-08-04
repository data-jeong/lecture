"""
도서관 관리 시스템 테스트
"""

import unittest
from datetime import datetime, timedelta
from library_system.models import PhysicalBook, EBook, AudioBook, RegularMember, PremiumMember, Transaction, TransactionType
from library_system.services import Library, Validator

class TestBookModels(unittest.TestCase):
    """도서 모델 테스트"""
    
    def test_physical_book_creation(self):
        """일반 도서 생성 테스트"""
        book = PhysicalBook("테스트 도서", "테스트 저자", pages=300, location="A-1")
        
        self.assertEqual(book.title, "테스트 도서")
        self.assertEqual(book.author, "테스트 저자")
        self.assertEqual(book.pages, 300)
        self.assertEqual(book.get_type(), "일반도서")
        self.assertEqual(book.get_loan_period(), 14)
        self.assertTrue(book.is_available)
    
    def test_ebook_creation(self):
        """전자책 생성 테스트"""
        book = EBook("전자책", "저자", file_size=10.5, file_format="PDF")
        
        self.assertEqual(book.get_type(), "전자책")
        self.assertEqual(book.get_loan_period(), 7)
        self.assertEqual(book.file_size, 10.5)
        self.assertEqual(book.download(), "전자책.pdf")
    
    def test_audiobook_creation(self):
        """오디오북 생성 테스트"""
        book = AudioBook("오디오북", "저자", duration=180, narrator="성우")
        
        self.assertEqual(book.get_type(), "오디오북")
        self.assertEqual(book.get_loan_period(), 10)
        self.assertEqual(book.get_duration_formatted(), "3시간 0분")
    
    def test_isbn_generation(self):
        """ISBN 자동 생성 테스트"""
        book1 = PhysicalBook("도서1", "저자1")
        book2 = PhysicalBook("도서2", "저자2")
        
        self.assertIsNotNone(book1.isbn)
        self.assertIsNotNone(book2.isbn)
        self.assertNotEqual(book1.isbn, book2.isbn)

class TestMemberModels(unittest.TestCase):
    """회원 모델 테스트"""
    
    def test_regular_member_creation(self):
        """일반 회원 생성 테스트"""
        member = RegularMember("홍길동", "hong@example.com", "010-1234-5678")
        
        self.assertEqual(member.name, "홍길동")
        self.assertEqual(member.email, "hong@example.com")
        self.assertEqual(member.get_max_borrow_count(), 3)
        self.assertEqual(member.get_late_fee_per_day(), 200)
    
    def test_premium_member_creation(self):
        """프리미엄 회원 생성 테스트"""
        member = PremiumMember("김프리미엄", "kim@example.com", "010-1111-2222")
        
        self.assertEqual(member.get_max_borrow_count(), 5)
        self.assertEqual(member.get_late_fee_per_day(), 100)
        self.assertTrue(member.is_membership_valid())
    
    def test_email_validation(self):
        """이메일 검증 테스트"""
        with self.assertRaises(ValueError):
            RegularMember("테스트", "invalid-email", "010-1234-5678")
    
    def test_phone_validation(self):
        """전화번호 검증 테스트"""
        # 정상적인 전화번호
        member1 = RegularMember("테스트1", "test1@example.com", "010-1234-5678")
        self.assertEqual(member1.phone, "01012345678")
        
        # 하이픈 없는 전화번호
        member2 = RegularMember("테스트2", "test2@example.com", "01012345678")
        self.assertEqual(member2.phone, "01012345678")
        
        # 잘못된 전화번호
        with self.assertRaises(ValueError):
            RegularMember("테스트3", "test3@example.com", "123-456")
    
    def test_member_can_borrow(self):
        """대출 가능 여부 테스트"""
        member = RegularMember("테스트", "test@example.com", "010-1234-5678")
        
        # 초기 상태: 대출 가능
        can_borrow, message = member.can_borrow()
        self.assertTrue(can_borrow)
        
        # 대출 한도 초과
        for i in range(3):
            member.add_borrowed_book(i)
        can_borrow, message = member.can_borrow()
        self.assertFalse(can_borrow)
        self.assertIn("한도", message)
        
        # 연체료 있음
        member.borrowed_books.clear()
        member.fines = 1000
        can_borrow, message = member.can_borrow()
        self.assertFalse(can_borrow)
        self.assertIn("연체료", message)

class TestLibrarySystem(unittest.TestCase):
    """도서관 시스템 테스트"""
    
    def setUp(self):
        """테스트 준비"""
        self.library = Library("테스트 도서관")
        
        # 테스트용 도서
        self.book1 = PhysicalBook("도서1", "저자1", pages=300)
        self.book2 = EBook("도서2", "저자2", file_size=5.0)
        
        # 테스트용 회원
        self.member1 = RegularMember("회원1", "member1@test.com", "010-1111-1111")
        self.member2 = RegularMember("회원2", "member2@test.com", "010-2222-2222")
        
        # 도서관에 추가
        self.library.add_book(self.book1)
        self.library.add_book(self.book2)
        self.library.add_member(self.member1)
        self.library.add_member(self.member2)
    
    def test_add_remove_book(self):
        """도서 추가/삭제 테스트"""
        # 추가
        book3 = AudioBook("도서3", "저자3", duration=120)
        success, message = self.library.add_book(book3)
        self.assertTrue(success)
        self.assertIn(book3.id, self.library.books)
        
        # 삭제
        success, message = self.library.remove_book(book3.id)
        self.assertTrue(success)
        self.assertNotIn(book3.id, self.library.books)
        
        # 대출 중인 도서 삭제 시도
        self.library.borrow_book(self.member1.id, self.book1.id)
        success, message = self.library.remove_book(self.book1.id)
        self.assertFalse(success)
    
    def test_borrow_return_book(self):
        """도서 대출/반납 테스트"""
        # 대출
        success, message = self.library.borrow_book(self.member1.id, self.book1.id)
        self.assertTrue(success)
        self.assertFalse(self.book1.is_available)
        self.assertEqual(self.book1.borrowed_by, self.member1.id)
        self.assertIn(self.book1.id, self.member1.borrowed_books)
        
        # 중복 대출 시도
        success, message = self.library.borrow_book(self.member2.id, self.book1.id)
        self.assertFalse(success)
        
        # 반납
        success, message = self.library.return_book(self.member1.id, self.book1.id)
        self.assertTrue(success)
        self.assertTrue(self.book1.is_available)
        self.assertIsNone(self.book1.borrowed_by)
        self.assertNotIn(self.book1.id, self.member1.borrowed_books)
    
    def test_overdue_calculation(self):
        """연체료 계산 테스트"""
        # 대출
        self.library.borrow_book(self.member1.id, self.book1.id)
        
        # 반납일을 과거로 설정 (3일 연체)
        self.book1.return_date = datetime.now() - timedelta(days=3)
        
        # 반납
        success, message = self.library.return_book(self.member1.id, self.book1.id)
        self.assertTrue(success)
        
        # 연체료 확인 (3일 * 200원)
        self.assertEqual(self.member1.fines, 600)
    
    def test_reservation_system(self):
        """예약 시스템 테스트"""
        # 도서 대출
        self.library.borrow_book(self.member1.id, self.book1.id)
        
        # 예약
        success, message = self.library.reserve_book(self.member2.id, self.book1.id)
        self.assertTrue(success)
        self.assertIn(self.member2.id, self.book1.reservation_queue)
        
        # 중복 예약 시도
        success, message = self.library.reserve_book(self.member2.id, self.book1.id)
        self.assertFalse(success)
        
        # 대출 가능한 도서 예약 시도
        success, message = self.library.reserve_book(self.member1.id, self.book2.id)
        self.assertFalse(success)
    
    def test_search_functionality(self):
        """검색 기능 테스트"""
        # 키워드 검색
        results = self.library.search_books(keyword="도서1")
        self.assertEqual(len(results), 1)
        self.assertEqual(results[0].title, "도서1")
        
        # 저자 검색
        results = self.library.search_books(author="저자2")
        self.assertEqual(len(results), 1)
        self.assertEqual(results[0].author, "저자2")
        
        # 대출 가능 도서만 검색
        self.library.borrow_book(self.member1.id, self.book1.id)
        results = self.library.search_books(available_only=True)
        self.assertEqual(len(results), 1)
        self.assertEqual(results[0].id, self.book2.id)

class TestTransaction(unittest.TestCase):
    """거래 테스트"""
    
    def test_transaction_creation(self):
        """거래 생성 테스트"""
        transaction = Transaction("M0001", 1000, TransactionType.BORROW)
        
        self.assertEqual(transaction.member_id, "M0001")
        self.assertEqual(transaction.book_id, 1000)
        self.assertEqual(transaction.transaction_type, TransactionType.BORROW)
        self.assertFalse(transaction.is_completed)
    
    def test_overdue_calculation(self):
        """거래 연체일 계산 테스트"""
        transaction = Transaction("M0001", 1000, TransactionType.BORROW)
        transaction.set_due_date(14)
        
        # 연체 전
        self.assertEqual(transaction.calculate_overdue_days(), 0)
        self.assertFalse(transaction.is_overdue())
        
        # 연체 시뮬레이션
        transaction.due_date = datetime.now() - timedelta(days=3)
        self.assertEqual(transaction.calculate_overdue_days(), 3)
        self.assertTrue(transaction.is_overdue())

class TestValidator(unittest.TestCase):
    """검증기 테스트"""
    
    def test_email_validation(self):
        """이메일 검증 테스트"""
        self.assertTrue(Validator.validate_email("test@example.com"))
        self.assertTrue(Validator.validate_email("user.name@domain.co.kr"))
        self.assertFalse(Validator.validate_email("invalid-email"))
        self.assertFalse(Validator.validate_email("@example.com"))
    
    def test_phone_validation(self):
        """전화번호 검증 테스트"""
        self.assertTrue(Validator.validate_phone("010-1234-5678"))
        self.assertTrue(Validator.validate_phone("01012345678"))
        self.assertTrue(Validator.validate_phone("02-123-4567"))
        self.assertFalse(Validator.validate_phone("123-456"))
        self.assertFalse(Validator.validate_phone("010-12-34"))
    
    def test_year_validation(self):
        """연도 검증 테스트"""
        current_year = datetime.now().year
        
        self.assertTrue(Validator.validate_year(2020))
        self.assertTrue(Validator.validate_year(current_year))
        self.assertFalse(Validator.validate_year(999))
        self.assertFalse(Validator.validate_year(current_year + 1))

def run_all_tests():
    """모든 테스트 실행"""
    unittest.main(verbosity=2)

if __name__ == "__main__":
    print("도서관 관리 시스템 테스트 시작...\n")
    run_all_tests()