"""
API v1 package
"""

from fastapi import APIRouter

from .auth import router as auth_router
from .users import router as users_router
from .posts import router as posts_router
from .comments import router as comments_router

api_router = APIRouter()

api_router.include_router(auth_router, prefix="/auth", tags=["Authentication"])
api_router.include_router(users_router, prefix="/users", tags=["Users"])
api_router.include_router(posts_router, prefix="/posts", tags=["Posts"])
api_router.include_router(comments_router, prefix="/comments", tags=["Comments"])