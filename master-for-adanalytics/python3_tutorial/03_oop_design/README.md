# 객체지향 프로그래밍 - 도서관 관리 시스템

## 프로젝트 소개
Python의 객체지향 프로그래밍 개념을 학습하면서 실제 도서관 관리 시스템을 구축하는 프로젝트입니다.

## 학습 내용
- 클래스와 객체
- 생성자와 속성
- 메서드 (인스턴스, 클래스, 정적)
- 상속과 다형성
- 캡슐화와 추상화
- 매직 메서드
- 추상 클래스 (ABC)

## 파일 구조
```
03_oop_design/
├── README.md              # 이 파일
├── PROJECT_PLAN.md       # 프로젝트 계획
├── step_by_step.md       # 단계별 학습 가이드
├── main.py               # 메인 프로그램
├── examples.py           # 사용 예제
├── tests.py              # 테스트 코드
└── library_system/       # 패키지 디렉토리
    ├── models/           # 모델 클래스
    │   ├── __init__.py
    │   ├── book.py       # 도서 클래스
    │   ├── member.py     # 회원 클래스
    │   └── transaction.py # 거래 클래스
    ├── services/         # 서비스 클래스
    │   ├── __init__.py
    │   ├── library.py    # 도서관 시스템
    │   └── validator.py  # 유효성 검증
    └── utils/            # 유틸리티
        ├── __init__.py
        ├── storage.py    # 데이터 저장
        └── helpers.py    # 헬퍼 함수
```

## 클래스 구조

### 상속 계층
```
Book (추상 클래스)
├── PhysicalBook (일반 도서)
├── EBook (전자책)
└── AudioBook (오디오북)

Member (추상 클래스)
├── RegularMember (일반 회원)
└── PremiumMember (프리미엄 회원)
```

### 주요 클래스
- **Book**: 도서 정보와 대출 관리
- **Member**: 회원 정보와 대출 권한
- **Transaction**: 대출/반납 거래 기록
- **Library**: 전체 시스템 관리

## 실행 방법

### 메인 프로그램 실행
```bash
python main.py
```

### 예제 실행
```bash
python examples.py
```

### 테스트 실행
```bash
python tests.py
```

## 주요 기능

### 1. 도서 관리
- 도서 추가/삭제
- 도서 검색 (제목, 저자, 장르)
- 도서 상세 정보 조회
- 도서 타입별 관리 (일반/전자책/오디오북)

### 2. 회원 관리
- 회원 등록/탈퇴
- 회원 정보 조회
- 회원 등급별 혜택
  - 일반회원: 3권 대출, 200원/일 연체료
  - 프리미엄회원: 5권 대출, 100원/일 연체료

### 3. 대출/반납
- 도서 대출
- 도서 반납
- 대출 연장
- 도서 예약
- 연체료 계산

### 4. 통계 및 리포트
- 도서관 운영 현황
- 연체 도서 리포트
- 인기 도서 TOP 10
- 회원별 대출 이력

## 객체지향 개념 활용

### 1. 추상화
```python
from abc import ABC, abstractmethod

class Book(ABC):
    @abstractmethod
    def get_type(self):
        pass
```

### 2. 상속
```python
class PhysicalBook(Book):
    def get_type(self):
        return "일반도서"
```

### 3. 캡슐화
```python
class BankAccount:
    def __init__(self):
        self.__balance = 0  # Private 속성
    
    @property
    def balance(self):
        return self.__balance
```

### 4. 다형성
```python
books = [PhysicalBook(), EBook(), AudioBook()]
for book in books:
    print(book.get_type())  # 각 클래스의 메서드 호출
```

### 5. 매직 메서드
```python
def __str__(self):
    return f"{self.title} by {self.author}"

def __eq__(self, other):
    return self.isbn == other.isbn
```

## 학습 포인트

### 1. 클래스 설계
- 단일 책임 원칙 (SRP)
- 개방-폐쇄 원칙 (OCP)
- 리스코프 치환 원칙 (LSP)
- 인터페이스 분리 원칙 (ISP)
- 의존성 역전 원칙 (DIP)

### 2. 데이터 검증
- 이메일, 전화번호 형식 검증
- ISBN 유효성 검사
- 입력값 정제

### 3. 예외 처리
- 커스텀 예외 클래스
- try-except 블록
- 에러 메시지 관리

## 확장 아이디어
1. GUI 인터페이스 추가 (tkinter)
2. 바코드 스캐너 연동
3. 회원 카드 시스템
4. 도서 추천 시스템
5. 웹 인터페이스 (Flask/Django)

## 다음 단계
다음 프로젝트에서는 Type Hints와 현대적인 Python 기능을 활용하여 타입 안전한 ToDo 앱을 만들 예정입니다.