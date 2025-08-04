from typing import Optional, List
from datetime import datetime
from pydantic import BaseModel, Field, field_validator
import re

from ..models.post import PostStatus


class TagBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=50)
    
    @field_validator('name')
    @classmethod
    def validate_tag_name(cls, v):
        v = v.strip().lower()
        if not re.match(r'^[a-z0-9-]+$', v):
            raise ValueError('Tag must contain only lowercase letters, numbers, and hyphens')
        return v


class Tag(TagBase):
    id: int
    slug: str
    created_at: datetime
    
    class Config:
        from_attributes = True


class CategoryBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=100)
    description: Optional[str] = Field(None, max_length=500)


class Category(CategoryBase):
    id: int
    slug: str
    created_at: datetime
    updated_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True


class PostBase(BaseModel):
    title: str = Field(..., min_length=1, max_length=200)
    content: str = Field(..., min_length=10)
    excerpt: Optional[str] = Field(None, max_length=500)
    category_id: Optional[int] = None
    tags: Optional[List[str]] = []
    status: PostStatus = PostStatus.DRAFT
    is_featured: bool = False
    allow_comments: bool = True
    featured_image: Optional[str] = None
    meta_title: Optional[str] = Field(None, max_length=200)
    meta_description: Optional[str] = Field(None, max_length=300)
    meta_keywords: Optional[str] = Field(None, max_length=200)
    
    @field_validator('title')
    @classmethod
    def validate_title(cls, v):
        v = v.strip()
        if not v:
            raise ValueError('Title cannot be empty')
        return v
        
    @field_validator('excerpt')
    @classmethod
    def generate_excerpt(cls, v, values):
        if not v and 'content' in values.data:
            content = values.data['content']
            # Strip HTML tags if present
            content = re.sub(r'<[^>]+>', '', content)
            # Take first 200 characters
            v = content[:200] + '...' if len(content) > 200 else content
        return v


class PostCreate(PostBase):
    pass


class PostUpdate(BaseModel):
    title: Optional[str] = Field(None, min_length=1, max_length=200)
    content: Optional[str] = Field(None, min_length=10)
    excerpt: Optional[str] = Field(None, max_length=500)
    category_id: Optional[int] = None
    tags: Optional[List[str]] = None
    status: Optional[PostStatus] = None
    is_featured: Optional[bool] = None
    allow_comments: Optional[bool] = None
    featured_image: Optional[str] = None
    meta_title: Optional[str] = Field(None, max_length=200)
    meta_description: Optional[str] = Field(None, max_length=300)
    meta_keywords: Optional[str] = Field(None, max_length=200)


class AuthorInfo(BaseModel):
    id: int
    username: str
    full_name: Optional[str] = None
    avatar_url: Optional[str] = None
    
    class Config:
        from_attributes = True


class Post(PostBase):
    id: int
    slug: str
    author: AuthorInfo
    category: Optional[Category] = None
    tags: List[Tag] = []
    views_count: int = 0
    likes_count: int = 0
    comments_count: int = 0
    created_at: datetime
    updated_at: Optional[datetime] = None
    published_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True


class PostInDB(Post):
    author_id: int


class PostList(BaseModel):
    id: int
    title: str
    slug: str
    excerpt: Optional[str] = None
    author: AuthorInfo
    category: Optional[Category] = None
    tags: List[Tag] = []
    featured_image: Optional[str] = None
    status: PostStatus
    is_featured: bool
    views_count: int = 0
    likes_count: int = 0
    comments_count: int = 0
    created_at: datetime
    published_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True