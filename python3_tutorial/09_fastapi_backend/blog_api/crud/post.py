from typing import Optional, List
from sqlalchemy.orm import Session, joinedload
from datetime import datetime
import re

from ..models.post import Post, Category, Tag, PostStatus
from ..models.user import User
from ..schemas.post import PostCreate, PostUpdate


class PostCRUD:
    def create(
        self,
        db: Session,
        post_create: PostCreate,
        author_id: int
    ) -> Post:
        """Create a new post"""
        # Generate slug from title
        slug = self._generate_slug(post_create.title)
        
        # Ensure slug is unique
        slug = self._ensure_unique_slug(db, slug)
        
        # Create post
        db_post = Post(
            title=post_create.title,
            slug=slug,
            content=post_create.content,
            excerpt=post_create.excerpt,
            category_id=post_create.category_id,
            author_id=author_id,
            status=post_create.status,
            is_featured=post_create.is_featured,
            allow_comments=post_create.allow_comments,
            featured_image=post_create.featured_image,
            meta_title=post_create.meta_title,
            meta_description=post_create.meta_description,
            meta_keywords=post_create.meta_keywords
        )
        
        # Handle tags
        if post_create.tags:
            tags = self._get_or_create_tags(db, post_create.tags)
            db_post.tags = tags
            
        # Set published_at if publishing
        if post_create.status == PostStatus.PUBLISHED:
            db_post.published_at = datetime.utcnow()
            
        db.add(db_post)
        db.commit()
        db.refresh(db_post)
        
        return db_post
        
    def get(self, db: Session, post_id: int) -> Optional[Post]:
        """Get post by ID"""
        return db.query(Post).options(
            joinedload(Post.author),
            joinedload(Post.category),
            joinedload(Post.tags)
        ).filter(Post.id == post_id).first()
        
    def get_by_slug(self, db: Session, slug: str) -> Optional[Post]:
        """Get post by slug"""
        post = db.query(Post).options(
            joinedload(Post.author),
            joinedload(Post.category),
            joinedload(Post.tags)
        ).filter(Post.slug == slug).first()
        
        # Increment view count
        if post:
            post.views_count += 1
            db.commit()
            
        return post
        
    def get_multi(
        self,
        db: Session,
        skip: int = 0,
        limit: int = 100,
        status: Optional[PostStatus] = None,
        author_id: Optional[int] = None,
        category_id: Optional[int] = None,
        tag: Optional[str] = None,
        is_featured: Optional[bool] = None
    ) -> List[Post]:
        """Get multiple posts"""
        query = db.query(Post).options(
            joinedload(Post.author),
            joinedload(Post.category),
            joinedload(Post.tags)
        )
        
        if status:
            query = query.filter(Post.status == status)
        if author_id:
            query = query.filter(Post.author_id == author_id)
        if category_id:
            query = query.filter(Post.category_id == category_id)
        if is_featured is not None:
            query = query.filter(Post.is_featured == is_featured)
        if tag:
            query = query.join(Post.tags).filter(Tag.name == tag)
            
        return query.order_by(Post.created_at.desc()).offset(skip).limit(limit).all()
        
    def update(
        self,
        db: Session,
        db_post: Post,
        post_update: PostUpdate
    ) -> Post:
        """Update post"""
        update_data = post_update.dict(exclude_unset=True)
        
        # Handle slug update if title changed
        if "title" in update_data:
            new_slug = self._generate_slug(update_data["title"])
            if new_slug != db_post.slug:
                update_data["slug"] = self._ensure_unique_slug(db, new_slug, db_post.id)
                
        # Handle tags
        if "tags" in update_data:
            tags = update_data.pop("tags")
            db_post.tags = self._get_or_create_tags(db, tags)
            
        # Handle status change
        if "status" in update_data:
            if update_data["status"] == PostStatus.PUBLISHED and not db_post.published_at:
                db_post.published_at = datetime.utcnow()
                
        # Update fields
        for field, value in update_data.items():
            setattr(db_post, field, value)
            
        db_post.updated_at = datetime.utcnow()
        
        db.add(db_post)
        db.commit()
        db.refresh(db_post)
        
        return db_post
        
    def delete(self, db: Session, db_post: Post) -> None:
        """Delete post"""
        db.delete(db_post)
        db.commit()
        
    def search(
        self,
        db: Session,
        query: str,
        skip: int = 0,
        limit: int = 100
    ) -> List[Post]:
        """Search posts"""
        search_filter = Post.title.ilike(f"%{query}%") | Post.content.ilike(f"%{query}%")
        
        return db.query(Post).options(
            joinedload(Post.author),
            joinedload(Post.category),
            joinedload(Post.tags)
        ).filter(
            search_filter,
            Post.status == PostStatus.PUBLISHED
        ).order_by(Post.created_at.desc()).offset(skip).limit(limit).all()
        
    def get_popular(
        self,
        db: Session,
        limit: int = 10
    ) -> List[Post]:
        """Get popular posts"""
        return db.query(Post).options(
            joinedload(Post.author),
            joinedload(Post.category),
            joinedload(Post.tags)
        ).filter(
            Post.status == PostStatus.PUBLISHED
        ).order_by(Post.views_count.desc()).limit(limit).all()
        
    def _generate_slug(self, title: str) -> str:
        """Generate slug from title"""
        # Convert to lowercase and replace spaces with hyphens
        slug = title.lower().strip()
        slug = re.sub(r'[^\w\s-]', '', slug)
        slug = re.sub(r'[-\s]+', '-', slug)
        return slug
        
    def _ensure_unique_slug(
        self,
        db: Session,
        slug: str,
        exclude_id: Optional[int] = None
    ) -> str:
        """Ensure slug is unique"""
        original_slug = slug
        counter = 1
        
        while True:
            query = db.query(Post).filter(Post.slug == slug)
            if exclude_id:
                query = query.filter(Post.id != exclude_id)
                
            if not query.first():
                break
                
            slug = f"{original_slug}-{counter}"
            counter += 1
            
        return slug
        
    def _get_or_create_tags(self, db: Session, tag_names: List[str]) -> List[Tag]:
        """Get or create tags"""
        tags = []
        
        for name in tag_names:
            name = name.strip().lower()
            slug = re.sub(r'[^\w-]', '', name)
            
            tag = db.query(Tag).filter(Tag.name == name).first()
            if not tag:
                tag = Tag(name=name, slug=slug)
                db.add(tag)
                
            tags.append(tag)
            
        return tags
        
    def get_categories(self, db: Session) -> List[Category]:
        """Get all categories"""
        return db.query(Category).all()
        
    def get_tags(self, db: Session) -> List[Tag]:
        """Get all tags"""
        return db.query(Tag).all()


# Create instance
post_crud = PostCRUD()