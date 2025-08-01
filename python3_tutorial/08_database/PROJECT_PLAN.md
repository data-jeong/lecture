# 08. 데이터베이스 - 학생 성적 관리 시스템

## 프로젝트 개요
SQLite와 SQLAlchemy ORM을 활용하여 학생 성적 관리 시스템을 구축합니다.

## 학습 목표
- 관계형 데이터베이스 개념 이해
- SQL 기본 문법 (CREATE, SELECT, INSERT, UPDATE, DELETE)
- SQLAlchemy ORM 활용
- 데이터베이스 설계와 정규화
- 트랜잭션과 인덱스

## 프로젝트 기능
1. **학생 관리**
   - 학생 등록/수정/삭제
   - 학생 정보 조회
   - 학생 검색 (이름, 학번)
   - 학생 사진 저장

2. **과목 및 성적 관리**
   - 과목 등록/수정/삭제
   - 성적 입력/수정
   - 학점 계산 (GPA)
   - 성적 증명서 발급

3. **통계 및 분석**
   - 과목별 평균 성적
   - 학생별 성적 추이
   - 석차 계산
   - 성적 분포 차트

4. **리포트 생성**
   - PDF 성적표 생성
   - Excel 통계 리포트
   - 학기별 성적 비교
   - 졸업 요건 확인

## 주요 학습 포인트
- SQLite 데이터베이스 연결
- 테이블 관계 설정 (1:N, N:M)
- ORM을 통한 쿼리 작성
- 마이그레이션 관리
- 데이터베이스 백업/복원

## 코드 구조
```
grade_system/
    database/
        __init__.py
        models.py           # SQLAlchemy 모델
        connection.py       # DB 연결 관리
        migrations/         # DB 마이그레이션
    models/
        student.py          # Student 모델
        course.py           # Course 모델
        grade.py            # Grade 모델
        enrollment.py       # Enrollment 모델
    services/
        student_service.py  # 학생 관련 로직
        grade_service.py    # 성적 관련 로직
        report_service.py   # 리포트 생성
    utils/
        validators.py       # 데이터 검증
        calculators.py      # 학점 계산
        exporters.py        # 데이터 내보내기
    templates/
        grade_report.html   # 성적표 템플릿
        transcript.html     # 성적 증명서 템플릿
main.py                    # 메인 프로그램
schema.sql                 # DB 스키마
```

## 데이터베이스 스키마
```sql
-- 학생 테이블
CREATE TABLE students (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    student_id VARCHAR(20) UNIQUE NOT NULL,
    name VARCHAR(100) NOT NULL,
    email VARCHAR(100),
    enrollment_date DATE,
    major VARCHAR(50)
);

-- 과목 테이블
CREATE TABLE courses (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    course_code VARCHAR(20) UNIQUE NOT NULL,
    name VARCHAR(100) NOT NULL,
    credits INTEGER NOT NULL,
    professor VARCHAR(100)
);

-- 수강 테이블
CREATE TABLE enrollments (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    student_id INTEGER,
    course_id INTEGER,
    semester VARCHAR(20),
    year INTEGER,
    FOREIGN KEY (student_id) REFERENCES students(id),
    FOREIGN KEY (course_id) REFERENCES courses(id)
);

-- 성적 테이블
CREATE TABLE grades (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    enrollment_id INTEGER,
    midterm_score FLOAT,
    final_score FLOAT,
    assignment_score FLOAT,
    total_score FLOAT,
    grade VARCHAR(2),
    FOREIGN KEY (enrollment_id) REFERENCES enrollments(id)
);
```

## SQLAlchemy 모델 예제
```python
from sqlalchemy import Column, Integer, String, Float, ForeignKey
from sqlalchemy.orm import relationship

class Student(Base):
    __tablename__ = 'students'
    
    id = Column(Integer, primary_key=True)
    student_id = Column(String(20), unique=True, nullable=False)
    name = Column(String(100), nullable=False)
    email = Column(String(100))
    
    enrollments = relationship("Enrollment", back_populates="student")
```

## 실행 방법
```bash
# 데이터베이스 초기화
python main.py --init-db

# 학생 등록
python main.py --add-student

# 성적 입력
python main.py --add-grade

# 리포트 생성
python main.py --generate-report --semester "2024-1"
```