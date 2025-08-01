"""
Generic 타입 정의
"""

from typing import TypeVar, Generic, Optional, Union, Callable
from dataclasses import dataclass

T = TypeVar('T')
E = TypeVar('E')

@dataclass(frozen=True)
class Result(Generic[T, E]):
    """
    Result 타입 - 성공 또는 실패를 나타냄
    Rust의 Result<T, E>와 유사
    """
    _value: Union[T, E]
    _is_ok: bool
    
    @classmethod
    def ok(cls, value: T) -> 'Result[T, E]':
        """성공 결과 생성"""
        return cls(_value=value, _is_ok=True)
    
    @classmethod
    def err(cls, error: E) -> 'Result[T, E]':
        """실패 결과 생성"""
        return cls(_value=error, _is_ok=False)
    
    def is_ok(self) -> bool:
        """성공 여부"""
        return self._is_ok
    
    def is_err(self) -> bool:
        """실패 여부"""
        return not self._is_ok
    
    def unwrap(self) -> T:
        """값 추출 (실패시 예외)"""
        if self._is_ok:
            return self._value  # type: ignore
        raise ValueError(f"Called unwrap on an Err value: {self._value}")
    
    def unwrap_err(self) -> E:
        """에러 추출 (성공시 예외)"""
        if not self._is_ok:
            return self._value  # type: ignore
        raise ValueError(f"Called unwrap_err on an Ok value: {self._value}")
    
    def unwrap_or(self, default: T) -> T:
        """값 추출 또는 기본값"""
        return self._value if self._is_ok else default  # type: ignore
    
    def map(self, f: Callable[[T], T]) -> 'Result[T, E]':
        """성공값에 함수 적용"""
        if self._is_ok:
            return Result.ok(f(self._value))  # type: ignore
        return self  # type: ignore
    
    def map_err(self, f: Callable[[E], E]) -> 'Result[T, E]':
        """에러값에 함수 적용"""
        if not self._is_ok:
            return Result.err(f(self._value))  # type: ignore
        return self  # type: ignore

@dataclass(frozen=True)
class Option(Generic[T]):
    """
    Option 타입 - 값이 있거나 없음을 나타냄
    Rust의 Option<T>와 유사
    """
    _value: Optional[T]
    
    @classmethod
    def some(cls, value: T) -> 'Option[T]':
        """값이 있는 Option 생성"""
        return cls(_value=value)
    
    @classmethod
    def none(cls) -> 'Option[T]':
        """값이 없는 Option 생성"""
        return cls(_value=None)
    
    def is_some(self) -> bool:
        """값 존재 여부"""
        return self._value is not None
    
    def is_none(self) -> bool:
        """값 없음 여부"""
        return self._value is None
    
    def unwrap(self) -> T:
        """값 추출 (없으면 예외)"""
        if self._value is not None:
            return self._value
        raise ValueError("Called unwrap on a None value")
    
    def unwrap_or(self, default: T) -> T:
        """값 추출 또는 기본값"""
        return self._value if self._value is not None else default
    
    def map(self, f: Callable[[T], T]) -> 'Option[T]':
        """값에 함수 적용"""
        if self._value is not None:
            return Option.some(f(self._value))
        return Option.none()
    
    def filter(self, predicate: Callable[[T], bool]) -> 'Option[T]':
        """조건에 맞는 경우만 유지"""
        if self._value is not None and predicate(self._value):
            return self
        return Option.none()

# Generic Cache type
K = TypeVar('K')
V = TypeVar('V')

class Cache(Generic[K, V]):
    """제네릭 캐시"""
    
    def __init__(self) -> None:
        self._cache: dict[K, tuple[V, datetime]] = {}
        self._ttl: int = 3600  # 기본 1시간
    
    def get(self, key: K) -> Optional[V]:
        """캐시에서 값 조회"""
        if key in self._cache:
            value, cached_at = self._cache[key]
            if self._is_valid(cached_at):
                return value
            else:
                del self._cache[key]
        return None
    
    def set(self, key: K, value: V) -> None:
        """캐시에 값 저장"""
        from datetime import datetime
        self._cache[key] = (value, datetime.now())
    
    def invalidate(self, key: K) -> None:
        """캐시 무효화"""
        self._cache.pop(key, None)
    
    def clear(self) -> None:
        """전체 캐시 초기화"""
        self._cache.clear()
    
    def _is_valid(self, cached_at) -> bool:
        """캐시 유효성 확인"""
        from datetime import datetime, timedelta
        return datetime.now() - cached_at < timedelta(seconds=self._ttl)

# Paged result type
@dataclass
class Page(Generic[T]):
    """페이지네이션 결과"""
    items: list[T]
    total: int
    page: int
    per_page: int
    
    @property
    def total_pages(self) -> int:
        """전체 페이지 수"""
        return (self.total + self.per_page - 1) // self.per_page
    
    @property
    def has_next(self) -> bool:
        """다음 페이지 존재 여부"""
        return self.page < self.total_pages
    
    @property
    def has_prev(self) -> bool:
        """이전 페이지 존재 여부"""
        return self.page > 1