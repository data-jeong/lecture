"""
도서관 관리 시스템 메인 프로그램
"""

import sys
from library_system.services import Library
from library_system.models import PhysicalBook, EBook, AudioBook, RegularMember, PremiumMember
from library_system.services import Validator
from library_system.utils import generate_report

class LibraryApp:
    """도서관 애플리케이션"""
    
    def __init__(self):
        self.library = Library("파이썬 도서관")
        self.validator = Validator()
        self._load_sample_data()
    
    def _load_sample_data(self):
        """샘플 데이터 로드"""
        # 도서 추가
        books = [
            PhysicalBook("파이썬 프로그래밍", "김파이썬", genre="컴퓨터", pages=500, location="A-1"),
            PhysicalBook("데이터 분석 입문", "이분석", genre="컴퓨터", pages=400, location="A-2"),
            EBook("머신러닝 가이드", "박머신", genre="컴퓨터", file_size=25, file_format="PDF"),
            AudioBook("영어 회화 마스터", "John Smith", genre="외국어", duration=300, narrator="Jane Doe"),
            PhysicalBook("삼국지", "나관중", genre="소설", pages=800, location="B-1"),
        ]
        
        for book in books:
            self.library.add_book(book)
        
        # 회원 추가
        members = [
            RegularMember("김철수", "kim@example.com", "010-1234-5678"),
            RegularMember("이영희", "lee@example.com", "010-2345-6789"),
            PremiumMember("박프리미엄", "park@example.com", "010-3456-7890"),
        ]
        
        for member in members:
            self.library.add_member(member)
    
    def run(self):
        """메인 실행"""
        while True:
            self._display_menu()
            choice = input("\n선택하세요: ").strip()
            
            if choice == "0":
                print("\n프로그램을 종료합니다.")
                self._save_and_exit()
                break
            
            self._handle_choice(choice)
    
    def _display_menu(self):
        """메뉴 표시"""
        print("\n" + "="*50)
        print(f"{self.library.name} 관리 시스템")
        print("="*50)
        print("1. 도서 관리")
        print("2. 회원 관리")
        print("3. 대출/반납")
        print("4. 검색")
        print("5. 통계 및 리포트")
        print("6. 데이터 관리")
        print("0. 종료")
    
    def _handle_choice(self, choice):
        """메뉴 선택 처리"""
        if choice == "1":
            self._book_management()
        elif choice == "2":
            self._member_management()
        elif choice == "3":
            self._loan_management()
        elif choice == "4":
            self._search_menu()
        elif choice == "5":
            self._statistics_menu()
        elif choice == "6":
            self._data_management()
        else:
            print("잘못된 선택입니다.")
    
    def _book_management(self):
        """도서 관리"""
        print("\n[도서 관리]")
        print("1. 도서 추가")
        print("2. 도서 삭제")
        print("3. 도서 목록")
        print("4. 도서 상세 정보")
        
        choice = input("선택: ").strip()
        
        if choice == "1":
            self._add_book()
        elif choice == "2":
            self._remove_book()
        elif choice == "3":
            self._list_books()
        elif choice == "4":
            self._book_detail()
    
    def _add_book(self):
        """도서 추가"""
        print("\n[도서 추가]")
        print("1. 일반도서")
        print("2. 전자책")
        print("3. 오디오북")
        
        book_type = input("도서 유형: ").strip()
        
        # 공통 정보
        title = input("제목: ").strip()
        author = input("저자: ").strip()
        genre = input("장르 (기본: 일반): ").strip() or "일반"
        
        if book_type == "1":
            pages = int(input("페이지 수: ") or "0")
            location = input("위치: ").strip()
            book = PhysicalBook(title, author, genre=genre, pages=pages, location=location)
        elif book_type == "2":
            file_size = float(input("파일 크기(MB): ") or "0")
            file_format = input("파일 형식 (기본: PDF): ").strip() or "PDF"
            book = EBook(title, author, genre=genre, file_size=file_size, file_format=file_format)
        elif book_type == "3":
            duration = int(input("재생 시간(분): ") or "0")
            narrator = input("낭독자: ").strip()
            book = AudioBook(title, author, genre=genre, duration=duration, narrator=narrator)
        else:
            print("잘못된 선택입니다.")
            return
        
        success, message = self.library.add_book(book)
        print(message)
    
    def _remove_book(self):
        """도서 삭제"""
        book_id = input("삭제할 도서 ID: ").strip()
        try:
            book_id = int(book_id)
            success, message = self.library.remove_book(book_id)
            print(message)
        except ValueError:
            print("올바른 ID를 입력하세요.")
    
    def _list_books(self):
        """도서 목록"""
        print("\n[도서 목록]")
        if not self.library.books:
            print("등록된 도서가 없습니다.")
            return
        
        for book in self.library.books.values():
            print(book)
    
    def _book_detail(self):
        """도서 상세 정보"""
        book_id = input("도서 ID: ").strip()
        try:
            book_id = int(book_id)
            if book_id in self.library.books:
                book = self.library.books[book_id]
                print(f"\n[도서 상세 정보]")
                print(f"ID: {book.id}")
                print(f"제목: {book.title}")
                print(f"저자: {book.author}")
                print(f"ISBN: {book.isbn}")
                print(f"장르: {book.genre}")
                print(f"출판년도: {book.publication_year}")
                print(f"타입: {book.get_type()}")
                print(f"대출 기간: {book.get_loan_period()}일")
                print(f"상태: {'대출 가능' if book.is_available else f'대출 중 ({book.borrowed_by})'}")
                
                if book.reservation_queue:
                    print(f"예약 대기: {len(book.reservation_queue)}명")
            else:
                print("존재하지 않는 도서입니다.")
        except ValueError:
            print("올바른 ID를 입력하세요.")
    
    def _member_management(self):
        """회원 관리"""
        print("\n[회원 관리]")
        print("1. 회원 등록")
        print("2. 회원 탈퇴")
        print("3. 회원 목록")
        print("4. 회원 정보 조회")
        
        choice = input("선택: ").strip()
        
        if choice == "1":
            self._add_member()
        elif choice == "2":
            self._remove_member()
        elif choice == "3":
            self._list_members()
        elif choice == "4":
            self._member_info()
    
    def _add_member(self):
        """회원 등록"""
        print("\n[회원 등록]")
        print("1. 일반회원")
        print("2. 프리미엄회원")
        
        member_type = input("회원 유형: ").strip()
        
        name = input("이름: ").strip()
        email = input("이메일: ").strip()
        phone = input("전화번호: ").strip()
        
        try:
            if member_type == "1":
                member = RegularMember(name, email, phone)
            elif member_type == "2":
                member = PremiumMember(name, email, phone)
            else:
                print("잘못된 선택입니다.")
                return
            
            success, message = self.library.add_member(member)
            print(message)
        except ValueError as e:
            print(f"입력 오류: {e}")
    
    def _remove_member(self):
        """회원 탈퇴"""
        member_id = input("탈퇴할 회원 ID: ").strip()
        success, message = self.library.remove_member(member_id)
        print(message)
    
    def _list_members(self):
        """회원 목록"""
        print("\n[회원 목록]")
        if not self.library.members:
            print("등록된 회원이 없습니다.")
            return
        
        for member in self.library.members.values():
            if member.is_active:
                print(member)
    
    def _member_info(self):
        """회원 정보 조회"""
        member_id = input("회원 ID: ").strip()
        info = self.library.get_member_info(member_id)
        
        if info:
            member = info['member']
            print(f"\n[회원 정보]")
            print(f"ID: {member.id}")
            print(f"이름: {member.name}")
            print(f"이메일: {member.email}")
            print(f"전화번호: {member.phone}")
            print(f"회원 유형: {member.get_member_type()}")
            print(f"가입일: {member.registration_date.strftime('%Y-%m-%d')}")
            print(f"대출 가능 권수: {member.get_max_borrow_count() - len(member.borrowed_books)}권")
            print(f"연체료: ₩{member.fines:,}")
            
            if info['borrowed_books']:
                print("\n[대출 중인 도서]")
                for book in info['borrowed_books']:
                    print(f"- {book.title} (반납일: {book.return_date.strftime('%Y-%m-%d')})")
        else:
            print("존재하지 않는 회원입니다.")
    
    def _loan_management(self):
        """대출/반납 관리"""
        print("\n[대출/반납]")
        print("1. 도서 대출")
        print("2. 도서 반납")
        print("3. 대출 연장")
        print("4. 도서 예약")
        print("5. 연체 도서 조회")
        
        choice = input("선택: ").strip()
        
        if choice == "1":
            self._borrow_book()
        elif choice == "2":
            self._return_book()
        elif choice == "3":
            self._renew_book()
        elif choice == "4":
            self._reserve_book()
        elif choice == "5":
            self._overdue_books()
    
    def _borrow_book(self):
        """도서 대출"""
        member_id = input("회원 ID: ").strip()
        book_id = input("도서 ID: ").strip()
        
        try:
            book_id = int(book_id)
            success, message = self.library.borrow_book(member_id, book_id)
            print(message)
        except ValueError:
            print("올바른 도서 ID를 입력하세요.")
    
    def _return_book(self):
        """도서 반납"""
        member_id = input("회원 ID: ").strip()
        book_id = input("도서 ID: ").strip()
        
        try:
            book_id = int(book_id)
            success, message = self.library.return_book(member_id, book_id)
            print(message)
        except ValueError:
            print("올바른 도서 ID를 입력하세요.")
    
    def _renew_book(self):
        """대출 연장"""
        member_id = input("회원 ID: ").strip()
        book_id = input("도서 ID: ").strip()
        
        try:
            book_id = int(book_id)
            success, message = self.library.renew_book(member_id, book_id)
            print(message)
        except ValueError:
            print("올바른 도서 ID를 입력하세요.")
    
    def _reserve_book(self):
        """도서 예약"""
        member_id = input("회원 ID: ").strip()
        book_id = input("도서 ID: ").strip()
        
        try:
            book_id = int(book_id)
            success, message = self.library.reserve_book(member_id, book_id)
            print(message)
        except ValueError:
            print("올바른 도서 ID를 입력하세요.")
    
    def _overdue_books(self):
        """연체 도서 조회"""
        overdue_list = self.library.get_overdue_books()
        
        if not overdue_list:
            print("\n연체된 도서가 없습니다.")
        else:
            print("\n[연체 도서 목록]")
            for item in overdue_list:
                book = item['book']
                member = item['member']
                print(f"도서: {book.title}, 대출자: {member.name}, "
                      f"연체일: {item['overdue_days']}일, 연체료: ₩{item['fine']:,}")
    
    def _search_menu(self):
        """검색 메뉴"""
        print("\n[검색]")
        keyword = input("검색어 (제목): ").strip()
        author = input("저자 (선택사항): ").strip() or None
        genre = input("장르 (선택사항): ").strip() or None
        available_only = input("대출 가능한 도서만 (y/n): ").strip().lower() == 'y'
        
        results = self.library.search_books(
            keyword=keyword,
            author=author,
            genre=genre,
            available_only=available_only
        )
        
        if results:
            print(f"\n검색 결과: {len(results)}건")
            for book in results:
                print(book)
        else:
            print("검색 결과가 없습니다.")
    
    def _statistics_menu(self):
        """통계 및 리포트"""
        print("\n[통계 및 리포트]")
        print("1. 요약 리포트")
        print("2. 연체 리포트")
        print("3. 인기 도서 리포트")
        
        choice = input("선택: ").strip()
        
        if choice == "1":
            print(generate_report(self.library, "summary"))
        elif choice == "2":
            print(generate_report(self.library, "overdue"))
        elif choice == "3":
            print(generate_report(self.library, "popular"))
    
    def _data_management(self):
        """데이터 관리"""
        print("\n[데이터 관리]")
        print("1. 데이터 저장")
        print("2. 데이터 불러오기")
        
        choice = input("선택: ").strip()
        
        if choice == "1":
            success, message = self.library.save_data()
            print(message)
        elif choice == "2":
            print("데이터 불러오기 기능은 구현 예정입니다.")
    
    def _save_and_exit(self):
        """저장하고 종료"""
        save = input("데이터를 저장하시겠습니까? (y/n): ").strip().lower()
        if save == 'y':
            self.library.save_data()

def main():
    """메인 함수"""
    app = LibraryApp()
    app.run()

if __name__ == "__main__":
    main()