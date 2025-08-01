# Python 기초 - 계산기 앱 단계별 학습

## 목차
1. [Python 설치 및 환경 설정](#1-python-설치-및-환경-설정)
2. [변수와 자료형](#2-변수와-자료형)
3. [기본 연산자](#3-기본-연산자)
4. [조건문](#4-조건문)
5. [반복문](#5-반복문)
6. [함수 기초](#6-함수-기초)
7. [에러 처리](#7-에러-처리)
8. [계산기 프로젝트](#8-계산기-프로젝트)

## 1. Python 설치 및 환경 설정

### Python 설치 확인
```bash
python --version
# 또는
python3 --version
```

### 첫 번째 Python 프로그램
```python
print("Hello, Python!")
print("안녕하세요, 파이썬!")
```

## 2. 변수와 자료형

### 변수 선언
```python
# 변수는 값을 저장하는 공간
name = "김파이썬"
age = 25
height = 175.5
is_student = True

print(f"이름: {name}")
print(f"나이: {age}")
print(f"키: {height}")
print(f"학생입니까? {is_student}")
```

### 자료형 확인
```python
# type() 함수로 자료형 확인
print(type(name))      # <class 'str'>
print(type(age))       # <class 'int'>
print(type(height))    # <class 'float'>
print(type(is_student)) # <class 'bool'>
```

### 자료형 변환
```python
# 문자열을 숫자로
user_input = "123"
number = int(user_input)
print(number + 10)  # 133

# 숫자를 문자열로
age = 25
age_str = str(age)
print("나이는 " + age_str + "살입니다")
```

## 3. 기본 연산자

### 산술 연산자
```python
a = 10
b = 3

print(f"{a} + {b} = {a + b}")     # 덧셈: 13
print(f"{a} - {b} = {a - b}")     # 뺄셈: 7
print(f"{a} * {b} = {a * b}")     # 곱셈: 30
print(f"{a} / {b} = {a / b}")     # 나눗셈: 3.333...
print(f"{a} // {b} = {a // b}")   # 몫: 3
print(f"{a} % {b} = {a % b}")     # 나머지: 1
print(f"{a} ** {b} = {a ** b}")   # 거듭제곱: 1000
```

### 비교 연산자
```python
x = 5
y = 10

print(f"{x} > {y} = {x > y}")     # False
print(f"{x} < {y} = {x < y}")     # True
print(f"{x} == {y} = {x == y}")   # False
print(f"{x} != {y} = {x != y}")   # True
print(f"{x} >= {y} = {x >= y}")   # False
print(f"{x} <= {y} = {x <= y}")   # True
```

## 4. 조건문

### if-elif-else 구조
```python
score = 85

if score >= 90:
    grade = "A"
elif score >= 80:
    grade = "B"
elif score >= 70:
    grade = "C"
elif score >= 60:
    grade = "D"
else:
    grade = "F"

print(f"점수: {score}, 학점: {grade}")
```

### 중첩 조건문
```python
age = 20
has_license = True

if age >= 18:
    if has_license:
        print("운전할 수 있습니다.")
    else:
        print("면허를 취득해야 합니다.")
else:
    print("나이가 부족합니다.")
```

## 5. 반복문

### while 반복문
```python
count = 1
while count <= 5:
    print(f"카운트: {count}")
    count += 1

# 무한 루프와 break
while True:
    user_input = input("종료하려면 'q'를 입력하세요: ")
    if user_input == 'q':
        break
    print(f"입력하신 내용: {user_input}")
```

### for 반복문
```python
# 리스트 순회
fruits = ["사과", "바나나", "오렌지"]
for fruit in fruits:
    print(f"과일: {fruit}")

# range 사용
for i in range(1, 6):
    print(f"{i}번째 반복")

# 구구단 출력
for i in range(2, 10):
    print(f"\n[{i}단]")
    for j in range(1, 10):
        print(f"{i} x {j} = {i * j}")
```

## 6. 함수 기초

### 함수 정의와 호출
```python
def greet(name):
    return f"안녕하세요, {name}님!"

message = greet("김파이썬")
print(message)
```

### 여러 개의 매개변수
```python
def add(a, b):
    return a + b

def calculate(a, b, operation="+"):
    if operation == "+":
        return a + b
    elif operation == "-":
        return a - b
    elif operation == "*":
        return a * b
    elif operation == "/":
        return a / b if b != 0 else "0으로 나눌 수 없습니다"

print(calculate(10, 5))        # 15 (기본값 +)
print(calculate(10, 5, "-"))   # 5
print(calculate(10, 5, "*"))   # 50
print(calculate(10, 5, "/"))   # 2.0
```

## 7. 에러 처리

### try-except 구문
```python
def safe_divide(a, b):
    try:
        result = a / b
        return result
    except ZeroDivisionError:
        print("에러: 0으로 나눌 수 없습니다.")
        return None
    except TypeError:
        print("에러: 숫자만 입력해주세요.")
        return None

print(safe_divide(10, 2))    # 5.0
print(safe_divide(10, 0))    # 에러 메시지
print(safe_divide(10, "a"))  # 에러 메시지
```

### 여러 예외 처리
```python
def get_number():
    while True:
        try:
            user_input = input("숫자를 입력하세요: ")
            number = float(user_input)
            return number
        except ValueError:
            print("올바른 숫자를 입력해주세요.")
        except KeyboardInterrupt:
            print("\n프로그램을 종료합니다.")
            exit()
```

## 8. 계산기 프로젝트

이제 배운 내용을 종합하여 계산기를 만들어봅시다!

### 8.1 기본 계산기 구조
```python
def main():
    print("=== 파이썬 계산기 ===")
    
    while True:
        print("\n메뉴:")
        print("1. 더하기")
        print("2. 빼기")
        print("3. 곱하기")
        print("4. 나누기")
        print("0. 종료")
        
        choice = input("\n선택하세요: ")
        
        if choice == "0":
            print("계산기를 종료합니다.")
            break
            
        if choice not in ["1", "2", "3", "4"]:
            print("올바른 메뉴를 선택해주세요.")
            continue
            
        # 숫자 입력 받기
        try:
            num1 = float(input("첫 번째 숫자: "))
            num2 = float(input("두 번째 숫자: "))
        except ValueError:
            print("올바른 숫자를 입력해주세요.")
            continue
            
        # 계산 수행
        if choice == "1":
            result = num1 + num2
            print(f"{num1} + {num2} = {result}")
        elif choice == "2":
            result = num1 - num2
            print(f"{num1} - {num2} = {result}")
        elif choice == "3":
            result = num1 * num2
            print(f"{num1} * {num2} = {result}")
        elif choice == "4":
            if num2 == 0:
                print("0으로 나눌 수 없습니다.")
            else:
                result = num1 / num2
                print(f"{num1} / {num2} = {result}")

if __name__ == "__main__":
    main()
```

### 8.2 리스트와 딕셔너리 활용
```python
# 계산 히스토리를 저장하는 리스트
history = []

# 메뉴를 딕셔너리로 관리
menu = {
    "1": ("더하기", "+"),
    "2": ("빼기", "-"),
    "3": ("곱하기", "*"),
    "4": ("나누기", "/"),
    "5": ("제곱", "**"),
    "6": ("나머지", "%"),
    "7": ("히스토리", None),
    "0": ("종료", None)
}

def show_menu():
    print("\n=== 메뉴 ===")
    for key, (name, _) in menu.items():
        print(f"{key}. {name}")
```

### 8.3 실습 과제

1. **메모리 기능 추가**
   - M+ (메모리에 더하기)
   - M- (메모리에서 빼기)
   - MR (메모리 읽기)
   - MC (메모리 초기화)

2. **공학 계산 기능**
   - 제곱근 (math.sqrt)
   - 삼각함수 (math.sin, math.cos, math.tan)
   - 로그 (math.log)

3. **단위 변환 기능**
   - 길이: m ↔ km, cm ↔ inch
   - 무게: kg ↔ g, kg ↔ pound
   - 온도: °C ↔ °F ↔ K

### 다음 단계
다음 프로젝트에서는 함수와 모듈을 더 깊이 배우면서 텍스트 처리 유틸리티를 만들어볼 예정입니다!