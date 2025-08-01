# 09. FastAPI 백엔드 - RESTful 블로그 API

## 프로젝트 개요
FastAPI를 활용하여 현대적이고 고성능의 RESTful 블로그 API 서버를 구축합니다.

## 학습 목표
- FastAPI 프레임워크 마스터
- RESTful API 설계 원칙
- Pydantic을 통한 데이터 검증
- JWT 인증 구현
- API 문서 자동 생성

## 프로젝트 기능
1. **사용자 관리**
   - 회원가입/로그인/로그아웃
   - JWT 토큰 인증
   - 프로필 관리
   - 권한 관리 (Admin/User)

2. **블로그 포스트**
   - CRUD 작업 (생성/조회/수정/삭제)
   - 페이지네이션
   - 검색 기능
   - 카테고리/태그 관리

3. **댓글 시스템**
   - 댓글 작성/수정/삭제
   - 대댓글 기능
   - 좋아요/싫어요
   - 댓글 알림

4. **고급 기능**
   - 파일 업로드 (이미지)
   - 실시간 알림 (WebSocket)
   - API Rate Limiting
   - 캐싱 (Redis)

5. **관리자 기능**
   - 사용자 관리
   - 포스트 승인/거부
   - 통계 대시보드
   - 백업/복원

## 주요 학습 포인트
```python
from fastapi import FastAPI, Depends, HTTPException, status
from pydantic import BaseModel, Field, validator
from sqlalchemy.orm import Session
from jose import JWTError, jwt
from passlib.context import CryptContext
```

## 코드 구조
```
blog_api/
    app/
        __init__.py
        main.py              # FastAPI 앱
        config.py            # 설정 관리
        
    api/
        __init__.py
        v1/
            __init__.py
            auth.py          # 인증 엔드포인트
            users.py         # 사용자 엔드포인트
            posts.py         # 포스트 엔드포인트
            comments.py      # 댓글 엔드포인트
            admin.py         # 관리자 엔드포인트
            
    core/
        __init__.py
        security.py          # 보안 관련
        dependencies.py      # 의존성 주입
        middleware.py        # 미들웨어
        
    models/
        __init__.py
        user.py              # User 모델
        post.py              # Post 모델
        comment.py           # Comment 모델
        
    schemas/
        __init__.py
        user.py              # User Pydantic 스키마
        post.py              # Post Pydantic 스키마
        comment.py           # Comment Pydantic 스키마
        auth.py              # Auth 스키마
        
    crud/
        __init__.py
        user.py              # User CRUD
        post.py              # Post CRUD
        comment.py           # Comment CRUD
        
    db/
        __init__.py
        base.py              # DB 베이스
        session.py           # DB 세션
        
    utils/
        __init__.py
        pagination.py        # 페이지네이션
        email.py             # 이메일 전송
        cache.py             # Redis 캐싱
        
    tests/
        __init__.py
        test_auth.py         # 인증 테스트
        test_posts.py        # 포스트 테스트
        test_comments.py     # 댓글 테스트
        
alembic/                    # DB 마이그레이션
    alembic.ini
    versions/
    
requirements.txt            # 의존성
.env.example               # 환경 변수 예제
docker-compose.yml         # Docker 설정
```

## API 엔드포인트 예제
```python
@router.post("/posts/", response_model=PostResponse)
async def create_post(
    post: PostCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    새 블로그 포스트를 생성합니다.
    
    - **title**: 포스트 제목
    - **content**: 포스트 내용
    - **category**: 카테고리 ID
    - **tags**: 태그 리스트
    """
    return crud.create_post(db=db, post=post, user_id=current_user.id)
```

## Pydantic 스키마 예제
```python
class PostBase(BaseModel):
    title: str = Field(..., min_length=1, max_length=200)
    content: str = Field(..., min_length=10)
    category_id: Optional[int] = None
    tags: List[str] = []
    
    @validator('title')
    def title_must_not_be_empty(cls, v):
        if not v or v.isspace():
            raise ValueError('Title cannot be empty')
        return v

class PostCreate(PostBase):
    pass

class PostResponse(PostBase):
    id: int
    author: UserBasic
    created_at: datetime
    updated_at: datetime
    likes_count: int = 0
    comments_count: int = 0
    
    class Config:
        from_attributes = True
```

## 보안 설정
```python
# JWT 설정
SECRET_KEY = "your-secret-key"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

# 비밀번호 해싱
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# 인증 의존성
async def get_current_user(token: str = Depends(oauth2_scheme)):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    # ... 토큰 검증 로직
```

## 실행 방법
```bash
# 개발 서버 실행
uvicorn app.main:app --reload --port 8000

# Docker로 실행
docker-compose up -d

# 테스트 실행
pytest

# API 문서 확인
# http://localhost:8000/docs (Swagger UI)
# http://localhost:8000/redoc (ReDoc)
```

## 환경 변수 (.env)
```
DATABASE_URL=postgresql://user:password@localhost/blog_db
SECRET_KEY=your-secret-key-here
REDIS_URL=redis://localhost:6379
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_USERNAME=your-email
EMAIL_PASSWORD=your-password
```