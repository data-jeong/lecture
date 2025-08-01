# 함수와 모듈 - 텍스트 처리 유틸리티 단계별 학습

## 목차
1. [함수 심화](#1-함수-심화)
2. [모듈과 패키지](#2-모듈과-패키지)
3. [문자열 처리](#3-문자열-처리)
4. [정규표현식](#4-정규표현식)
5. [파일 처리](#5-파일-처리)
6. [명령줄 인자](#6-명령줄-인자)
7. [텍스트 처리 프로젝트](#7-텍스트-처리-프로젝트)

## 1. 함수 심화

### 함수의 매개변수
```python
# 위치 인자
def greet(name, age):
    return f"{name}님은 {age}살입니다."

# 기본값 매개변수
def greet_with_default(name, age=20):
    return f"{name}님은 {age}살입니다."

# 키워드 인자
print(greet(name="김파이썬", age=25))

# 가변 인자 (*args)
def sum_all(*numbers):
    return sum(numbers)

print(sum_all(1, 2, 3, 4, 5))  # 15

# 키워드 가변 인자 (**kwargs)
def print_info(**info):
    for key, value in info.items():
        print(f"{key}: {value}")

print_info(name="김파이썬", age=25, city="서울")
```

### 함수의 반환값
```python
# 여러 값 반환
def get_min_max(numbers):
    return min(numbers), max(numbers)

minimum, maximum = get_min_max([1, 2, 3, 4, 5])
print(f"최소: {minimum}, 최대: {maximum}")

# None 반환
def print_message(msg):
    print(msg)
    # return None (암시적)
```

### 람다 함수
```python
# 기본 람다
square = lambda x: x ** 2
print(square(5))  # 25

# 정렬에 활용
students = [
    {"name": "김철수", "score": 85},
    {"name": "이영희", "score": 92},
    {"name": "박민수", "score": 78}
]

# 점수 기준 정렬
students.sort(key=lambda x: x["score"], reverse=True)
print(students)

# filter와 함께 사용
numbers = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10]
evens = list(filter(lambda x: x % 2 == 0, numbers))
print(evens)  # [2, 4, 6, 8, 10]

# map과 함께 사용
squared = list(map(lambda x: x ** 2, numbers))
print(squared)  # [1, 4, 9, 16, ...]
```

### 클로저와 데코레이터
```python
# 클로저
def outer_function(x):
    def inner_function(y):
        return x + y
    return inner_function

add_five = outer_function(5)
print(add_five(3))  # 8

# 데코레이터
def timer_decorator(func):
    import time
    def wrapper(*args, **kwargs):
        start = time.time()
        result = func(*args, **kwargs)
        end = time.time()
        print(f"{func.__name__} 실행 시간: {end - start:.4f}초")
        return result
    return wrapper

@timer_decorator
def slow_function():
    import time
    time.sleep(1)
    return "완료"

result = slow_function()
```

## 2. 모듈과 패키지

### 모듈 만들기
```python
# my_module.py
def say_hello(name):
    return f"안녕하세요, {name}님!"

def calculate_age(birth_year):
    from datetime import datetime
    return datetime.now().year - birth_year

PI = 3.14159
```

### 모듈 사용하기
```python
# 전체 모듈 import
import my_module
print(my_module.say_hello("김파이썬"))

# 특정 함수만 import
from my_module import say_hello, PI
print(say_hello("이파이썬"))
print(PI)

# 별칭 사용
import my_module as mm
from my_module import calculate_age as calc_age
```

### 패키지 구조
```
text_utils/
    __init__.py        # 패키지 초기화 파일
    statistics.py      # 통계 모듈
    transformers.py    # 변환 모듈
    searchers.py       # 검색 모듈
```

### __init__.py 파일
```python
# text_utils/__init__.py
from .statistics import word_count, sentence_count
from .transformers import to_uppercase, to_lowercase
from .searchers import find_pattern

__all__ = ['word_count', 'sentence_count', 'to_uppercase', 'to_lowercase', 'find_pattern']
__version__ = '1.0.0'
```

## 3. 문자열 처리

### 문자열 메서드
```python
text = "  Hello, Python World!  "

# 공백 제거
print(text.strip())      # 양쪽 공백 제거
print(text.lstrip())     # 왼쪽 공백 제거
print(text.rstrip())     # 오른쪽 공백 제거

# 대소문자 변환
print(text.upper())      # 모두 대문자
print(text.lower())      # 모두 소문자
print(text.title())      # 단어 첫글자 대문자
print(text.capitalize()) # 문장 첫글자 대문자

# 문자열 분할과 결합
words = text.strip().split()  # 공백 기준 분할
print(words)
print("-".join(words))        # 하이픈으로 결합

# 문자열 치환
new_text = text.replace("Python", "Java")
print(new_text)

# 문자열 검색
print("Python" in text)       # True
print(text.find("Python"))    # 인덱스 반환 (없으면 -1)
print(text.index("Python"))   # 인덱스 반환 (없으면 에러)
print(text.count("o"))        # 특정 문자 개수
```

### 문자열 포맷팅
```python
name = "김파이썬"
age = 25
height = 175.5

# % 포맷팅 (구식)
print("이름: %s, 나이: %d" % (name, age))

# .format() 메서드
print("이름: {}, 나이: {}".format(name, age))
print("이름: {0}, 나이: {1}, 이름: {0}".format(name, age))
print("이름: {n}, 나이: {a}".format(n=name, a=age))

# f-string (권장)
print(f"이름: {name}, 나이: {age}")
print(f"키: {height:.1f}cm")  # 소수점 1자리
print(f"나이: {age:03d}")     # 3자리, 0으로 채움

# 정렬
print(f"{'왼쪽':<10}|")      # 왼쪽 정렬
print(f"{'가운데':^10}|")     # 가운데 정렬
print(f"{'오른쪽':>10}|")     # 오른쪽 정렬
```

## 4. 정규표현식

### 기본 패턴
```python
import re

text = "연락처: 010-1234-5678, 이메일: python@example.com"

# 전화번호 찾기
phone_pattern = r'\d{3}-\d{4}-\d{4}'
phone = re.search(phone_pattern, text)
if phone:
    print(f"전화번호: {phone.group()}")

# 이메일 찾기
email_pattern = r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}'
email = re.search(email_pattern, text)
if email:
    print(f"이메일: {email.group()}")

# 모든 숫자 찾기
numbers = re.findall(r'\d+', text)
print(f"숫자들: {numbers}")

# 문자열 치환
new_text = re.sub(r'\d{3}-\d{4}-\d{4}', '***-****-****', text)
print(new_text)
```

### 정규표현식 패턴
```python
# 주요 패턴
# .     : 임의의 한 문자
# *     : 0개 이상
# +     : 1개 이상
# ?     : 0개 또는 1개
# ^     : 문자열 시작
# $     : 문자열 끝
# []    : 문자 클래스
# |     : OR
# ()    : 그룹
# \d    : 숫자 [0-9]
# \w    : 단어 문자 [a-zA-Z0-9_]
# \s    : 공백 문자

# 예제
patterns = {
    "한글": r'[가-힣]+',
    "영어단어": r'[a-zA-Z]+',
    "우편번호": r'\d{5}',
    "주민번호": r'\d{6}-\d{7}',
    "URL": r'https?://[\w\-.]+\.[a-zA-Z]{2,}'
}
```

## 5. 파일 처리

### 텍스트 파일 읽기/쓰기
```python
# 파일 쓰기
with open('sample.txt', 'w', encoding='utf-8') as f:
    f.write("안녕하세요\n")
    f.write("파이썬 파일 처리입니다.\n")

# 파일 읽기 (전체)
with open('sample.txt', 'r', encoding='utf-8') as f:
    content = f.read()
    print(content)

# 파일 읽기 (줄 단위)
with open('sample.txt', 'r', encoding='utf-8') as f:
    for line in f:
        print(line.strip())

# 파일 읽기 (리스트로)
with open('sample.txt', 'r', encoding='utf-8') as f:
    lines = f.readlines()
    print(lines)

# 파일 추가
with open('sample.txt', 'a', encoding='utf-8') as f:
    f.write("추가된 내용\n")
```

### 경로 처리
```python
import os
from pathlib import Path

# os 모듈
current_dir = os.getcwd()
print(f"현재 디렉토리: {current_dir}")

# 경로 결합
file_path = os.path.join(current_dir, "data", "file.txt")
print(f"파일 경로: {file_path}")

# 파일 존재 확인
if os.path.exists(file_path):
    print("파일이 존재합니다")

# pathlib 사용 (권장)
path = Path("data") / "file.txt"
if path.exists():
    content = path.read_text(encoding='utf-8')
    
# 디렉토리 내 파일 목록
for file in Path(".").glob("*.txt"):
    print(file)
```

## 6. 명령줄 인자

### sys.argv 사용
```python
import sys

# python script.py arg1 arg2
print(f"스크립트 이름: {sys.argv[0]}")
print(f"인자 개수: {len(sys.argv) - 1}")

for i, arg in enumerate(sys.argv[1:], 1):
    print(f"인자 {i}: {arg}")
```

### argparse 사용
```python
import argparse

parser = argparse.ArgumentParser(description='텍스트 처리 유틸리티')
parser.add_argument('filename', help='처리할 파일명')
parser.add_argument('-a', '--action', choices=['stats', 'transform', 'search'],
                    default='stats', help='수행할 작업')
parser.add_argument('-o', '--output', help='출력 파일명')
parser.add_argument('-v', '--verbose', action='store_true', help='자세한 출력')

args = parser.parse_args()

print(f"파일명: {args.filename}")
print(f"작업: {args.action}")
print(f"출력: {args.output}")
print(f"자세히: {args.verbose}")
```

## 7. 텍스트 처리 프로젝트

이제 배운 내용을 종합하여 텍스트 처리 유틸리티를 만들어봅시다!

### 프로젝트 구조
```
text_utils/
    __init__.py
    statistics.py      # 통계 함수
    transformers.py    # 변환 함수
    searchers.py       # 검색 함수
    file_handlers.py   # 파일 처리
main.py               # 메인 프로그램
```

### 주요 기능
1. **텍스트 통계**: 단어 수, 문장 수, 문자 수, 평균 길이
2. **텍스트 변환**: 대소문자, 정렬, 치환
3. **패턴 검색**: 정규표현식 검색, 단어 빈도
4. **파일 처리**: 여러 파일 일괄 처리

### 실습 과제
1. **단어 빈도 분석기**: 가장 많이 사용된 단어 TOP N
2. **텍스트 요약기**: 긴 텍스트를 요약
3. **텍스트 정리기**: 불필요한 공백, 특수문자 제거
4. **번역기 연동**: 구글 번역 API 활용

### 다음 단계
다음 프로젝트에서는 객체지향 프로그래밍을 배우면서 도서관 관리 시스템을 만들 예정입니다!