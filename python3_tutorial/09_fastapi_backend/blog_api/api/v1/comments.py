from typing import Any, List
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session

from ...core.dependencies import get_current_user, get_current_active_user
from ...crud import comment_crud
from ...db.session import get_db
from ...models.user import User
from ...schemas.comment import Comment, CommentCreate, CommentUpdate

router = APIRouter()


@router.post("/", response_model=Comment)
def create_comment(
    *,
    db: Session = Depends(get_db),
    comment_in: CommentCreate,
    current_user: User = Depends(get_current_active_user)
) -> Any:
    """Create new comment"""
    comment = comment_crud.create(
        db,
        comment_create=comment_in,
        author_id=current_user.id
    )
    return comment


@router.get("/{comment_id}", response_model=Comment)
def read_comment(
    *,
    db: Session = Depends(get_db),
    comment_id: int
) -> Any:
    """Get comment by ID"""
    comment = comment_crud.get(db, comment_id=comment_id)
    if not comment:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Comment not found"
        )
    return comment


@router.get("/post/{post_id}", response_model=List[Comment])
def read_post_comments(
    *,
    db: Session = Depends(get_db),
    post_id: int,
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=100)
) -> Any:
    """Get comments for a post"""
    comments = comment_crud.get_by_post(
        db,
        post_id=post_id,
        skip=skip,
        limit=limit
    )
    return comments


@router.put("/{comment_id}", response_model=Comment)
def update_comment(
    *,
    db: Session = Depends(get_db),
    comment_id: int,
    comment_in: CommentUpdate,
    current_user: User = Depends(get_current_active_user)
) -> Any:
    """Update comment"""
    comment = comment_crud.get(db, comment_id=comment_id)
    if not comment:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Comment not found"
        )
    
    # Check if user is the author
    if comment.author_id != current_user.id and not current_user.is_superuser:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions"
        )
    
    comment = comment_crud.update(
        db,
        db_comment=comment,
        comment_update=comment_in
    )
    return comment


@router.delete("/{comment_id}")
def delete_comment(
    *,
    db: Session = Depends(get_db),
    comment_id: int,
    current_user: User = Depends(get_current_active_user)
) -> Any:
    """Delete comment"""
    comment = comment_crud.get(db, comment_id=comment_id)
    if not comment:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Comment not found"
        )
    
    # Check if user is the author or admin
    if comment.author_id != current_user.id and not current_user.is_superuser:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions"
        )
    
    comment_crud.delete(db, db_comment=comment)
    return {"message": "Comment deleted successfully"}