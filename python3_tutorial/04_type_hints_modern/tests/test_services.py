"""
Service 테스트
"""

import pytest
from datetime import datetime, timedelta
from todo_app.models.todo import TodoCreate, TodoUpdate
from todo_app.models.user import UserCreate
from todo_app.models.category import CategoryCreate
from todo_app.repositories.todo_repository import TodoRepository
from todo_app.repositories.user_repository import UserRepository
from todo_app.repositories.category_repository import CategoryRepository
from todo_app.services.todo_service import TodoService
from todo_app.services.user_service import UserService
from todo_app.services.category_service import CategoryService
from todo_app.types.base import TodoId, UserId, CategoryId

class TestTodoService:
    """Todo Service 테스트"""
    
    def setup_method(self):
        """테스트 전 초기화"""
        self.todo_repo = TodoRepository()
        self.user_repo = UserRepository()
        self.category_repo = CategoryRepository()
        
        self.todo_service = TodoService(self.todo_repo, self.user_repo, self.category_repo)
        self.user_service = UserService(self.user_repo)
        
        # 테스트용 사용자 생성
        user_data = UserCreate(
            username="testuser",
            email="test@example.com",
            full_name="테스트 사용자",
            password="password123"
        )
        user_result = self.user_service.register_user(user_data)
        self.user_id = user_result.unwrap().id
    
    def test_create_todo(self):
        """Todo 생성 테스트"""
        todo_data = TodoCreate(
            title="테스트 Todo",
            description="테스트용 Todo입니다",
            priority="high",
            tags=["test", "important"]
        )
        
        result = self.todo_service.create_todo(todo_data, self.user_id)
        
        assert result.is_ok()
        todo = result.unwrap()
        assert todo.title == "테스트 Todo"
        assert todo.created_by == self.user_id
        assert todo.priority == "high"
        assert "test" in todo.tags
    
    def test_create_todo_invalid_user(self):
        """존재하지 않는 사용자로 Todo 생성 테스트"""
        todo_data = TodoCreate(title="테스트 Todo")
        invalid_user_id = UserId(999)
        
        result = self.todo_service.create_todo(todo_data, invalid_user_id)
        
        assert result.is_err()
        assert "not found" in result.unwrap_err()
    
    def test_get_todo_with_permission(self):
        """권한이 있는 Todo 조회 테스트"""
        # Todo 생성
        todo_data = TodoCreate(title="내 Todo")
        create_result = self.todo_service.create_todo(todo_data, self.user_id)
        todo = create_result.unwrap()
        
        # 조회
        get_result = self.todo_service.get_todo(todo.id, self.user_id)
        
        assert get_result.is_some()
        retrieved_todo = get_result.unwrap()
        assert retrieved_todo.title == "내 Todo"
    
    def test_get_todo_without_permission(self):
        """권한이 없는 Todo 조회 테스트"""
        # 다른 사용자 생성
        other_user_data = UserCreate(
            username="otheruser",
            email="other@example.com",
            full_name="다른 사용자",
            password="password123"
        )
        other_user_result = self.user_service.register_user(other_user_data)
        other_user_id = other_user_result.unwrap().id
        
        # Todo 생성 (다른 사용자)
        todo_data = TodoCreate(title="다른 사용자의 Todo")
        create_result = self.todo_service.create_todo(todo_data, other_user_id)
        todo = create_result.unwrap()
        
        # 권한 없는 조회 시도
        get_result = self.todo_service.get_todo(todo.id, self.user_id)
        
        assert get_result.is_none()
    
    def test_update_todo(self):
        """Todo 업데이트 테스트"""
        # Todo 생성
        todo_data = TodoCreate(title="원본 Todo", priority="low")
        create_result = self.todo_service.create_todo(todo_data, self.user_id)
        todo = create_result.unwrap()
        
        # 업데이트
        update_data = TodoUpdate(title="수정된 Todo", priority="high", status="in_progress")
        update_result = self.todo_service.update_todo(todo.id, update_data, self.user_id)
        
        assert update_result.is_ok()
        updated_todo = update_result.unwrap()
        assert updated_todo.title == "수정된 Todo"
        assert updated_todo.priority == "high"
        assert updated_todo.status == "in_progress"
    
    def test_complete_todo(self):
        """Todo 완료 처리 테스트"""
        # Todo 생성
        todo_data = TodoCreate(title="완료할 Todo")
        create_result = self.todo_service.create_todo(todo_data, self.user_id)
        todo = create_result.unwrap()
        
        # 완료 처리
        complete_result = self.todo_service.complete_todo(todo.id, self.user_id)
        
        assert complete_result.is_ok()
        
        # 상태 확인
        completed_todo = self.todo_service.get_todo(todo.id, self.user_id).unwrap()
        assert completed_todo.status == "completed"
        assert completed_todo.completed_at is not None
    
    def test_delete_todo(self):
        """Todo 삭제 테스트"""
        # Todo 생성
        todo_data = TodoCreate(title="삭제할 Todo")
        create_result = self.todo_service.create_todo(todo_data, self.user_id)
        todo = create_result.unwrap()
        
        # 삭제
        delete_result = self.todo_service.delete_todo(todo.id, self.user_id)
        
        assert delete_result.is_ok()
        
        # 삭제 확인
        get_result = self.todo_service.get_todo(todo.id, self.user_id)
        assert get_result.is_none()
    
    def test_get_user_todos(self):
        """사용자 Todo 목록 조회 테스트"""
        # 여러 Todo 생성
        todo_titles = ["첫 번째 Todo", "두 번째 Todo", "세 번째 Todo"]
        for title in todo_titles:
            todo_data = TodoCreate(title=title)
            self.todo_service.create_todo(todo_data, self.user_id)
        
        # 목록 조회
        result = self.todo_service.get_user_todos(self.user_id)
        
        assert result.is_ok()
        page = result.unwrap()
        assert len(page.items) == 3
        
        # 제목 확인
        retrieved_titles = [todo.title for todo in page.items]
        for title in todo_titles:
            assert title in retrieved_titles
    
    def test_search_todos(self):
        """Todo 검색 테스트"""
        # 검색 대상 Todo 생성
        todos = [
            TodoCreate(title="Python 학습", description="Python 기초 학습하기"),
            TodoCreate(title="Java 공부", description="Java 프로그래밍"),
            TodoCreate(title="운동하기", description="헬스장에서 운동")
        ]
        
        for todo_data in todos:
            self.todo_service.create_todo(todo_data, self.user_id)
        
        # "Python" 검색
        python_results = self.todo_service.search_todos("Python", self.user_id)
        assert len(python_results) == 1
        assert python_results[0].title == "Python 학습"
        
        # "학습" 검색 (제목 + 설명)
        study_results = self.todo_service.search_todos("학습", self.user_id)
        assert len(study_results) == 1
        
        # "공부" 검색
        study_results2 = self.todo_service.search_todos("공부", self.user_id)
        assert len(study_results2) == 1
        assert study_results2[0].title == "Java 공부"
    
    def test_get_overdue_todos(self):
        """지연된 Todo 조회 테스트"""
        # 지연된 Todo 생성
        overdue_todo = TodoCreate(
            title="지연된 Todo",
            due_date=datetime.now() - timedelta(days=1)
        )
        create_result = self.todo_service.create_todo(overdue_todo, self.user_id)
        
        # 미래 마감일 Todo 생성
        future_todo = TodoCreate(
            title="미래 Todo",
            due_date=datetime.now() + timedelta(days=1)
        )
        self.todo_service.create_todo(future_todo, self.user_id)
        
        # 지연된 Todo 조회
        overdue_todos = self.todo_service.get_overdue_todos(self.user_id)
        
        assert len(overdue_todos) == 1
        assert overdue_todos[0].title == "지연된 Todo"
    
    def test_get_statistics(self):
        """Todo 통계 조회 테스트"""
        # 다양한 상태의 Todo 생성
        todos = [
            TodoCreate(title="완료된 Todo 1", priority="high"),
            TodoCreate(title="완료된 Todo 2", priority="medium"),
            TodoCreate(title="진행중 Todo", priority="low"),
            TodoCreate(title="대기중 Todo", priority="urgent")
        ]
        
        created_todos = []
        for todo_data in todos:
            result = self.todo_service.create_todo(todo_data, self.user_id)
            created_todos.append(result.unwrap())
        
        # 처음 두 개 완료 처리
        for i in range(2):
            self.todo_service.complete_todo(created_todos[i].id, self.user_id)
        
        # 세 번째를 진행중으로 변경
        update_data = TodoUpdate(status="in_progress")
        self.todo_service.update_todo(created_todos[2].id, update_data, self.user_id)
        
        # 통계 조회
        stats = self.todo_service.get_todo_statistics(self.user_id)
        
        assert stats['total'] == 4
        assert stats['completed'] == 2
        assert stats['in_progress'] == 1
        assert stats['pending'] == 1
        assert stats['completion_rate'] == 0.5
        
        # 우선순위별 통계
        assert stats['by_priority']['high'] == 1
        assert stats['by_priority']['medium'] == 1
        assert stats['by_priority']['low'] == 1
        assert stats['by_priority']['urgent'] == 1

class TestUserService:
    """User Service 테스트"""
    
    def setup_method(self):
        """테스트 전 초기화"""
        self.user_repo = UserRepository()
        self.user_service = UserService(self.user_repo)
    
    def test_register_user(self):
        """사용자 등록 테스트"""
        user_data = UserCreate(
            username="newuser",
            email="new@example.com",
            full_name="새 사용자",
            password="password123"
        )
        
        result = self.user_service.register_user(user_data)
        
        assert result.is_ok()
        user = result.unwrap()
        assert user.username == "newuser"
        assert user.email == "new@example.com"
        assert user.is_active
    
    def test_register_duplicate_username(self):
        """중복 사용자명 등록 테스트"""
        user_data = UserCreate(
            username="duplicate",
            email="first@example.com",
            full_name="첫 번째",
            password="password123"
        )
        
        # 첫 번째 등록 성공
        result1 = self.user_service.register_user(user_data)
        assert result1.is_ok()
        
        # 같은 사용자명으로 두 번째 등록 시도
        user_data2 = UserCreate(
            username="duplicate",  # 같은 사용자명
            email="second@example.com",
            full_name="두 번째",
            password="password123"
        )
        
        result2 = self.user_service.register_user(user_data2)
        assert result2.is_err()
        assert "already exists" in result2.unwrap_err()
    
    def test_authenticate(self):
        """사용자 인증 테스트"""
        # 사용자 등록
        user_data = UserCreate(
            username="authuser",
            email="auth@example.com",
            full_name="인증 사용자",
            password="password123"
        )
        self.user_service.register_user(user_data)
        
        # 올바른 인증
        auth_result = self.user_service.authenticate("authuser", "password123")
        assert auth_result.is_some()
        
        user = auth_result.unwrap()
        assert user.username == "authuser"
        
        # 잘못된 비밀번호
        wrong_auth = self.user_service.authenticate("authuser", "wrongpassword")
        assert wrong_auth.is_none()
        
        # 존재하지 않는 사용자
        no_user = self.user_service.authenticate("nouser", "password123")
        assert no_user.is_none()
    
    def test_change_password(self):
        """비밀번호 변경 테스트"""
        # 사용자 등록
        user_data = UserCreate(
            username="pwduser",
            email="pwd@example.com",
            full_name="비밀번호 사용자",
            password="oldpassword"
        )
        result = self.user_service.register_user(user_data)
        user_id = result.unwrap().id
        
        # 비밀번호 변경
        change_result = self.user_service.change_password(
            user_id, "oldpassword", "newpassword"
        )
        assert change_result.is_ok()
        
        # 새 비밀번호로 인증
        auth_result = self.user_service.authenticate("pwduser", "newpassword")
        assert auth_result.is_some()
        
        # 이전 비밀번호로는 인증 실패
        old_auth = self.user_service.authenticate("pwduser", "oldpassword")
        assert old_auth.is_none()

class TestCategoryService:
    """Category Service 테스트"""
    
    def setup_method(self):
        """테스트 전 초기화"""
        self.category_repo = CategoryRepository()
        self.user_repo = UserRepository()
        self.category_service = CategoryService(self.category_repo, self.user_repo)
        self.user_service = UserService(self.user_repo)
        
        # 테스트용 사용자 생성
        user_data = UserCreate(
            username="catuser",
            email="cat@example.com",
            full_name="카테고리 사용자",
            password="password123"
        )
        user_result = self.user_service.register_user(user_data)
        self.user_id = user_result.unwrap().id
    
    def test_create_category(self):
        """카테고리 생성 테스트"""
        category_data = CategoryCreate(
            name="업무",
            description="업무 관련 카테고리",
            color="#FF0000"
        )
        
        result = self.category_service.create_category(category_data, self.user_id)
        
        assert result.is_ok()
        category = result.unwrap()
        assert category.name == "업무"
        assert category.created_by == self.user_id
        assert category.color == "#FF0000"
    
    def test_create_subcategory(self):
        """하위 카테고리 생성 테스트"""
        # 부모 카테고리 생성
        parent_data = CategoryCreate(name="업무", color="#FF0000")
        parent_result = self.category_service.create_category(parent_data, self.user_id)
        parent = parent_result.unwrap()
        
        # 하위 카테고리 생성
        child_data = CategoryCreate(
            name="프로젝트",
            color="#00FF00",
            parent_id=parent.id
        )
        child_result = self.category_service.create_category(child_data, self.user_id)
        
        assert child_result.is_ok()
        child = child_result.unwrap()
        assert child.parent_id == parent.id
    
    def test_get_user_categories(self):
        """사용자 카테고리 조회 테스트"""
        # 여러 카테고리 생성
        categories = ["업무", "개인", "학습"]
        for name in categories:
            category_data = CategoryCreate(name=name, color="#000000")
            self.category_service.create_category(category_data, self.user_id)
        
        # 조회
        result = self.category_service.get_user_categories(self.user_id)
        
        assert result.is_ok()
        user_categories = result.unwrap()
        assert len(user_categories) == 3
        
        category_names = [cat.name for cat in user_categories]
        for name in categories:
            assert name in category_names
    
    def test_update_category(self):
        """카테고리 업데이트 테스트"""
        # 카테고리 생성
        category_data = CategoryCreate(name="원본 카테고리", color="#FF0000")
        create_result = self.category_service.create_category(category_data, self.user_id)
        category = create_result.unwrap()
        
        # 업데이트
        from todo_app.models.category import CategoryUpdate
        update_data = CategoryUpdate(name="수정된 카테고리", color="#00FF00")
        update_result = self.category_service.update_category(
            category.id, update_data, self.user_id
        )
        
        assert update_result.is_ok()
        updated_category = update_result.unwrap()
        assert updated_category.name == "수정된 카테고리"
        assert updated_category.color == "#00FF00"
    
    def test_delete_category(self):
        """카테고리 삭제 테스트"""
        # 카테고리 생성
        category_data = CategoryCreate(name="삭제할 카테고리", color="#FF0000")
        create_result = self.category_service.create_category(category_data, self.user_id)
        category = create_result.unwrap()
        
        # 삭제
        delete_result = self.category_service.delete_category(category.id, self.user_id)
        
        assert delete_result.is_ok()
        
        # 삭제 확인
        get_result = self.category_service.get_category(category.id, self.user_id)
        assert get_result.is_none()
    
    def test_move_category(self):
        """카테고리 이동 테스트"""
        # 두 개의 부모 카테고리 생성
        parent1_data = CategoryCreate(name="부모1", color="#FF0000")
        parent1_result = self.category_service.create_category(parent1_data, self.user_id)
        parent1 = parent1_result.unwrap()
        
        parent2_data = CategoryCreate(name="부모2", color="#00FF00")
        parent2_result = self.category_service.create_category(parent2_data, self.user_id)
        parent2 = parent2_result.unwrap()
        
        # 자식 카테고리 생성
        child_data = CategoryCreate(
            name="자식",
            color="#0000FF",
            parent_id=parent1.id
        )
        child_result = self.category_service.create_category(child_data, self.user_id)
        child = child_result.unwrap()
        
        # 이동
        move_result = self.category_service.move_category(
            child.id, parent2.id, self.user_id
        )
        
        assert move_result.is_ok()
        
        # 이동 확인
        moved_child = self.category_service.get_category(child.id, self.user_id).unwrap()
        assert moved_child.parent_id == parent2.id