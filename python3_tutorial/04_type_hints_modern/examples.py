"""
Type Hints & Modern Python 예제 모음
"""

from typing import List, Dict, Optional, Union, TypeVar, Generic, Protocol, Literal, overload
from datetime import datetime
import asyncio

# 1. 기본 타입 힌트 예제
def demonstrate_basic_types():
    """기본 타입 힌트 시연"""
    print("=== 기본 타입 힌트 ===")
    
    name: str = "Python"
    age: int = 25
    height: float = 175.5
    is_student: bool = True
    
    def greet(name: str) -> str:
        return f"Hello, {name}!"
    
    def add(a: int, b: int) -> int:
        return a + b
    
    print(f"이름: {name}")
    print(f"나이: {age}")
    print(greet(name))
    print(f"5 + 3 = {add(5, 3)}")


# 2. Generic 예제
T = TypeVar('T')

class Stack(Generic[T]):
    """제네릭 스택 구현"""
    
    def __init__(self) -> None:
        self._items: List[T] = []
    
    def push(self, item: T) -> None:
        self._items.append(item)
    
    def pop(self) -> Optional[T]:
        return self._items.pop() if self._items else None
    
    def peek(self) -> Optional[T]:
        return self._items[-1] if self._items else None
    
    def size(self) -> int:
        return len(self._items)
    
    def is_empty(self) -> bool:
        return len(self._items) == 0

def demonstrate_generics():
    """제네릭 시연"""
    print("\n=== 제네릭 타입 ===")
    
    # 정수 스택
    int_stack: Stack[int] = Stack()
    int_stack.push(10)
    int_stack.push(20)
    int_stack.push(30)
    
    print(f"정수 스택 크기: {int_stack.size()}")
    print(f"peek: {int_stack.peek()}")
    print(f"pop: {int_stack.pop()}")
    
    # 문자열 스택
    str_stack: Stack[str] = Stack()
    str_stack.push("hello")
    str_stack.push("world")
    
    print(f"문자열 스택 크기: {str_stack.size()}")
    print(f"peek: {str_stack.peek()}")


# 3. Protocol 예제
class Drawable(Protocol):
    """그릴 수 있는 객체의 프로토콜"""
    def draw(self) -> str:
        ...

class Circle:
    def __init__(self, radius: float):
        self.radius = radius
    
    def draw(self) -> str:
        return f"Drawing a circle with radius {self.radius}"

class Rectangle:
    def __init__(self, width: float, height: float):
        self.width = width
        self.height = height
    
    def draw(self) -> str:
        return f"Drawing a rectangle {self.width}x{self.height}"

def render_shape(shape: Drawable) -> None:
    """Drawable 프로토콜을 만족하는 모든 객체를 그릴 수 있음"""
    print(shape.draw())

def demonstrate_protocols():
    """프로토콜 시연"""
    print("\n=== Protocol 타입 ===")
    
    shapes: List[Drawable] = [
        Circle(5.0),
        Rectangle(10.0, 8.0),
        Circle(3.2)
    ]
    
    for shape in shapes:
        render_shape(shape)


# 4. Union과 Optional 예제
def process_id(user_id: Union[int, str]) -> str:
    """사용자 ID 처리 (int 또는 str)"""
    if isinstance(user_id, int):
        return f"ID-{user_id:04d}"
    else:
        return f"ID-{user_id.upper()}"

def find_user(user_id: int) -> Optional[str]:
    """사용자 찾기 - 없으면 None 반환"""
    users = {1: "Alice", 2: "Bob", 3: "Charlie"}
    return users.get(user_id)

def demonstrate_union_optional():
    """Union과 Optional 시연"""
    print("\n=== Union과 Optional ===")
    
    # Union 타입
    print(process_id(123))      # ID-0123
    print(process_id("abc"))    # ID-ABC
    
    # Optional 타입
    user = find_user(1)
    if user:
        print(f"사용자 발견: {user}")
    else:
        print("사용자를 찾을 수 없습니다")
    
    missing_user = find_user(999)
    print(f"없는 사용자: {missing_user}")


# 5. Literal 타입 예제
Priority = Literal["low", "medium", "high", "urgent"]
Status = Literal["pending", "in_progress", "completed", "cancelled"]

class Task:
    def __init__(self, title: str, priority: Priority = "medium"):
        self.title = title
        self.priority = priority
        self.status: Status = "pending"
    
    def set_priority(self, priority: Priority) -> None:
        self.priority = priority
    
    def set_status(self, status: Status) -> None:
        self.status = status
    
    def __str__(self) -> str:
        return f"Task('{self.title}', {self.priority}, {self.status})"

def demonstrate_literal():
    """Literal 타입 시연"""
    print("\n=== Literal 타입 ===")
    
    task = Task("Python 학습", "high")
    print(task)
    
    task.set_status("in_progress")
    print(task)
    
    task.set_status("completed")
    print(task)


# 6. overload 예제
@overload
def process_value(value: int) -> str: ...

@overload
def process_value(value: str) -> int: ...

@overload
def process_value(value: List[str]) -> str: ...

def process_value(value: Union[int, str, List[str]]) -> Union[str, int]:
    """다양한 타입을 처리하는 함수"""
    if isinstance(value, int):
        return f"Number: {value}"
    elif isinstance(value, str):
        return len(value)
    elif isinstance(value, list):
        return ", ".join(value)
    else:
        raise TypeError(f"Unsupported type: {type(value)}")

def demonstrate_overload():
    """overload 시연"""
    print("\n=== overload 데코레이터 ===")
    
    result1 = process_value(42)
    print(f"정수 처리: {result1}")
    
    result2 = process_value("hello")
    print(f"문자열 처리: {result2}")
    
    result3 = process_value(["a", "b", "c"])
    print(f"리스트 처리: {result3}")


# 7. Result 타입 패턴 (함수형 프로그래밍)
from dataclasses import dataclass
from typing import Callable

E = TypeVar('E')

@dataclass(frozen=True)
class Result(Generic[T, E]):
    """Result 타입 - 성공 또는 실패를 나타냄"""
    _value: Union[T, E]
    _is_ok: bool
    
    @classmethod
    def ok(cls, value: T) -> 'Result[T, E]':
        return cls(_value=value, _is_ok=True)
    
    @classmethod
    def err(cls, error: E) -> 'Result[T, E]':
        return cls(_value=error, _is_ok=False)
    
    def is_ok(self) -> bool:
        return self._is_ok
    
    def is_err(self) -> bool:
        return not self._is_ok
    
    def unwrap(self) -> T:
        if self._is_ok:
            return self._value  # type: ignore
        raise ValueError(f"Called unwrap on an Err value: {self._value}")
    
    def unwrap_or(self, default: T) -> T:
        return self._value if self._is_ok else default  # type: ignore
    
    def map(self, f: Callable[[T], T]) -> 'Result[T, E]':
        if self._is_ok:
            return Result.ok(f(self._value))  # type: ignore
        return self  # type: ignore

def safe_divide(a: float, b: float) -> Result[float, str]:
    """안전한 나눗셈 - 0으로 나누기 오류 처리"""
    if b == 0:
        return Result.err("Division by zero")
    return Result.ok(a / b)

def demonstrate_result_type():
    """Result 타입 시연"""
    print("\n=== Result 타입 (함수형 패턴) ===")
    
    # 성공 케이스
    result1 = safe_divide(10, 2)
    if result1.is_ok():
        print(f"10 / 2 = {result1.unwrap()}")
    
    # 오류 케이스
    result2 = safe_divide(10, 0)
    if result2.is_err():
        print(f"오류: {result2._value}")
    
    # unwrap_or 사용
    safe_result = result2.unwrap_or(0.0)
    print(f"기본값 사용: {safe_result}")
    
    # map 함수 사용
    result3 = safe_divide(20, 4).map(lambda x: x * 2)
    print(f"결과에 2를 곱함: {result3.unwrap()}")


# 8. 비동기 타입 힌트 예제
async def fetch_data(url: str) -> str:
    """비동기 데이터 가져오기"""
    await asyncio.sleep(1)  # 네트워크 요청 시뮬레이션
    return f"Data from {url}"

async def fetch_multiple(urls: List[str]) -> List[str]:
    """여러 URL에서 데이터 가져오기"""
    tasks = [fetch_data(url) for url in urls]
    return await asyncio.gather(*tasks)

def demonstrate_async_types():
    """비동기 타입 힌트 시연"""
    print("\n=== 비동기 타입 힌트 ===")
    
    async def main():
        urls = ["http://api1.com", "http://api2.com", "http://api3.com"]
        results = await fetch_multiple(urls)
        
        for i, result in enumerate(results, 1):
            print(f"결과 {i}: {result}")
    
    # 비동기 실행
    asyncio.run(main())


# 9. 실제 사용 예제 - 타입 안전한 설정 관리
from typing import TypedDict

class DatabaseConfig(TypedDict):
    host: str
    port: int
    database: str
    username: str

class AppConfig(TypedDict, total=False):  # 모든 필드가 선택적
    debug: bool
    database: DatabaseConfig
    api_key: Optional[str]

def load_config() -> AppConfig:
    """설정 로드"""
    return {
        "debug": True,
        "database": {
            "host": "localhost",
            "port": 5432,
            "database": "myapp",
            "username": "user"
        },
        "api_key": "secret-key"
    }

def demonstrate_typed_dict():
    """TypedDict 시연"""
    print("\n=== TypedDict 설정 관리 ===")
    
    config = load_config()
    
    if "database" in config:
        db_config = config["database"]
        print(f"DB 연결: {db_config['username']}@{db_config['host']}:{db_config['port']}")
    
    debug_mode = config.get("debug", False)
    print(f"디버그 모드: {debug_mode}")


# 메인 실행 함수
def main():
    """모든 예제 실행"""
    print("🎯 Type Hints & Modern Python 예제")
    print("=" * 50)
    
    demonstrate_basic_types()
    demonstrate_generics()
    demonstrate_protocols()
    demonstrate_union_optional()
    demonstrate_literal()
    demonstrate_overload()
    demonstrate_result_type()
    demonstrate_async_types()
    demonstrate_typed_dict()
    
    print("\n" + "=" * 50)
    print("✅ 모든 예제 실행 완료!")
    print("\n💡 다음 단계:")
    print("1. mypy로 타입 체크: mypy examples.py")
    print("2. Todo 앱 실행: python -m todo_app.main")
    print("3. 테스트 실행: python -m pytest tests/")

if __name__ == "__main__":
    main()