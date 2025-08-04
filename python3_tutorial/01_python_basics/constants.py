"""
상수 정의 모듈
계산기에서 사용하는 상수들을 정의합니다
"""

import math

# 수학 상수
PI = math.pi
E = math.e
GOLDEN_RATIO = (1 + math.sqrt(5)) / 2

# 물리 상수
SPEED_OF_LIGHT = 299792458  # m/s
GRAVITY = 9.80665  # m/s²

# 단위 변환 상수
# 길이
METER_TO_KILOMETER = 0.001
METER_TO_CENTIMETER = 100
METER_TO_INCH = 39.3701
METER_TO_FEET = 3.28084
KILOMETER_TO_MILE = 0.621371

# 무게
KILOGRAM_TO_GRAM = 1000
KILOGRAM_TO_POUND = 2.20462
KILOGRAM_TO_OUNCE = 35.274

# 온도 변환 함수는 operations.py에 정의되어 있습니다

# 메뉴 상수
BASIC_MENU = {
    "1": ("더하기", "+"),
    "2": ("빼기", "-"),
    "3": ("곱하기", "*"),
    "4": ("나누기", "/"),
}

ADVANCED_MENU = {
    "5": ("거듭제곱", "**"),
    "6": ("제곱근", "√"),
    "7": ("팩토리얼", "!"),
    "8": ("나머지", "%"),
}

TRIGONOMETRY_MENU = {
    "9": ("사인(sin)", "sin"),
    "10": ("코사인(cos)", "cos"),
    "11": ("탄젠트(tan)", "tan"),
}

LOGARITHM_MENU = {
    "12": ("상용로그(log10)", "log10"),
    "13": ("자연로그(ln)", "ln"),
    "14": ("임의 밑 로그", "log"),
}