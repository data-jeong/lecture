"""
Type-Safe Todo 애플리케이션 메인
"""

import argparse
import json
from typing import Dict, Any, Optional, List
from datetime import datetime, timedelta
from pathlib import Path

from .models.todo import TodoCreate, TodoUpdate
from .models.user import UserCreate, UserUpdate
from .models.category import CategoryCreate, CategoryUpdate
from .repositories.todo_repository import TodoRepository
from .repositories.user_repository import UserRepository
from .repositories.category_repository import CategoryRepository
from .services.todo_service import TodoService
from .services.user_service import UserService
from .services.category_service import CategoryService
from .types.base import TodoId, UserId, CategoryId, Status, Priority
from .types.generics import Result, Option

class TodoApp:
    """Todo 애플리케이션"""
    
    def __init__(self):
        # Repository 초기화
        self.todo_repo = TodoRepository()
        self.user_repo = UserRepository()
        self.category_repo = CategoryRepository()
        
        # Service 초기화
        self.todo_service = TodoService(self.todo_repo, self.user_repo, self.category_repo)
        self.user_service = UserService(self.user_repo)
        self.category_service = CategoryService(self.category_repo, self.user_repo)
        
        # 현재 로그인 사용자
        self.current_user_id: Optional[UserId] = None
        
        # 샘플 데이터 로드
        self._load_sample_data()
    
    def _load_sample_data(self) -> None:
        """샘플 데이터 로드"""
        # 샘플 사용자 생성
        sample_users = [
            UserCreate(
                username="admin",
                email="admin@example.com",
                full_name="관리자",
                password="Admin123!"
            ),
            UserCreate(
                username="john",
                email="john@example.com", 
                full_name="John Doe",
                password="User123!"
            ),
            UserCreate(
                username="jane",
                email="jane@example.com",
                full_name="Jane Smith", 
                password="User123!"
            )
        ]
        
        user_ids = []
        for user_data in sample_users:
            result = self.user_service.register_user(user_data)
            if result.is_ok():
                user = result.unwrap()
                user_ids.append(user.id)
                
                # 첫 번째 사용자를 관리자로 설정
                if user.username == "admin":
                    self.user_repo.grant_admin(user.id)
        
        if not user_ids:
            return
        
        # 샘플 카테고리 생성
        categories_data = [
            CategoryCreate(name="업무", description="업무 관련", color="#EF4444"),
            CategoryCreate(name="개인", description="개인적인 일", color="#3B82F6"),
            CategoryCreate(name="학습", description="공부 및 학습", color="#10B981"),
        ]
        
        category_ids = []
        for cat_data in categories_data:
            result = self.category_service.create_category(cat_data, user_ids[0])
            if result.is_ok():
                category_ids.append(result.unwrap().id)
        
        # 샘플 Todo 생성
        todos_data = [
            TodoCreate(
                title="프로젝트 계획서 작성",
                description="Q4 프로젝트 계획서를 작성해야 함",
                priority="high",
                category_id=category_ids[0] if category_ids else None,
                tags=["프로젝트", "계획"],
                due_date=datetime.now() + timedelta(days=7)
            ),
            TodoCreate(
                title="Python 타입 힌트 학습",
                description="고급 타입 힌트 기능들을 학습하기",
                priority="medium",
                category_id=category_ids[2] if len(category_ids) > 2 else None,
                tags=["python", "학습"],
                due_date=datetime.now() + timedelta(days=3)
            ),
            TodoCreate(
                title="운동하기",
                description="헬스장에서 1시간 운동",
                priority="low",
                category_id=category_ids[1] if len(category_ids) > 1 else None,
                tags=["건강", "운동"]
            )
        ]
        
        for todo_data in todos_data:
            self.todo_service.create_todo(todo_data, user_ids[0])
    
    def login(self, username: str, password: str) -> bool:
        """로그인"""
        user_opt = self.user_service.authenticate(username, password)
        if user_opt.is_some():
            self.current_user_id = user_opt.unwrap().id
            return True
        return False
    
    def logout(self) -> None:
        """로그아웃"""
        self.current_user_id = None
    
    def _require_login(self) -> bool:
        """로그인 필요 확인"""
        if self.current_user_id is None:
            print("❌ 로그인이 필요합니다.")
            return False
        return True
    
    def cmd_login(self, args: argparse.Namespace) -> None:
        """로그인 명령"""
        username = args.username or input("사용자명: ")
        password = args.password or input("비밀번호: ")
        
        if self.login(username, password):
            user = self.user_service.get_user(self.current_user_id).unwrap()
            print(f"✅ 로그인 성공! 환영합니다, {user.full_name}님.")
        else:
            print("❌ 로그인 실패. 사용자명과 비밀번호를 확인해주세요.")
    
    def cmd_logout(self, args: argparse.Namespace) -> None:
        """로그아웃 명령"""
        if self.current_user_id:
            self.logout()
            print("✅ 로그아웃되었습니다.")
        else:
            print("❌ 로그인 상태가 아닙니다.")
    
    def cmd_register(self, args: argparse.Namespace) -> None:
        """사용자 등록 명령"""
        username = args.username or input("사용자명: ")
        email = args.email or input("이메일: ")
        full_name = args.full_name or input("전체 이름: ")
        password = args.password or input("비밀번호: ")
        
        user_data = UserCreate(
            username=username,
            email=email,
            full_name=full_name,
            password=password
        )
        
        result = self.user_service.register_user(user_data)
        if result.is_ok():
            user = result.unwrap()
            print(f"✅ 사용자 등록 성공! ID: {user.id}")
        else:
            print(f"❌ 등록 실패: {result.unwrap_err()}")
    
    def cmd_list_todos(self, args: argparse.Namespace) -> None:
        """Todo 목록 조회"""
        if not self._require_login():
            return
        
        # 필터 옵션 구성
        filters = {}
        if args.status:
            filters['status'] = args.status
        if args.priority:
            filters['priority'] = args.priority
        if args.category:
            filters['category_id'] = CategoryId(args.category)
        if args.search:
            filters['search_query'] = args.search
        
        # 페이지네이션 옵션
        pagination = {
            'page': args.page or 1,
            'per_page': args.limit or 10,
            'sort_by': args.sort_by or 'updated_at',
            'sort_order': args.sort_order or 'desc'
        }
        
        result = self.todo_service.get_user_todos(self.current_user_id, filters, pagination)
        if result.is_err():
            print(f"❌ 조회 실패: {result.unwrap_err()}")
            return
        
        page = result.unwrap()
        
        if not page.items:
            print("📝 할 일이 없습니다.")
            return
        
        print(f"\n📋 할 일 목록 (페이지 {page.page}/{page.total_pages}, 총 {page.total}개)")
        print("-" * 80)
        
        for todo in page.items:
            status_emoji = {
                'pending': '⏳',
                'in_progress': '🔄', 
                'completed': '✅',
                'cancelled': '❌'
            }.get(todo.status, '❓')
            
            priority_emoji = {
                'low': '🟢',
                'medium': '🟡',
                'high': '🟠',
                'urgent': '🔴'
            }.get(todo.priority, '⚪')
            
            print(f"{status_emoji} [{todo.id}] {todo.title}")
            print(f"   {priority_emoji} 우선순위: {todo.priority}")
            
            if todo.description:
                print(f"   📄 {todo.description}")
            
            if todo.tags:
                tags_str = ', '.join(f"#{tag}" for tag in todo.tags)
                print(f"   🏷️  {tags_str}")
            
            if todo.due_date:
                due_str = todo.due_date.strftime("%Y-%m-%d %H:%M")
                overdue = "⚠️ 지연!" if todo.is_overdue() else ""
                print(f"   📅 마감: {due_str} {overdue}")
            
            print()
    
    def cmd_add_todo(self, args: argparse.Namespace) -> None:
        """Todo 추가"""
        if not self._require_login():
            return
        
        title = args.title or input("제목: ")
        description = args.description or input("설명 (선택): ") or None
        priority = args.priority or "medium"
        
        # 카테고리 선택
        category_id = None
        if args.category:
            category_id = CategoryId(args.category)
        
        # 태그 처리
        tags = []
        if args.tags:
            tags = [tag.strip() for tag in args.tags.split(',')]
        
        # 마감일 처리
        due_date = None
        if args.due_date:
            try:
                due_date = datetime.fromisoformat(args.due_date)
            except ValueError:
                print("❌ 잘못된 날짜 형식입니다. YYYY-MM-DD HH:MM 형식을 사용해주세요.")
                return
        
        todo_data = TodoCreate(
            title=title,
            description=description,
            priority=priority,
            category_id=category_id,
            tags=tags,
            due_date=due_date
        )
        
        result = self.todo_service.create_todo(todo_data, self.current_user_id)
        if result.is_ok():
            todo = result.unwrap()
            print(f"✅ Todo 추가 완료! ID: {todo.id}")
        else:
            print(f"❌ 추가 실패: {result.unwrap_err()}")
    
    def cmd_complete_todo(self, args: argparse.Namespace) -> None:
        """Todo 완료 처리"""
        if not self._require_login():
            return
        
        todo_id = TodoId(args.id)
        result = self.todo_service.complete_todo(todo_id, self.current_user_id)
        
        if result.is_ok():
            print(f"✅ Todo {todo_id} 완료 처리되었습니다!")
        else:
            print(f"❌ 완료 처리 실패: {result.unwrap_err()}")
    
    def cmd_delete_todo(self, args: argparse.Namespace) -> None:
        """Todo 삭제"""
        if not self._require_login():
            return
        
        todo_id = TodoId(args.id)
        result = self.todo_service.delete_todo(todo_id, self.current_user_id)
        
        if result.is_ok():
            print(f"✅ Todo {todo_id} 삭제되었습니다!")
        else:
            print(f"❌ 삭제 실패: {result.unwrap_err()}")
    
    def cmd_list_categories(self, args: argparse.Namespace) -> None:
        """카테고리 목록 조회"""
        if not self._require_login():
            return
        
        result = self.category_service.get_user_categories(self.current_user_id, include_tree=args.tree)
        if result.is_err():
            print(f"❌ 조회 실패: {result.unwrap_err()}")
            return
        
        if args.tree:
            # 트리 구조로 출력
            trees = result.unwrap()
            if not trees:
                print("📁 카테고리가 없습니다.")
                return
            
            print("\n📁 카테고리 트리")
            print("-" * 40)
            
            def print_tree(tree_nodes, indent=0):
                for node in tree_nodes:
                    prefix = "  " * indent + ("└─ " if indent > 0 else "")
                    print(f"{prefix}[{node.category.id}] {node.category.name}")
                    if node.category.description:
                        print(f"{'  ' * (indent + 1)}📄 {node.category.description}")
                    print_tree(node.children, indent + 1)
            
            print_tree(trees)
        else:
            # 평면 목록
            categories = result.unwrap()
            if not categories:
                print("📁 카테고리가 없습니다.")
                return
            
            print(f"\n📁 카테고리 목록 (총 {len(categories)}개)")
            print("-" * 40)
            
            for cat in categories:
                print(f"[{cat.id}] {cat.name}")
                if cat.description:
                    print(f"  📄 {cat.description}")
                print(f"  🎨 {cat.color} | 📊 Todo: {cat.todo_count}개")
                print()
    
    def cmd_add_category(self, args: argparse.Namespace) -> None:
        """카테고리 추가"""
        if not self._require_login():
            return
        
        name = args.name or input("카테고리 이름: ")
        description = args.description or input("설명 (선택): ") or None
        color = args.color or "#3B82F6"
        
        parent_id = None
        if args.parent:
            parent_id = CategoryId(args.parent)
        
        category_data = CategoryCreate(
            name=name,
            description=description,
            color=color,
            parent_id=parent_id
        )
        
        result = self.category_service.create_category(category_data, self.current_user_id)
        if result.is_ok():
            category = result.unwrap()
            print(f"✅ 카테고리 추가 완료! ID: {category.id}")
        else:
            print(f"❌ 추가 실패: {result.unwrap_err()}")
    
    def cmd_stats(self, args: argparse.Namespace) -> None:
        """통계 조회"""
        if not self._require_login():
            return
        
        # Todo 통계
        todo_stats = self.todo_service.get_todo_statistics(self.current_user_id)
        
        print("\n📊 Todo 통계")
        print("-" * 40)
        print(f"전체: {todo_stats['total']}개")
        print(f"완료: {todo_stats['completed']}개")
        print(f"진행중: {todo_stats['in_progress']}개")
        print(f"대기중: {todo_stats['pending']}개")
        print(f"지연: {todo_stats['overdue']}개")
        print(f"완료율: {todo_stats['completion_rate']:.1%}")
        
        if todo_stats['average_completion_time']:
            print(f"평균 완료 시간: {todo_stats['average_completion_time']:.1f}시간")
        
        # 우선순위별 통계
        print("\n🔥 우선순위별")
        for priority, count in todo_stats['by_priority'].items():
            if count > 0:
                print(f"  {priority}: {count}개")
        
        # 카테고리 통계
        result = self.category_service.get_category_statistics(self.current_user_id)
        if result.is_ok():
            cat_stats = result.unwrap()
            print(f"\n📁 카테고리: {cat_stats['total_categories']}개")
            print(f"최대 깊이: {cat_stats['max_depth']}단계")

def create_parser() -> argparse.ArgumentParser:
    """CLI 파서 생성"""
    parser = argparse.ArgumentParser(description="Type-Safe Todo 애플리케이션")
    subparsers = parser.add_subparsers(dest='command', help='사용 가능한 명령어')
    
    # 로그인
    login_parser = subparsers.add_parser('login', help='로그인')
    login_parser.add_argument('--username', '-u', help='사용자명')
    login_parser.add_argument('--password', '-p', help='비밀번호')
    
    # 로그아웃
    subparsers.add_parser('logout', help='로그아웃')
    
    # 사용자 등록
    register_parser = subparsers.add_parser('register', help='사용자 등록')
    register_parser.add_argument('--username', '-u', help='사용자명')
    register_parser.add_argument('--email', '-e', help='이메일')
    register_parser.add_argument('--full-name', '-n', help='전체 이름')
    register_parser.add_argument('--password', '-p', help='비밀번호')
    
    # Todo 목록
    list_parser = subparsers.add_parser('list', help='Todo 목록 조회')
    list_parser.add_argument('--status', choices=['pending', 'in_progress', 'completed', 'cancelled'])
    list_parser.add_argument('--priority', choices=['low', 'medium', 'high', 'urgent'])
    list_parser.add_argument('--category', type=int, help='카테고리 ID')
    list_parser.add_argument('--search', help='검색어')
    list_parser.add_argument('--page', type=int, default=1, help='페이지 번호')
    list_parser.add_argument('--limit', type=int, default=10, help='페이지당 개수')
    list_parser.add_argument('--sort-by', choices=['created_at', 'updated_at', 'priority', 'title'], default='updated_at')
    list_parser.add_argument('--sort-order', choices=['asc', 'desc'], default='desc')
    
    # Todo 추가
    add_parser = subparsers.add_parser('add', help='Todo 추가')
    add_parser.add_argument('--title', '-t', help='제목')
    add_parser.add_argument('--description', '-d', help='설명')
    add_parser.add_argument('--priority', '-p', choices=['low', 'medium', 'high', 'urgent'], default='medium')
    add_parser.add_argument('--category', '-c', type=int, help='카테고리 ID')
    add_parser.add_argument('--tags', help='태그 (쉼표로 구분)')
    add_parser.add_argument('--due-date', help='마감일 (YYYY-MM-DD HH:MM)')
    
    # Todo 완료
    complete_parser = subparsers.add_parser('complete', help='Todo 완료 처리')
    complete_parser.add_argument('id', type=int, help='Todo ID')
    
    # Todo 삭제
    delete_parser = subparsers.add_parser('delete', help='Todo 삭제')
    delete_parser.add_argument('id', type=int, help='Todo ID')
    
    # 카테고리 목록
    cat_list_parser = subparsers.add_parser('categories', help='카테고리 목록')
    cat_list_parser.add_argument('--tree', action='store_true', help='트리 구조로 출력')
    
    # 카테고리 추가
    cat_add_parser = subparsers.add_parser('category', help='카테고리 추가')
    cat_add_parser.add_argument('--name', '-n', help='카테고리 이름')
    cat_add_parser.add_argument('--description', '-d', help='설명')
    cat_add_parser.add_argument('--color', '-c', help='색상 코드')
    cat_add_parser.add_argument('--parent', '-p', type=int, help='부모 카테고리 ID')
    
    # 통계
    subparsers.add_parser('stats', help='통계 조회')
    
    return parser

def main():
    """메인 함수"""
    app = TodoApp()
    parser = create_parser()
    
    # 인터랙티브 모드 또는 명령행 모드
    import sys
    if len(sys.argv) == 1:
        # 인터랙티브 모드
        print("🎯 Type-Safe Todo 애플리케이션")
        print("도움말: --help 또는 -h")
        print("종료: exit 또는 quit")
        print()
        
        while True:
            try:
                command = input("todo> ").strip()
                if command in ['exit', 'quit']:
                    break
                if not command:
                    continue
                
                args = parser.parse_args(command.split())
                
                # 명령어 실행
                command_methods = {
                    'login': app.cmd_login,
                    'logout': app.cmd_logout,
                    'register': app.cmd_register,
                    'list': app.cmd_list_todos,
                    'add': app.cmd_add_todo,
                    'complete': app.cmd_complete_todo,
                    'delete': app.cmd_delete_todo,
                    'categories': app.cmd_list_categories,
                    'category': app.cmd_add_category,
                    'stats': app.cmd_stats,
                }
                
                if args.command in command_methods:
                    command_methods[args.command](args)
                else:
                    print(f"❌ 알 수 없는 명령어: {args.command}")
            
            except KeyboardInterrupt:
                print("\n👋 안녕히 가세요!")
                break
            except Exception as e:
                print(f"❌ 오류: {e}")
    else:
        # 명령행 모드
        args = parser.parse_args()
        
        command_methods = {
            'login': app.cmd_login,
            'logout': app.cmd_logout,
            'register': app.cmd_register,
            'list': app.cmd_list_todos,
            'add': app.cmd_add_todo,
            'complete': app.cmd_complete_todo,
            'delete': app.cmd_delete_todo,
            'categories': app.cmd_list_categories,
            'category': app.cmd_add_category,
            'stats': app.cmd_stats,
        }
        
        if args.command in command_methods:
            command_methods[args.command](args)
        else:
            parser.print_help()

if __name__ == "__main__":
    main()