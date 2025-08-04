from typing import Any, List, Optional
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session

from ...core.dependencies import get_current_user, get_current_active_user
from ...crud import post_crud
from ...db.session import get_db
from ...models.user import User
from ...models.post import PostStatus
from ...schemas.post import (
    Post, PostCreate, PostUpdate, PostList,
    Category, Tag
)

router = APIRouter()


@router.post("/", response_model=Post)
def create_post(
    *,
    db: Session = Depends(get_db),
    post_in: PostCreate,
    current_user: User = Depends(get_current_active_user)
) -> Any:
    """Create new post"""
    post = post_crud.create(db, post_create=post_in, author_id=current_user.id)
    return post


@router.get("/{post_id}", response_model=Post)
def read_post(
    *,
    db: Session = Depends(get_db),
    post_id: int
) -> Any:
    """Get post by ID"""
    post = post_crud.get(db, post_id=post_id)
    if not post:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Post not found"
        )
    
    # Check if post is published or user is the author
    if post.status != PostStatus.PUBLISHED:
        # Need to check if current user is the author
        # This is a simplified version - in production, handle this better
        pass
    
    return post


@router.get("/slug/{slug}", response_model=Post)
def read_post_by_slug(
    *,
    db: Session = Depends(get_db),
    slug: str
) -> Any:
    """Get post by slug"""
    post = post_crud.get_by_slug(db, slug=slug)
    if not post:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Post not found"
        )
    return post


@router.get("/", response_model=List[PostList])
def read_posts(
    db: Session = Depends(get_db),
    skip: int = Query(0, ge=0),
    limit: int = Query(10, ge=1, le=100),
    status: Optional[PostStatus] = Query(PostStatus.PUBLISHED),
    category_id: Optional[int] = None,
    tag: Optional[str] = None,
    author_id: Optional[int] = None,
    is_featured: Optional[bool] = None
) -> Any:
    """Get multiple posts"""
    posts = post_crud.get_multi(
        db,
        skip=skip,
        limit=limit,
        status=status,
        category_id=category_id,
        tag=tag,
        author_id=author_id,
        is_featured=is_featured
    )
    return posts


@router.put("/{post_id}", response_model=Post)
def update_post(
    *,
    db: Session = Depends(get_db),
    post_id: int,
    post_in: PostUpdate,
    current_user: User = Depends(get_current_active_user)
) -> Any:
    """Update post"""
    post = post_crud.get(db, post_id=post_id)
    if not post:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Post not found"
        )
    
    # Check if user is the author or admin
    if post.author_id != current_user.id and not current_user.is_superuser:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions"
        )
    
    post = post_crud.update(db, db_post=post, post_update=post_in)
    return post


@router.delete("/{post_id}")
def delete_post(
    *,
    db: Session = Depends(get_db),
    post_id: int,
    current_user: User = Depends(get_current_active_user)
) -> Any:
    """Delete post"""
    post = post_crud.get(db, post_id=post_id)
    if not post:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Post not found"
        )
    
    # Check if user is the author or admin
    if post.author_id != current_user.id and not current_user.is_superuser:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions"
        )
    
    post_crud.delete(db, db_post=post)
    return {"message": "Post deleted successfully"}


@router.get("/search/", response_model=List[PostList])
def search_posts(
    *,
    db: Session = Depends(get_db),
    q: str = Query(..., min_length=1),
    skip: int = Query(0, ge=0),
    limit: int = Query(10, ge=1, le=100)
) -> Any:
    """Search posts"""
    posts = post_crud.search(db, query=q, skip=skip, limit=limit)
    return posts


@router.get("/popular/", response_model=List[PostList])
def get_popular_posts(
    *,
    db: Session = Depends(get_db),
    limit: int = Query(10, ge=1, le=50)
) -> Any:
    """Get popular posts"""
    posts = post_crud.get_popular(db, limit=limit)
    return posts


@router.get("/my-posts/", response_model=List[PostList])
def get_my_posts(
    db: Session = Depends(get_db),
    skip: int = Query(0, ge=0),
    limit: int = Query(10, ge=1, le=100),
    status: Optional[PostStatus] = None,
    current_user: User = Depends(get_current_active_user)
) -> Any:
    """Get current user's posts"""
    posts = post_crud.get_multi(
        db,
        skip=skip,
        limit=limit,
        status=status,
        author_id=current_user.id
    )
    return posts


@router.get("/categories/", response_model=List[Category])
def get_categories(
    db: Session = Depends(get_db)
) -> Any:
    """Get all categories"""
    categories = post_crud.get_categories(db)
    return categories


@router.get("/tags/", response_model=List[Tag])
def get_tags(
    db: Session = Depends(get_db)
) -> Any:
    """Get all tags"""
    tags = post_crud.get_tags(db)
    return tags