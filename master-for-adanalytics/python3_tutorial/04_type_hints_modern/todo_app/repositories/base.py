"""
기본 Repository 구현
"""

from typing import TypeVar, Generic, Optional, List, Dict, Any, Type
from abc import ABC, abstractmethod
from datetime import datetime
from ..types.protocols import Repository, Identifiable
from ..types.generics import Result, Option, Page
from ..types.base import FilterOptions, PaginationOptions

T = TypeVar('T', bound=Identifiable)
ID = TypeVar('ID')

class BaseRepository(Generic[T, ID], ABC):
    """추상 Repository 클래스"""
    
    @abstractmethod
    def add(self, item: T) -> Result[ID, str]:
        """아이템 추가"""
        pass
    
    @abstractmethod
    def get(self, id: ID) -> Option[T]:
        """ID로 아이템 조회"""
        pass
    
    @abstractmethod
    def get_all(self) -> List[T]:
        """모든 아이템 조회"""
        pass
    
    @abstractmethod
    def update(self, id: ID, item: T) -> Result[bool, str]:
        """아이템 업데이트"""
        pass
    
    @abstractmethod
    def delete(self, id: ID) -> Result[bool, str]:
        """아이템 삭제"""
        pass
    
    @abstractmethod
    def exists(self, id: ID) -> bool:
        """아이템 존재 여부 확인"""
        pass
    
    @abstractmethod
    def count(self) -> int:
        """전체 아이템 수"""
        pass
    
    @abstractmethod
    def filter(self, predicate: callable) -> List[T]:
        """조건에 맞는 아이템 필터링"""
        pass
    
    @abstractmethod
    def find_one(self, predicate: callable) -> Option[T]:
        """조건에 맞는 첫 번째 아이템"""
        pass
    
    @abstractmethod
    def clear(self) -> None:
        """모든 아이템 삭제"""
        pass

class InMemoryRepository(BaseRepository[T, ID]):
    """메모리 기반 Repository 구현"""
    
    def __init__(self, item_type: Type[T]):
        self._items: Dict[ID, T] = {}
        self._next_id: int = 1
        self._item_type = item_type
    
    def add(self, item: T) -> Result[ID, str]:
        """아이템 추가"""
        try:
            # ID 생성 (숫자 타입 ID 가정)
            item_id = self._get_next_id()
            item.id = item_id  # type: ignore
            
            # 타임스탬프 추가
            now = datetime.now()
            if hasattr(item, 'created_at'):
                item.created_at = now
            if hasattr(item, 'updated_at'):
                item.updated_at = now
            
            self._items[item_id] = item
            return Result.ok(item_id)
        except Exception as e:
            return Result.err(str(e))
    
    def get(self, id: ID) -> Option[T]:
        """ID로 아이템 조회"""
        if id in self._items:
            return Option.some(self._items[id])
        return Option.none()
    
    def get_all(self) -> List[T]:
        """모든 아이템 조회"""
        return list(self._items.values())
    
    def update(self, id: ID, item: T) -> Result[bool, str]:
        """아이템 업데이트"""
        if id not in self._items:
            return Result.err(f"Item with id {id} not found")
        
        try:
            # 기존 아이템 유지하면서 업데이트
            existing = self._items[id]
            
            # 업데이트 시간 갱신
            if hasattr(item, 'updated_at'):
                item.updated_at = datetime.now()
            
            # ID는 변경하지 않음
            item.id = id  # type: ignore
            
            # created_at은 유지
            if hasattr(existing, 'created_at') and hasattr(item, 'created_at'):
                item.created_at = existing.created_at
            
            self._items[id] = item
            return Result.ok(True)
        except Exception as e:
            return Result.err(str(e))
    
    def delete(self, id: ID) -> Result[bool, str]:
        """아이템 삭제"""
        if id not in self._items:
            return Result.err(f"Item with id {id} not found")
        
        del self._items[id]
        return Result.ok(True)
    
    def exists(self, id: ID) -> bool:
        """아이템 존재 여부 확인"""
        return id in self._items
    
    def count(self) -> int:
        """전체 아이템 수"""
        return len(self._items)
    
    def filter(self, predicate: callable) -> List[T]:
        """조건에 맞는 아이템 필터링"""
        return [item for item in self._items.values() if predicate(item)]
    
    def find_one(self, predicate: callable) -> Option[T]:
        """조건에 맞는 첫 번째 아이템"""
        for item in self._items.values():
            if predicate(item):
                return Option.some(item)
        return Option.none()
    
    def clear(self) -> None:
        """모든 아이템 삭제"""
        self._items.clear()
        self._next_id = 1
    
    def _get_next_id(self) -> ID:
        """다음 ID 생성"""
        next_id = self._next_id
        self._next_id += 1
        return next_id  # type: ignore
    
    def get_page(self, options: PaginationOptions) -> Page[T]:
        """페이지네이션된 결과 반환"""
        items = list(self._items.values())
        
        # 정렬
        sort_key = options.get('sort_by', 'id')
        reverse = options.get('sort_order', 'asc') == 'desc'
        
        if hasattr(items[0] if items else None, sort_key):
            items.sort(key=lambda x: getattr(x, sort_key, ''), reverse=reverse)
        
        # 페이지네이션
        page = options.get('page', 1)
        per_page = options.get('per_page', 10)
        start = (page - 1) * per_page
        end = start + per_page
        
        return Page(
            items=items[start:end],
            total=len(items),
            page=page,
            per_page=per_page
        )
    
    def batch_add(self, items: List[T]) -> Result[List[ID], str]:
        """여러 아이템 일괄 추가"""
        added_ids = []
        for item in items:
            result = self.add(item)
            if result.is_err():
                # 롤백
                for id in added_ids:
                    self.delete(id)
                return Result.err(f"Failed to add item: {result.unwrap_err()}")
            added_ids.append(result.unwrap())
        return Result.ok(added_ids)
    
    def batch_delete(self, ids: List[ID]) -> Result[int, str]:
        """여러 아이템 일괄 삭제"""
        deleted_count = 0
        for id in ids:
            if self.exists(id):
                self.delete(id)
                deleted_count += 1
        return Result.ok(deleted_count)