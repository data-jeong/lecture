"""
User Repository 구현
"""

from typing import List, Optional
from datetime import datetime
from ..models.user import User, UserWithPassword
from ..types.base import UserId, Email
from ..types.generics import Result, Option
from .base import InMemoryRepository

class UserRepository(InMemoryRepository[User, UserId]):
    """User 전용 Repository"""
    
    def __init__(self):
        super().__init__(User)
        self._passwords: dict[UserId, str] = {}  # 실제로는 해시된 비밀번호 저장
    
    def add_with_password(self, user: User, password: str) -> Result[UserId, str]:
        """비밀번호와 함께 사용자 추가"""
        # 중복 검사
        if self.find_by_username(user.username).is_some():
            return Result.err(f"Username {user.username} already exists")
        
        if self.find_by_email(user.email).is_some():
            return Result.err(f"Email {user.email} already exists")
        
        # 사용자 추가
        result = self.add(user)
        if result.is_ok():
            user_id = result.unwrap()
            # 실제로는 비밀번호를 해시화해야 함
            self._passwords[user_id] = self._hash_password(password)
        
        return result
    
    def find_by_username(self, username: str) -> Option[User]:
        """사용자명으로 조회"""
        username_lower = username.lower()
        return self.find_one(lambda u: u.username.lower() == username_lower)
    
    def find_by_email(self, email: Email) -> Option[User]:
        """이메일로 조회"""
        email_lower = email.lower()
        return self.find_one(lambda u: u.email.lower() == email_lower)
    
    def authenticate(self, username: str, password: str) -> Option[User]:
        """사용자 인증"""
        user_opt = self.find_by_username(username)
        if user_opt.is_none():
            return Option.none()
        
        user = user_opt.unwrap()
        stored_password = self._passwords.get(user.id)
        
        # 비밀번호 검증 (실제로는 해시 비교)
        if stored_password and self._verify_password(password, stored_password):
            # 마지막 로그인 시간 업데이트
            user.last_login = datetime.now()
            self.update(user.id, user)
            return Option.some(user)
        
        return Option.none()
    
    def get_active_users(self) -> List[User]:
        """활성 사용자 조회"""
        return self.filter(lambda u: u.is_active)
    
    def get_admin_users(self) -> List[User]:
        """관리자 조회"""
        return self.filter(lambda u: u.is_admin)
    
    def search_users(self, query: str) -> List[User]:
        """사용자 검색"""
        query_lower = query.lower()
        return self.filter(
            lambda u: query_lower in u.username.lower()
            or query_lower in u.full_name.lower()
            or query_lower in u.email.lower()
        )
    
    def deactivate_user(self, user_id: UserId) -> Result[bool, str]:
        """사용자 비활성화"""
        user_opt = self.get(user_id)
        if user_opt.is_none():
            return Result.err(f"User {user_id} not found")
        
        user = user_opt.unwrap()
        user.is_active = False
        user.updated_at = datetime.now()
        
        return self.update(user_id, user)
    
    def activate_user(self, user_id: UserId) -> Result[bool, str]:
        """사용자 활성화"""
        user_opt = self.get(user_id)
        if user_opt.is_none():
            return Result.err(f"User {user_id} not found")
        
        user = user_opt.unwrap()
        user.is_active = True
        user.updated_at = datetime.now()
        
        return self.update(user_id, user)
    
    def change_password(self, user_id: UserId, old_password: str, new_password: str) -> Result[bool, str]:
        """비밀번호 변경"""
        user_opt = self.get(user_id)
        if user_opt.is_none():
            return Result.err(f"User {user_id} not found")
        
        # 기존 비밀번호 확인
        stored_password = self._passwords.get(user_id)
        if not stored_password or not self._verify_password(old_password, stored_password):
            return Result.err("Invalid old password")
        
        # 새 비밀번호 저장
        self._passwords[user_id] = self._hash_password(new_password)
        
        # 업데이트 시간 갱신
        user = user_opt.unwrap()
        user.updated_at = datetime.now()
        self.update(user_id, user)
        
        return Result.ok(True)
    
    def reset_password(self, user_id: UserId, new_password: str) -> Result[bool, str]:
        """비밀번호 재설정 (관리자용)"""
        if not self.exists(user_id):
            return Result.err(f"User {user_id} not found")
        
        self._passwords[user_id] = self._hash_password(new_password)
        return Result.ok(True)
    
    def get_with_password(self, user_id: UserId) -> Option[UserWithPassword]:
        """비밀번호 포함 사용자 조회 (내부용)"""
        user_opt = self.get(user_id)
        if user_opt.is_none():
            return Option.none()
        
        user = user_opt.unwrap()
        hashed_password = self._passwords.get(user_id, "")
        
        user_dict = user.dict()
        user_dict['hashed_password'] = hashed_password
        
        return Option.some(UserWithPassword(**user_dict))
    
    def grant_admin(self, user_id: UserId) -> Result[bool, str]:
        """관리자 권한 부여"""
        user_opt = self.get(user_id)
        if user_opt.is_none():
            return Result.err(f"User {user_id} not found")
        
        user = user_opt.unwrap()
        user.is_admin = True
        user.updated_at = datetime.now()
        
        return self.update(user_id, user)
    
    def revoke_admin(self, user_id: UserId) -> Result[bool, str]:
        """관리자 권한 회수"""
        user_opt = self.get(user_id)
        if user_opt.is_none():
            return Result.err(f"User {user_id} not found")
        
        user = user_opt.unwrap()
        user.is_admin = False
        user.updated_at = datetime.now()
        
        return self.update(user_id, user)
    
    def _hash_password(self, password: str) -> str:
        """비밀번호 해시화 (실제로는 bcrypt 등 사용)"""
        # 시뮬레이션을 위한 간단한 해시
        import hashlib
        return hashlib.sha256(password.encode()).hexdigest()
    
    def _verify_password(self, password: str, hashed: str) -> bool:
        """비밀번호 검증"""
        return self._hash_password(password) == hashed
    
    def get_user_statistics(self) -> dict[str, any]:
        """사용자 통계"""
        users = self.get_all()
        active_users = [u for u in users if u.is_active]
        admin_users = [u for u in users if u.is_admin]
        
        # 최근 로그인한 사용자
        logged_in_users = [u for u in users if u.last_login is not None]
        
        return {
            "total_users": len(users),
            "active_users": len(active_users),
            "inactive_users": len(users) - len(active_users),
            "admin_users": len(admin_users),
            "logged_in_users": len(logged_in_users),
            "activation_rate": len(active_users) / len(users) if users else 0.0,
        }