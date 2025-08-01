"""
계산기 사용 예제
초보자를 위한 Python 계산기 사용 예제 모음
"""

from calculator import add, subtract, multiply, divide
from operations import *
from constants import *
from utils import format_number

def example_basic():
    """기본 연산 예제"""
    print("=== 기본 연산 예제 ===")
    
    # 변수에 값 저장
    a = 10
    b = 3
    
    print(f"a = {a}, b = {b}")
    print(f"덧셈: {a} + {b} = {add(a, b)}")
    print(f"뺄셈: {a} - {b} = {subtract(a, b)}")
    print(f"곱셈: {a} × {b} = {multiply(a, b)}")
    print(f"나눗셈: {a} ÷ {b} = {format_number(divide(a, b))}")

def example_variables():
    """변수 활용 예제"""
    print("\n=== 변수 활용 예제 ===")
    
    # 장보기 계산
    apple_price = 1500
    apple_count = 5
    banana_price = 800
    banana_count = 10
    
    apple_total = multiply(apple_price, apple_count)
    banana_total = multiply(banana_price, banana_count)
    total = add(apple_total, banana_total)
    
    print(f"사과 {apple_count}개 × {apple_price}원 = {apple_total}원")
    print(f"바나나 {banana_count}개 × {banana_price}원 = {banana_total}원")
    print(f"총 금액: {total}원")

def example_circle():
    """원의 넓이와 둘레 계산 예제"""
    print("\n=== 원 계산 예제 ===")
    
    radius = 5
    
    # 원의 둘레 = 2πr
    circumference = multiply(multiply(2, PI), radius)
    
    # 원의 넓이 = πr²
    area = multiply(PI, power(radius, 2))
    
    print(f"반지름이 {radius}인 원:")
    print(f"둘레 = 2 × π × {radius} = {format_number(circumference)}")
    print(f"넓이 = π × {radius}² = {format_number(area)}")

def example_temperature():
    """온도 변환 예제"""
    print("\n=== 온도 변환 예제 ===")
    
    celsius_temps = [0, 25, 37, 100]
    
    print("섭씨 → 화씨 변환:")
    for c in celsius_temps:
        f = celsius_to_fahrenheit(c)
        print(f"{c}°C = {f}°F")
    
    print("\n물의 상태 변화:")
    print(f"어는점: 0°C = {celsius_to_fahrenheit(0)}°F = {celsius_to_kelvin(0)}K")
    print(f"끓는점: 100°C = {celsius_to_fahrenheit(100)}°F = {celsius_to_kelvin(100)}K")

def example_loan_interest():
    """대출 이자 계산 예제"""
    print("\n=== 대출 이자 계산 예제 ===")
    
    principal = 10000000  # 원금 1천만원
    annual_rate = 0.035   # 연 이율 3.5%
    years = 3             # 대출 기간 3년
    
    # 단리 계산: 이자 = 원금 × 이율 × 기간
    simple_interest = multiply(multiply(principal, annual_rate), years)
    simple_total = add(principal, simple_interest)
    
    # 복리 계산: 원리금 = 원금 × (1 + 이율)^기간
    compound_total = multiply(principal, power(add(1, annual_rate), years))
    compound_interest = subtract(compound_total, principal)
    
    print(f"원금: {principal:,}원")
    print(f"연이율: {percentage(annual_rate, 1)}%")
    print(f"대출 기간: {years}년")
    print(f"\n단리 이자: {simple_interest:,.0f}원")
    print(f"단리 총 상환액: {simple_total:,.0f}원")
    print(f"\n복리 이자: {compound_interest:,.0f}원")
    print(f"복리 총 상환액: {compound_total:,.0f}원")

def example_trigonometry():
    """삼각함수 활용 예제"""
    print("\n=== 삼각함수 예제 ===")
    
    # 직각삼각형에서 각도로 변의 길이 구하기
    angle = 30  # 30도
    hypotenuse = 10  # 빗변의 길이
    
    # 높이 = 빗변 × sin(각도)
    height = multiply(hypotenuse, sin_degrees(angle))
    
    # 밑변 = 빗변 × cos(각도)
    base = multiply(hypotenuse, cos_degrees(angle))
    
    print(f"직각삼각형 (빗변={hypotenuse}, 각도={angle}°):")
    print(f"높이 = {hypotenuse} × sin({angle}°) = {format_number(height)}")
    print(f"밑변 = {hypotenuse} × cos({angle}°) = {format_number(base)}")

def example_statistics():
    """통계 계산 예제"""
    print("\n=== 통계 계산 예제 ===")
    
    scores = [85, 90, 78, 92, 88, 76, 95, 89]
    
    # 평균 계산
    total = sum(scores)
    count = len(scores)
    average = divide(total, count)
    
    print(f"점수: {scores}")
    print(f"총점: {total}")
    print(f"인원: {count}명")
    print(f"평균: {format_number(average)}점")
    
    # 표준편차는 다음 프로젝트에서 다룹니다

def run_all_examples():
    """모든 예제 실행"""
    print("Python 계산기 사용 예제\n")
    
    example_basic()
    example_variables()
    example_circle()
    example_temperature()
    example_loan_interest()
    example_trigonometry()
    example_statistics()
    
    print("\n" + "="*50)
    print("더 많은 기능을 원하시면 advanced_calculator.py를 실행해보세요!")

if __name__ == "__main__":
    run_all_examples()