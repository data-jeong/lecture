# 🏦 Project 02: OOP Design - 은행 시스템

## 🎯 학습 목표
객체지향 프로그래밍(OOP)의 핵심 개념을 실제 은행 시스템 구현을 통해 마스터합니다.

## 📖 학습 순서

### 1단계: OOP 개념 이해 (30분)
```python
# 핵심 OOP 원칙
# 1. 캡슐화 (Encapsulation)
# 2. 상속 (Inheritance)  
# 3. 다형성 (Polymorphism)
# 4. 추상화 (Abstraction)
```

**코드 실행:**
```bash
cd banking_system
python main.py
```

### 2단계: 클래스 설계 패턴 (30분)

#### 🔍 핵심 패턴 분석
```python
from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Optional

@dataclass
class Transaction:
    """불변 트랜잭션 객체"""
    amount: float
    transaction_type: str
    timestamp: datetime
    
class Account(ABC):
    """추상 계좌 클래스"""
    @abstractmethod
    def withdraw(self, amount: float) -> bool:
        pass
    
class SavingsAccount(Account):
    """저축 계좌 - 이자율 적용"""
    def calculate_interest(self) -> float:
        return self.balance * self.interest_rate
```

### 3단계: 실습 과제 (60분)

#### 🔥 초급 과제
1. **신용카드 클래스 추가**
   - 한도 설정
   - 결제 기능
   - 청구서 생성

2. **ATM 시뮬레이터**
   ```python
   class ATM:
       def authenticate(self, card_number, pin):
           # 구현하세요
           pass
   ```

#### 🚀 중급 과제
1. **대출 시스템 구현**
   - 신용 점수 체크
   - 이자 계산
   - 상환 스케줄

2. **다중 통화 지원**
   ```python
   class CurrencyConverter:
       rates = {'USD': 1.0, 'KRW': 1200.0, 'EUR': 0.85}
   ```

#### 💎 고급 과제
1. **블록체인 거래 기록**
2. **AI 사기 탐지 시스템**
3. **실시간 환율 API 연동**

### 4단계: 디자인 패턴 적용 (30분)

#### Singleton Pattern - 은행 시스템
```python
class Bank:
    _instance = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance
```

#### Factory Pattern - 계좌 생성
```python
class AccountFactory:
    @staticmethod
    def create_account(account_type: str) -> Account:
        accounts = {
            'savings': SavingsAccount,
            'checking': CheckingAccount,
            'business': BusinessAccount
        }
        return accounts[account_type]()
```

#### Observer Pattern - 거래 알림
```python
class TransactionObserver:
    def update(self, transaction: Transaction):
        # SMS, Email, Push 알림
        pass
```

## 💡 학습 팁

### 🎨 SOLID 원칙
1. **S**ingle Responsibility: 하나의 클래스 = 하나의 책임
2. **O**pen/Closed: 확장에는 열려있고, 수정에는 닫혀있게
3. **L**iskov Substitution: 자식 클래스는 부모를 대체 가능
4. **I**nterface Segregation: 작고 구체적인 인터페이스
5. **D**ependency Inversion: 추상화에 의존

### 🐛 일반적인 실수
```python
# 나쁜 예 - 직접 잔액 접근
account.balance = 1000000  # 위험!

# 좋은 예 - 메서드를 통한 접근
account.deposit(1000000)  # 안전!
```

### 📊 성능 최적화
```python
# 트랜잭션 캐싱
from functools import lru_cache

@lru_cache(maxsize=128)
def get_transaction_history(account_id: str):
    # DB 조회 최적화
    pass
```

## 🏆 도전 과제

### 프로젝트: "차세대 디지털 뱅킹"
```python
class DigitalBank:
    """
    구현 요구사항:
    1. 생체 인증 (지문, 얼굴)
    2. P2P 송금
    3. 가상 카드 발급
    4. 투자 포트폴리오 관리
    5. 예산 관리 AI
    """
    
    def __init__(self):
        self.blockchain = Blockchain()
        self.ai_advisor = AIAdvisor()
        self.security = BiometricAuth()
```

### 추가 기능 아이디어
- 💳 QR 코드 결제
- 📱 모바일 전용 계좌
- 🤖 챗봇 상담
- 📈 실시간 주식 연동
- 🎮 게이미피케이션 (저축 목표 달성)

## 📝 체크리스트
- [ ] 계좌 클래스 계층 구조 설계
- [ ] 트랜잭션 시스템 구현
- [ ] 예외 처리 완료
- [ ] 단위 테스트 작성 (coverage > 80%)
- [ ] 디자인 패턴 2개 이상 적용
- [ ] 문서화 (docstring) 완료
- [ ] 보안 기능 구현 (암호화)

## 🔐 보안 고려사항
```python
import hashlib
import secrets

class Security:
    @staticmethod
    def hash_password(password: str) -> str:
        salt = secrets.token_hex(16)
        return hashlib.pbkdf2_hmac('sha256', 
                                   password.encode(), 
                                   salt.encode(), 
                                   100000)
    
    @staticmethod
    def validate_transaction(amount: float) -> bool:
        # 이상 거래 탐지
        if amount > 10000000:  # 1천만원 이상
            return require_2fa()
        return True
```

## 🎯 다음 단계
✅ 완료 후 **Project 03: Data Structures**로 이동하여 알고리즘을 학습하세요!

---
💻 **실행**: `python banking_system/main.py`
🧪 **테스트**: `pytest banking_system/tests/ -v`
📊 **데모**: `demo.html`을 브라우저에서 열기
📚 **문서**: `python -m pydoc banking_system`