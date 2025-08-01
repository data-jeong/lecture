"""
Todo Pydantic 모델
"""

from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel, Field, validator, root_validator
from ..types.base import TodoId, UserId, CategoryId, Priority, Status, TagName

class TodoBase(BaseModel):
    """Todo 기본 모델"""
    title: str = Field(..., min_length=1, max_length=200, description="할 일 제목")
    description: Optional[str] = Field(None, max_length=1000, description="설명")
    priority: Priority = Field("medium", description="우선순위")
    category_id: Optional[CategoryId] = Field(None, description="카테고리 ID")
    assigned_to: Optional[UserId] = Field(None, description="담당자 ID")
    tags: List[TagName] = Field(default_factory=list, description="태그 목록")
    due_date: Optional[datetime] = Field(None, description="마감일")
    
    @validator('title')
    def title_must_not_be_empty(cls, v: str) -> str:
        """제목 검증"""
        if not v or v.isspace():
            raise ValueError('제목은 비어있을 수 없습니다')
        return v.strip()
    
    @validator('tags', each_item=True)
    def validate_tag(cls, v: str) -> str:
        """태그 검증"""
        if not v or v.isspace():
            raise ValueError('태그는 비어있을 수 없습니다')
        if len(v) > 20:
            raise ValueError('태그는 20자를 초과할 수 없습니다')
        return v.strip().lower()
    
    @validator('due_date')
    def due_date_must_be_future(cls, v: Optional[datetime]) -> Optional[datetime]:
        """마감일 검증"""
        if v and v < datetime.now():
            raise ValueError('마감일은 미래여야 합니다')
        return v

class TodoCreate(TodoBase):
    """Todo 생성 모델"""
    pass

class TodoUpdate(BaseModel):
    """Todo 업데이트 모델"""
    title: Optional[str] = Field(None, min_length=1, max_length=200)
    description: Optional[str] = Field(None, max_length=1000)
    priority: Optional[Priority] = None
    status: Optional[Status] = None
    category_id: Optional[CategoryId] = None
    assigned_to: Optional[UserId] = None
    tags: Optional[List[TagName]] = None
    due_date: Optional[datetime] = None
    
    @validator('title')
    def title_must_not_be_empty(cls, v: Optional[str]) -> Optional[str]:
        """제목 검증"""
        if v is not None and (not v or v.isspace()):
            raise ValueError('제목은 비어있을 수 없습니다')
        return v.strip() if v else None
    
    @root_validator(skip_on_failure=True)
    def at_least_one_field(cls, values: dict) -> dict:
        """최소 하나의 필드는 있어야 함"""
        if not any(v is not None for v in values.values()):
            raise ValueError('최소 하나의 필드를 업데이트해야 합니다')
        return values

class Todo(TodoBase):
    """Todo 전체 모델"""
    id: TodoId
    status: Status = "pending"
    created_at: datetime
    updated_at: datetime
    completed_at: Optional[datetime] = None
    created_by: UserId
    
    class Config:
        """Pydantic 설정"""
        from_attributes = True
        json_encoders = {
            datetime: lambda v: v.isoformat(),
        }
        json_schema_extra = {
            "example": {
                "id": 1,
                "title": "프로젝트 완료하기",
                "description": "Python 타입 힌트 프로젝트 마무리",
                "priority": "high",
                "status": "in_progress",
                "category_id": 1,
                "assigned_to": 1,
                "tags": ["프로젝트", "python"],
                "due_date": "2024-12-31T23:59:59",
                "created_at": "2024-01-01T00:00:00",
                "updated_at": "2024-01-01T00:00:00",
                "created_by": 1
            }
        }
    
    def is_overdue(self) -> bool:
        """마감일 초과 여부"""
        if self.due_date and self.status != "completed":
            return datetime.now() > self.due_date
        return False
    
    def can_edit(self, user_id: UserId) -> bool:
        """편집 권한 확인"""
        return user_id == self.created_by or user_id == self.assigned_to
    
    def mark_completed(self) -> None:
        """완료 처리"""
        self.status = "completed"
        self.completed_at = datetime.now()
        self.updated_at = datetime.now()
    
    def assign_to(self, user_id: UserId) -> None:
        """담당자 할당"""
        self.assigned_to = user_id
        self.updated_at = datetime.now()

class TodoWithStats(Todo):
    """통계가 포함된 Todo 모델"""
    comments_count: int = 0
    attachments_count: int = 0
    completion_time: Optional[float] = None  # 완료까지 걸린 시간 (시간 단위)
    
    @root_validator(skip_on_failure=True)
    def calculate_completion_time(cls, values: dict) -> dict:
        """완료 시간 계산"""
        if values.get('completed_at') and values.get('created_at'):
            delta = values['completed_at'] - values['created_at']
            values['completion_time'] = delta.total_seconds() / 3600
        return values