"""
Category 서비스
"""

from typing import List, Optional, Dict, Any
from datetime import datetime
from ..models.category import Category, CategoryCreate, CategoryUpdate, CategoryTree
from ..types.base import CategoryId, UserId
from ..types.generics import Result, Option
from ..repositories.category_repository import CategoryRepository
from ..repositories.user_repository import UserRepository

class CategoryService:
    """Category 비즈니스 로직"""
    
    def __init__(self, category_repo: CategoryRepository, user_repo: UserRepository):
        self._category_repo = category_repo
        self._user_repo = user_repo
    
    def create_category(self, category_data: CategoryCreate, user_id: UserId) -> Result[Category, str]:
        """카테고리 생성"""
        # 사용자 존재 및 권한 확인
        user_opt = self._user_repo.get(user_id)
        if user_opt.is_none():
            return Result.err(f"User {user_id} not found")
        
        user = user_opt.unwrap()
        if not user.is_active:
            return Result.err("Inactive user cannot create categories")
        
        # 부모 카테고리 존재 확인
        if category_data.parent_id:
            parent_opt = self._category_repo.get(category_data.parent_id)
            if parent_opt.is_none():
                return Result.err(f"Parent category {category_data.parent_id} not found")
            
            # 부모 카테고리 소유자 확인 (선택사항)
            parent = parent_opt.unwrap()
            if parent.created_by != user_id and not user.is_admin:
                return Result.err("Cannot create subcategory under other user's category")
        
        # 같은 이름의 카테고리 중복 확인 (같은 부모 하에서)
        existing_categories = self._category_repo.get_by_user(user_id)
        for cat in existing_categories:
            if (cat.name.lower() == category_data.name.lower() and 
                cat.parent_id == category_data.parent_id):
                return Result.err(f"Category '{category_data.name}' already exists at this level")
        
        # Category 객체 생성
        now = datetime.now()
        category = Category(
            **category_data.dict(),
            id=CategoryId(0),  # Repository에서 할당
            created_by=user_id,
            created_at=now,
            updated_at=now,
        )
        
        # 저장
        result = self._category_repo.add(category)
        if result.is_err():
            return Result.err(result.unwrap_err())
        
        category_id = result.unwrap()
        created_category = self._category_repo.get(category_id).unwrap()
        
        return Result.ok(created_category)
    
    def get_category(self, category_id: CategoryId, user_id: UserId) -> Option[Category]:
        """카테고리 조회 (권한 확인)"""
        category_opt = self._category_repo.get(category_id)
        if category_opt.is_none():
            return Option.none()
        
        category = category_opt.unwrap()
        
        # 비활성 카테고리는 소유자와 관리자만 볼 수 있음
        if not category.is_active:
            if category.created_by != user_id:
                user_opt = self._user_repo.get(user_id)
                if user_opt.is_none() or not user_opt.unwrap().is_admin:
                    return Option.none()
        
        return Option.some(category)
    
    def update_category(self, category_id: CategoryId, update_data: CategoryUpdate, user_id: UserId) -> Result[Category, str]:
        """카테고리 업데이트"""
        category_opt = self.get_category(category_id, user_id)
        if category_opt.is_none():
            return Result.err("Category not found")
        
        category = category_opt.unwrap()
        
        # 권한 확인
        user_opt = self._user_repo.get(user_id)
        if user_opt.is_none():
            return Result.err("User not found")
        
        user = user_opt.unwrap()
        if category.created_by != user_id and not user.is_admin:
            return Result.err("Permission denied")
        
        # 업데이트할 필드만 적용
        update_dict = update_data.dict(exclude_unset=True)
        
        # 부모 카테고리 변경 시 검증
        if 'parent_id' in update_dict:
            new_parent_id = update_dict['parent_id']
            if new_parent_id:
                # 부모 카테고리 존재 확인
                parent_opt = self._category_repo.get(new_parent_id)
                if parent_opt.is_none():
                    return Result.err(f"Parent category {new_parent_id} not found")
                
                # 순환 참조 방지
                all_categories = self._category_repo.get_all()
                if not category.can_be_parent_of(new_parent_id, all_categories):
                    return Result.err("Cannot create circular reference")
        
        # 이름 중복 확인
        if 'name' in update_dict:
            new_name = update_dict['name']
            parent_id = update_dict.get('parent_id', category.parent_id)
            
            user_categories = self._category_repo.get_by_user(category.created_by)
            for cat in user_categories:
                if (cat.id != category_id and 
                    cat.name.lower() == new_name.lower() and 
                    cat.parent_id == parent_id):
                    return Result.err(f"Category '{new_name}' already exists at this level")
        
        # 필드 업데이트
        for field, value in update_dict.items():
            setattr(category, field, value)
        
        category.updated_at = datetime.now()
        
        result = self._category_repo.update(category_id, category)
        if result.is_err():
            return Result.err(result.unwrap_err())
        
        return Result.ok(category)
    
    def delete_category(self, category_id: CategoryId, user_id: UserId, force: bool = False) -> Result[bool, str]:
        """카테고리 삭제"""
        category_opt = self.get_category(category_id, user_id)
        if category_opt.is_none():
            return Result.err("Category not found")
        
        category = category_opt.unwrap()
        
        # 권한 확인
        user_opt = self._user_repo.get(user_id)
        if user_opt.is_none():
            return Result.err("User not found")
        
        user = user_opt.unwrap()
        if category.created_by != user_id and not user.is_admin:
            return Result.err("Permission denied")
        
        # 자식 카테고리 확인
        children = self._category_repo.get_children(category_id)
        if children and not force:
            return Result.err("Cannot delete category with subcategories. Use force=True to delete all.")
        
        # Todo 연결 확인 (실제로는 Todo 서비스와 연동)
        if category.todo_count > 0 and not force:
            return Result.err("Cannot delete category with todos. Use force=True to proceed.")
        
        if force:
            # 자식 카테고리들과 함께 비활성화
            return self._category_repo.deactivate_with_descendants(category_id).map(lambda count: count > 0)
        else:
            # 단일 카테고리 삭제
            return self._category_repo.delete(category_id)
    
    def get_user_categories(self, user_id: UserId, include_tree: bool = False) -> Result[List[Category] | List[CategoryTree], str]:
        """사용자 카테고리 조회"""
        user_opt = self._user_repo.get(user_id)
        if user_opt.is_none():
            return Result.err("User not found")
        
        if include_tree:
            tree = self._category_repo.get_tree(user_id)
            return Result.ok(tree)
        else:
            categories = self._category_repo.get_by_user(user_id)
            return Result.ok(categories)
    
    def get_category_tree(self, user_id: UserId) -> Result[List[CategoryTree], str]:
        """카테고리 트리 구조 조회"""
        return self.get_user_categories(user_id, include_tree=True)
    
    def move_category(self, category_id: CategoryId, new_parent_id: Optional[CategoryId], user_id: UserId) -> Result[bool, str]:
        """카테고리 이동"""
        category_opt = self.get_category(category_id, user_id)
        if category_opt.is_none():
            return Result.err("Category not found")
        
        category = category_opt.unwrap()
        
        # 권한 확인
        user_opt = self._user_repo.get(user_id)
        if user_opt.is_none():
            return Result.err("User not found")
        
        user = user_opt.unwrap()
        if category.created_by != user_id and not user.is_admin:
            return Result.err("Permission denied")
        
        # 새 부모 카테고리 권한 확인
        if new_parent_id:
            parent_opt = self.get_category(new_parent_id, user_id)
            if parent_opt.is_none():
                return Result.err("New parent category not found or no permission")
        
        return self._category_repo.move_category(category_id, new_parent_id)
    
    def search_categories(self, query: str, user_id: UserId) -> List[Category]:
        """카테고리 검색"""
        user_categories = self._category_repo.get_by_user(user_id)
        query_lower = query.lower()
        
        return [
            cat for cat in user_categories
            if query_lower in cat.name.lower()
            or (cat.description and query_lower in cat.description.lower())
        ]
    
    def get_category_path(self, category_id: CategoryId, user_id: UserId) -> Result[str, str]:
        """카테고리 전체 경로 조회"""
        if self.get_category(category_id, user_id).is_none():
            return Result.err("Category not found or no permission")
        
        path = self._category_repo.get_path(category_id)
        return Result.ok(path)
    
    def merge_categories(self, source_id: CategoryId, target_id: CategoryId, user_id: UserId) -> Result[bool, str]:
        """카테고리 병합"""
        # 두 카테고리 모두 접근 권한 확인
        source_opt = self.get_category(source_id, user_id)
        target_opt = self.get_category(target_id, user_id)
        
        if source_opt.is_none():
            return Result.err("Source category not found or no permission")
        if target_opt.is_none():
            return Result.err("Target category not found or no permission")
        
        source = source_opt.unwrap()
        target = target_opt.unwrap()
        
        # 권한 확인
        user_opt = self._user_repo.get(user_id)
        if user_opt.is_none():
            return Result.err("User not found")
        
        user = user_opt.unwrap()
        if ((source.created_by != user_id or target.created_by != user_id) and 
            not user.is_admin):
            return Result.err("Permission denied")
        
        return self._category_repo.merge_categories(source_id, target_id)
    
    def get_category_statistics(self, user_id: UserId) -> Result[Dict[str, Any], str]:
        """카테고리 통계"""
        user_opt = self._user_repo.get(user_id)
        if user_opt.is_none():
            return Result.err("User not found")
        
        stats = self._category_repo.get_statistics(user_id)
        return Result.ok(stats)
    
    def validate_category_hierarchy(self, user_id: UserId) -> Result[List[str], str]:
        """카테고리 계층 구조 검증"""
        user_opt = self._user_repo.get(user_id)
        if user_opt.is_none():
            return Result.err("User not found")
        
        errors = self._category_repo.validate_hierarchy()
        return Result.ok(errors)
    
    def get_popular_categories(self, user_id: Optional[UserId] = None, limit: int = 10) -> List[tuple[str, int]]:
        """인기 카테고리 조회 (Todo 수 기준)"""
        if user_id:
            categories = self._category_repo.get_by_user(user_id)
        else:
            categories = self._category_repo.get_all()
        
        # Todo 수 기준으로 정렬
        category_stats = [(cat.name, cat.todo_count) for cat in categories if cat.is_active]
        category_stats.sort(key=lambda x: x[1], reverse=True)
        
        return category_stats[:limit]
    
    def bulk_update_categories(self, category_ids: List[CategoryId], update_data: CategoryUpdate, user_id: UserId) -> Result[int, str]:
        """여러 카테고리 일괄 업데이트"""
        updated_count = 0
        
        for category_id in category_ids:
            result = self.update_category(category_id, update_data, user_id)
            if result.is_ok():
                updated_count += 1
        
        return Result.ok(updated_count)