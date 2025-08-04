# FastAPI Blog API

고성능 RESTful 블로그 API 서버 (FastAPI 기반)

## 프로젝트 구조

```
09_fastapi_backend/
├── blog_api/
│   ├── app/              # 애플리케이션 설정
│   ├── api/              # API 엔드포인트
│   ├── core/             # 핵심 기능 (보안, 의존성)
│   ├── crud/             # CRUD 작업
│   ├── db/               # 데이터베이스
│   ├── models/           # SQLAlchemy 모델
│   └── schemas/          # Pydantic 스키마
├── tests/                # 테스트
├── alembic/              # 데이터베이스 마이그레이션
└── requirements.txt      # 의존성
```

## 설치 방법

```bash
# 가상환경 생성
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# 의존성 설치
pip install -r requirements.txt

# 환경 변수 설정
cp .env.example .env
# .env 파일 수정

# 데이터베이스 마이그레이션
alembic init alembic
alembic revision --autogenerate -m "Initial migration"
alembic upgrade head
```

## 실행 방법

```bash
# 개발 서버 실행
uvicorn blog_api.app.main:app --reload --port 8000

# 프로덕션 서버 실행
uvicorn blog_api.app.main:app --host 0.0.0.0 --port 8000 --workers 4
```

## API 문서

서버 실행 후:
- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

## 주요 기능

### 1. 사용자 관리
- 회원가입/로그인 (JWT 인증)
- 프로필 관리
- 권한 관리 (User/Admin/Moderator)

### 2. 블로그 포스트
- CRUD 작업
- 상태 관리 (Draft/Published/Archived)
- 카테고리 및 태그
- 검색 및 필터링
- 페이지네이션

### 3. 댓글 시스템
- 댓글 및 대댓글
- 수정/삭제 (소프트 삭제)
- 좋아요/싫어요

### 4. 보안
- JWT 토큰 인증
- 비밀번호 해싱 (bcrypt)
- CORS 설정
- Rate Limiting

## API 엔드포인트

### 인증
- `POST /api/v1/auth/register` - 회원가입
- `POST /api/v1/auth/login` - 로그인
- `POST /api/v1/auth/refresh` - 토큰 갱신
- `POST /api/v1/auth/logout` - 로그아웃
- `POST /api/v1/auth/change-password` - 비밀번호 변경
- `POST /api/v1/auth/reset-password` - 비밀번호 재설정

### 사용자
- `GET /api/v1/users/me` - 현재 사용자 정보
- `PUT /api/v1/users/me` - 현재 사용자 정보 수정
- `GET /api/v1/users/{user_id}` - 특정 사용자 조회
- `GET /api/v1/users/username/{username}` - 사용자명으로 조회

### 포스트
- `POST /api/v1/posts/` - 포스트 생성
- `GET /api/v1/posts/` - 포스트 목록
- `GET /api/v1/posts/{post_id}` - 특정 포스트 조회
- `GET /api/v1/posts/slug/{slug}` - 슬러그로 조회
- `PUT /api/v1/posts/{post_id}` - 포스트 수정
- `DELETE /api/v1/posts/{post_id}` - 포스트 삭제
- `GET /api/v1/posts/search/` - 포스트 검색
- `GET /api/v1/posts/popular/` - 인기 포스트

### 댓글
- `POST /api/v1/comments/` - 댓글 작성
- `GET /api/v1/comments/{comment_id}` - 댓글 조회
- `GET /api/v1/comments/post/{post_id}` - 포스트의 댓글 목록
- `PUT /api/v1/comments/{comment_id}` - 댓글 수정
- `DELETE /api/v1/comments/{comment_id}` - 댓글 삭제

## 데이터베이스 스키마

### Users
- id, email, username, hashed_password
- full_name, bio, avatar_url
- role, is_active, email_verified
- created_at, updated_at

### Posts
- id, title, slug, content
- author_id, category_id
- status, is_featured
- views_count, likes_count, comments_count
- created_at, updated_at, published_at

### Comments
- id, content, post_id, author_id
- parent_id (for replies)
- likes_count, dislikes_count
- created_at, updated_at

## 테스트

```bash
# 테스트 실행
pytest

# 커버리지 확인
pytest --cov=blog_api

# 특정 테스트 실행
pytest tests/test_auth.py -v
```

## 환경 변수

```env
# Application
APP_NAME="Blog API"
DEBUG=True

# Database
DATABASE_URL=postgresql://user:password@localhost/blog_db

# Security
SECRET_KEY=your-secret-key
ACCESS_TOKEN_EXPIRE_MINUTES=30

# Redis
REDIS_HOST=localhost
REDIS_PORT=6379

# Email
MAIL_USERNAME=your-email@gmail.com
MAIL_PASSWORD=your-app-password
```

## 학습 포인트

- **FastAPI**: 현대적인 Python 웹 프레임워크
- **Pydantic**: 데이터 검증 및 설정 관리
- **SQLAlchemy**: ORM 및 데이터베이스 관리
- **JWT**: 토큰 기반 인증
- **비동기 프로그래밍**: async/await 패턴
- **API 설계**: RESTful 원칙
- **자동 문서화**: OpenAPI/Swagger