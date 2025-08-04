# 🏛️ 03. 객체지향 설계 - 도서관 관리 시스템

## 🎯 프로젝트 목표
Python의 객체지향 프로그래밍 핵심 개념을 학습하면서 실제 도서관 관리 시스템을 구축하는 프로젝트입니다. SOLID 원칙을 적용한 확장 가능하고 유지보수가 용이한 시스템을 설계합니다.

## 📚 핵심 학습 주제
- 🏗️ **클래스와 객체**: 개념 모델링과 인스턴스 생성
- 🔧 **생성자와 속성**: 초기화와 상태 관리
- ⚙️ **메서드 종류**: 인스턴스, 클래스, 정적 메서드
- 🌳 **상속과 다형성**: 코드 재사용과 인터페이스 일관성
- 🔒 **캡슐화와 추상화**: 정보 은닉과 인터페이스 설계
- ✨ **매직 메서드**: 특수 연산자 오버로딩
- 📐 **추상 클래스**: ABC 모듈과 인터페이스 정의
- 🎯 **SOLID 원칙**: 객체지향 설계 원칙 적용

## 📁 프로젝트 구조
```
03_oop_design/
├── 📄 README.md              # 종합 가이드
├── 📋 PROJECT_PLAN.md       # 프로젝트 설계 문서
├── 📚 step_by_step.md       # 단계별 구현 가이드
├── 🖥️ main.py               # CLI 메인 애플리케이션
├── 🎯 examples.py           # OOP 개념별 예제
├── 🧪 tests.py              # 자동화된 테스트 스위트
├── 📋 requirements.txt      # 의존성 목록
├── 📁 data/                 # 데이터 저장 디렉토리
└── 🏛️ library_system/       # 도서관 시스템 패키지
    ├── 📚 models/           # 도메인 모델 클래스들
    │   ├── 🔧 __init__.py
    │   ├── 📖 book.py       # 도서 클래스 계층구조
    │   ├── 👤 member.py     # 회원 클래스 계층구조
    │   └── 📋 transaction.py # 거래 기록 클래스
    ├── ⚙️ services/         # 비즈니스 로직 서비스
    │   ├── 🔧 __init__.py
    │   ├── 🏛️ library.py    # 도서관 관리 시스템
    │   └── ✅ validator.py  # 데이터 유효성 검증
    └── 🛠️ utils/            # 유틸리티 모듈
        ├── 🔧 __init__.py
        ├── 💾 storage.py    # 데이터 영속성 관리
        └── 🔧 helpers.py    # 공통 헬퍼 함수
```

## 🏗️ 객체지향 아키텍처

### 🌳 클래스 상속 계층구조
```
📚 Book (추상 클래스)
├── 📖 PhysicalBook    # 일반 도서 (페이지, 위치)
├── 💻 EBook          # 전자책 (파일 크기, 형식)
└── 🎧 AudioBook      # 오디오북 (재생 시간, 낭독자)

👤 Member (추상 클래스)
├── 🟢 RegularMember   # 일반 회원 (3권, 연체료 200원/일)
└── 🟨 PremiumMember   # 프리미엄 회원 (5권, 연체료 100원/일)

📋 Transaction        # 대출/반납 거래 기록
🏛️ Library            # 도서관 전체 시스템 관리
✅ Validator          # 데이터 유효성 검증
```

### 🎯 핵심 클래스 역할
- **📚 Book**: 도서 정보 관리, 대출 상태 추적, 예약 큐 관리
- **👤 Member**: 회원 정보, 대출 권한, 연체료 계산
- **📋 Transaction**: 대출/반납 이력, 날짜 추적, 연체 계산
- **🏛️ Library**: 시스템 전체 조율, 비즈니스 로직 구현
- **✅ Validator**: 이메일, 전화번호, ISBN 유효성 검증

## 🚀 빠른 시작 가이드

### 1️⃣ 설치 및 설정
```bash
# 프로젝트 디렉토리로 이동
cd 03_oop_design

# 의존성 설치
pip install -r requirements.txt

# 데이터 디렉토리 생성
mkdir -p data
```

### 2️⃣ 실행 방법
```bash
# 🎮 대화형 도서관 관리 시스템 (추천)
python main.py

# 🎯 OOP 개념별 예제 실행
python examples.py

# 🧪 자동화된 테스트 실행
python tests.py

# 또는 pytest 사용
pytest tests.py -v
```

### 3️⃣ 샘플 데이터 확인
시스템 시작 시 자동으로 로드되는 데이터:
- 📚 **도서 5권**: 파이썬 책 3권, 소설 1권, 오디오북 1권
- 👥 **회원 3명**: 일반회원 2명, 프리미엄회원 1명

## ✨ 주요 기능

### 📚 1. 지능형 도서 관리
- **다형성 기반 도서 관리**: 일반도서, 전자책, 오디오북 통합 관리
- **스마트 검색**: 제목, 저자, 장르, ISBN으로 다중 검색
- **재고 추적**: 실시간 대출 상태 및 예약 큐 관리
- **자동 분류**: 장르별, 타입별 자동 카테고리 분류

### 👥 2. 계층적 회원 시스템
- **회원 등급 관리**: 일반/프리미엄 회원 차등 혜택
  - 🟢 **일반회원**: 3권 대출, 14일 기간, 200원/일 연체료
  - 🟨 **프리미엄회원**: 5권 대출, 21일 기간, 100원/일 연체료
- **회원 정보 관리**: 연락처, 대출 이력, 연체료 추적
- **자동 유효성 검증**: 이메일, 전화번호 형식 검증

### 🔄 3. 트랜잭션 관리
- **대출/반납 시스템**: 날짜 추적 및 상태 관리
- **스마트 예약**: 대출 중인 도서 예약 큐 시스템
- **자동 연장**: 연체 없는 도서 대출 기간 연장
- **연체료 계산**: 회원 등급별 차등 연체료 자동 계산

### 📊 4. 리포팅 및 분석
- **운영 현황**: 실시간 도서관 운영 통계
- **연체 관리**: 연체 도서 및 회원 추적
- **인기 분석**: 대출 빈도 기반 인기 도서 랭킹
- **회원 분석**: 개별 회원 대출 패턴 분석

## 🎓 객체지향 핵심 개념 구현

### 🏗️ 1. 추상화 (Abstraction)
```python
from abc import ABC, abstractmethod
from datetime import datetime, timedelta

class Book(ABC):
    """도서 추상 클래스 - 모든 도서 타입의 공통 인터페이스"""
    
    def __init__(self, title, author, isbn=None, genre="일반"):
        self.id = self._generate_id()
        self.title = title
        self.author = author
        self.isbn = isbn or self._generate_isbn()
        self.genre = genre
        self.publication_year = datetime.now().year
        self.is_available = True
        self.borrowed_by = None
        self.return_date = None
        self.reservation_queue = []
    
    @abstractmethod
    def get_type(self) -> str:
        """도서 타입 반환 - 각 하위 클래스에서 구현 필수"""
        pass
    
    @abstractmethod
    def get_loan_period(self) -> int:
        """대출 기간 반환 - 도서 타입별로 다름"""
        pass
    
    @abstractmethod
    def get_display_info(self) -> dict:
        """표시용 정보 반환 - 타입별 특수 정보 포함"""
        pass
```

### 🌳 2. 상속 (Inheritance)
```python
class PhysicalBook(Book):
    """일반 도서 - Book 클래스 상속"""
    
    def __init__(self, title, author, pages=0, location="", **kwargs):
        super().__init__(title, author, **kwargs)
        self.pages = pages
        self.location = location  # 도서관 내 위치
    
    def get_type(self) -> str:
        return "일반도서"
    
    def get_loan_period(self) -> int:
        return 14  # 일반도서는 14일
    
    def get_display_info(self) -> dict:
        return {
            **self._base_info(),
            "페이지": self.pages,
            "위치": self.location
        }

class EBook(Book):
    """전자책 - Book 클래스 상속"""
    
    def __init__(self, title, author, file_size=0, file_format="PDF", **kwargs):
        super().__init__(title, author, **kwargs)
        self.file_size = file_size  # MB
        self.file_format = file_format
    
    def get_type(self) -> str:
        return "전자책"
    
    def get_loan_period(self) -> int:
        return 21  # 전자책은 21일
    
    def get_display_info(self) -> dict:
        return {
            **self._base_info(),
            "파일크기": f"{self.file_size}MB",
            "형식": self.file_format
        }
```

### 🔒 3. 캡슐화 (Encapsulation)
```python
class Member(ABC):
    """회원 추상 클래스 - 정보 은닉과 접근 제어"""
    
    def __init__(self, name, email, phone):
        self.id = self._generate_member_id()
        self._name = name  # Protected
        self.__email = email  # Private
        self.__phone = phone  # Private
        self._borrowed_books = []  # Protected
        self.__fines = 0  # Private - 연체료
        self.registration_date = datetime.now()
        self.is_active = True
    
    # Getter/Setter를 통한 접근 제어
    @property
    def name(self):
        return self._name
    
    @name.setter
    def name(self, value):
        if not value or len(value.strip()) < 2:
            raise ValueError("이름은 2글자 이상이어야 합니다")
        self._name = value.strip()
    
    @property
    def email(self):
        return self.__email
    
    @email.setter
    def email(self, value):
        if not self._validate_email(value):
            raise ValueError("유효하지 않은 이메일 형식입니다")
        self.__email = value
    
    @property
    def fines(self):
        """연체료 조회 - 읽기 전용"""
        return self.__fines
    
    def add_fine(self, amount):
        """연체료 추가 - 메서드를 통한 제어된 접근"""
        if amount > 0:
            self.__fines += amount
    
    def _validate_email(self, email):
        """이메일 유효성 검증 - Protected 메서드"""
        import re
        pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        return re.match(pattern, email) is not None
```

### 🔄 4. 다형성 (Polymorphism)
```python
def process_books(books: list[Book]):
    """다형성을 활용한 도서 처리 - 타입에 관계없이 동일한 인터페이스 사용"""
    
    for book in books:
        print(f"제목: {book.title}")
        print(f"타입: {book.get_type()}")  # 각 클래스별로 다른 구현
        print(f"대출기간: {book.get_loan_period()}일")  # 각 클래스별로 다른 값
        
        # 타입별 특수 정보 출력
        info = book.get_display_info()
        for key, value in info.items():
            print(f"{key}: {value}")
        print("-" * 30)

# 사용 예제
books = [
    PhysicalBook("파이썬 프로그래밍", "김개발", pages=500, location="A-1"),
    EBook("웹 개발 가이드", "이코딩", file_size=25, file_format="PDF"),
    AudioBook("영어 회화", "John Smith", duration=180, narrator="Jane Doe")
]

process_books(books)  # 모든 도서 타입을 동일하게 처리
```

### ✨ 5. 매직 메서드 (Magic Methods)
```python
class Book(ABC):
    # 문자열 표현
    def __str__(self):
        """사용자 친화적 문자열 표현"""
        status = "대출가능" if self.is_available else f"대출중({self.borrowed_by})"
        return f"[{self.id}] {self.title} - {self.author} ({status})"
    
    def __repr__(self):
        """개발자용 정확한 객체 표현"""
        return f"{self.__class__.__name__}(title='{self.title}', author='{self.author}')"
    
    # 비교 연산자
    def __eq__(self, other):
        """동등성 비교 - ISBN으로 판단"""
        if not isinstance(other, Book):
            return False
        return self.isbn == other.isbn
    
    def __lt__(self, other):
        """정렬을 위한 비교 - 제목순"""
        if not isinstance(other, Book):
            return NotImplemented
        return self.title < other.title
    
    # 해시 지원 (set, dict 키 사용 가능)
    def __hash__(self):
        return hash((self.isbn, self.title))
    
    # 속성 접근 제어
    def __getattribute__(self, name):
        """속성 접근 로깅"""
        if name.startswith('_'):
            print(f"⚠️ Protected/Private 속성 접근: {name}")
        return super().__getattribute__(name)

class Library:
    # 컨테이너 동작
    def __len__(self):
        """len(library) - 전체 도서 수"""
        return len(self.books)
    
    def __contains__(self, book):
        """book in library - 도서 포함 여부"""
        return book.id in self.books
    
    def __iter__(self):
        """for book in library - 반복 가능"""
        return iter(self.books.values())
    
    def __getitem__(self, book_id):
        """library[book_id] - 인덱스 접근"""
        return self.books.get(book_id)
```

## 🎯 SOLID 원칙 적용

### 🔹 1. 단일 책임 원칙 (SRP)
```python
# ❌ 잘못된 예 - 여러 책임을 가진 클래스
class BadBook:
    def __init__(self, title):
        self.title = title
    
    def save_to_database(self):  # 데이터베이스 책임
        pass
    
    def send_email(self):  # 이메일 발송 책임
        pass

# ✅ 올바른 예 - 각각 하나의 책임만
class Book:
    """도서 정보만 관리"""
    def __init__(self, title):
        self.title = title

class BookRepository:
    """데이터 저장만 담당"""
    def save(self, book):
        pass

class EmailService:
    """이메일 발송만 담당"""
    def send_notification(self, message):
        pass
```

### 🔹 2. 개방-폐쇄 원칙 (OCP)
```python
# ✅ 확장에는 열려있고 수정에는 닫혀있는 설계
class FineCalculator:
    """연체료 계산 전략 패턴"""
    
    def calculate(self, member, days_overdue):
        return member.get_daily_fine() * days_overdue

class RegularMember(Member):
    def get_daily_fine(self):
        return 200  # 일반회원 연체료

class PremiumMember(Member):
    def get_daily_fine(self):
        return 100  # 프리미엄회원 연체료

# 새로운 회원 타입 추가 시 기존 코드 수정 불필요
class StudentMember(Member):
    def get_daily_fine(self):
        return 50  # 학생회원 연체료
```

### 🔹 3. 리스코프 치환 원칙 (LSP)
```python
def process_member_loan(member: Member, book: Book):
    """모든 Member 하위클래스가 동일하게 동작해야 함"""
    if member.can_borrow():
        member.borrow_book(book)
        return True
    return False

# 모든 Member 하위클래스는 이 함수에서 동일하게 작동
regular = RegularMember("김일반", "kim@example.com", "010-1234-5678")
premium = PremiumMember("박프리미엄", "park@example.com", "010-5678-1234")

process_member_loan(regular, book)  # 정상 동작
process_member_loan(premium, book)  # 정상 동작
```

### 🔹 4. 인터페이스 분리 원칙 (ISP)
```python
# ✅ 필요한 인터페이스만 구현
class Borrowable(ABC):
    @abstractmethod
    def borrow(self, member_id: str):
        pass

class Reservable(ABC):
    @abstractmethod
    def reserve(self, member_id: str):
        pass

class PhysicalBook(Book, Borrowable, Reservable):
    """물리적 도서는 대출과 예약 모두 가능"""
    def borrow(self, member_id: str):
        self.is_available = False
        self.borrowed_by = member_id
    
    def reserve(self, member_id: str):
        self.reservation_queue.append(member_id)

class ReferenceBook(Book, Reservable):
    """참고도서는 예약만 가능 (대출 불가)"""
    def reserve(self, member_id: str):
        self.reservation_queue.append(member_id)
```

### 🔹 5. 의존성 역전 원칙 (DIP)
```python
# ✅ 구체적인 구현이 아닌 추상화에 의존
class NotificationService(ABC):
    @abstractmethod
    def send(self, message: str, recipient: str):
        pass

class EmailNotification(NotificationService):
    def send(self, message: str, recipient: str):
        print(f"이메일 발송: {recipient}에게 {message}")

class SMSNotification(NotificationService):
    def send(self, message: str, recipient: str):
        print(f"SMS 발송: {recipient}에게 {message}")

class Library:
    def __init__(self, notification_service: NotificationService):
        self.notification_service = notification_service  # 추상화에 의존
    
    def notify_overdue(self, member):
        message = f"{member.name}님, 연체된 도서가 있습니다."
        self.notification_service.send(message, member.email)
```

## ✅ 학습 체크리스트

### 🏗️ 객체지향 설계
- [ ] 추상 클래스와 인터페이스 정의
- [ ] 상속 계층구조 설계와 구현
- [ ] 캡슐화를 통한 데이터 보호
- [ ] 다형성을 활용한 유연한 코드 작성
- [ ] 매직 메서드를 통한 pythonic 구현

### 🎯 SOLID 원칙 적용
- [ ] 단일 책임 원칙 (SRP) 준수
- [ ] 개방-폐쇄 원칙 (OCP) 적용
- [ ] 리스코프 치환 원칙 (LSP) 이해
- [ ] 인터페이스 분리 원칙 (ISP) 구현
- [ ] 의존성 역전 원칙 (DIP) 활용

### 🔧 고급 기능
- [ ] Property와 descriptor 사용
- [ ] 컨텍스트 매니저 구현
- [ ] 커스텀 예외 클래스 정의
- [ ] 데코레이터 패턴 적용
- [ ] 팩토리 패턴 구현

## 🔧 문제 해결 가이드

### ❌ 자주 발생하는 오류
```python
# 1. 추상 클래스 인스턴스화 오류
# TypeError: Can't instantiate abstract class Book
# 해결: 추상 메서드를 모두 구현한 하위 클래스 사용

# 2. 순환 import 오류
# ImportError: cannot import name 'Book' from partially initialized module
# 해결: __init__.py에서 import 순서 조정 또는 지연 import 사용

# 3. 속성 접근 오류
# AttributeError: 'Book' object has no attribute '__isbn'
# 해결: private 속성은 _ClassName__attribute 형태로 접근

# 4. 매직 메서드 구현 오류
# TypeError: '<' not supported between instances
# 해결: __lt__, __eq__ 등 비교 메서드 구현
```

### 💡 디자인 패턴 활용
- **팩토리 패턴**: 도서 타입별 객체 생성
- **전략 패턴**: 연체료 계산 알고리즘
- **옵저버 패턴**: 도서 반납 알림 시스템
- **싱글톤 패턴**: 도서관 시스템 인스턴스 관리

## 🚀 확장 아이디어

### 🎯 중급 확장
1. **GUI 인터페이스**: tkinter/PyQt로 시각적 도서관 관리
2. **바코드 시스템**: ISBN 바코드 스캐너 연동
3. **회원카드 시스템**: RFID/NFC 카드 인증
4. **알림 시스템**: 이메일/SMS 자동 알림

### 🔥 고급 확장
1. **추천 시스템**: 머신러닝 기반 도서 추천
2. **웹 인터페이스**: Django/FastAPI 웹 애플리케이션
3. **마이크로서비스**: 도메인별 서비스 분리
4. **클라우드 연동**: AWS/Azure 클라우드 배포

## 📚 참고 자료
- [Python ABC 모듈 가이드](https://docs.python.org/ko/3/library/abc.html)
- [매직 메서드 완전 가이드](https://docs.python.org/ko/3/reference/datamodel.html)
- [SOLID 원칙 상세 설명](https://en.wikipedia.org/wiki/SOLID)
- [디자인 패턴 in Python](https://refactoring.guru/design-patterns/python)

## ➡️ 다음 프로젝트
**[04. 타입 힌트 & 현대적 Python - Todo 애플리케이션](../04_type_hints_modern/README.md)**  
Type Hints, Generics, Protocols 등 현대적인 Python 기능을 활용하여 타입 안전한 Todo 앱을 구현합니다.