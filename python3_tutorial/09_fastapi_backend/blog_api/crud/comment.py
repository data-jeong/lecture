from typing import Optional, List
from sqlalchemy.orm import Session, joinedload
from datetime import datetime

from ..models.comment import Comment
from ..schemas.comment import CommentCreate, CommentUpdate


class CommentCRUD:
    def create(
        self,
        db: Session,
        comment_create: CommentCreate,
        author_id: int
    ) -> Comment:
        """Create a new comment"""
        db_comment = Comment(
            content=comment_create.content,
            post_id=comment_create.post_id,
            author_id=author_id,
            parent_id=comment_create.parent_id
        )
        
        # Update post comment count
        from ..models.post import Post
        post = db.query(Post).filter(Post.id == comment_create.post_id).first()
        if post:
            post.comments_count += 1
        
        db.add(db_comment)
        db.commit()
        db.refresh(db_comment)
        
        return db_comment
    
    def get(self, db: Session, comment_id: int) -> Optional[Comment]:
        """Get comment by ID"""
        return db.query(Comment).options(
            joinedload(Comment.author),
            joinedload(Comment.replies)
        ).filter(Comment.id == comment_id).first()
    
    def get_by_post(
        self,
        db: Session,
        post_id: int,
        skip: int = 0,
        limit: int = 100,
        parent_id: Optional[int] = None
    ) -> List[Comment]:
        """Get comments for a post"""
        query = db.query(Comment).options(
            joinedload(Comment.author),
            joinedload(Comment.replies)
        ).filter(
            Comment.post_id == post_id,
            Comment.is_deleted == False
        )
        
        # Filter top-level comments only if parent_id not specified
        if parent_id is None:
            query = query.filter(Comment.parent_id == None)
        else:
            query = query.filter(Comment.parent_id == parent_id)
        
        return query.order_by(Comment.created_at.desc()).offset(skip).limit(limit).all()
    
    def update(
        self,
        db: Session,
        db_comment: Comment,
        comment_update: CommentUpdate
    ) -> Comment:
        """Update comment"""
        db_comment.content = comment_update.content
        db_comment.updated_at = datetime.utcnow()
        
        db.add(db_comment)
        db.commit()
        db.refresh(db_comment)
        
        return db_comment
    
    def delete(self, db: Session, db_comment: Comment) -> None:
        """Delete comment (soft delete)"""
        # Soft delete to preserve thread structure
        db_comment.is_deleted = True
        db_comment.content = "[deleted]"
        
        # Update post comment count
        from ..models.post import Post
        post = db.query(Post).filter(Post.id == db_comment.post_id).first()
        if post and post.comments_count > 0:
            post.comments_count -= 1
        
        db.add(db_comment)
        db.commit()
    
    def get_user_comments(
        self,
        db: Session,
        user_id: int,
        skip: int = 0,
        limit: int = 100
    ) -> List[Comment]:
        """Get comments by user"""
        return db.query(Comment).options(
            joinedload(Comment.post)
        ).filter(
            Comment.author_id == user_id,
            Comment.is_deleted == False
        ).order_by(Comment.created_at.desc()).offset(skip).limit(limit).all()


# Create instance
comment_crud = CommentCRUD()