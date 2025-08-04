"""
Category Repository 구현
"""

from typing import List, Optional, Dict, Set
from ..models.category import Category, CategoryTree
from ..types.base import CategoryId, UserId
from ..types.generics import Result, Option
from .base import InMemoryRepository

class CategoryRepository(InMemoryRepository[Category, CategoryId]):
    """Category 전용 Repository"""
    
    def __init__(self):
        super().__init__(Category)
    
    def get_by_user(self, user_id: UserId) -> List[Category]:
        """사용자가 생성한 카테고리 조회"""
        return self.filter(lambda c: c.created_by == user_id and c.is_active)
    
    def get_root_categories(self) -> List[Category]:
        """루트 카테고리 조회"""
        return self.filter(lambda c: c.parent_id is None and c.is_active)
    
    def get_children(self, parent_id: CategoryId) -> List[Category]:
        """자식 카테고리 조회"""
        return self.filter(lambda c: c.parent_id == parent_id and c.is_active)
    
    def get_descendants(self, category_id: CategoryId) -> List[Category]:
        """모든 자손 카테고리 조회"""
        descendants = []
        to_check = [category_id]
        
        while to_check:
            current_id = to_check.pop()
            children = self.get_children(current_id)
            descendants.extend(children)
            to_check.extend([c.id for c in children])
        
        return descendants
    
    def get_ancestors(self, category_id: CategoryId) -> List[Category]:
        """모든 조상 카테고리 조회"""
        ancestors = []
        current_opt = self.get(category_id)
        
        while current_opt.is_some():
            current = current_opt.unwrap()
            if current.parent_id:
                parent_opt = self.get(current.parent_id)
                if parent_opt.is_some():
                    ancestors.append(parent_opt.unwrap())
                    current_opt = parent_opt
                else:
                    break
            else:
                break
        
        return list(reversed(ancestors))
    
    def find_by_name(self, name: str, user_id: Optional[UserId] = None) -> List[Category]:
        """이름으로 카테고리 검색"""
        name_lower = name.lower()
        categories = self.filter(
            lambda c: name_lower in c.name.lower() and c.is_active
        )
        
        if user_id:
            categories = [c for c in categories if c.created_by == user_id]
        
        return categories
    
    def get_tree(self, user_id: Optional[UserId] = None) -> List[CategoryTree]:
        """카테고리 트리 구조 반환"""
        if user_id:
            categories = self.get_by_user(user_id)
        else:
            categories = self.filter(lambda c: c.is_active)
        
        return CategoryTree.build_tree(categories)
    
    def move_category(self, category_id: CategoryId, new_parent_id: Optional[CategoryId]) -> Result[bool, str]:
        """카테고리 이동"""
        category_opt = self.get(category_id)
        if category_opt.is_none():
            return Result.err(f"Category {category_id} not found")
        
        category = category_opt.unwrap()
        
        # 자기 자신을 부모로 설정하는 것 방지
        if new_parent_id == category_id:
            return Result.err("Category cannot be its own parent")
        
        # 순환 참조 방지
        if new_parent_id:
            descendants = self.get_descendants(category_id)
            if any(d.id == new_parent_id for d in descendants):
                return Result.err("Cannot move category to its descendant")
        
        # 부모 변경
        category.parent_id = new_parent_id
        return self.update(category_id, category)
    
    def deactivate_with_descendants(self, category_id: CategoryId) -> Result[int, str]:
        """카테고리와 모든 자손 비활성화"""
        category_opt = self.get(category_id)
        if category_opt.is_none():
            return Result.err(f"Category {category_id} not found")
        
        # 자손 포함 모든 카테고리 가져오기
        to_deactivate = [category_opt.unwrap()]
        to_deactivate.extend(self.get_descendants(category_id))
        
        # 비활성화
        deactivated_count = 0
        for cat in to_deactivate:
            cat.is_active = False
            result = self.update(cat.id, cat)
            if result.is_ok():
                deactivated_count += 1
        
        return Result.ok(deactivated_count)
    
    def merge_categories(self, source_id: CategoryId, target_id: CategoryId) -> Result[bool, str]:
        """카테고리 병합"""
        if source_id == target_id:
            return Result.err("Cannot merge category with itself")
        
        source_opt = self.get(source_id)
        target_opt = self.get(target_id)
        
        if source_opt.is_none():
            return Result.err(f"Source category {source_id} not found")
        if target_opt.is_none():
            return Result.err(f"Target category {target_id} not found")
        
        source = source_opt.unwrap()
        target = target_opt.unwrap()
        
        # 자식 카테고리들을 타겟으로 이동
        children = self.get_children(source_id)
        for child in children:
            child.parent_id = target_id
            self.update(child.id, child)
        
        # 소스 카테고리 비활성화
        source.is_active = False
        return self.update(source_id, source)
    
    def get_path(self, category_id: CategoryId) -> str:
        """카테고리 전체 경로 반환"""
        category_opt = self.get(category_id)
        if category_opt.is_none():
            return ""
        
        category = category_opt.unwrap()
        ancestors = self.get_ancestors(category_id)
        
        path_parts = [c.name for c in ancestors]
        path_parts.append(category.name)
        
        return " > ".join(path_parts)
    
    def validate_hierarchy(self) -> List[str]:
        """계층 구조 검증"""
        errors = []
        categories = self.get_all()
        
        for category in categories:
            if category.parent_id:
                # 부모 존재 확인
                parent_opt = self.get(category.parent_id)
                if parent_opt.is_none():
                    errors.append(f"Category {category.id} has invalid parent {category.parent_id}")
                
                # 순환 참조 확인
                visited = set()
                current = category
                
                while current.parent_id and current.id not in visited:
                    visited.add(current.id)
                    parent_opt = self.get(current.parent_id)
                    if parent_opt.is_none():
                        break
                    current = parent_opt.unwrap()
                    
                    if current.id in visited:
                        errors.append(f"Circular reference detected for category {category.id}")
                        break
        
        return errors
    
    def get_statistics(self, user_id: Optional[UserId] = None) -> Dict[str, any]:
        """카테고리 통계"""
        if user_id:
            categories = self.get_by_user(user_id)
        else:
            categories = self.filter(lambda c: c.is_active)
        
        root_count = len([c for c in categories if c.parent_id is None])
        max_depth = self._calculate_max_depth(categories)
        
        # 각 카테고리의 자식 수 계산
        children_counts = {}
        for cat in categories:
            children_counts[cat.id] = len(self.get_children(cat.id))
        
        avg_children = sum(children_counts.values()) / len(categories) if categories else 0
        
        return {
            "total_categories": len(categories),
            "root_categories": root_count,
            "max_depth": max_depth,
            "average_children": avg_children,
            "categories_with_children": len([c for c in children_counts.values() if c > 0]),
            "leaf_categories": len([c for c in children_counts.values() if c == 0]),
        }
    
    def _calculate_max_depth(self, categories: List[Category]) -> int:
        """최대 깊이 계산"""
        if not categories:
            return 0
        
        tree = CategoryTree.build_tree(categories)
        return self._get_tree_depth(tree)
    
    def _get_tree_depth(self, trees: List[CategoryTree]) -> int:
        """트리 깊이 계산"""
        if not trees:
            return 0
        
        max_depth = 0
        for tree in trees:
            depth = 1 + self._get_tree_depth(tree.children)
            max_depth = max(max_depth, depth)
        
        return max_depth