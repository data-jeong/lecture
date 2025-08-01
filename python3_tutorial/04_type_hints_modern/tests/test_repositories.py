"""
Repository 테스트
"""

import pytest
from datetime import datetime, timedelta
from todo_app.models.todo import Todo
from todo_app.models.user import User
from todo_app.models.category import Category
from todo_app.repositories.todo_repository import TodoRepository
from todo_app.repositories.user_repository import UserRepository
from todo_app.repositories.category_repository import CategoryRepository
from todo_app.types.base import TodoId, UserId, CategoryId

class TestTodoRepository:
    """Todo Repository 테스트"""
    
    def setup_method(self):
        """테스트 전 초기화"""
        self.repo = TodoRepository()
        
        # 샘플 Todo 생성
        self.sample_todo = Todo(
            id=TodoId(1),
            title="테스트 Todo",
            description="테스트용 Todo입니다",
            priority="medium",
            status="pending",
            category_id=None,
            assigned_to=None,
            tags=["test"],
            created_at=datetime.now(),
            updated_at=datetime.now(),
            created_by=UserId(1),
            due_date=datetime.now() + timedelta(days=1)
        )
    
    def test_add_todo(self):
        """Todo 추가 테스트"""
        result = self.repo.add(self.sample_todo)
        
        assert result.is_ok()
        todo_id = result.unwrap()
        assert isinstance(todo_id, int)
        assert self.repo.exists(todo_id)
    
    def test_get_todo(self):
        """Todo 조회 테스트"""
        # Todo 추가
        result = self.repo.add(self.sample_todo)
        todo_id = result.unwrap()
        
        # 조회
        todo_opt = self.repo.get(todo_id)
        assert todo_opt.is_some()
        
        todo = todo_opt.unwrap()
        assert todo.title == "테스트 Todo"
        assert todo.created_by == UserId(1)
    
    def test_update_todo(self):
        """Todo 업데이트 테스트"""
        # Todo 추가
        result = self.repo.add(self.sample_todo)
        todo_id = result.unwrap()
        
        # 업데이트
        updated_todo = self.sample_todo
        updated_todo.title = "업데이트된 Todo"
        updated_todo.status = "completed"
        
        update_result = self.repo.update(todo_id, updated_todo)
        assert update_result.is_ok()
        
        # 확인
        todo_opt = self.repo.get(todo_id)
        todo = todo_opt.unwrap()
        assert todo.title == "업데이트된 Todo"
        assert todo.status == "completed"
    
    def test_delete_todo(self):
        """Todo 삭제 테스트"""
        # Todo 추가
        result = self.repo.add(self.sample_todo)
        todo_id = result.unwrap()
        
        # 삭제
        delete_result = self.repo.delete(todo_id)
        assert delete_result.is_ok()
        assert not self.repo.exists(todo_id)
    
    def test_filter_todos(self):
        """Todo 필터링 테스트"""
        # 여러 Todo 추가
        todo1 = self.sample_todo
        todo1.priority = "high"
        
        todo2 = Todo(
            id=TodoId(2),
            title="두 번째 Todo",
            priority="low",
            status="pending",
            created_at=datetime.now(),
            updated_at=datetime.now(),
            created_by=UserId(2),
            tags=["other"]
        )
        
        self.repo.add(todo1)
        self.repo.add(todo2)
        
        # 우선순위로 필터링
        high_priority_todos = self.repo.filter(lambda t: t.priority == "high")
        assert len(high_priority_todos) == 1
        assert high_priority_todos[0].title == "테스트 Todo"
    
    def test_get_by_user(self):
        """사용자별 Todo 조회 테스트"""
        # 다른 사용자의 Todo 추가
        todo2 = Todo(
            id=TodoId(2),
            title="다른 사용자 Todo",
            priority="medium",
            status="pending",
            created_at=datetime.now(),
            updated_at=datetime.now(),
            created_by=UserId(2),
            assigned_to=UserId(2),
            tags=[]
        )
        
        self.repo.add(self.sample_todo)
        self.repo.add(todo2)
        
        # 사용자 1의 Todo만 조회
        user1_todos = self.repo.get_by_user(UserId(1))
        assert len(user1_todos) == 1
        assert user1_todos[0].title == "테스트 Todo"
    
    def test_search_todos(self):
        """Todo 검색 테스트"""
        self.repo.add(self.sample_todo)
        
        # 제목으로 검색
        results = self.repo.search("테스트")
        assert len(results) == 1
        
        # 설명으로 검색
        results = self.repo.search("테스트용")
        assert len(results) == 1
        
        # 없는 내용 검색
        results = self.repo.search("없는내용")
        assert len(results) == 0
    
    def test_get_overdue_todos(self):
        """지연된 Todo 조회 테스트"""
        # 과거 마감일 Todo
        overdue_todo = Todo(
            id=TodoId(2),
            title="지연된 Todo",
            priority="medium",
            status="pending",
            created_at=datetime.now(),
            updated_at=datetime.now(),
            created_by=UserId(1),
            due_date=datetime.now() - timedelta(days=1),
            tags=[]
        )
        
        self.repo.add(self.sample_todo)  # 미래 마감일
        self.repo.add(overdue_todo)     # 과거 마감일
        
        overdue_todos = self.repo.get_overdue()
        assert len(overdue_todos) == 1
        assert overdue_todos[0].title == "지연된 Todo"

class TestUserRepository:
    """User Repository 테스트"""
    
    def setup_method(self):
        """테스트 전 초기화"""
        self.repo = UserRepository()
        
        self.sample_user = User(
            id=UserId(1),
            username="testuser",
            email="test@example.com",
            full_name="테스트 사용자",
            created_at=datetime.now(),
            updated_at=datetime.now()
        )
    
    def test_add_user_with_password(self):
        """비밀번호와 함께 사용자 추가 테스트"""
        result = self.repo.add_with_password(self.sample_user, "password123")
        
        assert result.is_ok()
        user_id = result.unwrap()
        assert self.repo.exists(user_id)
    
    def test_find_by_username(self):
        """사용자명으로 조회 테스트"""
        self.repo.add_with_password(self.sample_user, "password123")
        
        user_opt = self.repo.find_by_username("testuser")
        assert user_opt.is_some()
        
        user = user_opt.unwrap()
        assert user.email == "test@example.com"
    
    def test_authenticate(self):
        """사용자 인증 테스트"""
        self.repo.add_with_password(self.sample_user, "password123")
        
        # 올바른 인증
        auth_result = self.repo.authenticate("testuser", "password123")
        assert auth_result.is_some()
        
        # 잘못된 비밀번호
        wrong_auth = self.repo.authenticate("testuser", "wrongpassword")
        assert wrong_auth.is_none()
        
        # 없는 사용자
        no_user = self.repo.authenticate("nouser", "password123")
        assert no_user.is_none()
    
    def test_change_password(self):
        """비밀번호 변경 테스트"""
        result = self.repo.add_with_password(self.sample_user, "oldpassword")
        user_id = result.unwrap()
        
        # 비밀번호 변경
        change_result = self.repo.change_password(user_id, "oldpassword", "newpassword")
        assert change_result.is_ok()
        
        # 새 비밀번호로 인증
        auth_result = self.repo.authenticate("testuser", "newpassword")
        assert auth_result.is_some()
        
        # 이전 비밀번호로는 인증 실패
        old_auth = self.repo.authenticate("testuser", "oldpassword")
        assert old_auth.is_none()

class TestCategoryRepository:
    """Category Repository 테스트"""
    
    def setup_method(self):
        """테스트 전 초기화"""
        self.repo = CategoryRepository()
        
        self.sample_category = Category(
            id=CategoryId(1),
            name="테스트 카테고리",
            description="테스트용 카테고리",
            color="#FF0000",
            created_by=UserId(1),
            created_at=datetime.now(),
            updated_at=datetime.now()
        )
    
    def test_add_category(self):
        """카테고리 추가 테스트"""
        result = self.repo.add(self.sample_category)
        
        assert result.is_ok()
        category_id = result.unwrap()
        assert self.repo.exists(category_id)
    
    def test_get_by_user(self):
        """사용자별 카테고리 조회 테스트"""
        # 다른 사용자 카테고리
        other_category = Category(
            id=CategoryId(2),
            name="다른 사용자 카테고리",
            color="#00FF00",
            created_by=UserId(2),
            created_at=datetime.now(),
            updated_at=datetime.now()
        )
        
        self.repo.add(self.sample_category)
        self.repo.add(other_category)
        
        user1_categories = self.repo.get_by_user(UserId(1))
        assert len(user1_categories) == 1
        assert user1_categories[0].name == "테스트 카테고리"
    
    def test_hierarchy_operations(self):
        """계층 구조 테스트"""
        # 부모 카테고리 추가
        parent_result = self.repo.add(self.sample_category)
        parent_id = parent_result.unwrap()
        
        # 자식 카테고리 추가
        child_category = Category(
            id=CategoryId(2),
            name="자식 카테고리",
            color="#00FF00",
            parent_id=parent_id,
            created_by=UserId(1),
            created_at=datetime.now(),
            updated_at=datetime.now()
        )
        
        child_result = self.repo.add(child_category)
        child_id = child_result.unwrap()
        
        # 루트 카테고리 조회
        root_categories = self.repo.get_root_categories()
        assert len(root_categories) == 1
        assert root_categories[0].name == "테스트 카테고리"
        
        # 자식 카테고리 조회
        children = self.repo.get_children(parent_id)
        assert len(children) == 1
        assert children[0].name == "자식 카테고리"
        
        # 자손 카테고리 조회
        descendants = self.repo.get_descendants(parent_id)
        assert len(descendants) == 1
        assert descendants[0].name == "자식 카테고리"
    
    def test_move_category(self):
        """카테고리 이동 테스트"""
        # 두 개의 루트 카테고리 생성
        parent1_result = self.repo.add(self.sample_category)
        parent1_id = parent1_result.unwrap()
        
        parent2 = Category(
            id=CategoryId(2),
            name="두 번째 부모",
            color="#00FF00",
            created_by=UserId(1),
            created_at=datetime.now(),
            updated_at=datetime.now()
        )
        parent2_result = self.repo.add(parent2)
        parent2_id = parent2_result.unwrap()
        
        # 자식 카테고리 생성
        child = Category(
            id=CategoryId(3),
            name="자식 카테고리",
            color="#0000FF",
            parent_id=parent1_id,
            created_by=UserId(1),
            created_at=datetime.now(),
            updated_at=datetime.now()
        )
        child_result = self.repo.add(child)
        child_id = child_result.unwrap()
        
        # 자식을 다른 부모로 이동
        move_result = self.repo.move_category(child_id, parent2_id)
        assert move_result.is_ok()
        
        # 확인
        moved_child = self.repo.get(child_id).unwrap()
        assert moved_child.parent_id == parent2_id