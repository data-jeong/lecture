"""
Todo Repository 구현
"""

from typing import List, Optional, Dict, Set
from datetime import datetime, timedelta
from ..models.todo import Todo, TodoWithStats
from ..types.base import TodoId, UserId, CategoryId, Status, Priority, FilterOptions
from ..types.generics import Result, Option, Page
from .base import InMemoryRepository

class TodoRepository(InMemoryRepository[Todo, TodoId]):
    """Todo 전용 Repository"""
    
    def __init__(self):
        super().__init__(Todo)
        self._comments_count: Dict[TodoId, int] = {}
        self._attachments_count: Dict[TodoId, int] = {}
    
    def get_by_user(self, user_id: UserId) -> List[Todo]:
        """사용자별 Todo 조회"""
        return self.filter(lambda t: t.created_by == user_id or t.assigned_to == user_id)
    
    def get_by_category(self, category_id: CategoryId) -> List[Todo]:
        """카테고리별 Todo 조회"""
        return self.filter(lambda t: t.category_id == category_id)
    
    def get_by_status(self, status: Status) -> List[Todo]:
        """상태별 Todo 조회"""
        return self.filter(lambda t: t.status == status)
    
    def get_overdue(self) -> List[Todo]:
        """마감일 지난 Todo 조회"""
        now = datetime.now()
        return self.filter(
            lambda t: t.due_date is not None 
            and t.due_date < now 
            and t.status != "completed"
        )
    
    def get_due_soon(self, days: int = 7) -> List[Todo]:
        """곧 마감인 Todo 조회"""
        now = datetime.now()
        future = now + timedelta(days=days)
        return self.filter(
            lambda t: t.due_date is not None 
            and now <= t.due_date <= future
            and t.status != "completed"
        )
    
    def search(self, query: str) -> List[Todo]:
        """제목과 설명에서 검색"""
        query_lower = query.lower()
        return self.filter(
            lambda t: query_lower in t.title.lower() 
            or (t.description and query_lower in t.description.lower())
        )
    
    def get_filtered(self, filters: FilterOptions) -> List[Todo]:
        """필터 옵션으로 조회"""
        todos = self.get_all()
        
        # 상태 필터
        if filters.get('status'):
            todos = [t for t in todos if t.status == filters['status']]
        
        # 우선순위 필터
        if filters.get('priority'):
            todos = [t for t in todos if t.priority == filters['priority']]
        
        # 카테고리 필터
        if filters.get('category_id'):
            todos = [t for t in todos if t.category_id == filters['category_id']]
        
        # 담당자 필터
        if filters.get('assigned_to'):
            todos = [t for t in todos if t.assigned_to == filters['assigned_to']]
        
        # 태그 필터
        if filters.get('tags'):
            filter_tags = set(filters['tags'])
            todos = [t for t in todos if filter_tags.intersection(set(t.tags))]
        
        # 날짜 필터
        if filters.get('created_after'):
            todos = [t for t in todos if t.created_at >= filters['created_after']]
        
        if filters.get('created_before'):
            todos = [t for t in todos if t.created_at <= filters['created_before']]
        
        # 검색어 필터
        if filters.get('search_query'):
            query = filters['search_query'].lower()
            todos = [
                t for t in todos 
                if query in t.title.lower() 
                or (t.description and query in t.description.lower())
                or any(query in tag.lower() for tag in t.tags)
            ]
        
        return todos
    
    def mark_completed(self, todo_id: TodoId) -> Result[bool, str]:
        """Todo 완료 처리"""
        todo_opt = self.get(todo_id)
        if todo_opt.is_none():
            return Result.err(f"Todo {todo_id} not found")
        
        todo = todo_opt.unwrap()
        todo.mark_completed()
        
        return self.update(todo_id, todo)
    
    def assign_to_user(self, todo_id: TodoId, user_id: UserId) -> Result[bool, str]:
        """Todo 담당자 할당"""
        todo_opt = self.get(todo_id)
        if todo_opt.is_none():
            return Result.err(f"Todo {todo_id} not found")
        
        todo = todo_opt.unwrap()
        todo.assign_to(user_id)
        
        return self.update(todo_id, todo)
    
    def get_statistics(self, user_id: Optional[UserId] = None) -> Dict[str, any]:
        """통계 정보 반환"""
        todos = self.get_by_user(user_id) if user_id else self.get_all()
        
        total = len(todos)
        completed = len([t for t in todos if t.status == "completed"])
        pending = len([t for t in todos if t.status == "pending"])
        in_progress = len([t for t in todos if t.status == "in_progress"])
        overdue = len([t for t in todos if t.is_overdue()])
        
        # 우선순위별 통계
        by_priority = {
            "low": len([t for t in todos if t.priority == "low"]),
            "medium": len([t for t in todos if t.priority == "medium"]),
            "high": len([t for t in todos if t.priority == "high"]),
            "urgent": len([t for t in todos if t.priority == "urgent"]),
        }
        
        # 카테고리별 통계
        by_category: Dict[Optional[CategoryId], int] = {}
        for todo in todos:
            cat_id = todo.category_id
            by_category[cat_id] = by_category.get(cat_id, 0) + 1
        
        # 평균 완료 시간 계산
        completion_times = []
        for todo in todos:
            if todo.status == "completed" and todo.completed_at:
                time_diff = (todo.completed_at - todo.created_at).total_seconds() / 3600
                completion_times.append(time_diff)
        
        avg_completion_time = sum(completion_times) / len(completion_times) if completion_times else None
        
        return {
            "total": total,
            "completed": completed,
            "pending": pending,
            "in_progress": in_progress,
            "overdue": overdue,
            "by_priority": by_priority,
            "by_category": by_category,
            "completion_rate": completed / total if total > 0 else 0.0,
            "average_completion_time": avg_completion_time
        }
    
    def get_with_stats(self, todo_id: TodoId) -> Option[TodoWithStats]:
        """통계 정보가 포함된 Todo 조회"""
        todo_opt = self.get(todo_id)
        if todo_opt.is_none():
            return Option.none()
        
        todo = todo_opt.unwrap()
        todo_dict = todo.dict()
        
        # 통계 정보 추가
        todo_dict['comments_count'] = self._comments_count.get(todo_id, 0)
        todo_dict['attachments_count'] = self._attachments_count.get(todo_id, 0)
        
        # 완료 시간 계산
        if todo.completed_at and todo.created_at:
            delta = todo.completed_at - todo.created_at
            todo_dict['completion_time'] = delta.total_seconds() / 3600
        
        return Option.some(TodoWithStats(**todo_dict))
    
    def add_comment(self, todo_id: TodoId) -> Result[bool, str]:
        """댓글 수 증가 (시뮬레이션)"""
        if not self.exists(todo_id):
            return Result.err(f"Todo {todo_id} not found")
        
        self._comments_count[todo_id] = self._comments_count.get(todo_id, 0) + 1
        return Result.ok(True)
    
    def add_attachment(self, todo_id: TodoId) -> Result[bool, str]:
        """첨부파일 수 증가 (시뮬레이션)"""
        if not self.exists(todo_id):
            return Result.err(f"Todo {todo_id} not found")
        
        self._attachments_count[todo_id] = self._attachments_count.get(todo_id, 0) + 1
        return Result.ok(True)
    
    def get_popular_tags(self, limit: int = 10) -> List[tuple[str, int]]:
        """인기 태그 조회"""
        tag_count: Dict[str, int] = {}
        
        for todo in self.get_all():
            for tag in todo.tags:
                tag_count[tag] = tag_count.get(tag, 0) + 1
        
        # 상위 N개 태그 반환
        sorted_tags = sorted(tag_count.items(), key=lambda x: x[1], reverse=True)
        return sorted_tags[:limit]