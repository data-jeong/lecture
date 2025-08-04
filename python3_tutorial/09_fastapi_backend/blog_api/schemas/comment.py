from typing import Optional, List
from datetime import datetime
from pydantic import BaseModel, Field

from .user import User


class CommentBase(BaseModel):
    content: str = Field(..., min_length=1)
    parent_id: Optional[int] = None
    
    @field_validator('content')
    @classmethod
    def validate_content(cls, v):
        v = v.strip()
        if not v:
            raise ValueError('Comment cannot be empty')
        if len(v) > 1000:
            raise ValueError('Comment is too long (max 1000 characters)')
        return v


class CommentCreate(CommentBase):
    post_id: int


class CommentUpdate(BaseModel):
    content: str = Field(..., min_length=1)


class CommentAuthor(BaseModel):
    id: int
    username: str
    avatar_url: Optional[str] = None
    
    class Config:
        from_attributes = True


class Comment(CommentBase):
    id: int
    post_id: int
    author: CommentAuthor
    is_approved: bool = True
    is_deleted: bool = False
    likes_count: int = 0
    dislikes_count: int = 0
    created_at: datetime
    updated_at: Optional[datetime] = None
    replies: List['Comment'] = []
    
    class Config:
        from_attributes = True


class CommentInDB(Comment):
    author_id: int


# Update forward references
Comment.model_rebuild()