"""
기본 타입 정의
"""

from typing import NewType, Literal, TypeAlias, TypedDict, Optional
from datetime import datetime

# NewType을 사용한 타입 안전성
TodoId = NewType('TodoId', int)
UserId = NewType('UserId', int)
CategoryId = NewType('CategoryId', int)

# Literal 타입
Priority = Literal['low', 'medium', 'high', 'urgent']
Status = Literal['pending', 'in_progress', 'completed', 'cancelled']
SortOrder = Literal['asc', 'desc']
SortField = Literal['created_at', 'updated_at', 'priority', 'title']

# Type Alias
Email: TypeAlias = str
TagName: TypeAlias = str
Color: TypeAlias = str  # Hex color code

# TypedDict for structured data
class FilterOptions(TypedDict, total=False):
    """필터 옵션"""
    status: Optional[Status]
    priority: Optional[Priority]
    category_id: Optional[CategoryId]
    assigned_to: Optional[UserId]
    tags: Optional[list[TagName]]
    created_after: Optional[datetime]
    created_before: Optional[datetime]
    search_query: Optional[str]

class PaginationOptions(TypedDict):
    """페이지네이션 옵션"""
    page: int
    per_page: int
    sort_by: SortField
    sort_order: SortOrder

class TodoDict(TypedDict):
    """Todo 딕셔너리 타입"""
    id: TodoId
    title: str
    description: Optional[str]
    priority: Priority
    status: Status
    category_id: Optional[CategoryId]
    assigned_to: Optional[UserId]
    tags: list[TagName]
    created_at: datetime
    updated_at: datetime
    completed_at: Optional[datetime]

class UserDict(TypedDict):
    """User 딕셔너리 타입"""
    id: UserId
    username: str
    email: Email
    full_name: str
    is_active: bool
    created_at: datetime

class CategoryDict(TypedDict):
    """Category 딕셔너리 타입"""
    id: CategoryId
    name: str
    color: Color
    icon: Optional[str]
    parent_id: Optional[CategoryId]

# Config TypedDict
class AppConfig(TypedDict):
    """애플리케이션 설정"""
    debug: bool
    database_url: str
    max_todos_per_user: int
    default_page_size: int
    cache_ttl: int
    enable_notifications: bool

class DatabaseConfig(TypedDict):
    """데이터베이스 설정"""
    host: str
    port: int
    database: str
    username: str
    password: str
    pool_size: int
    echo: bool

# Error types
class ErrorInfo(TypedDict):
    """에러 정보"""
    code: str
    message: str
    details: Optional[dict[str, any]]
    timestamp: datetime

# Statistics types
class TodoStatistics(TypedDict):
    """Todo 통계"""
    total: int
    completed: int
    pending: int
    in_progress: int
    overdue: int
    by_priority: dict[Priority, int]
    by_category: dict[str, int]
    completion_rate: float
    average_completion_time: Optional[float]  # in hours