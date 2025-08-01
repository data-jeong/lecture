"""
Category Pydantic 모델
"""

from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel, Field, validator, root_validator
from ..types.base import CategoryId, UserId, Color, TodoId

class CategoryBase(BaseModel):
    """Category 기본 모델"""
    name: str = Field(..., min_length=1, max_length=50, description="카테고리 이름")
    description: Optional[str] = Field(None, max_length=200, description="설명")
    color: Color = Field("#3B82F6", pattern="^#[0-9A-Fa-f]{6}$", description="색상 코드")
    icon: Optional[str] = Field(None, max_length=50, description="아이콘 이름")
    parent_id: Optional[CategoryId] = Field(None, description="부모 카테고리 ID")
    
    @validator('name')
    def name_must_not_be_empty(cls, v: str) -> str:
        """이름 검증"""
        if not v or v.isspace():
            raise ValueError('카테고리 이름은 비어있을 수 없습니다')
        return v.strip()
    
    @validator('color')
    def color_must_be_valid(cls, v: str) -> str:
        """색상 코드 검증"""
        v = v.upper()
        if not v.startswith('#'):
            v = f'#{v}'
        if len(v) != 7:
            raise ValueError('색상 코드는 #RRGGBB 형식이어야 합니다')
        return v

class CategoryCreate(CategoryBase):
    """Category 생성 모델"""
    pass

class CategoryUpdate(BaseModel):
    """Category 업데이트 모델"""
    name: Optional[str] = Field(None, min_length=1, max_length=50)
    description: Optional[str] = Field(None, max_length=200)
    color: Optional[Color] = Field(None, pattern="^#[0-9A-Fa-f]{6}$")
    icon: Optional[str] = Field(None, max_length=50)
    parent_id: Optional[CategoryId] = None
    
    @root_validator(skip_on_failure=True)
    def at_least_one_field(cls, values: dict) -> dict:
        """최소 하나의 필드는 있어야 함"""
        if not any(v is not None for v in values.values()):
            raise ValueError('최소 하나의 필드를 업데이트해야 합니다')
        return values

class Category(CategoryBase):
    """Category 전체 모델"""
    id: CategoryId
    created_by: UserId
    created_at: datetime
    updated_at: datetime
    is_active: bool = True
    
    # 관계
    todo_count: int = 0
    subcategory_ids: List[CategoryId] = Field(default_factory=list)
    
    class Config:
        """Pydantic 설정"""
        from_attributes = True
        json_encoders = {
            datetime: lambda v: v.isoformat(),
        }
        schema_extra = {
            "example": {
                "id": 1,
                "name": "업무",
                "description": "업무 관련 할 일",
                "color": "#EF4444",
                "icon": "briefcase",
                "parent_id": None,
                "created_by": 1,
                "created_at": "2024-01-01T00:00:00",
                "updated_at": "2024-01-01T00:00:00",
                "is_active": True,
                "todo_count": 15,
                "subcategory_ids": [2, 3]
            }
        }
    
    def get_full_path(self, categories: List['Category']) -> str:
        """전체 경로 반환 (부모 > 자식)"""
        path_parts = [self.name]
        current = self
        
        while current.parent_id:
            parent = next((c for c in categories if c.id == current.parent_id), None)
            if parent:
                path_parts.insert(0, parent.name)
                current = parent
            else:
                break
        
        return " > ".join(path_parts)
    
    def can_be_parent_of(self, category_id: CategoryId, all_categories: List['Category']) -> bool:
        """순환 참조 방지 - 특정 카테고리의 부모가 될 수 있는지 확인"""
        if self.id == category_id:
            return False
        
        # 자신의 자손인지 확인
        descendants = self._get_descendants(all_categories)
        return category_id not in descendants
    
    def _get_descendants(self, all_categories: List['Category']) -> set[CategoryId]:
        """모든 자손 카테고리 ID 반환"""
        descendants = set()
        to_check = [self.id]
        
        while to_check:
            current_id = to_check.pop()
            for cat in all_categories:
                if cat.parent_id == current_id and cat.id not in descendants:
                    descendants.add(cat.id)
                    to_check.append(cat.id)
        
        return descendants

class CategoryTree(BaseModel):
    """카테고리 트리 구조"""
    category: Category
    children: List['CategoryTree'] = Field(default_factory=list)
    depth: int = 0
    
    class Config:
        """Pydantic 설정"""
        from_attributes = True
    
    @classmethod
    def build_tree(cls, categories: List[Category], parent_id: Optional[CategoryId] = None, depth: int = 0) -> List['CategoryTree']:
        """카테고리 리스트에서 트리 구조 생성"""
        tree = []
        for category in categories:
            if category.parent_id == parent_id:
                node = cls(
                    category=category,
                    depth=depth,
                    children=cls.build_tree(categories, category.id, depth + 1)
                )
                tree.append(node)
        return tree
    
    def flatten(self) -> List[tuple[Category, int]]:
        """트리를 평탄화 - (카테고리, 깊이) 튜플 리스트 반환"""
        result = [(self.category, self.depth)]
        for child in self.children:
            result.extend(child.flatten())
        return result

class CategoryStatistics(BaseModel):
    """카테고리 통계"""
    category_id: CategoryId
    name: str
    total_todos: int = 0
    completed_todos: int = 0
    pending_todos: int = 0
    in_progress_todos: int = 0
    overdue_todos: int = 0
    
    @property
    def completion_rate(self) -> float:
        """완료율"""
        if self.total_todos == 0:
            return 0.0
        return self.completed_todos / self.total_todos
    
    @property
    def is_empty(self) -> bool:
        """비어있는지 확인"""
        return self.total_todos == 0

# Update forward reference
CategoryTree.model_rebuild()