"""
계산기 테스트 코드
계산기 함수들이 올바르게 작동하는지 확인합니다
"""

from calculator import add, subtract, multiply, divide
from operations import *
from constants import *

def test_basic_operations():
    """기본 연산 테스트"""
    print("=== 기본 연산 테스트 ===")
    
    # 덧셈
    assert add(2, 3) == 5
    assert add(-1, 1) == 0
    assert add(0.1, 0.2) - 0.3 < 0.0001  # 부동소수점 오차 고려
    print("✓ 덧셈 테스트 통과")
    
    # 뺄셈
    assert subtract(5, 3) == 2
    assert subtract(0, 5) == -5
    print("✓ 뺄셈 테스트 통과")
    
    # 곱셈
    assert multiply(4, 5) == 20
    assert multiply(-2, 3) == -6
    assert multiply(0, 100) == 0
    print("✓ 곱셈 테스트 통과")
    
    # 나눗셈
    assert divide(10, 2) == 5
    assert divide(1, 3) - 0.333333 < 0.0001
    assert divide(5, 0) == "에러: 0으로 나눌 수 없습니다"
    print("✓ 나눗셈 테스트 통과")

def test_advanced_operations():
    """고급 연산 테스트"""
    print("\n=== 고급 연산 테스트 ===")
    
    # 거듭제곱
    assert power(2, 3) == 8
    assert power(5, 0) == 1
    print("✓ 거듭제곱 테스트 통과")
    
    # 제곱근
    assert square_root(4) == 2
    assert square_root(9) == 3
    assert square_root(-1) == "에러: 음수의 제곱근은 계산할 수 없습니다"
    print("✓ 제곱근 테스트 통과")
    
    # 팩토리얼
    assert factorial(5) == 120
    assert factorial(0) == 1
    assert factorial(-1) == "에러: 음수의 팩토리얼은 정의되지 않습니다"
    print("✓ 팩토리얼 테스트 통과")

def test_trigonometry():
    """삼각함수 테스트"""
    print("\n=== 삼각함수 테스트 ===")
    
    # sin
    assert abs(sin_degrees(0)) < 0.0001
    assert abs(sin_degrees(90) - 1) < 0.0001
    print("✓ 사인 테스트 통과")
    
    # cos
    assert abs(cos_degrees(0) - 1) < 0.0001
    assert abs(cos_degrees(90)) < 0.0001
    print("✓ 코사인 테스트 통과")
    
    # tan
    assert abs(tan_degrees(0)) < 0.0001
    assert abs(tan_degrees(45) - 1) < 0.0001
    assert tan_degrees(90) == "에러: 탄젠트가 정의되지 않습니다"
    print("✓ 탄젠트 테스트 통과")

def test_unit_conversion():
    """단위 변환 테스트"""
    print("\n=== 단위 변환 테스트 ===")
    
    # 온도 변환
    assert celsius_to_fahrenheit(0) == 32
    assert celsius_to_fahrenheit(100) == 212
    assert fahrenheit_to_celsius(32) == 0
    assert celsius_to_kelvin(0) == 273.15
    print("✓ 온도 변환 테스트 통과")
    
    # 길이 변환
    assert 1000 * METER_TO_KILOMETER == 1
    assert 1 * METER_TO_CENTIMETER == 100
    print("✓ 길이 변환 테스트 통과")

def run_all_tests():
    """모든 테스트 실행"""
    print("계산기 테스트를 시작합니다...\n")
    
    try:
        test_basic_operations()
        test_advanced_operations()
        test_trigonometry()
        test_unit_conversion()
        
        print("\n✅ 모든 테스트를 통과했습니다!")
    except AssertionError as e:
        print(f"\n❌ 테스트 실패: {e}")
    except Exception as e:
        print(f"\n❌ 예상치 못한 오류: {e}")

if __name__ == "__main__":
    run_all_tests()