from typing import Optional, List
from sqlalchemy.orm import Session
from datetime import datetime

from ..models.user import User
from ..schemas.user import UserCreate, UserUpdate
from ..core.security import get_password_hash, verify_password


class UserCRUD:
    def create(self, db: Session, user_create: UserCreate) -> User:
        """Create a new user"""
        db_user = User(
            email=user_create.email,
            username=user_create.username,
            full_name=user_create.full_name,
            bio=user_create.bio,
            website=user_create.website,
            location=user_create.location,
            hashed_password=get_password_hash(user_create.password)
        )
        
        db.add(db_user)
        db.commit()
        db.refresh(db_user)
        
        return db_user
        
    def get(self, db: Session, user_id: int) -> Optional[User]:
        """Get user by ID"""
        return db.query(User).filter(User.id == user_id).first()
        
    def get_by_email(self, db: Session, email: str) -> Optional[User]:
        """Get user by email"""
        return db.query(User).filter(User.email == email).first()
        
    def get_by_username(self, db: Session, username: str) -> Optional[User]:
        """Get user by username"""
        return db.query(User).filter(User.username == username).first()
        
    def get_multi(
        self,
        db: Session,
        skip: int = 0,
        limit: int = 100,
        is_active: Optional[bool] = None
    ) -> List[User]:
        """Get multiple users"""
        query = db.query(User)
        
        if is_active is not None:
            query = query.filter(User.is_active == is_active)
            
        return query.offset(skip).limit(limit).all()
        
    def update(
        self,
        db: Session,
        db_user: User,
        user_update: UserUpdate
    ) -> User:
        """Update user"""
        update_data = user_update.dict(exclude_unset=True)
        
        for field, value in update_data.items():
            setattr(db_user, field, value)
            
        db_user.updated_at = datetime.utcnow()
        
        db.add(db_user)
        db.commit()
        db.refresh(db_user)
        
        return db_user
        
    def delete(self, db: Session, db_user: User) -> None:
        """Delete user"""
        db.delete(db_user)
        db.commit()
        
    def authenticate(
        self,
        db: Session,
        username: str,
        password: str
    ) -> Optional[User]:
        """Authenticate user"""
        user = self.get_by_username(db, username=username)
        if not user:
            user = self.get_by_email(db, email=username)
            
        if not user:
            return None
            
        if not verify_password(password, user.hashed_password):
            return None
            
        # Update last login
        user.last_login = datetime.utcnow()
        db.add(user)
        db.commit()
        
        return user
        
    def is_active(self, user: User) -> bool:
        """Check if user is active"""
        return user.is_active
        
    def is_superuser(self, user: User) -> bool:
        """Check if user is superuser"""
        return user.is_superuser
        
    def update_password(
        self,
        db: Session,
        user: User,
        new_password: str
    ) -> None:
        """Update user password"""
        user.hashed_password = get_password_hash(new_password)
        user.updated_at = datetime.utcnow()
        
        db.add(user)
        db.commit()


# Create instance
user_crud = UserCRUD()