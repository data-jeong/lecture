# Type Hints와 모던 Python - 타입 안전 ToDo 앱 단계별 학습

## 목차
1. [Type Hints 기초](#1-type-hints-기초)
2. [Generic과 TypeVar](#2-generic과-typevar)
3. [Protocol과 구조적 타이핑](#3-protocol과-구조적-타이핑)
4. [Union과 Optional](#4-union과-optional)
5. [TypedDict와 Literal](#5-typeddict와-literal)
6. [Pydantic 모델](#6-pydantic-모델)
7. [Pattern Matching](#7-pattern-matching)
8. [타입 안전 ToDo 앱 프로젝트](#8-타입-안전-todo-앱-프로젝트)

## 1. Type Hints 기초

### 기본 타입 힌트
```python
# 변수 타입 힌트
name: str = "Python"
age: int = 25
height: float = 175.5
is_student: bool = True

# 함수 타입 힌트
def greet(name: str) -> str:
    return f"Hello, {name}!"

def add(a: int, b: int) -> int:
    return a + b

# 반환값이 없는 함수
def print_message(msg: str) -> None:
    print(msg)
```

### 컬렉션 타입
```python
from typing import List, Dict, Tuple, Set

# 리스트
numbers: List[int] = [1, 2, 3, 4, 5]
names: List[str] = ["Alice", "Bob", "Charlie"]

# 딕셔너리
scores: Dict[str, int] = {"Alice": 90, "Bob": 85}
config: Dict[str, Any] = {"debug": True, "port": 8080}

# 튜플
point: Tuple[float, float] = (10.5, 20.3)
rgb: Tuple[int, int, int] = (255, 0, 0)

# 집합
tags: Set[str] = {"python", "programming", "tutorial"}
```

### 타입 별칭
```python
from typing import List, Tuple

# 타입 별칭 정의
Coordinate = Tuple[float, float]
Path = List[Coordinate]

def calculate_distance(point1: Coordinate, point2: Coordinate) -> float:
    x1, y1 = point1
    x2, y2 = point2
    return ((x2 - x1) ** 2 + (y2 - y1) ** 2) ** 0.5

path: Path = [(0, 0), (1, 1), (2, 0)]
```

## 2. Generic과 TypeVar

### TypeVar 사용
```python
from typing import TypeVar, List, Optional

T = TypeVar('T')

def first_element(items: List[T]) -> Optional[T]:
    """리스트의 첫 번째 요소 반환"""
    return items[0] if items else None

# 사용 예
first_int = first_element([1, 2, 3])  # Optional[int]
first_str = first_element(["a", "b", "c"])  # Optional[str]
```

### Generic 클래스
```python
from typing import Generic, TypeVar

T = TypeVar('T')

class Stack(Generic[T]):
    def __init__(self) -> None:
        self._items: List[T] = []
    
    def push(self, item: T) -> None:
        self._items.append(item)
    
    def pop(self) -> Optional[T]:
        return self._items.pop() if self._items else None
    
    def peek(self) -> Optional[T]:
        return self._items[-1] if self._items else None

# 사용
int_stack: Stack[int] = Stack()
int_stack.push(10)
int_stack.push(20)

str_stack: Stack[str] = Stack()
str_stack.push("hello")
```

### 제한된 TypeVar
```python
from typing import TypeVar

# 숫자 타입만 허용
Number = TypeVar('Number', int, float)

def add_numbers(a: Number, b: Number) -> Number:
    return a + b

# OK
result1 = add_numbers(10, 20)  # int
result2 = add_numbers(10.5, 20.3)  # float

# Error (mypy에서)
# result3 = add_numbers("10", "20")  # str은 허용되지 않음
```

## 3. Protocol과 구조적 타이핑

### Protocol 정의
```python
from typing import Protocol

class Drawable(Protocol):
    """그릴 수 있는 객체의 프로토콜"""
    def draw(self) -> str:
        ...

class Circle:
    def draw(self) -> str:
        return "Drawing a circle"

class Square:
    def draw(self) -> str:
        return "Drawing a square"

def render(shape: Drawable) -> None:
    print(shape.draw())

# 사용 - Circle과 Square는 Drawable을 상속하지 않아도 됨
render(Circle())  # OK
render(Square())  # OK
```

### 런타임 체크 가능한 Protocol
```python
from typing import Protocol, runtime_checkable

@runtime_checkable
class Comparable(Protocol):
    def __lt__(self, other: Any) -> bool: ...
    def __eq__(self, other: Any) -> bool: ...

def sort_items(items: List[Comparable]) -> List[Comparable]:
    return sorted(items)

# 런타임 체크
print(isinstance(10, Comparable))  # True
print(isinstance("hello", Comparable))  # True
```

## 4. Union과 Optional

### Union 타입
```python
from typing import Union

def process_id(user_id: Union[int, str]) -> str:
    """사용자 ID 처리 (int 또는 str)"""
    if isinstance(user_id, int):
        return f"ID-{user_id:04d}"
    else:
        return f"ID-{user_id}"

# Python 3.10+
def process_id_modern(user_id: int | str) -> str:
    """파이프 연산자 사용 (3.10+)"""
    return f"ID-{user_id}"
```

### Optional 타입
```python
from typing import Optional

def find_user(user_id: int) -> Optional[str]:
    """사용자 찾기 - 없으면 None 반환"""
    users = {1: "Alice", 2: "Bob"}
    return users.get(user_id)

# Python 3.10+
def find_user_modern(user_id: int) -> str | None:
    """Union 문법 사용"""
    users = {1: "Alice", 2: "Bob"}
    return users.get(user_id)
```

## 5. TypedDict와 Literal

### TypedDict
```python
from typing import TypedDict, Optional

class UserDict(TypedDict):
    """사용자 정보 딕셔너리 타입"""
    id: int
    name: str
    email: str
    age: Optional[int]

# total=False로 선택적 필드 정의
class ConfigDict(TypedDict, total=False):
    debug: bool
    port: int
    host: str

# 사용
user: UserDict = {
    "id": 1,
    "name": "Alice",
    "email": "alice@example.com",
    "age": 25
}

config: ConfigDict = {
    "debug": True,
    "port": 8080
    # host는 선택적
}
```

### Literal 타입
```python
from typing import Literal

# 특정 값만 허용
Mode = Literal["read", "write", "append"]
Priority = Literal["low", "medium", "high"]

def open_file(filename: str, mode: Mode) -> None:
    print(f"Opening {filename} in {mode} mode")

def set_priority(task_id: int, priority: Priority) -> None:
    print(f"Setting task {task_id} to {priority} priority")

# OK
open_file("data.txt", "read")
set_priority(1, "high")

# Error (mypy에서)
# open_file("data.txt", "delete")  # "delete"는 허용되지 않음
```

## 6. Pydantic 모델

### 기본 모델
```python
from pydantic import BaseModel, Field, validator
from datetime import datetime
from typing import Optional, List

class Todo(BaseModel):
    """할 일 모델"""
    id: int
    title: str = Field(..., min_length=1, max_length=100)
    description: Optional[str] = None
    priority: Literal["low", "medium", "high"] = "medium"
    completed: bool = False
    created_at: datetime = Field(default_factory=datetime.now)
    tags: List[str] = []
    
    @validator('title')
    def title_must_not_be_empty(cls, v):
        if not v or v.isspace():
            raise ValueError('Title cannot be empty')
        return v.strip()
    
    class Config:
        # JSON 스키마 예제
        schema_extra = {
            "example": {
                "id": 1,
                "title": "Buy groceries",
                "description": "Milk, bread, eggs",
                "priority": "high",
                "tags": ["shopping", "urgent"]
            }
        }
```

### 중첩 모델
```python
class User(BaseModel):
    id: int
    username: str
    email: str

class TodoWithUser(BaseModel):
    id: int
    title: str
    assignee: Optional[User] = None
    
# 사용
todo_data = {
    "id": 1,
    "title": "Complete project",
    "assignee": {
        "id": 10,
        "username": "alice",
        "email": "alice@example.com"
    }
}

todo = TodoWithUser(**todo_data)
print(todo.assignee.username)  # alice
```

## 7. Pattern Matching

### 기본 패턴 매칭 (Python 3.10+)
```python
def process_command(command: str) -> str:
    match command.split():
        case ["quit"]:
            return "Goodbye!"
        case ["hello", name]:
            return f"Hello, {name}!"
        case ["add", *numbers]:
            total = sum(int(n) for n in numbers)
            return f"Sum: {total}"
        case _:
            return "Unknown command"

# 사용
print(process_command("hello Alice"))  # Hello, Alice!
print(process_command("add 1 2 3"))   # Sum: 6
```

### 타입 패턴 매칭
```python
from typing import Union

def describe_value(value: Union[int, str, list, dict]) -> str:
    match value:
        case int(n) if n > 0:
            return f"Positive integer: {n}"
        case int(n):
            return f"Non-positive integer: {n}"
        case str(s):
            return f"String of length {len(s)}"
        case list(items):
            return f"List with {len(items)} items"
        case dict(d):
            return f"Dictionary with {len(d)} keys"
        case _:
            return "Unknown type"
```

## 8. 타입 안전 ToDo 앱 프로젝트

이제 배운 내용을 종합하여 타입 안전한 ToDo 앱을 만들어봅시다!

### 주요 특징
1. **완벽한 타입 힌트**: 모든 함수와 변수에 타입 힌트
2. **Pydantic 모델**: 자동 검증과 직렬화
3. **Generic Repository**: 재사용 가능한 저장소 패턴
4. **Protocol 기반 인터페이스**: 유연한 구조
5. **런타임 타입 검증**: 안전한 데이터 처리

### 프로젝트 구조
```
todo_app/
    types/          # 타입 정의
    models/         # Pydantic 모델
    repositories/   # Generic 저장소
    services/       # 비즈니스 로직
    utils/          # 유틸리티
```

### mypy 설정
```ini
[mypy]
python_version = 3.10
warn_return_any = True
warn_unused_configs = True
disallow_untyped_defs = True
disallow_incomplete_defs = True
check_untyped_defs = True
disallow_untyped_decorators = True
no_implicit_optional = True
warn_redundant_casts = True
warn_unused_ignores = True
warn_no_return = True
warn_unreachable = True
strict_equality = True
```

### 실습 과제
1. **커스텀 타입 가드**: 런타임 타입 체크 함수
2. **제네릭 캐시**: 타입 안전한 캐싱 시스템
3. **타입 안전 설정**: TypedDict로 설정 관리
4. **비동기 타입**: async/await와 타입 힌트

### 다음 단계
다음 프로젝트에서는 GIL과 비동기 프로그래밍을 배우면서 효율적인 파일 처리 시스템을 만들 예정입니다!