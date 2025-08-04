# 🏷️ 04. 타입 힌트 & 현대적 Python - Todo 애플리케이션

## 🎯 학습 목표

이 프로젝트를 통해 다음을 마스터하게 됩니다:

- **타입 힌트 완벽 이해**: Python의 정적 타입 검사 시스템
- **Generic과 TypeVar**: 재사용 가능한 타입 안전 코드 작성
- **Protocol과 구조적 타이핑**: 덕 타이핑의 타입 안전 버전
- **최신 Python 기능**: Pattern Matching, Walrus Operator 등
- **코드 품질 향상**: mypy를 통한 타입 체크와 버그 예방

## 📚 단계별 학습 경로

### 단계 1: 기본 타입 힌트 (Beginner)
```python
# 1.1 기본 타입
def greet(name: str) -> str:
    return f"Hello, {name}!"

def add_numbers(a: int, b: int) -> int:
    return a + b

# 1.2 컬렉션 타입
from typing import List, Dict, Optional

def process_names(names: List[str]) -> Dict[str, int]:
    return {name: len(name) for name in names}

def find_user(user_id: int) -> Optional[str]:
    users = {1: "Alice", 2: "Bob"}
    return users.get(user_id)
```

### 단계 2: 고급 타입 (Intermediate)
```python
# 2.1 Union과 Literal
from typing import Union, Literal

Priority = Literal['high', 'medium', 'low']
Status = Literal['pending', 'in_progress', 'completed']

def set_priority(priority: Priority) -> None:
    print(f"Priority set to: {priority}")

# 2.2 TypedDict
from typing import TypedDict

class TodoDict(TypedDict):
    id: int
    title: str
    completed: bool
    priority: Priority
```

### 단계 3: Generic과 Protocol (Advanced)
```python
# 3.1 Generic 클래스
from typing import TypeVar, Generic, Protocol

T = TypeVar('T')

class Repository(Generic[T]):
    def __init__(self) -> None:
        self._items: List[T] = []
    
    def add(self, item: T) -> None:
        self._items.append(item)
    
    def get_all(self) -> List[T]:
        return self._items.copy()

# 3.2 Protocol 정의
class Serializable(Protocol):
    def serialize(self) -> dict: ...
    def deserialize(self, data: dict) -> None: ...
```

## 💡 코드 예제와 설명

### 예제 1: 타입 안전 ToDo 모델
```python
from dataclasses import dataclass
from datetime import datetime
from typing import Optional, List
from enum import Enum

class Priority(Enum):
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"

@dataclass
class Todo:
    """타입 안전 ToDo 모델"""
    id: int
    title: str
    description: Optional[str] = None
    completed: bool = False
    priority: Priority = Priority.MEDIUM
    created_at: datetime = datetime.now()
    tags: List[str] = None
    
    def __post_init__(self):
        if self.tags is None:
            self.tags = []
    
    def mark_completed(self) -> None:
        """할일을 완료로 표시"""
        self.completed = True
    
    def add_tag(self, tag: str) -> None:
        """태그 추가"""
        if tag not in self.tags:
            self.tags.append(tag)
```

### 예제 2: Generic Repository 패턴
```python
from typing import TypeVar, Generic, Optional, List, Dict
from abc import ABC, abstractmethod

T = TypeVar('T')
ID = TypeVar('ID')

class BaseRepository(Generic[T, ID], ABC):
    """제네릭 저장소 기본 클래스"""
    
    @abstractmethod
    async def create(self, entity: T) -> T:
        """엔티티 생성"""
        pass
    
    @abstractmethod
    async def get_by_id(self, id: ID) -> Optional[T]:
        """ID로 엔티티 조회"""
        pass
    
    @abstractmethod
    async def update(self, id: ID, entity: T) -> Optional[T]:
        """엔티티 업데이트"""
        pass
    
    @abstractmethod
    async def delete(self, id: ID) -> bool:
        """엔티티 삭제"""
        pass

class TodoRepository(BaseRepository[Todo, int]):
    """ToDo 저장소 구현"""
    
    def __init__(self):
        self._todos: Dict[int, Todo] = {}
        self._next_id = 1
    
    async def create(self, todo: Todo) -> Todo:
        todo.id = self._next_id
        self._todos[self._next_id] = todo
        self._next_id += 1
        return todo
    
    async def get_by_id(self, todo_id: int) -> Optional[Todo]:
        return self._todos.get(todo_id)
    
    async def get_by_priority(self, priority: Priority) -> List[Todo]:
        return [todo for todo in self._todos.values() 
                if todo.priority == priority]
```

### 예제 3: Protocol을 활용한 인터페이스
```python
from typing import Protocol, runtime_checkable

@runtime_checkable
class Notifiable(Protocol):
    """알림 가능한 객체의 프로토콜"""
    
    def send_notification(self, message: str) -> bool:
        """알림 전송"""
        ...
    
    def get_notification_preferences(self) -> Dict[str, bool]:
        """알림 설정 조회"""
        ...

class EmailNotifier:
    """이메일 알림 구현"""
    
    def send_notification(self, message: str) -> bool:
        print(f"📧 Email: {message}")
        return True
    
    def get_notification_preferences(self) -> Dict[str, bool]:
        return {"email": True, "push": False}

class PushNotifier:
    """푸시 알림 구현"""
    
    def send_notification(self, message: str) -> bool:
        print(f"📱 Push: {message}")
        return True
    
    def get_notification_preferences(self) -> Dict[str, bool]:
        return {"email": False, "push": True}

def notify_user(notifier: Notifiable, message: str) -> None:
    """타입 안전 알림 함수"""
    # 런타임에 프로토콜 준수 확인
    if isinstance(notifier, Notifiable):
        notifier.send_notification(message)
```

## 🏋️‍♂️ 실습 연습문제

### 초급 연습문제
1. **기본 타입 힌트**: 계산기 함수들에 타입 힌트 추가
2. **Optional 활용**: 사용자 검색 함수 구현
3. **List와 Dict**: 학생 성적 관리 함수 작성

### 중급 연습문제
1. **Literal 타입**: 상태 머신 구현
2. **TypedDict**: 설정 관리 시스템
3. **Union 타입**: 다양한 입력 타입 처리

### 고급 연습문제
1. **Generic 클래스**: 캐시 시스템 구현
2. **Protocol**: 플러그인 시스템 설계
3. **TypeVar bounds**: 제약이 있는 제네릭 함수

## ⚠️ 흔한 실수와 해결법

### 실수 1: 가변 기본값 사용
```python
# ❌ 잘못된 방법
def create_todo(tags: List[str] = []) -> Todo:
    # 모든 호출에서 같은 리스트 공유
    pass

# ✅ 올바른 방법
def create_todo(tags: Optional[List[str]] = None) -> Todo:
    if tags is None:
        tags = []
    # 또는 dataclass의 field(default_factory=list) 사용
```

### 실수 2: 잘못된 타입 어노테이션
```python
# ❌ 잘못된 방법
def process_data(data: list) -> dict:  # 구체적이지 않음
    pass

# ✅ 올바른 방법
def process_data(data: List[str]) -> Dict[str, int]:
    pass
```

### 실수 3: mypy 설정 누락
```python
# mypy.ini 파일 필요
[mypy]
python_version = 3.8
warn_return_any = True
warn_unused_configs = True
disallow_untyped_defs = True
```

## 💪 도전 프로젝트

### 프로젝트 1: 타입 안전 ORM (중급)
- Generic을 활용한 모델 기본 클래스
- Repository 패턴으로 데이터 접근 계층
- 타입 안전 쿼리 빌더

### 프로젝트 2: 플러그인 시스템 (고급)
- Protocol을 활용한 플러그인 인터페이스
- 동적 플러그인 로딩
- 타입 체크가 되는 설정 시스템

### 프로젝트 3: 비동기 태스크 큐 (전문가)
- Generic을 활용한 태스크 정의
- 타입 안전 직렬화/역직렬화
- 에러 처리와 재시도 로직

## ✅ 완료 체크리스트

### 기본 개념
- [ ] 기본 타입 힌트 (str, int, float, bool) 이해
- [ ] 함수 반환 타입 명시
- [ ] Optional과 None 처리
- [ ] List, Dict, Tuple 타입 힌트

### 고급 개념
- [ ] Generic 클래스 작성
- [ ] TypeVar와 bounds 활용
- [ ] Protocol 정의와 구현
- [ ] Union과 Literal 타입

### 실전 적용
- [ ] mypy 설정과 타입 체크
- [ ] Pydantic 모델 활용
- [ ] 실제 프로젝트에 타입 힌트 적용
- [ ] 타입 가드 함수 작성

### 최신 기능
- [ ] Pattern Matching (Python 3.10+)
- [ ] ParamSpec와 Concatenate
- [ ] TypeGuard와 TypeIs
- [ ] Self 타입 (Python 3.11+)

## 🚀 다음 단계

이 프로젝트를 완료했다면:
1. **05_gil_async**: 비동기 프로그래밍과 타입 힌트 결합
2. **타입 안전 웹 API**: FastAPI와 Pydantic 활용
3. **고급 디자인 패턴**: 타입 안전 팩토리, 빌더 패턴
4. **타입 레벨 프로그래밍**: 더 복잡한 타입 시스템 탐구

## 📖 추가 학습 자료

- [Python 공식 typing 문서](https://docs.python.org/3/library/typing.html)
- [mypy 공식 문서](https://mypy.readthedocs.io/)
- [PEP 484 - Type Hints](https://www.python.org/dev/peps/pep-0484/)
- [Real Python - Type Checking](https://realpython.com/python-type-checking/)

---

**💡 팁**: 타입 힌트는 코드의 가독성과 유지보수성을 크게 향상시킵니다. 처음에는 번거로울 수 있지만, 큰 프로젝트에서 그 가치를 실감하게 될 것입니다!