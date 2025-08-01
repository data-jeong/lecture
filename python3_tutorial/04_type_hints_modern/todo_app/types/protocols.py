"""
Protocol 정의
"""

from typing import Protocol, TypeVar, Optional, runtime_checkable
from datetime import datetime
from .base import TodoId, UserId

T = TypeVar('T')
ID = TypeVar('ID')

class Repository(Protocol[T, ID]):
    """저장소 프로토콜"""
    
    def add(self, item: T) -> ID:
        """아이템 추가"""
        ...
    
    def get(self, id: ID) -> Optional[T]:
        """ID로 아이템 조회"""
        ...
    
    def get_all(self) -> list[T]:
        """모든 아이템 조회"""
        ...
    
    def update(self, id: ID, item: T) -> bool:
        """아이템 업데이트"""
        ...
    
    def delete(self, id: ID) -> bool:
        """아이템 삭제"""
        ...
    
    def exists(self, id: ID) -> bool:
        """아이템 존재 여부 확인"""
        ...

@runtime_checkable
class Cacheable(Protocol):
    """캐시 가능한 객체"""
    
    def cache_key(self) -> str:
        """캐시 키 생성"""
        ...
    
    def is_cache_valid(self, cached_at: datetime) -> bool:
        """캐시 유효성 확인"""
        ...

class Validator(Protocol[T]):
    """검증기 프로토콜"""
    
    def validate(self, value: T) -> tuple[bool, Optional[str]]:
        """값 검증 - (성공여부, 에러메시지)"""
        ...

class Timestamped(Protocol):
    """타임스탬프가 있는 객체"""
    created_at: datetime
    updated_at: datetime

class Identifiable(Protocol[ID]):
    """식별 가능한 객체"""
    id: ID

class Authorizable(Protocol):
    """권한 확인 가능한 객체"""
    
    def can_read(self, user_id: UserId) -> bool:
        """읽기 권한 확인"""
        ...
    
    def can_write(self, user_id: UserId) -> bool:
        """쓰기 권한 확인"""
        ...
    
    def can_delete(self, user_id: UserId) -> bool:
        """삭제 권한 확인"""
        ...

class Searchable(Protocol):
    """검색 가능한 객체"""
    
    def search_text(self) -> str:
        """검색용 텍스트 반환"""
        ...
    
    def matches(self, query: str) -> bool:
        """검색어 매칭 여부"""
        ...

class Serializable(Protocol[T]):
    """직렬화 가능한 객체"""
    
    def to_dict(self) -> dict[str, any]:
        """딕셔너리로 변환"""
        ...
    
    @classmethod
    def from_dict(cls, data: dict[str, any]) -> T:
        """딕셔너리에서 생성"""
        ...

class EventEmitter(Protocol):
    """이벤트 발생 객체"""
    
    def emit(self, event_name: str, data: dict[str, any]) -> None:
        """이벤트 발생"""
        ...
    
    def on(self, event_name: str, handler: callable) -> None:
        """이벤트 핸들러 등록"""
        ...
    
    def off(self, event_name: str, handler: callable) -> None:
        """이벤트 핸들러 제거"""
        ...

class Logger(Protocol):
    """로거 프로토콜"""
    
    def debug(self, message: str, **kwargs: any) -> None: ...
    def info(self, message: str, **kwargs: any) -> None: ...
    def warning(self, message: str, **kwargs: any) -> None: ...
    def error(self, message: str, **kwargs: any) -> None: ...
    def critical(self, message: str, **kwargs: any) -> None: ...