# 03. 객체지향 프로그래밍 - 도서관 관리 시스템

## 프로젝트 개요
객체지향 프로그래밍의 핵심 개념을 활용하여 도서관 관리 시스템을 구축합니다.

## 학습 목표
- 클래스와 객체 이해
- 상속과 다형성 활용
- 캡슐화와 추상화 구현
- 매직 메서드 활용
- 디자인 패턴 기초

## 프로젝트 기능
1. **도서 관리**
   - Book 클래스 (일반도서, 전자책, 오디오북)
   - 도서 추가/삭제/검색
   - ISBN 자동 생성
   - 장르별 분류

2. **회원 관리**
   - Member 클래스 (일반회원, 프리미엄회원)
   - 회원 등록/탈퇴
   - 대출 한도 관리
   - 연체료 계산

3. **대출/반납 시스템**
   - Transaction 클래스
   - 대출 가능 여부 확인
   - 대출 기간 연장
   - 연체 도서 알림

4. **데이터 저장**
   - JSON 파일 저장/불러오기
   - 백업 기능
   - 통계 리포트

## 주요 학습 포인트
- `class` 키워드와 `__init__` 메서드
- `@property` 데코레이터
- `super()`를 통한 상속
- 추상 클래스 (ABC)
- `__str__`, `__repr__` 등 매직 메서드

## 코드 구조
```
library_system/
    models/
        __init__.py
        book.py          # Book 클래스와 서브클래스
        member.py        # Member 클래스와 서브클래스
        transaction.py   # Transaction 클래스
    services/
        library.py       # Library 메인 클래스
        validator.py     # 입력 검증
    utils/
        storage.py       # 파일 저장/불러오기
        helpers.py       # 유틸리티 함수
main.py                 # 메인 프로그램
```

## 실행 방법
```bash
python main.py
```

## UML 다이어그램
```
Book (Abstract)
├── PhysicalBook
├── EBook
└── AudioBook

Member (Abstract)
├── RegularMember
└── PremiumMember

Library
├── books: List[Book]
├── members: List[Member]
└── transactions: List[Transaction]
```