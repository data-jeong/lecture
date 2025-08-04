# 🚀 09. FastAPI 백엔드 - 블로그 API 서버

## 🎯 프로젝트 목표
FastAPI를 활용하여 고성능 RESTful 블로그 API 서버를 구축하는 프로젝트입니다. 현대적인 웹 API 개발의 모범 사례를 학습하고, 인증, 데이터베이스 연동, 자동 문서화 등 실무에서 필요한 핵심 기능을 구현합니다.

## 📚 핵심 학습 주제
- 🔥 **FastAPI 프레임워크**: 고성능 비동기 웹 프레임워크
- 🔐 **JWT 인증**: 토큰 기반 보안 시스템
- 🗄️ **SQLAlchemy ORM**: 데이터베이스 모델링과 관계 정의
- 📄 **Pydantic 스키마**: 자동 데이터 검증과 직렬화
- 🔄 **CRUD 패턴**: Create, Read, Update, Delete 작업
- 📚 **자동 API 문서화**: OpenAPI/Swagger 통합
- 🧪 **API 테스팅**: pytest와 테스트 클라이언트
- 🐳 **컨테이너화**: Docker를 활용한 배포

## 📁 프로젝트 구조
```
09_fastapi_backend/
├── 📄 README.md              # 종합 가이드
├── 📋 requirements.txt       # Python 의존성
├── 🐳 Dockerfile            # 컨테이너 설정
├── 📋 Makefile              # 빌드 자동화
├── 🐳 docker-compose.yml    # 서비스 오케스트레이션
└── 🚀 blog_api/             # 메인 애플리케이션
    ├── 🏠 app/              # 애플리케이션 설정
    │   ├── 🔧 __init__.py
    │   ├── ⚙️ config.py     # 환경 설정
    │   └── 🖥️ main.py       # FastAPI 앱 인스턴스
    ├── 🛣️ api/              # API 라우터
    │   ├── 🔧 __init__.py
    │   └── 📁 v1/           # API 버전 1
    │       ├── 🔧 __init__.py
    │       ├── 🔐 auth.py   # 인증 엔드포인트
    │       ├── 👤 users.py  # 사용자 관리
    │       ├── 📝 posts.py  # 블로그 포스트
    │       └── 💬 comments.py # 댓글 시스템
    ├── 🔐 core/             # 핵심 기능
    │   ├── 🔧 __init__.py
    │   ├── 🔐 security.py   # JWT, 패스워드 해싱
    │   └── 🔗 dependencies.py # 의존성 주입
    ├── 📊 crud/             # 데이터베이스 작업
    │   ├── 🔧 __init__.py
    │   ├── 👤 user.py       # 사용자 CRUD
    │   ├── 📝 post.py       # 포스트 CRUD
    │   └── 💬 comment.py    # 댓글 CRUD
    ├── 🗄️ db/               # 데이터베이스 설정
    │   ├── 🔧 __init__.py
    │   ├── 🔗 session.py    # DB 세션 관리
    │   └── 🏗️ base.py       # Base 모델
    ├── 📊 models/           # SQLAlchemy 모델
    │   ├── 🔧 __init__.py
    │   ├── 👤 user.py       # 사용자 모델
    │   ├── 📝 post.py       # 포스트 모델
    │   └── 💬 comment.py    # 댓글 모델
    └── 📋 schemas/          # Pydantic 스키마
        ├── 🔧 __init__.py
        ├── 🔐 auth.py       # 인증 스키마
        ├── 👤 user.py       # 사용자 스키마
        ├── 📝 post.py       # 포스트 스키마
        └── 💬 comment.py    # 댓글 스키마
```

## 🚀 빠른 시작 가이드

### 1️⃣ 환경 설정
```bash
# 프로젝트 디렉토리로 이동
cd 09_fastapi_backend

# 가상환경 생성 및 활성화
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# 의존성 설치
pip install -r requirements.txt

# 환경 변수 설정
cp .env.example .env
# .env 파일을 편집하여 설정 조정
```

### 2️⃣ 데이터베이스 설정
```bash
# PostgreSQL 실행 (Docker 사용)
docker run --name postgres-blog \
  -e POSTGRES_USER=bloguser \
  -e POSTGRES_PASSWORD=blogpass \
  -e POSTGRES_DB=blogdb \
  -p 5432:5432 -d postgres:13

# 또는 docker-compose 사용
docker-compose up -d postgres
```

### 3️⃣ 서버 실행
```bash
# 개발 서버 실행 (자동 리로드)
uvicorn blog_api.app.main:app --reload --port 8000

# 또는 Makefile 사용
make dev

# API 문서 확인
# http://localhost:8000/docs (Swagger UI)
# http://localhost:8000/redoc (ReDoc)
```

## ✨ 주요 기능

### 🔐 1. JWT 인증 시스템
- **사용자 등록**: 이메일/패스워드 기반 회원가입
- **로그인**: JWT 토큰 발급
- **토큰 검증**: Bearer 토큰 인증
- **권한 확인**: 역할 기반 접근 제어

### 👤 2. 사용자 관리
- **프로필 관리**: 사용자 정보 CRUD
- **비밀번호 변경**: 안전한 패스워드 업데이트
- **사용자 목록**: 페이징과 필터링
- **프로필 이미지**: 파일 업로드

### 📝 3. 블로그 포스트
- **포스트 작성**: 마크다운 지원
- **포스트 목록**: 검색, 필터링, 정렬
- **포스트 상세**: 조회수 추적
- **태그 시스템**: 다대다 관계

### 💬 4. 댓글 시스템
- **댓글 작성**: 중첩 댓글 지원
- **댓글 관리**: 수정, 삭제
- **좋아요**: 댓글 평가 시스템
- **관리자**: 댓글 승인/거부

## 💡 핵심 코드 패턴 & 예제

### 🚀 FastAPI 앱 설정
```python
# blog_api/app/main.py
from fastapi import FastAPI, middleware
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware

from blog_api.api.v1 import auth, users, posts, comments
from blog_api.core.config import settings

# FastAPI 앱 인스턴스 생성
app = FastAPI(
    title="Blog API",
    description="고성능 블로그 API 서버",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# CORS 미들웨어 설정
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.ALLOWED_HOSTS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 보안 미들웨어
app.add_middleware(
    TrustedHostMiddleware, 
    allowed_hosts=settings.ALLOWED_HOSTS
)

# API 라우터 등록
app.include_router(auth.router, prefix="/api/v1/auth", tags=["auth"])
app.include_router(users.router, prefix="/api/v1/users", tags=["users"])
app.include_router(posts.router, prefix="/api/v1/posts", tags=["posts"])
app.include_router(comments.router, prefix="/api/v1/comments", tags=["comments"])

@app.get("/")
async def root():
    return {"message": "Blog API Server", "version": "1.0.0"}

@app.get("/health")
async def health_check():
    return {"status": "healthy", "timestamp": datetime.utcnow()}
```

### 🗄️ SQLAlchemy 모델
```python
# blog_api/models/post.py
from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey, Table
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from blog_api.db.base import Base

# 다대다 관계를 위한 연결 테이블
post_tags = Table(
    'post_tags',
    Base.metadata,
    Column('post_id', Integer, ForeignKey('posts.id'), primary_key=True),
    Column('tag_id', Integer, ForeignKey('tags.id'), primary_key=True)
)

class Post(Base):
    __tablename__ = "posts"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(200), nullable=False, index=True)
    content = Column(Text, nullable=False)
    slug = Column(String(200), unique=True, index=True)
    summary = Column(String(500))
    view_count = Column(Integer, default=0)
    
    # 외래키
    author_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    
    # 타임스탬프
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # 관계 정의
    author = relationship("User", back_populates="posts")
    comments = relationship("Comment", back_populates="post", cascade="all, delete-orphan")
    tags = relationship("Tag", secondary=post_tags, back_populates="posts")

class Tag(Base):
    __tablename__ = "tags"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(50), unique=True, nullable=False, index=True)
    color = Column(String(7), default="#6B73FF")  # HEX 색상 코드
    
    # 관계
    posts = relationship("Post", secondary=post_tags, back_populates="tags")
```

### 📋 Pydantic 스키마
```python
# blog_api/schemas/post.py
from datetime import datetime
from typing import List, Optional
from pydantic import BaseModel, validator

from blog_api.schemas.user import UserBase
from blog_api.schemas.tag import TagBase

class PostBase(BaseModel):
    title: str
    content: str
    summary: Optional[str] = None
    tags: Optional[List[str]] = []

class PostCreate(PostBase):
    @validator('title')
    def validate_title(cls, v):
        if len(v.strip()) < 5:
            raise ValueError('제목은 5글자 이상이어야 합니다')
        return v.strip()

class PostUpdate(BaseModel):
    title: Optional[str] = None
    content: Optional[str] = None
    summary: Optional[str] = None
    tags: Optional[List[str]] = None

class PostInDBBase(PostBase):
    id: int
    slug: str
    view_count: int
    author_id: int
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        orm_mode = True

class Post(PostInDBBase):
    author: UserBase
    tags: List[TagBase] = []

class PostList(BaseModel):
    items: List[Post]
    total: int
    page: int
    size: int
    pages: int
```

### 🔐 JWT 인증
```python
# blog_api/core/security.py
from datetime import datetime, timedelta
from typing import Optional
from jose import JWTError, jwt
from passlib.context import CryptContext
from fastapi import HTTPException, status

from blog_api.core.config import settings

# 패스워드 해싱 설정
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    """JWT 액세스 토큰 생성"""
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(
            minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES
        )
    
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(
        to_encode, 
        settings.SECRET_KEY, 
        algorithm=settings.ALGORITHM
    )
    return encoded_jwt

def verify_token(token: str) -> Optional[dict]:
    """JWT 토큰 검증"""
    try:
        payload = jwt.decode(
            token, 
            settings.SECRET_KEY, 
            algorithms=[settings.ALGORITHM]
        )
        return payload
    except JWTError:
        return None

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """패스워드 검증"""
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password: str) -> str:
    """패스워드 해싱"""
    return pwd_context.hash(password)
```

### 🛣️ API 엔드포인트
```python
# blog_api/api/v1/posts.py
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from blog_api import crud, models, schemas
from blog_api.db.session import get_db
from blog_api.core.dependencies import get_current_user

router = APIRouter()

@router.post("/", response_model=schemas.Post, status_code=status.HTTP_201_CREATED)
async def create_post(
    post_in: schemas.PostCreate,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    """새 블로그 포스트 작성"""
    return crud.post.create_with_owner(
        db=db, obj_in=post_in, owner_id=current_user.id
    )

@router.get("/", response_model=schemas.PostList)
async def get_posts(
    skip: int = Query(0, ge=0, description="건너뛸 항목 수"),
    limit: int = Query(20, ge=1, le=100, description="가져올 항목 수"),
    search: Optional[str] = Query(None, description="검색어"),
    tag: Optional[str] = Query(None, description="태그 필터"),
    author: Optional[str] = Query(None, description="작성자 필터"),
    db: Session = Depends(get_db)
):
    """블로그 포스트 목록 조회"""
    posts = crud.post.get_multi_with_filters(
        db=db, skip=skip, limit=limit, 
        search=search, tag=tag, author=author
    )
    total = crud.post.count_with_filters(
        db=db, search=search, tag=tag, author=author
    )
    
    return schemas.PostList(
        items=posts,
        total=total,
        page=skip // limit + 1,
        size=limit,
        pages=(total + limit - 1) // limit
    )

@router.get("/{post_id}", response_model=schemas.Post)
async def get_post(
    post_id: int,
    db: Session = Depends(get_db)
):
    """블로그 포스트 상세 조회"""
    post = crud.post.get(db=db, id=post_id)
    if not post:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="포스트를 찾을 수 없습니다"
        )
    
    # 조회수 증가
    crud.post.increment_view_count(db=db, post_id=post_id)
    
    return post
```

## ✅ 학습 체크리스트

### 🚀 FastAPI 기초
- [ ] FastAPI 앱 생성 및 설정
- [ ] 라우터와 의존성 주입
- [ ] 요청/응답 모델 정의
- [ ] 자동 API 문서화 활용

### 🔐 인증 & 보안
- [ ] JWT 토큰 인증 구현
- [ ] 패스워드 해싱과 검증
- [ ] 권한 기반 접근 제어
- [ ] CORS 및 보안 미들웨어

### 🗄️ 데이터베이스
- [ ] SQLAlchemy 모델 정의
- [ ] 데이터베이스 관계 설정
- [ ] CRUD 패턴 구현
- [ ] 마이그레이션 관리

### 📋 데이터 검증
- [ ] Pydantic 스키마 작성
- [ ] 입력 데이터 검증
- [ ] 커스텀 밸리데이터
- [ ] 에러 처리

## 🔧 문제 해결 가이드

### ❌ 자주 발생하는 오류
```python
# 1. 순환 import 오류
# ImportError: cannot import name 'User' from partially initialized module
# 해결: TYPE_CHECKING을 활용한 지연 import

from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from blog_api.models.user import User

# 2. 데이터베이스 세션 오류
# sqlalchemy.exc.StatementError: Session is closed
# 해결: 의존성 주입을 통한 세션 관리

# 3. JWT 토큰 검증 오류
# HTTPException: Could not validate credentials
# 해결: 토큰 헤더 및 설정 확인
```

### 💡 성능 최적화 팁
- **N+1 쿼리 방지**: `joinedload`, `selectinload` 활용
- **페이지네이션**: 대용량 데이터 처리
- **캐싱**: Redis를 활용한 응답 캐시
- **비동기 처리**: `async/await` 패턴 활용

## 🚀 확장 아이디어

### 🎯 중급 확장
1. **파일 업로드**: S3/MinIO 연동 이미지 업로드
2. **이메일 알림**: 댓글 알림 시스템
3. **검색 엔진**: Elasticsearch 통합
4. **캐싱**: Redis 캐시 레이어

### 🔥 고급 확장
1. **GraphQL API**: Strawberry 통합
2. **웹소켓**: 실시간 댓글 시스템
3. **마이크로서비스**: 서비스 분리
4. **모니터링**: Prometheus/Grafana 통합

## 📚 참고 자료
- [FastAPI 공식 문서](https://fastapi.tiangolo.com/)
- [SQLAlchemy 가이드](https://docs.sqlalchemy.org/)
- [Pydantic 문서](https://pydantic-docs.helpmanual.io/)
- [JWT 토큰 가이드](https://jwt.io/introduction/)

## ➡️ 다음 프로젝트
**[10. Streamlit 대시보드 - 데이터 시각화 프로젝트](../10_streamlit_project/README.md)**  
Streamlit을 활용하여 인터랙티브한 데이터 대시보드를 구축하고 실시간 데이터 시각화를 구현합니다.