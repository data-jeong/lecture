"""
Python 기초 - 공학용 계산기 패키지

이 패키지는 Python 기초 학습을 위한 계산기 프로그램을 제공합니다.

주요 모듈:
- calculator: 기본 계산기 함수들
- operations: 고급 수학 연산 함수들
- constants: 수학/물리 상수 정의
- utils: 유틸리티 함수와 Calculator 클래스
- examples: 사용 예제 모음

사용 예:
    from python_basics import add, subtract, multiply, divide
    result = add(10, 5)
    print(result)  # 15
"""

# 기본 계산기 함수들
from .calculator import (
    add,
    subtract,
    multiply,
    divide,
    get_number
)

# 고급 연산 함수들
from .operations import (
    power,
    square_root,
    factorial,
    modulo,
    sin_degrees,
    cos_degrees,
    tan_degrees,
    logarithm,
    natural_log,
    exponential,
    percentage,
    celsius_to_fahrenheit,
    fahrenheit_to_celsius,
    celsius_to_kelvin
)

# 상수들
from .constants import (
    PI,
    E,
    GOLDEN_RATIO,
    SPEED_OF_LIGHT,
    GRAVITY
)

# 유틸리티 함수들
from .utils import (
    format_number,
    format_calculation,
    save_history,
    load_history,
    print_header,
    print_menu,
    get_choice,
    is_valid_number,
    Calculator
)

__version__ = '1.0.0'
__author__ = 'Python Tutorial'

__all__ = [
    # calculator
    'add', 'subtract', 'multiply', 'divide', 'get_number',
    # operations
    'power', 'square_root', 'factorial', 'modulo',
    'sin_degrees', 'cos_degrees', 'tan_degrees',
    'logarithm', 'natural_log', 'exponential', 'percentage',
    'celsius_to_fahrenheit', 'fahrenheit_to_celsius', 'celsius_to_kelvin',
    # constants
    'PI', 'E', 'GOLDEN_RATIO', 'SPEED_OF_LIGHT', 'GRAVITY',
    # utils
    'format_number', 'format_calculation', 'save_history', 'load_history',
    'print_header', 'print_menu', 'get_choice', 'is_valid_number',
    'Calculator'
]