# 객체지향 프로그래밍 - 도서관 관리 시스템 단계별 학습

## 목차
1. [클래스와 객체](#1-클래스와-객체)
2. [생성자와 속성](#2-생성자와-속성)
3. [메서드](#3-메서드)
4. [상속](#4-상속)
5. [다형성](#5-다형성)
6. [캡슐화](#6-캡슐화)
7. [추상 클래스](#7-추상-클래스)
8. [도서관 관리 시스템 프로젝트](#8-도서관-관리-시스템-프로젝트)

## 1. 클래스와 객체

### 클래스 정의
```python
# 클래스는 객체를 만들기 위한 템플릿
class Book:
    pass

# 객체(인스턴스) 생성
book1 = Book()
book2 = Book()

print(type(book1))  # <class '__main__.Book'>
print(book1 == book2)  # False (서로 다른 객체)
```

### 속성과 메서드
```python
class Dog:
    # 클래스 변수 (모든 인스턴스가 공유)
    species = "Canis familiaris"
    
    def bark(self):
        return "왈왈!"

# 사용
my_dog = Dog()
print(my_dog.species)  # Canis familiaris
print(my_dog.bark())   # 왈왈!
```

## 2. 생성자와 속성

### __init__ 메서드
```python
class Person:
    def __init__(self, name, age):
        # 인스턴스 변수
        self.name = name
        self.age = age
    
    def introduce(self):
        return f"안녕하세요, 저는 {self.name}이고, {self.age}살입니다."

# 사용
person1 = Person("김철수", 25)
person2 = Person("이영희", 30)

print(person1.introduce())  # 안녕하세요, 저는 김철수이고, 25살입니다.
print(person2.name)         # 이영희
```

### 인스턴스 변수 vs 클래스 변수
```python
class Counter:
    # 클래스 변수
    total_count = 0
    
    def __init__(self):
        # 인스턴스 변수
        self.count = 0
        Counter.total_count += 1
    
    def increment(self):
        self.count += 1

# 사용
c1 = Counter()
c2 = Counter()
c1.increment()
c1.increment()
c2.increment()

print(f"c1의 카운트: {c1.count}")  # 2
print(f"c2의 카운트: {c2.count}")  # 1
print(f"전체 카운터 수: {Counter.total_count}")  # 2
```

## 3. 메서드

### 인스턴스 메서드
```python
class Calculator:
    def __init__(self):
        self.result = 0
    
    def add(self, value):
        self.result += value
        return self.result
    
    def reset(self):
        self.result = 0
```

### 클래스 메서드와 정적 메서드
```python
class MathUtils:
    pi = 3.14159
    
    @classmethod
    def circle_area(cls, radius):
        # 클래스 변수 사용
        return cls.pi * radius ** 2
    
    @staticmethod
    def is_even(number):
        # 클래스와 무관한 유틸리티 함수
        return number % 2 == 0

# 사용
print(MathUtils.circle_area(5))  # 78.53975
print(MathUtils.is_even(4))      # True
```

### 매직 메서드
```python
class Book:
    def __init__(self, title, author, pages):
        self.title = title
        self.author = author
        self.pages = pages
    
    def __str__(self):
        # print()할 때 호출
        return f"{self.title} by {self.author}"
    
    def __repr__(self):
        # 개발자를 위한 문자열 표현
        return f"Book('{self.title}', '{self.author}', {self.pages})"
    
    def __len__(self):
        # len() 함수 사용 가능
        return self.pages
    
    def __eq__(self, other):
        # == 연산자 정의
        if not isinstance(other, Book):
            return False
        return self.title == other.title and self.author == other.author

# 사용
book = Book("Python 입문", "김파이썬", 300)
print(book)           # Python 입문 by 김파이썬
print(repr(book))     # Book('Python 입문', '김파이썬', 300)
print(len(book))      # 300
```

## 4. 상속

### 기본 상속
```python
# 부모 클래스
class Animal:
    def __init__(self, name):
        self.name = name
    
    def speak(self):
        pass
    
    def move(self):
        return f"{self.name}가 움직입니다."

# 자식 클래스
class Dog(Animal):
    def speak(self):
        return f"{self.name}가 왈왈 짖습니다."
    
    def wag_tail(self):
        return f"{self.name}가 꼬리를 흔듭니다."

class Cat(Animal):
    def speak(self):
        return f"{self.name}가 야옹 웁니다."

# 사용
dog = Dog("멍멍이")
cat = Cat("야옹이")

print(dog.speak())      # 멍멍이가 왈왈 짖습니다.
print(dog.move())       # 멍멍이가 움직입니다. (상속받은 메서드)
print(dog.wag_tail())   # 멍멍이가 꼬리를 흔듭니다.
print(cat.speak())      # 야옹이가 야옹 웁니다.
```

### super() 사용
```python
class Vehicle:
    def __init__(self, brand, model):
        self.brand = brand
        self.model = model
        self.is_running = False
    
    def start(self):
        self.is_running = True
        return f"{self.brand} {self.model} 시동을 겁니다."

class Car(Vehicle):
    def __init__(self, brand, model, doors):
        super().__init__(brand, model)  # 부모 생성자 호출
        self.doors = doors
    
    def open_trunk(self):
        return "트렁크를 엽니다."

# 사용
car = Car("현대", "소나타", 4)
print(car.start())      # 현대 소나타 시동을 겁니다.
print(car.doors)        # 4
```

## 5. 다형성

### 메서드 오버라이딩
```python
class Shape:
    def area(self):
        return 0
    
    def perimeter(self):
        return 0

class Rectangle(Shape):
    def __init__(self, width, height):
        self.width = width
        self.height = height
    
    def area(self):
        return self.width * self.height
    
    def perimeter(self):
        return 2 * (self.width + self.height)

class Circle(Shape):
    def __init__(self, radius):
        self.radius = radius
    
    def area(self):
        import math
        return math.pi * self.radius ** 2
    
    def perimeter(self):
        import math
        return 2 * math.pi * self.radius

# 다형성 활용
shapes = [
    Rectangle(5, 3),
    Circle(4),
    Rectangle(10, 2)
]

for shape in shapes:
    print(f"면적: {shape.area():.2f}, 둘레: {shape.perimeter():.2f}")
```

## 6. 캡슐화

### Private 속성과 메서드
```python
class BankAccount:
    def __init__(self, owner, balance=0):
        self.owner = owner
        self.__balance = balance  # Private 속성
        self.__transaction_fee = 0.01  # Private 속성
    
    def deposit(self, amount):
        if amount > 0:
            self.__balance += amount
            return True
        return False
    
    def withdraw(self, amount):
        fee = amount * self.__transaction_fee
        total = amount + fee
        
        if total <= self.__balance:
            self.__balance -= total
            return amount
        return 0
    
    def get_balance(self):
        return self.__balance
    
    def __calculate_interest(self):  # Private 메서드
        return self.__balance * 0.02

# 사용
account = BankAccount("김철수", 10000)
account.deposit(5000)
print(account.get_balance())  # 15000

# print(account.__balance)  # AttributeError (직접 접근 불가)
# 하지만 파이썬에서는 완전한 private은 없음
print(account._BankAccount__balance)  # 15000 (권장하지 않음)
```

### Property 데코레이터
```python
class Temperature:
    def __init__(self, celsius=0):
        self._celsius = celsius
    
    @property
    def celsius(self):
        return self._celsius
    
    @celsius.setter
    def celsius(self, value):
        if value < -273.15:
            raise ValueError("절대영도보다 낮을 수 없습니다.")
        self._celsius = value
    
    @property
    def fahrenheit(self):
        return self._celsius * 9/5 + 32
    
    @fahrenheit.setter
    def fahrenheit(self, value):
        self._celsius = (value - 32) * 5/9

# 사용
temp = Temperature()
temp.celsius = 25
print(temp.fahrenheit)  # 77.0

temp.fahrenheit = 86
print(temp.celsius)     # 30.0
```

## 7. 추상 클래스

### ABC (Abstract Base Class)
```python
from abc import ABC, abstractmethod

class Employee(ABC):
    def __init__(self, name, employee_id):
        self.name = name
        self.employee_id = employee_id
    
    @abstractmethod
    def calculate_salary(self):
        pass
    
    @abstractmethod
    def get_role(self):
        pass

class FullTimeEmployee(Employee):
    def __init__(self, name, employee_id, monthly_salary):
        super().__init__(name, employee_id)
        self.monthly_salary = monthly_salary
    
    def calculate_salary(self):
        return self.monthly_salary
    
    def get_role(self):
        return "정규직"

class PartTimeEmployee(Employee):
    def __init__(self, name, employee_id, hourly_rate, hours_worked):
        super().__init__(name, employee_id)
        self.hourly_rate = hourly_rate
        self.hours_worked = hours_worked
    
    def calculate_salary(self):
        return self.hourly_rate * self.hours_worked
    
    def get_role(self):
        return "시간제"

# employee = Employee("김철수", "E001")  # TypeError: 추상 클래스는 인스턴스화 불가

employees = [
    FullTimeEmployee("김철수", "E001", 3000000),
    PartTimeEmployee("이영희", "E002", 15000, 120)
]

for emp in employees:
    print(f"{emp.name} ({emp.get_role()}): {emp.calculate_salary():,}원")
```

## 8. 도서관 관리 시스템 프로젝트

이제 배운 내용을 종합하여 도서관 관리 시스템을 만들어봅시다!

### 주요 클래스 설계
1. **Book 클래스**: 도서 정보
2. **Member 클래스**: 회원 정보
3. **Transaction 클래스**: 대출/반납 기록
4. **Library 클래스**: 전체 시스템 관리

### 상속 구조
- Book (추상 클래스)
  - PhysicalBook
  - EBook
  - AudioBook
- Member (추상 클래스)
  - RegularMember
  - PremiumMember

### 주요 기능
1. 도서 관리 (추가, 삭제, 검색)
2. 회원 관리 (등록, 탈퇴, 정보 수정)
3. 대출/반납 처리
4. 연체료 계산
5. 도서 예약
6. 통계 및 리포트

### 실습 과제
1. **ISBN 생성기**: 자동으로 고유한 ISBN 생성
2. **검색 기능**: 제목, 저자, 장르별 검색
3. **예약 시스템**: 대출 중인 도서 예약
4. **추천 시스템**: 회원의 대출 기록 기반 추천

### 다음 단계
다음 프로젝트에서는 Type Hints와 현대적인 Python 기능을 활용하여 타입 안전한 ToDo 앱을 만들 예정입니다!