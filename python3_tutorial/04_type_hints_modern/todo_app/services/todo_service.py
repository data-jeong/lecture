"""
Todo 서비스
"""

from typing import List, Optional, Dict, Any
from datetime import datetime, timedelta
from ..models.todo import Todo, TodoCreate, TodoUpdate, TodoWithStats
from ..models.user import User
from ..models.category import Category
from ..types.base import TodoId, UserId, CategoryId, Status, Priority, FilterOptions, PaginationOptions
from ..types.generics import Result, Option, Page
from ..repositories.todo_repository import TodoRepository
from ..repositories.user_repository import UserRepository
from ..repositories.category_repository import CategoryRepository

class TodoService:
    """Todo 비즈니스 로직"""
    
    def __init__(
        self,
        todo_repo: TodoRepository,
        user_repo: UserRepository,
        category_repo: CategoryRepository
    ):
        self._todo_repo = todo_repo
        self._user_repo = user_repo
        self._category_repo = category_repo
    
    def create_todo(self, todo_data: TodoCreate, user_id: UserId) -> Result[Todo, str]:
        """Todo 생성"""
        # 사용자 존재 확인
        user_opt = self._user_repo.get(user_id)
        if user_opt.is_none():
            return Result.err(f"User {user_id} not found")
        
        user = user_opt.unwrap()
        if not user.is_active:
            return Result.err("Inactive user cannot create todos")
        
        # 카테고리 존재 확인
        if todo_data.category_id:
            category_opt = self._category_repo.get(todo_data.category_id)
            if category_opt.is_none():
                return Result.err(f"Category {todo_data.category_id} not found")
        
        # Todo 객체 생성
        now = datetime.now()
        todo = Todo(
            **todo_data.dict(),
            id=TodoId(0),  # Repository에서 할당
            created_by=user_id,
            created_at=now,
            updated_at=now,
        )
        
        # 저장
        result = self._todo_repo.add(todo)
        if result.is_err():
            return Result.err(result.unwrap_err())
        
        todo_id = result.unwrap()
        created_todo = self._todo_repo.get(todo_id).unwrap()
        
        return Result.ok(created_todo)
    
    def get_todo(self, todo_id: TodoId, user_id: UserId) -> Option[Todo]:
        """Todo 조회 (권한 확인)"""
        todo_opt = self._todo_repo.get(todo_id)
        if todo_opt.is_none():
            return Option.none()
        
        todo = todo_opt.unwrap()
        
        # 권한 확인
        if not todo.can_edit(user_id):
            # 관리자 권한 확인
            user_opt = self._user_repo.get(user_id)
            if user_opt.is_none() or not user_opt.unwrap().is_admin:
                return Option.none()
        
        return Option.some(todo)
    
    def update_todo(self, todo_id: TodoId, update_data: TodoUpdate, user_id: UserId) -> Result[Todo, str]:
        """Todo 업데이트"""
        todo_opt = self.get_todo(todo_id, user_id)
        if todo_opt.is_none():
            return Result.err("Todo not found or no permission")
        
        todo = todo_opt.unwrap()
        
        # 업데이트할 필드만 적용
        update_dict = update_data.dict(exclude_unset=True)
        
        # 카테고리 변경 시 존재 확인
        if 'category_id' in update_dict and update_dict['category_id']:
            category_opt = self._category_repo.get(update_dict['category_id'])
            if category_opt.is_none():
                return Result.err(f"Category {update_dict['category_id']} not found")
        
        # 담당자 변경 시 존재 확인
        if 'assigned_to' in update_dict and update_dict['assigned_to']:
            assignee_opt = self._user_repo.get(update_dict['assigned_to'])
            if assignee_opt.is_none():
                return Result.err(f"User {update_dict['assigned_to']} not found")
        
        # 필드 업데이트
        for field, value in update_dict.items():
            setattr(todo, field, value)
        
        todo.updated_at = datetime.now()
        
        # 완료 처리 시 완료 시간 설정
        if update_dict.get('status') == 'completed' and not todo.completed_at:
            todo.completed_at = datetime.now()
        
        result = self._todo_repo.update(todo_id, todo)
        if result.is_err():
            return Result.err(result.unwrap_err())
        
        return Result.ok(todo)
    
    def delete_todo(self, todo_id: TodoId, user_id: UserId) -> Result[bool, str]:
        """Todo 삭제"""
        todo_opt = self.get_todo(todo_id, user_id)
        if todo_opt.is_none():
            return Result.err("Todo not found or no permission")
        
        return self._todo_repo.delete(todo_id)
    
    def get_user_todos(
        self, 
        user_id: UserId, 
        filters: Optional[FilterOptions] = None,
        pagination: Optional[PaginationOptions] = None
    ) -> Result[Page[Todo], str]:
        """사용자 Todo 목록 조회"""
        # 기본 필터에 사용자 필터 추가
        user_filters = filters or {}
        
        # 사용자 본인 Todo만 조회하도록 필터링
        todos = self._todo_repo.get_by_user(user_id)
        
        # 추가 필터 적용
        if user_filters:
            filtered_todos = []
            for todo in todos:
                if self._matches_filters(todo, user_filters):
                    filtered_todos.append(todo)
            todos = filtered_todos
        
        # 페이지네이션 적용
        if pagination:
            return self._paginate_todos(todos, pagination)
        
        # 기본 페이지네이션
        default_pagination = {
            'page': 1,
            'per_page': 20,
            'sort_by': 'updated_at',
            'sort_order': 'desc'
        }
        return self._paginate_todos(todos, default_pagination)
    
    def assign_todo(self, todo_id: TodoId, assignee_id: UserId, assigner_id: UserId) -> Result[bool, str]:
        """Todo 할당"""
        # Todo 존재 및 권한 확인
        todo_opt = self.get_todo(todo_id, assigner_id)
        if todo_opt.is_none():
            return Result.err("Todo not found or no permission")
        
        # 담당자 존재 확인
        assignee_opt = self._user_repo.get(assignee_id)
        if assignee_opt.is_none():
            return Result.err(f"User {assignee_id} not found")
        
        return self._todo_repo.assign_to_user(todo_id, assignee_id)
    
    def complete_todo(self, todo_id: TodoId, user_id: UserId) -> Result[bool, str]:
        """Todo 완료 처리"""
        todo_opt = self.get_todo(todo_id, user_id)
        if todo_opt.is_none():
            return Result.err("Todo not found or no permission")
        
        return self._todo_repo.mark_completed(todo_id)
    
    def get_overdue_todos(self, user_id: UserId) -> List[Todo]:
        """사용자의 지연된 Todo 조회"""
        user_todos = self._todo_repo.get_by_user(user_id)
        return [todo for todo in user_todos if todo.is_overdue()]
    
    def get_due_soon_todos(self, user_id: UserId, days: int = 7) -> List[Todo]:
        """곧 마감인 Todo 조회"""
        user_todos = self._todo_repo.get_by_user(user_id)
        now = datetime.now()
        future = now + timedelta(days=days)
        
        return [
            todo for todo in user_todos
            if todo.due_date and now <= todo.due_date <= future and todo.status != "completed"
        ]
    
    def search_todos(self, query: str, user_id: UserId) -> List[Todo]:
        """Todo 검색"""
        user_todos = self._todo_repo.get_by_user(user_id)
        query_lower = query.lower()
        
        return [
            todo for todo in user_todos
            if query_lower in todo.title.lower()
            or (todo.description and query_lower in todo.description.lower())
            or any(query_lower in tag.lower() for tag in todo.tags)
        ]
    
    def get_todo_statistics(self, user_id: UserId) -> Dict[str, Any]:
        """사용자 Todo 통계"""
        return self._todo_repo.get_statistics(user_id)
    
    def get_todo_with_stats(self, todo_id: TodoId, user_id: UserId) -> Option[TodoWithStats]:
        """통계가 포함된 Todo 조회"""
        # 권한 확인
        if self.get_todo(todo_id, user_id).is_none():
            return Option.none()
        
        return self._todo_repo.get_with_stats(todo_id)
    
    def bulk_update_status(self, todo_ids: List[TodoId], status: Status, user_id: UserId) -> Result[int, str]:
        """여러 Todo 상태 일괄 업데이트"""
        updated_count = 0
        
        for todo_id in todo_ids:
            update_data = TodoUpdate(status=status)
            result = self.update_todo(todo_id, update_data, user_id)
            if result.is_ok():
                updated_count += 1
        
        return Result.ok(updated_count)
    
    def get_popular_tags(self, user_id: Optional[UserId] = None, limit: int = 10) -> List[tuple[str, int]]:
        """인기 태그 조회"""
        if user_id:
            # 특정 사용자의 태그만
            todos = self._todo_repo.get_by_user(user_id)
            tag_count: Dict[str, int] = {}
            
            for todo in todos:
                for tag in todo.tags:
                    tag_count[tag] = tag_count.get(tag, 0) + 1
            
            sorted_tags = sorted(tag_count.items(), key=lambda x: x[1], reverse=True)
            return sorted_tags[:limit]
        else:
            # 전체 태그
            return self._todo_repo.get_popular_tags(limit)
    
    def _matches_filters(self, todo: Todo, filters: FilterOptions) -> bool:
        """Todo가 필터 조건에 맞는지 확인"""
        if filters.get('status') and todo.status != filters['status']:
            return False
        
        if filters.get('priority') and todo.priority != filters['priority']:
            return False
        
        if filters.get('category_id') and todo.category_id != filters['category_id']:
            return False
        
        if filters.get('assigned_to') and todo.assigned_to != filters['assigned_to']:
            return False
        
        if filters.get('tags'):
            filter_tags = set(filters['tags'])
            if not filter_tags.intersection(set(todo.tags)):
                return False
        
        if filters.get('created_after') and todo.created_at < filters['created_after']:
            return False
        
        if filters.get('created_before') and todo.created_at > filters['created_before']:
            return False
        
        if filters.get('search_query'):
            query = filters['search_query'].lower()
            if not (
                query in todo.title.lower()
                or (todo.description and query in todo.description.lower())
                or any(query in tag.lower() for tag in todo.tags)
            ):
                return False
        
        return True
    
    def _paginate_todos(self, todos: List[Todo], pagination: PaginationOptions) -> Result[Page[Todo], str]:
        """Todo 목록 페이지네이션"""
        # 정렬
        sort_field = pagination.get('sort_by', 'updated_at')
        reverse = pagination.get('sort_order', 'desc') == 'desc'
        
        try:
            todos.sort(key=lambda t: getattr(t, sort_field, ''), reverse=reverse)
        except AttributeError:
            return Result.err(f"Invalid sort field: {sort_field}")
        
        # 페이지네이션
        page = pagination.get('page', 1)
        per_page = pagination.get('per_page', 20)
        start = (page - 1) * per_page
        end = start + per_page
        
        page_result = Page(
            items=todos[start:end],
            total=len(todos),
            page=page,
            per_page=per_page
        )
        
        return Result.ok(page_result)