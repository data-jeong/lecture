"""
도서관 관리 시스템 사용 예제
"""

from library_system.models import PhysicalBook, EBook, AudioBook, RegularMember, PremiumMember
from library_system.services import Library
from library_system.utils import generate_report
from datetime import datetime, timedelta

def example_basic_operations():
    """기본 작업 예제"""
    print("=== 기본 작업 예제 ===\n")
    
    # 도서관 생성
    library = Library("예제 도서관")
    
    # 도서 추가
    book1 = PhysicalBook("파이썬 완벽 가이드", "귀도 반 로섬", pages=600, location="A-1")
    book2 = EBook("데이터 과학 입문", "김데이터", file_size=15.5, file_format="PDF")
    book3 = AudioBook("영어 회화 100일의 기적", "제임스", duration=600, narrator="네이티브")
    
    library.add_book(book1)
    library.add_book(book2)
    library.add_book(book3)
    
    print("도서 3권이 추가되었습니다.")
    
    # 회원 추가
    member1 = RegularMember("홍길동", "hong@example.com", "010-1111-2222")
    member2 = PremiumMember("김프리미엄", "kim@example.com", "010-3333-4444")
    
    library.add_member(member1)
    library.add_member(member2)
    
    print("회원 2명이 등록되었습니다.\n")
    
    # 도서 대출
    success, message = library.borrow_book(member1.id, book1.id)
    print(f"대출 시도: {message}")
    
    # 도서 정보 확인
    print(f"\n도서 상태: {book1}")
    print(f"회원 정보: {member1}")

def example_inheritance():
    """상속 예제"""
    print("\n\n=== 상속 예제 ===\n")
    
    # 다양한 도서 타입
    books = [
        PhysicalBook("소설책", "작가1", pages=300),
        EBook("전자책", "작가2", file_size=5.0),
        AudioBook("오디오북", "작가3", duration=180, narrator="성우")
    ]
    
    # 다형성 활용
    for book in books:
        print(f"도서: {book.title}")
        print(f"  타입: {book.get_type()}")
        print(f"  대출 기간: {book.get_loan_period()}일")
        print()

def example_member_benefits():
    """회원 혜택 비교"""
    print("\n=== 회원 혜택 비교 ===\n")
    
    regular = RegularMember("일반이", "regular@example.com", "010-1111-1111")
    premium = PremiumMember("프리미엄", "premium@example.com", "010-2222-2222")
    
    print(f"{regular.get_member_type()}:")
    print(f"  최대 대출: {regular.get_max_borrow_count()}권")
    print(f"  연체료: {regular.get_late_fee_per_day()}원/일")
    
    print(f"\n{premium.get_member_type()}:")
    print(f"  최대 대출: {premium.get_max_borrow_count()}권")
    print(f"  연체료: {premium.get_late_fee_per_day()}원/일")
    print(f"  멤버십 만료일: {premium.membership_expiry.strftime('%Y-%m-%d')}")

def example_transaction_flow():
    """거래 흐름 예제"""
    print("\n\n=== 거래 흐름 예제 ===\n")
    
    library = Library("거래 예제 도서관")
    
    # 도서와 회원 준비
    book = PhysicalBook("베스트셀러", "유명작가", pages=400)
    member = RegularMember("독서왕", "reader@example.com", "010-5555-5555")
    
    library.add_book(book)
    library.add_member(member)
    
    # 1. 대출
    print("1. 도서 대출")
    success, message = library.borrow_book(member.id, book.id)
    print(f"   {message}")
    
    # 2. 대출 연장 시도
    print("\n2. 대출 연장")
    success, message = library.renew_book(member.id, book.id)
    print(f"   {message}")
    
    # 3. 반납 (연체 시뮬레이션을 위해 반납일 조작)
    print("\n3. 연체 후 반납 시뮬레이션")
    book.return_date = datetime.now() - timedelta(days=3)  # 3일 연체
    success, message = library.return_book(member.id, book.id)
    print(f"   {message}")
    
    # 4. 연체료 확인
    print(f"\n4. 회원 연체료: ₩{member.fines:,}")

def example_reservation_system():
    """예약 시스템 예제"""
    print("\n\n=== 예약 시스템 예제 ===\n")
    
    library = Library("예약 도서관")
    
    # 인기 도서
    popular_book = PhysicalBook("인기도서", "베스트작가", pages=500)
    library.add_book(popular_book)
    
    # 여러 회원
    members = [
        RegularMember(f"회원{i}", f"member{i}@example.com", f"010-{i}000-{i}000")
        for i in range(1, 4)
    ]
    
    for member in members:
        library.add_member(member)
    
    # 첫 번째 회원이 대출
    library.borrow_book(members[0].id, popular_book.id)
    print(f"{members[0].name}이(가) 도서를 대출했습니다.")
    
    # 다른 회원들이 예약
    for member in members[1:]:
        success, message = library.reserve_book(member.id, popular_book.id)
        print(f"{member.name}: {message}")
    
    # 예약 대기열 확인
    print(f"\n예약 대기열: {popular_book.reservation_queue}")

def example_search_functionality():
    """검색 기능 예제"""
    print("\n\n=== 검색 기능 예제 ===\n")
    
    library = Library("검색 도서관")
    
    # 다양한 도서 추가
    books_data = [
        ("파이썬 프로그래밍", "김파이썬", "컴퓨터"),
        ("파이썬 데이터 분석", "이분석", "컴퓨터"),
        ("자바 프로그래밍", "박자바", "컴퓨터"),
        ("영어 회화", "John", "외국어"),
        ("한국사", "역사가", "역사")
    ]
    
    for title, author, genre in books_data:
        book = PhysicalBook(title, author, genre=genre, pages=300)
        library.add_book(book)
    
    # 검색 테스트
    print("1. '파이썬' 검색:")
    results = library.search_books(keyword="파이썬")
    for book in results:
        print(f"   - {book.title}")
    
    print("\n2. 장르 '컴퓨터' 검색:")
    results = library.search_books(genre="컴퓨터")
    for book in results:
        print(f"   - {book.title}")
    
    print("\n3. 대출 가능한 도서만 검색:")
    results = library.search_books(available_only=True)
    print(f"   대출 가능 도서: {len(results)}권")

def example_statistics_and_reports():
    """통계 및 리포트 예제"""
    print("\n\n=== 통계 및 리포트 예제 ===\n")
    
    library = Library("통계 도서관")
    
    # 샘플 데이터 생성
    for i in range(5):
        book = PhysicalBook(f"도서{i+1}", f"저자{i+1}", pages=200+i*50)
        library.add_book(book)
    
    for i in range(3):
        member = RegularMember(f"회원{i+1}", f"user{i+1}@example.com", f"010-{i}111-1111")
        library.add_member(member)
    
    # 일부 대출 처리
    library.borrow_book("M0001", 1000)
    library.borrow_book("M0002", 1001)
    
    # 통계 출력
    stats = library.get_statistics()
    print("도서관 통계:")
    print(f"  총 도서: {stats['books']['total']}권")
    print(f"  대출 가능: {stats['books']['available']}권")
    print(f"  대출 중: {stats['books']['borrowed']}권")
    print(f"  총 회원: {stats['members']['total']}명")
    print(f"  활성 회원: {stats['members']['active']}명")

def example_polymorphism():
    """다형성 예제"""
    print("\n\n=== 다형성 예제 ===\n")
    
    # 다양한 도서 타입을 하나의 리스트에서 처리
    books = [
        PhysicalBook("종이책", "저자A", pages=300),
        EBook("전자책", "저자B", file_size=2.5),
        AudioBook("오디오북", "저자C", duration=240, narrator="성우D")
    ]
    
    print("모든 도서의 대출 기간:")
    for book in books:
        # 각 도서 타입에 맞는 메서드가 호출됨 (다형성)
        print(f"  {book.title} ({book.get_type()}): {book.get_loan_period()}일")
    
    # 타입별 특수 기능
    print("\n타입별 특수 기능:")
    for book in books:
        if isinstance(book, PhysicalBook):
            print(f"  {book.title}: 위치 - {book.location}")
        elif isinstance(book, EBook):
            print(f"  {book.title}: {book.download()}")
        elif isinstance(book, AudioBook):
            print(f"  {book.title}: {book.play()}")

def example_encapsulation():
    """캡슐화 예제"""
    print("\n\n=== 캡슐화 예제 ===\n")
    
    # Member 클래스의 캡슐화된 속성
    member = RegularMember("테스트", "test@example.com", "010-1234-5678")
    
    print("Public 속성 접근:")
    print(f"  이름: {member.name}")
    print(f"  ID: {member.id}")
    
    print("\nPrivate 속성 보호:")
    try:
        # 직접 접근 시도 (실패)
        print(member.__email)
    except AttributeError:
        print("  Private 속성에 직접 접근할 수 없습니다.")
    
    # 올바른 접근 방법
    print(f"  이메일 (property): {member.email}")
    
    # 메서드를 통한 상태 변경
    can_borrow, message = member.can_borrow()
    print(f"\n대출 가능 여부: {can_borrow} - {message}")

def run_all_examples():
    """모든 예제 실행"""
    print("도서관 관리 시스템 예제 모음")
    print("=" * 60)
    
    example_basic_operations()
    example_inheritance()
    example_member_benefits()
    example_transaction_flow()
    example_reservation_system()
    example_search_functionality()
    example_statistics_and_reports()
    example_polymorphism()
    example_encapsulation()
    
    print("\n" + "=" * 60)
    print("모든 예제가 완료되었습니다!")

if __name__ == "__main__":
    run_all_examples()