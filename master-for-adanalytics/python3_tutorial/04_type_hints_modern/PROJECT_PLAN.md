# 04. Type Hints와 모던 Python - 타입 안전 ToDo 앱

## 프로젝트 개요
Python의 타입 힌트와 최신 기능을 활용하여 타입 안전성이 보장된 할 일 관리 앱을 만듭니다.

## 학습 목표
- Type Hints 완벽 이해
- Generic과 TypeVar 활용
- Protocol과 구조적 타이핑
- Union, Optional, Literal 타입
- mypy를 통한 타입 체크

## 프로젝트 기능
1. **할 일 관리**
   - 타입 안전 CRUD 작업
   - 우선순위 시스템 (High/Medium/Low)
   - 카테고리 분류
   - 태그 시스템

2. **고급 타입 기능**
   - Generic Repository 패턴
   - Protocol 기반 인터페이스
   - TypedDict로 설정 관리
   - Callable 타입 활용

3. **데이터 검증**
   - Pydantic 모델 활용
   - 런타임 타입 검증
   - 커스텀 validator
   - 에러 타입 정의

4. **현대적 Python 기능**
   - Pattern Matching (3.10+)
   - Walrus Operator
   - f-strings 고급 기능
   - dataclasses 활용

## 주요 학습 포인트
```python
from typing import TypeVar, Generic, Protocol, Union, Optional
from typing import List, Dict, Tuple, Set, Callable
from typing import Literal, Final, TypedDict, NewType
from dataclasses import dataclass
from abc import ABC, abstractmethod
import pydantic
```

## 코드 구조
```
todo_app/
    types/
        __init__.py
        base.py          # 기본 타입 정의
        protocols.py     # Protocol 정의
        generics.py      # Generic 클래스
    models/
        todo.py          # Pydantic 모델
        user.py          # User 모델
        category.py      # Category 모델
    repositories/
        base.py          # Generic Repository
        todo_repo.py     # Todo Repository
    services/
        todo_service.py  # 비즈니스 로직
        validator.py     # 검증 로직
    utils/
        type_guards.py   # 타입 가드 함수
main.py                 # 메인 프로그램
mypy.ini               # mypy 설정
```

## 타입 예제
```python
TodoId = NewType('TodoId', int)
Priority = Literal['high', 'medium', 'low']
Status = Literal['pending', 'in_progress', 'completed']

T = TypeVar('T')
class Repository(Generic[T], Protocol):
    def add(self, item: T) -> TodoId: ...
    def get(self, id: TodoId) -> Optional[T]: ...
    def update(self, id: TodoId, item: T) -> bool: ...
    def delete(self, id: TodoId) -> bool: ...
```

## 실행 방법
```bash
# 타입 체크
mypy todo_app/

# 앱 실행
python main.py
```