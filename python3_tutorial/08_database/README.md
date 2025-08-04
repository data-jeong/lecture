# Grade Management System

SQLAlchemy ORM을 활용한 학생 성적 관리 시스템

## 프로젝트 구조

```
08_database/
├── grade_system/
│   ├── database/         # 데이터베이스 연결 및 모델
│   ├── models/           # ORM 모델 래퍼
│   ├── services/         # 비즈니스 로직
│   └── utils/            # 유틸리티 함수
├── tests/                # 테스트 코드
├── main.py              # CLI 메인 프로그램
├── schema.sql           # 데이터베이스 스키마
└── requirements.txt     # 의존성 패키지
```

## 설치 방법

```bash
# 가상환경 생성
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# 의존성 설치
pip install -r requirements.txt

# 데이터베이스 초기화
python main.py init-db
```

## 사용 방법

### 학생 관리

```bash
# 학생 추가
python main.py add-student

# 학생 정보 조회
python main.py show-student --student-id 2024000001

# 학생 목록
python main.py list-students
```

### 과목 관리

```bash
# 과목 추가
python main.py add-course

# 과목 목록
python main.py list-courses
```

### 수강 신청

```bash
# 수강 신청
python main.py enroll --student-id 2024000001 --course-code CS101 --semester 2024-1 --year 2024
```

### 성적 관리

```bash
# 성적 입력
python main.py add-grade

# 성적표 생성
python main.py transcript --student-id 2024000001 --format excel --output transcript.xlsx
```

### 리포트 생성

```bash
# 학기별 통계 리포트
python main.py report --semester 2024-1 --year 2024 --output report.xlsx
```

## 주요 기능

### 1. 학생 관리
- 학생 등록/수정/삭제
- 학생 정보 조회 및 검색
- GPA 자동 계산
- 졸업 요건 확인

### 2. 과목 및 성적 관리
- 과목 등록/수정/삭제
- 성적 입력 및 수정
- 학점 자동 계산
- 성적 분포 분석

### 3. 통계 및 분석
- 과목별 평균 성적
- 학생별 성적 추이
- 석차 계산
- 성적 분포 차트

### 4. 리포트 생성
- Excel 성적표
- PDF 성적 증명서
- 학기별 통계 리포트
- 졸업 요건 체크리스트

## 데이터베이스 스키마

### 주요 테이블
- **students**: 학생 정보
- **courses**: 과목 정보
- **enrollments**: 수강 신청
- **grades**: 성적 정보
- **departments**: 학과 정보
- **professors**: 교수 정보

### 관계
- Student ↔ Enrollment ↔ Course (N:M)
- Enrollment → Grade (1:1)
- Student → Department (N:1)
- Course → Professor (N:1)

## 성적 계산 방식

```python
# 기본 가중치
midterm: 30%
final: 40%
assignment: 20%
attendance: 10%

# 학점 변환
95-100: A+ (4.5)
90-94:  A0 (4.0)
85-89:  A- (3.5)
80-84:  B+ (3.0)
75-79:  B0 (2.5)
70-74:  B- (2.0)
65-69:  C+ (1.5)
60-64:  C0 (1.0)
55-59:  C- (0.5)
0-54:   F  (0.0)
```

## 테스트

```bash
# 테스트 실행
pytest tests/ -v

# 커버리지 확인
pytest tests/ --cov=grade_system
```

## 학습 포인트

- **SQLAlchemy ORM**: 객체 관계 매핑
- **데이터베이스 설계**: 정규화, 관계 설정
- **트랜잭션 관리**: ACID 원칙
- **쿼리 최적화**: 인덱스, 조인
- **마이그레이션**: Alembic 활용
- **서비스 레이어**: 비즈니스 로직 분리