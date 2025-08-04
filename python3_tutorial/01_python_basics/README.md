# 📐 프로젝트 01: Python 기초 - 공학용 계산기

## 🎯 프로젝트 목표
Python의 기본 문법을 마스터하면서 실제로 사용 가능한 공학용 계산기를 구현합니다.

## 📚 핵심 학습 내용

### 기초 문법
- **변수와 자료형**: int, float, str, list, dict
- **제어문**: if-elif-else, while, for
- **함수**: 정의, 호출, 매개변수, 반환값
- **모듈**: import, from, as

### 고급 기능
- **예외 처리**: try-except-finally
- **파일 I/O**: JSON 형식으로 데이터 저장/불러오기
- **클래스 기초**: 메모리 기능 구현
- **데코레이터**: 함수 실행 시간 측정

## 📁 프로젝트 구조
```
01_python_basics/
├── README.md               # 프로젝트 문서
├── PROJECT_PLAN.md        # 상세 계획서
├── step_by_step.md        # 단계별 학습 가이드
├── requirements.txt       # 필요 패키지
├── demo.html             # 인터랙티브 데모
│
├── __init__.py           # 패키지 초기화 파일
├── calculator.py          # 기본 계산기 (초급)
├── advanced_calculator.py # 공학용 계산기 (중급)
├── operations.py          # 연산 함수 모듈
├── constants.py           # 수학/물리 상수
├── utils.py              # 유틸리티 함수
├── examples.py           # 사용 예제 모음
│
└── tests/
    ├── test_calculator.py     # 기본 계산기 테스트
    └── test_advanced.py       # 고급 연산 모듈 테스트
```

## 🚀 빠른 시작

### 1. 환경 설정
```bash
# 프로젝트 디렉토리로 이동
cd 01_python_basics

# 필요 패키지 설치 (선택사항)
pip install -r requirements.txt
```

### 2. 프로그램 실행
```bash
# 기본 계산기 (초급자용)
python calculator.py

# 공학용 계산기 (전체 기능)
python advanced_calculator.py
```

### 3. 테스트 실행
```bash
# 단위 테스트
python -m pytest tests/

# 커버리지 확인
python -m pytest --cov=. tests/
```

## ⚡ 주요 기능

### 📱 기본 계산기 (calculator.py)
- ✅ 사칙연산 (+, -, *, /)
- ✅ 계산 히스토리 관리
- ✅ 입력 검증 및 에러 처리
- ✅ 결과 포맷팅

### 🔬 공학용 계산기 (advanced_calculator.py)

#### 기본 연산
- 사칙연산, 거듭제곱, 제곱근
- 팩토리얼, 나머지 연산
- 절댓값, 반올림

#### 과학 계산
- **삼각함수**: sin, cos, tan, asin, acos, atan
- **로그함수**: log10, ln, log (임의 밑)
- **지수함수**: exp, sinh, cosh, tanh

#### 단위 변환
- **길이**: m ↔ km, inch, feet, mile
- **무게**: kg ↔ g, lb, oz
- **온도**: °C ↔ °F, K
- **각도**: degree ↔ radian

#### 특수 기능
- **메모리**: M+, M-, MR, MC
- **히스토리**: 계산 기록 저장/불러오기
- **상수**: π, e, 황금비, 빛의 속도 등
- **통계**: 평균, 표준편차

## 💡 핵심 코드 패턴

### 1. 타입 힌트와 문서화
```python
def calculate(a: float, b: float, operation: str) -> float:
    """
    두 수에 대한 연산을 수행합니다.
    
    Args:
        a: 첫 번째 숫자
        b: 두 번째 숫자
        operation: 연산 종류 (+, -, *, /)
    
    Returns:
        연산 결과
    
    Raises:
        ValueError: 잘못된 연산자
        ZeroDivisionError: 0으로 나누기
    """
    if operation == '+':
        return a + b
    elif operation == '-':
        return a - b
    # ...
```

### 2. 예외 처리 패턴
```python
def safe_divide(a: float, b: float) -> float:
    """안전한 나눗셈 처리"""
    try:
        return a / b
    except ZeroDivisionError:
        print("❌ 에러: 0으로 나눌 수 없습니다")
        return float('inf')
    except TypeError:
        print("❌ 에러: 숫자만 입력 가능합니다")
        return 0.0
    finally:
        print(f"계산 시도: {a} / {b}")
```

### 3. 클래스와 메모리 관리
```python
class Calculator:
    def __init__(self):
        self.memory = 0
        self.history = []
    
    def add_to_memory(self, value: float):
        """메모리에 값 추가"""
        self.memory += value
        self.history.append(f"M+ {value}")
    
    def clear_memory(self):
        """메모리 초기화"""
        self.memory = 0
        self.history.clear()
```

### 4. 데코레이터 활용
```python
import time
from functools import wraps

def measure_time(func):
    """함수 실행 시간 측정 데코레이터"""
    @wraps(func)
    def wrapper(*args, **kwargs):
        start = time.time()
        result = func(*args, **kwargs)
        end = time.time()
        print(f"⏱️ {func.__name__} 실행 시간: {end-start:.4f}초")
        return result
    return wrapper

@measure_time
def factorial(n: int) -> int:
    """
    팩토리얼 계산
    
    Note: Python의 기본 재귀 깊이 제한은 1000입니다.
    큰 수의 팩토리얼은 math.factorial() 사용을 권장합니다.
    재귀 깊이를 늘리려면:
    import sys
    sys.setrecursionlimit(10000)
    """
    if n <= 1:
        return 1
    return n * factorial(n - 1)
```

### 5. JSON 데이터 관리
```python
import json
from datetime import datetime

class HistoryManager:
    @staticmethod
    def save_history(history: list, filename: str = 'history.json'):
        """계산 히스토리 저장"""
        data = {
            'timestamp': datetime.now().isoformat(),
            'calculations': history
        }
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
    
    @staticmethod
    def load_history(filename: str = 'history.json') -> list:
        """계산 히스토리 불러오기"""
        try:
            with open(filename, 'r', encoding='utf-8') as f:
                data = json.load(f)
                return data.get('calculations', [])
        except FileNotFoundError:
            return []
```

## 🎓 학습 성과 체크리스트

### 초급 (calculator.py 완성)
- [ ] 변수 선언과 자료형 이해
- [ ] 조건문으로 분기 처리
- [ ] 반복문으로 메뉴 시스템 구현
- [ ] 함수로 코드 모듈화
- [ ] 기본 예외 처리

### 중급 (advanced_calculator.py 완성)
- [ ] 모듈 import와 활용
- [ ] 복잡한 수학 연산 구현
- [ ] 파일 I/O로 데이터 영속성
- [ ] 클래스 기초 이해
- [ ] 리스트/딕셔너리 활용

### 고급 (확장 기능)
- [ ] 데코레이터 작성
- [ ] 제너레이터 활용
- [ ] 컨텍스트 매니저
- [ ] 타입 힌트 적용
- [ ] 단위 테스트 작성

## 🔧 트러블슈팅

### 자주 발생하는 문제

1. **ModuleNotFoundError**
   ```bash
   # 해결: 현재 디렉토리에서 실행
   cd 01_python_basics
   python calculator.py
   ```

2. **JSONDecodeError**
   ```python
   # 해결: 파일이 없거나 손상된 경우
   try:
       data = json.load(f)
   except json.JSONDecodeError:
       data = []  # 기본값 사용
   ```

3. **ZeroDivisionError**
   ```python
   # 해결: 나누기 전 검증
   if b != 0:
       result = a / b
   else:
       print("0으로 나눌 수 없습니다")
   ```

## 🚦 다음 프로젝트
**[02_functions_modules](../02_functions_modules)**: 함수와 모듈을 심화 학습하며 텍스트 처리 유틸리티를 구현합니다.

## 📚 참고 자료
- [Python 공식 문서](https://docs.python.org/3/)
- [Python 수학 모듈](https://docs.python.org/3/library/math.html)
- [JSON 처리 가이드](https://docs.python.org/3/library/json.html)