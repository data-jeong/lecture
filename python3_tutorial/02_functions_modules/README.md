# 함수와 모듈 - 텍스트 처리 유틸리티

## 프로젝트 소개
Python의 함수와 모듈 개념을 학습하면서 실용적인 텍스트 처리 유틸리티를 만드는 프로젝트입니다.

## 학습 내용
- 함수 정의와 매개변수 (*args, **kwargs)
- 람다 함수와 고차 함수
- 모듈과 패키지 구조
- 정규표현식 (regex)
- 파일 입출력
- 명령줄 인자 처리 (argparse)
- 데코레이터

## 파일 구조
```
02_functions_modules/
├── README.md              # 이 파일
├── PROJECT_PLAN.md       # 프로젝트 계획
├── step_by_step.md       # 단계별 학습 가이드
├── main.py               # 메인 프로그램
├── examples.py           # 사용 예제
├── tests.py              # 테스트 코드
└── text_utils/           # 패키지 디렉토리
    ├── __init__.py       # 패키지 초기화
    ├── statistics.py     # 통계 함수
    ├── transformers.py   # 변환 함수
    ├── searchers.py      # 검색 함수
    └── file_handlers.py  # 파일 처리 함수
```

## 설치 및 실행

### 기본 실행
```bash
# 대화형 모드
python main.py -i

# 파일 통계
python main.py -f sample.txt -a stats

# 텍스트 변환
python main.py -f input.txt -a transform -t upper -o output.txt

# 패턴 검색
python main.py -f document.txt -a search
```

### 예제 실행
```bash
python examples.py
```

## 주요 기능

### 1. 텍스트 통계
- 단어 수, 문장 수, 문자 수 계산
- 평균 단어/문장 길이
- 단어 빈도 분석
- 가독성 점수
- 예상 읽기 시간

### 2. 텍스트 변환
- 대소문자 변환
- 공백 정리
- 구두점 제거
- 텍스트 정렬
- 민감정보 마스킹
- 단어 일괄 치환

### 3. 패턴 검색
- 이메일 주소 찾기
- 전화번호 찾기
- URL 찾기
- 날짜/시간 찾기
- 정규표현식 검색
- 해시태그/멘션 찾기

### 4. 파일 처리
- 텍스트 파일 읽기/쓰기
- 여러 파일 일괄 처리
- 파일 합치기/분할
- 파일 백업
- 파일 비교

## 사용 예제

### 통계 분석
```python
from text_utils import get_statistics, word_frequency

text = "Python은 배우기 쉽고 강력한 프로그래밍 언어입니다."
stats = get_statistics(text)
print(f"단어 수: {stats['단어 수']}")

# 가장 많이 사용된 단어
top_words = word_frequency(text, top_n=5)
```

### 텍스트 변환
```python
from text_utils import to_uppercase, remove_extra_spaces, mask_sensitive_data

# 대문자 변환
upper_text = to_uppercase("hello python")

# 공백 정리
clean_text = remove_extra_spaces("  too    many   spaces  ")

# 민감정보 마스킹
masked = mask_sensitive_data("이메일: user@example.com")
```

### 패턴 검색
```python
from text_utils import find_emails, find_phone_numbers, find_urls

text = "연락처: python@example.com, 010-1234-5678"

emails = find_emails(text)
phones = find_phone_numbers(text)
```

## 학습 포인트

### 1. 함수의 다양한 형태
```python
# 기본 함수
def greet(name):
    return f"Hello, {name}!"

# 기본값 매개변수
def greet_with_default(name="World"):
    return f"Hello, {name}!"

# 가변 인자
def sum_all(*args):
    return sum(args)

# 키워드 인자
def create_profile(**kwargs):
    return kwargs
```

### 2. 모듈과 패키지
```python
# 모듈 import
import text_utils
from text_utils import count_words
from text_utils.statistics import word_frequency

# __init__.py를 통한 패키지 구성
# __all__ 변수로 공개 API 정의
```

### 3. 정규표현식
```python
import re

# 이메일 패턴
email_pattern = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'

# 전화번호 패턴
phone_pattern = r'\d{3}-\d{4}-\d{4}'
```

### 4. 파일 처리
```python
# 컨텍스트 매니저 사용
with open('file.txt', 'r', encoding='utf-8') as f:
    content = f.read()

# pathlib 사용
from pathlib import Path
path = Path('data') / 'file.txt'
content = path.read_text()
```

## 확장 아이디어
1. GUI 버전 만들기 (tkinter)
2. 웹 인터페이스 추가 (Flask)
3. 다국어 지원
4. PDF 파일 처리
5. 자연어 처리 기능 추가 (NLTK)

## 다음 단계
다음 프로젝트에서는 객체지향 프로그래밍을 배우면서 도서관 관리 시스템을 만들 예정입니다.