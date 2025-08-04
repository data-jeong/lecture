"""
고급 연산 모듈
공학용 계산기를 위한 추가 연산 함수들
"""

import math

def power(base, exponent):
    """거듭제곱을 계산합니다"""
    return base ** exponent

def square_root(number):
    """제곱근을 계산합니다"""
    if number < 0:
        return "에러: 음수의 제곱근은 계산할 수 없습니다"
    return math.sqrt(number)

def factorial(n):
    """팩토리얼을 계산합니다"""
    if n < 0:
        return "에러: 음수의 팩토리얼은 정의되지 않습니다"
    if n == 0 or n == 1:
        return 1
    return math.factorial(int(n))

def sin_degrees(degrees):
    """각도(도)로 사인값을 계산합니다"""
    radians = math.radians(degrees)
    return math.sin(radians)

def cos_degrees(degrees):
    """각도(도)로 코사인값을 계산합니다"""
    radians = math.radians(degrees)
    return math.cos(radians)

def tan_degrees(degrees):
    """각도(도)로 탄젠트값을 계산합니다"""
    radians = math.radians(degrees)
    # 90도, 270도 등에서 탄젠트는 정의되지 않음
    if degrees % 180 == 90:
        return "에러: 탄젠트가 정의되지 않습니다"
    return math.tan(radians)

def logarithm(number, base=10):
    """로그를 계산합니다 (기본: 상용로그)"""
    if number <= 0:
        return "에러: 로그는 양수에 대해서만 정의됩니다"
    if base <= 0 or base == 1:
        return "에러: 로그의 밑은 양수이고 1이 아니어야 합니다"
    return math.log(number, base)

def natural_log(number):
    """자연로그를 계산합니다"""
    if number <= 0:
        return "에러: 로그는 양수에 대해서만 정의됩니다"
    return math.log(number)

def percentage(value, total):
    """백분율을 계산합니다"""
    if total == 0:
        return "에러: 전체값이 0일 수 없습니다"
    return (value / total) * 100

def modulo(a, b):
    """나머지를 계산합니다"""
    if b == 0:
        return "에러: 0으로 나눌 수 없습니다"
    return a % b

def exponential(x):
    """지수 함수를 계산합니다 (e^x)"""
    return math.exp(x)

def celsius_to_fahrenheit(celsius):
    """섭씨를 화씨로 변환합니다"""
    return (celsius * 9/5) + 32

def fahrenheit_to_celsius(fahrenheit):
    """화씨를 섭씨로 변환합니다"""
    return (fahrenheit - 32) * 5/9

def celsius_to_kelvin(celsius):
    """섭씨를 켈빈으로 변환합니다"""
    return celsius + 273.15