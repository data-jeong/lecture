from datetime import timedelta
from typing import Any
from fastapi import APIRouter, Body, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session

from ...app.config import settings
from ...core import security
from ...core.dependencies import get_current_user
from ...crud import user_crud
from ...db.session import get_db
from ...models.user import User
from ...schemas.auth import Token, PasswordChange, PasswordReset
from ...schemas.user import UserRegister, User as UserSchema

router = APIRouter()


@router.post("/register", response_model=UserSchema)
def register(
    *,
    db: Session = Depends(get_db),
    user_in: UserRegister
) -> Any:
    """Register new user"""
    # Check if user exists
    user = user_crud.get_by_email(db, email=user_in.email)
    if user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered"
        )
        
    user = user_crud.get_by_username(db, username=user_in.username)
    if user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Username already taken"
        )
        
    # Create user
    from ...schemas.user import UserCreate
    user_create = UserCreate(
        email=user_in.email,
        username=user_in.username,
        password=user_in.password,
        full_name=user_in.full_name
    )
    
    user = user_crud.create(db, user_create=user_create)
    
    return user


@router.post("/login", response_model=Token)
def login(
    db: Session = Depends(get_db),
    form_data: OAuth2PasswordRequestForm = Depends()
) -> Any:
    """Login for access token"""
    user = user_crud.authenticate(
        db, username=form_data.username, password=form_data.password
    )
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
        
    if not user_crud.is_active(user):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Inactive user"
        )
        
    # Create tokens
    access_token = security.create_access_token(subject=user.username)
    refresh_token = security.create_refresh_token(subject=user.username)
    
    return {
        "access_token": access_token,
        "refresh_token": refresh_token,
        "token_type": "bearer"
    }


@router.post("/refresh", response_model=Token)
def refresh_token(
    *,
    db: Session = Depends(get_db),
    refresh_token: str = Body(..., embed=True)
) -> Any:
    """Refresh access token"""
    # Verify refresh token
    username = security.verify_token(refresh_token, token_type="refresh")
    if not username:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid refresh token"
        )
        
    # Get user
    user = user_crud.get_by_username(db, username=username)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
        
    if not user_crud.is_active(user):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Inactive user"
        )
        
    # Create new access token
    access_token = security.create_access_token(subject=user.username)
    
    return {
        "access_token": access_token,
        "token_type": "bearer"
    }


@router.post("/logout")
def logout(
    current_user: User = Depends(get_current_user)
) -> Any:
    """Logout user (client should remove token)"""
    return {"message": "Successfully logged out"}


@router.post("/change-password")
def change_password(
    *,
    db: Session = Depends(get_db),
    password_change: PasswordChange,
    current_user: User = Depends(get_current_user)
) -> Any:
    """Change current user password"""
    # Verify current password
    if not security.verify_password(
        password_change.current_password,
        current_user.hashed_password
    ):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Incorrect password"
        )
        
    # Update password
    user_crud.update_password(
        db,
        user=current_user,
        new_password=password_change.new_password
    )
    
    return {"message": "Password updated successfully"}


@router.post("/reset-password")
def reset_password_request(
    *,
    db: Session = Depends(get_db),
    password_reset: PasswordReset
) -> Any:
    """Request password reset"""
    user = user_crud.get_by_email(db, email=password_reset.email)
    
    if user:
        # Generate reset token
        reset_token = security.generate_password_reset_token(user.email)
        
        # TODO: Send reset email with token
        # For now, just return the token (in production, never do this!)
        if settings.DEBUG:
            return {"message": "Password reset email sent", "token": reset_token}
            
    return {"message": "Password reset email sent"}


@router.post("/reset-password/confirm")
def reset_password_confirm(
    *,
    db: Session = Depends(get_db),
    token: str = Body(...),
    new_password: str = Body(..., min_length=8)
) -> Any:
    """Confirm password reset"""
    # Verify token
    email = security.verify_password_reset_token(token)
    if not email:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid or expired token"
        )
        
    # Get user
    user = user_crud.get_by_email(db, email=email)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
        
    # Update password
    user_crud.update_password(db, user=user, new_password=new_password)
    
    return {"message": "Password reset successfully"}