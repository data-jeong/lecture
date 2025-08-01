# Python 기초 - 계산기 프로젝트

## 프로젝트 소개
Python의 기본 문법을 학습하면서 실용적인 공학용 계산기를 만드는 프로젝트입니다.

## 학습 내용
- 변수와 자료형 (int, float, str, list, dict)
- 조건문 (if-elif-else)
- 반복문 (while, for)
- 함수 정의와 호출
- 모듈 import와 활용
- 에러 처리 (try-except)
- 파일 입출력 (JSON)

## 파일 구조
```
01_python_basics/
├── README.md               # 이 파일
├── PROJECT_PLAN.md        # 프로젝트 계획
├── step_by_step.md        # 단계별 학습 가이드
├── calculator.py          # 기본 계산기
├── advanced_calculator.py # 고급 공학용 계산기
├── operations.py          # 연산 함수 모듈
├── constants.py           # 상수 정의 모듈
└── utils.py              # 유틸리티 함수 모듈
```

## 실행 방법

### 기본 계산기
```bash
python calculator.py
```

### 고급 계산기
```bash
python advanced_calculator.py
```

## 기능 목록

### 기본 계산기 (calculator.py)
- 사칙연산 (+, -, *, /)
- 계산 히스토리
- 에러 처리

### 고급 계산기 (advanced_calculator.py)
1. **기본 연산**: 사칙연산
2. **고급 연산**: 거듭제곱, 제곱근, 팩토리얼, 나머지
3. **삼각함수**: sin, cos, tan
4. **로그함수**: 상용로그, 자연로그, 임의 밑 로그
5. **단위 변환**: 길이, 무게, 온도
6. **메모리 기능**: M+, M-, MR, MC
7. **계산 히스토리**: 저장/불러오기
8. **상수**: π, e, 황금비 등

## 학습 포인트

### 1. 변수와 자료형
```python
# 다양한 자료형 사용
number = 42          # int
pi = 3.14159        # float
name = "계산기"      # str
history = []        # list
menu = {}           # dict
```

### 2. 함수 정의
```python
def add(a, b):
    """두 수를 더합니다"""
    return a + b
```

### 3. 에러 처리
```python
try:
    result = float(input("숫자 입력: "))
except ValueError:
    print("올바른 숫자를 입력하세요")
```

### 4. 모듈 사용
```python
import math
from operations import square_root
from constants import PI
```

### 5. 파일 입출력
```python
import json

# 저장
with open('history.json', 'w') as f:
    json.dump(data, f)

# 불러오기
with open('history.json', 'r') as f:
    data = json.load(f)
```

## 확장 아이디어
1. GUI 버전 만들기 (tkinter)
2. 행렬 계산 기능 추가
3. 그래프 그리기 기능
4. 수식 파싱 기능
5. 웹 버전으로 변환

## 다음 단계
다음 프로젝트에서는 함수와 모듈을 더 깊이 학습하며 텍스트 처리 유틸리티를 만들 예정입니다.