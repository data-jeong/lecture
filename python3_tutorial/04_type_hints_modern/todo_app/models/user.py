"""
User Pydantic 모델
"""

from datetime import datetime
from typing import Optional, List, Set
from pydantic import BaseModel, Field, validator
try:
    from pydantic import EmailStr
except ImportError:
    EmailStr = str
from ..types.base import UserId, Email, TodoId

class UserBase(BaseModel):
    """User 기본 모델"""
    username: str = Field(..., min_length=3, max_length=50, pattern="^[a-zA-Z0-9_]+$")
    email: EmailStr
    full_name: str = Field(..., min_length=1, max_length=100)
    
    @validator('username')
    def username_alphanumeric(cls, v: str) -> str:
        """사용자명 검증"""
        assert v.replace('_', '').isalnum(), '사용자명은 영문자, 숫자, 언더스코어만 가능합니다'
        return v.lower()
    
    @validator('full_name')
    def full_name_valid(cls, v: str) -> str:
        """전체 이름 검증"""
        return v.strip()

class UserCreate(UserBase):
    """User 생성 모델"""
    password: str = Field(..., min_length=8, max_length=100)
    
    @validator('password')
    def password_strength(cls, v: str) -> str:
        """비밀번호 강도 검증"""
        if not any(c.isupper() for c in v):
            raise ValueError('비밀번호는 최소 하나의 대문자를 포함해야 합니다')
        if not any(c.islower() for c in v):
            raise ValueError('비밀번호는 최소 하나의 소문자를 포함해야 합니다')
        if not any(c.isdigit() for c in v):
            raise ValueError('비밀번호는 최소 하나의 숫자를 포함해야 합니다')
        return v

class UserUpdate(BaseModel):
    """User 업데이트 모델"""
    email: Optional[EmailStr] = None
    full_name: Optional[str] = Field(None, min_length=1, max_length=100)
    password: Optional[str] = Field(None, min_length=8, max_length=100)
    is_active: Optional[bool] = None

class User(UserBase):
    """User 전체 모델"""
    id: UserId
    is_active: bool = True
    is_admin: bool = False
    created_at: datetime
    updated_at: datetime
    last_login: Optional[datetime] = None
    
    # 관계
    created_todos: List[TodoId] = Field(default_factory=list)
    assigned_todos: List[TodoId] = Field(default_factory=list)
    
    class Config:
        """Pydantic 설정"""
        from_attributes = True
        json_encoders = {
            datetime: lambda v: v.isoformat(),
        }
    
    def can_create_todo(self, current_todo_count: int, max_todos: int = 100) -> bool:
        """Todo 생성 가능 여부"""
        return self.is_active and current_todo_count < max_todos
    
    def can_manage_user(self, target_user_id: UserId) -> bool:
        """다른 사용자 관리 권한"""
        return self.is_admin or self.id == target_user_id

class UserWithPassword(User):
    """비밀번호가 포함된 User 모델 (내부용)"""
    hashed_password: str

class UserProfile(BaseModel):
    """공개 프로필용 User 모델"""
    id: UserId
    username: str
    full_name: str
    created_at: datetime
    todo_count: int = 0
    completed_todo_count: int = 0
    
    @property
    def completion_rate(self) -> float:
        """할 일 완료율"""
        if self.todo_count == 0:
            return 0.0
        return self.completed_todo_count / self.todo_count

class UserSettings(BaseModel):
    """사용자 설정"""
    user_id: UserId
    theme: str = "light"
    language: str = "ko"
    timezone: str = "Asia/Seoul"
    notifications_enabled: bool = True
    email_notifications: bool = True
    daily_reminder_time: Optional[str] = "09:00"  # HH:MM format
    
    @validator('daily_reminder_time')
    def validate_time_format(cls, v: Optional[str]) -> Optional[str]:
        """시간 형식 검증"""
        if v is None:
            return v
        try:
            hour, minute = v.split(':')
            hour_int = int(hour)
            minute_int = int(minute)
            if not (0 <= hour_int <= 23 and 0 <= minute_int <= 59):
                raise ValueError
            return f"{hour_int:02d}:{minute_int:02d}"
        except (ValueError, AttributeError):
            raise ValueError('시간은 HH:MM 형식이어야 합니다')

# Type for user permissions
class UserPermissions(BaseModel):
    """사용자 권한"""
    can_create_todos: bool = True
    can_delete_todos: bool = True
    can_assign_todos: bool = True
    can_manage_categories: bool = True
    can_view_all_todos: bool = False
    can_manage_users: bool = False
    max_todos: int = 100
    max_categories: int = 20