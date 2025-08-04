"""
User 서비스
"""

from typing import List, Optional
from datetime import datetime
from ..models.user import User, UserCreate, UserUpdate, UserProfile, UserSettings
from ..types.base import UserId, Email
from ..types.generics import Result, Option
from ..repositories.user_repository import UserRepository

class UserService:
    """User 비즈니스 로직"""
    
    def __init__(self, user_repo: UserRepository):
        self._user_repo = user_repo
    
    def register_user(self, user_data: UserCreate) -> Result[User, str]:
        """사용자 등록"""
        # 사용자명 중복 확인
        if self._user_repo.find_by_username(user_data.username).is_some():
            return Result.err(f"Username '{user_data.username}' already exists")
        
        # 이메일 중복 확인
        if self._user_repo.find_by_email(user_data.email).is_some():
            return Result.err(f"Email '{user_data.email}' already exists")
        
        # User 객체 생성
        now = datetime.now()
        user = User(
            **user_data.dict(exclude={'password'}),
            id=UserId(0),  # Repository에서 할당
            created_at=now,
            updated_at=now,
        )
        
        # 비밀번호와 함께 저장
        result = self._user_repo.add_with_password(user, user_data.password)
        if result.is_err():
            return Result.err(result.unwrap_err())
        
        user_id = result.unwrap()
        created_user = self._user_repo.get(user_id).unwrap()
        
        return Result.ok(created_user)
    
    def authenticate(self, username: str, password: str) -> Option[User]:
        """사용자 인증"""
        return self._user_repo.authenticate(username, password)
    
    def get_user(self, user_id: UserId) -> Option[User]:
        """사용자 조회"""
        return self._user_repo.get(user_id)
    
    def get_user_by_username(self, username: str) -> Option[User]:
        """사용자명으로 조회"""
        return self._user_repo.find_by_username(username)
    
    def get_user_by_email(self, email: Email) -> Option[User]:
        """이메일로 조회"""
        return self._user_repo.find_by_email(email)
    
    def update_user(self, user_id: UserId, update_data: UserUpdate, updater_id: UserId) -> Result[User, str]:
        """사용자 정보 업데이트"""
        # 권한 확인
        if user_id != updater_id:
            updater_opt = self._user_repo.get(updater_id)
            if updater_opt.is_none() or not updater_opt.unwrap().is_admin:
                return Result.err("Permission denied")
        
        user_opt = self._user_repo.get(user_id)
        if user_opt.is_none():
            return Result.err(f"User {user_id} not found")
        
        user = user_opt.unwrap()
        
        # 업데이트할 필드만 적용
        update_dict = update_data.dict(exclude_unset=True, exclude={'password'})
        
        # 이메일 중복 확인
        if 'email' in update_dict:
            existing_user = self._user_repo.find_by_email(update_dict['email'])
            if existing_user.is_some() and existing_user.unwrap().id != user_id:
                return Result.err(f"Email '{update_dict['email']}' already exists")
        
        # 필드 업데이트
        for field, value in update_dict.items():
            setattr(user, field, value)
        
        user.updated_at = datetime.now()
        
        # 비밀번호 변경 처리
        if update_data.password:
            # 비밀번호는 별도 메서드로 처리하는 것이 좋지만, 여기서는 간단히 처리
            pass
        
        result = self._user_repo.update(user_id, user)
        if result.is_err():
            return Result.err(result.unwrap_err())
        
        return Result.ok(user)
    
    def change_password(self, user_id: UserId, old_password: str, new_password: str) -> Result[bool, str]:
        """비밀번호 변경"""
        return self._user_repo.change_password(user_id, old_password, new_password)
    
    def reset_password(self, user_id: UserId, new_password: str, admin_id: UserId) -> Result[bool, str]:
        """비밀번호 재설정 (관리자용)"""
        # 관리자 권한 확인
        admin_opt = self._user_repo.get(admin_id)
        if admin_opt.is_none() or not admin_opt.unwrap().is_admin:
            return Result.err("Admin permission required")
        
        return self._user_repo.reset_password(user_id, new_password)
    
    def deactivate_user(self, user_id: UserId, admin_id: UserId) -> Result[bool, str]:
        """사용자 비활성화"""
        # 자신은 비활성화 가능, 다른 사용자는 관리자만 가능
        if user_id != admin_id:
            admin_opt = self._user_repo.get(admin_id)
            if admin_opt.is_none() or not admin_opt.unwrap().is_admin:
                return Result.err("Permission denied")
        
        return self._user_repo.deactivate_user(user_id)
    
    def activate_user(self, user_id: UserId, admin_id: UserId) -> Result[bool, str]:
        """사용자 활성화"""
        # 관리자 권한 확인
        admin_opt = self._user_repo.get(admin_id)
        if admin_opt.is_none() or not admin_opt.unwrap().is_admin:
            return Result.err("Admin permission required")
        
        return self._user_repo.activate_user(user_id)
    
    def grant_admin_privileges(self, user_id: UserId, admin_id: UserId) -> Result[bool, str]:
        """관리자 권한 부여"""
        admin_opt = self._user_repo.get(admin_id)
        if admin_opt.is_none() or not admin_opt.unwrap().is_admin:
            return Result.err("Admin permission required")
        
        return self._user_repo.grant_admin(user_id)
    
    def revoke_admin_privileges(self, user_id: UserId, admin_id: UserId) -> Result[bool, str]:
        """관리자 권한 회수"""
        admin_opt = self._user_repo.get(admin_id)
        if admin_opt.is_none() or not admin_opt.unwrap().is_admin:
            return Result.err("Admin permission required")
        
        # 자기 자신의 권한은 회수할 수 없음
        if user_id == admin_id:
            return Result.err("Cannot revoke your own admin privileges")
        
        return self._user_repo.revoke_admin(user_id)
    
    def get_all_users(self, admin_id: UserId) -> Result[List[User], str]:
        """모든 사용자 조회 (관리자용)"""
        admin_opt = self._user_repo.get(admin_id)
        if admin_opt.is_none() or not admin_opt.unwrap().is_admin:
            return Result.err("Admin permission required")
        
        return Result.ok(self._user_repo.get_all())
    
    def get_active_users(self, admin_id: UserId) -> Result[List[User], str]:
        """활성 사용자 조회 (관리자용)"""
        admin_opt = self._user_repo.get(admin_id)
        if admin_opt.is_none() or not admin_opt.unwrap().is_admin:
            return Result.err("Admin permission required")
        
        return Result.ok(self._user_repo.get_active_users())
    
    def search_users(self, query: str, requester_id: UserId) -> Result[List[User], str]:
        """사용자 검색"""
        # 기본적으로 모든 사용자가 검색 가능하지만, 제한을 둘 수 있음
        requester_opt = self._user_repo.get(requester_id)
        if requester_opt.is_none():
            return Result.err("Invalid requester")
        
        users = self._user_repo.search_users(query)
        
        # 비활성 사용자는 관리자만 볼 수 있음
        requester = requester_opt.unwrap()
        if not requester.is_admin:
            users = [u for u in users if u.is_active]
        
        return Result.ok(users)
    
    def get_user_profile(self, user_id: UserId, requester_id: Optional[UserId] = None) -> Option[UserProfile]:
        """사용자 공개 프로필 조회"""
        user_opt = self._user_repo.get(user_id)
        if user_opt.is_none():
            return Option.none()
        
        user = user_opt.unwrap()
        
        # 비활성 사용자는 본인과 관리자만 볼 수 있음
        if not user.is_active and requester_id:
            if requester_id != user_id:
                requester_opt = self._user_repo.get(requester_id)
                if requester_opt.is_none() or not requester_opt.unwrap().is_admin:
                    return Option.none()
        
        # Todo 통계 계산 (실제로는 Todo 서비스에서 가져와야 함)
        todo_count = len(user.created_todos)
        completed_count = 0  # 실제 구현에서는 Todo 서비스를 통해 계산
        
        profile = UserProfile(
            id=user.id,
            username=user.username,
            full_name=user.full_name,
            created_at=user.created_at,
            todo_count=todo_count,
            completed_todo_count=completed_count
        )
        
        return Option.some(profile)
    
    def get_user_statistics(self, admin_id: UserId) -> Result[dict[str, any], str]:
        """사용자 통계 (관리자용)"""
        admin_opt = self._user_repo.get(admin_id)
        if admin_opt.is_none() or not admin_opt.unwrap().is_admin:
            return Result.err("Admin permission required")
        
        stats = self._user_repo.get_user_statistics()
        return Result.ok(stats)
    
    def validate_user_permissions(self, user_id: UserId, action: str) -> Result[bool, str]:
        """사용자 권한 검증"""
        user_opt = self._user_repo.get(user_id)
        if user_opt.is_none():
            return Result.err("User not found")
        
        user = user_opt.unwrap()
        
        if not user.is_active:
            return Result.err("User is inactive")
        
        # 액션별 권한 확인
        if action in ['create_todo', 'update_todo', 'delete_todo']:
            return Result.ok(True)  # 모든 활성 사용자 가능
        
        elif action in ['manage_users', 'view_all_todos']:
            return Result.ok(user.is_admin)
        
        else:
            return Result.err(f"Unknown action: {action}")
    
    def delete_user(self, user_id: UserId, admin_id: UserId) -> Result[bool, str]:
        """사용자 삭제 (관리자용)"""
        admin_opt = self._user_repo.get(admin_id)
        if admin_opt.is_none() or not admin_opt.unwrap().is_admin:
            return Result.err("Admin permission required")
        
        # 자기 자신은 삭제할 수 없음
        if user_id == admin_id:
            return Result.err("Cannot delete yourself")
        
        # 실제로는 soft delete를 권장
        return self._user_repo.delete(user_id)