"""
고급 계산기 테스트
advanced_calculator의 모든 기능을 테스트합니다
"""

import unittest
import math
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from operations import (
    power, square_root, factorial, modulo,
    sin_degrees, cos_degrees, tan_degrees,
    logarithm, natural_log, exponential,
    celsius_to_fahrenheit, fahrenheit_to_celsius, celsius_to_kelvin
)
from constants import PI, E, GOLDEN_RATIO
from utils import format_number, format_calculation, is_valid_number, Calculator


class TestAdvancedOperations(unittest.TestCase):
    """고급 연산 테스트"""
    
    def test_power(self):
        """거듭제곱 테스트"""
        self.assertEqual(power(2, 3), 8)
        self.assertEqual(power(5, 0), 1)
        self.assertEqual(power(10, -1), 0.1)
        self.assertAlmostEqual(power(2, 0.5), math.sqrt(2))
    
    def test_square_root(self):
        """제곱근 테스트"""
        self.assertEqual(square_root(4), 2)
        self.assertEqual(square_root(9), 3)
        self.assertAlmostEqual(square_root(2), math.sqrt(2))
        self.assertIn("음수", square_root(-1))
    
    def test_factorial(self):
        """팩토리얼 테스트"""
        self.assertEqual(factorial(0), 1)
        self.assertEqual(factorial(5), 120)
        self.assertEqual(factorial(10), 3628800)
        # factorial 함수는 정수로 변환하므로 에러가 아님
        self.assertEqual(factorial(3.5), 6)  # factorial(3) = 6
        self.assertIn("음수", factorial(-1))
    
    def test_modulo(self):
        """나머지 연산 테스트"""
        self.assertEqual(modulo(10, 3), 1)
        self.assertEqual(modulo(20, 5), 0)
        self.assertEqual(modulo(7, 2), 1)
        self.assertIn("0으로", modulo(5, 0))


class TestTrigonometry(unittest.TestCase):
    """삼각함수 테스트"""
    
    def test_sin_degrees(self):
        """사인 함수 테스트"""
        self.assertAlmostEqual(sin_degrees(0), 0)
        self.assertAlmostEqual(sin_degrees(30), 0.5)
        self.assertAlmostEqual(sin_degrees(90), 1)
        self.assertAlmostEqual(sin_degrees(180), 0, places=10)
    
    def test_cos_degrees(self):
        """코사인 함수 테스트"""
        self.assertAlmostEqual(cos_degrees(0), 1)
        self.assertAlmostEqual(cos_degrees(60), 0.5)
        self.assertAlmostEqual(cos_degrees(90), 0, places=10)
        self.assertAlmostEqual(cos_degrees(180), -1)
    
    def test_tan_degrees(self):
        """탄젠트 함수 테스트"""
        self.assertAlmostEqual(tan_degrees(0), 0)
        self.assertAlmostEqual(tan_degrees(45), 1)
        self.assertAlmostEqual(tan_degrees(135), -1, places=10)
        result = tan_degrees(90)
        self.assertIn("정의되지 않습니다", result)


class TestLogarithms(unittest.TestCase):
    """로그 함수 테스트"""
    
    def test_logarithm(self):
        """로그 함수 테스트"""
        self.assertAlmostEqual(logarithm(100, 10), 2)
        self.assertAlmostEqual(logarithm(8, 2), 3)
        self.assertAlmostEqual(logarithm(1, 10), 0)
        self.assertIn("양수", logarithm(-1, 10))
        self.assertIn("양수", logarithm(10, -1))
    
    def test_natural_log(self):
        """자연로그 테스트"""
        self.assertAlmostEqual(natural_log(E), 1)
        self.assertAlmostEqual(natural_log(1), 0)
        self.assertAlmostEqual(natural_log(E**2), 2)
        self.assertIn("양수", natural_log(-1))
    
    def test_exponential(self):
        """지수 함수 테스트"""
        self.assertAlmostEqual(exponential(0), 1)
        self.assertAlmostEqual(exponential(1), E)
        self.assertAlmostEqual(exponential(2), E**2)


class TestTemperatureConversion(unittest.TestCase):
    """온도 변환 테스트"""
    
    def test_celsius_to_fahrenheit(self):
        """섭씨 → 화씨 변환 테스트"""
        self.assertEqual(celsius_to_fahrenheit(0), 32)
        self.assertEqual(celsius_to_fahrenheit(100), 212)
        self.assertEqual(celsius_to_fahrenheit(-40), -40)
    
    def test_fahrenheit_to_celsius(self):
        """화씨 → 섭씨 변환 테스트"""
        self.assertEqual(fahrenheit_to_celsius(32), 0)
        self.assertEqual(fahrenheit_to_celsius(212), 100)
        self.assertEqual(fahrenheit_to_celsius(-40), -40)
    
    def test_celsius_to_kelvin(self):
        """섭씨 → 켈빈 변환 테스트"""
        self.assertAlmostEqual(celsius_to_kelvin(0), 273.15)
        self.assertAlmostEqual(celsius_to_kelvin(100), 373.15)
        self.assertAlmostEqual(celsius_to_kelvin(-273.15), 0)


class TestCalculatorClass(unittest.TestCase):
    """Calculator 클래스 테스트"""
    
    def setUp(self):
        """테스트 전 실행"""
        self.calc = Calculator()
    
    def test_memory_operations(self):
        """메모리 기능 테스트"""
        self.assertEqual(self.calc.get_memory(), 0)
        
        self.calc.add_to_memory(10)
        self.assertEqual(self.calc.get_memory(), 10)
        
        self.calc.subtract_from_memory(3)
        self.assertEqual(self.calc.get_memory(), 7)
        
        self.calc.clear_memory()
        self.assertEqual(self.calc.get_memory(), 0)
    
    def test_history(self):
        """히스토리 기능 테스트"""
        self.assertEqual(len(self.calc.get_history()), 0)
        
        self.calc.add_to_history("1 + 1 = 2")
        self.calc.add_to_history("2 * 3 = 6")
        
        history = self.calc.get_history()
        self.assertEqual(len(history), 2)
        self.assertEqual(history[0]['calculation'], "1 + 1 = 2")
        
        # 최대 100개 제한 테스트
        for i in range(105):
            self.calc.add_to_history(f"test {i}")
        
        # get_history는 기본적으로 10개만 반환
        self.assertEqual(len(self.calc.get_history()), 10)
        # 전체 히스토리는 100개로 제한
        self.assertEqual(len(self.calc.history), 100)
    
    def test_last_result(self):
        """마지막 결과 저장 테스트"""
        self.assertEqual(self.calc.last_result, 0)
        
        self.calc.last_result = 42
        self.assertEqual(self.calc.last_result, 42)


class TestUtilityFunctions(unittest.TestCase):
    """유틸리티 함수 테스트"""
    
    def test_format_number(self):
        """숫자 포맷팅 테스트"""
        self.assertEqual(format_number(3.14159), "3.1416")
        self.assertEqual(format_number(100), "100")
        self.assertEqual(format_number(0.0001), "0.0001")
        self.assertEqual(format_number(1000000), "1000000")
    
    def test_format_calculation(self):
        """계산식 포맷팅 테스트"""
        self.assertEqual(
            format_calculation(2, "+", 3, 5),
            "2 + 3 = 5"
        )
        self.assertEqual(
            format_calculation(4, "√", None, 2),
            "√(4) = 2"
        )
    
    def test_is_valid_number(self):
        """숫자 유효성 검사 테스트"""
        self.assertTrue(is_valid_number("123"))
        self.assertTrue(is_valid_number("-456"))
        self.assertTrue(is_valid_number("3.14"))
        self.assertFalse(is_valid_number("abc"))
        self.assertFalse(is_valid_number(""))
        self.assertFalse(is_valid_number("12.34.56"))


class TestConstants(unittest.TestCase):
    """상수 테스트"""
    
    def test_mathematical_constants(self):
        """수학 상수 테스트"""
        self.assertAlmostEqual(PI, math.pi)
        self.assertAlmostEqual(E, math.e)
        self.assertAlmostEqual(GOLDEN_RATIO, (1 + math.sqrt(5)) / 2)
    
    def test_physical_constants(self):
        """물리 상수 테스트"""
        from constants import SPEED_OF_LIGHT, GRAVITY
        self.assertEqual(SPEED_OF_LIGHT, 299792458)
        self.assertAlmostEqual(GRAVITY, 9.80665)


class TestEdgeCases(unittest.TestCase):
    """경계값 테스트"""
    
    def test_very_large_numbers(self):
        """매우 큰 수 테스트"""
        large = 10**100
        self.assertEqual(power(10, 100), large)
        self.assertIsInstance(logarithm(large, 10), float)
    
    def test_very_small_numbers(self):
        """매우 작은 수 테스트"""
        small = 10**-100
        self.assertAlmostEqual(power(10, -100), small)
        self.assertIsInstance(logarithm(small, 10), float)
    
    def test_special_values(self):
        """특수값 테스트"""
        # 매우 큰 수의 지수 함수
        result = exponential(100)
        self.assertGreater(result, 1e40)  # 매우 큰 수 확인
        
        # 0에 가까운 값
        self.assertAlmostEqual(sin_degrees(180), 0, places=10)
        self.assertAlmostEqual(cos_degrees(90), 0, places=10)


def run_tests():
    """모든 테스트 실행"""
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()
    
    # 모든 테스트 클래스 추가
    suite.addTests(loader.loadTestsFromTestCase(TestAdvancedOperations))
    suite.addTests(loader.loadTestsFromTestCase(TestTrigonometry))
    suite.addTests(loader.loadTestsFromTestCase(TestLogarithms))
    suite.addTests(loader.loadTestsFromTestCase(TestTemperatureConversion))
    suite.addTests(loader.loadTestsFromTestCase(TestCalculatorClass))
    suite.addTests(loader.loadTestsFromTestCase(TestUtilityFunctions))
    suite.addTests(loader.loadTestsFromTestCase(TestConstants))
    suite.addTests(loader.loadTestsFromTestCase(TestEdgeCases))
    
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    # 테스트 결과 요약
    print("\n" + "=" * 50)
    print("테스트 결과 요약")
    print("=" * 50)
    print(f"실행된 테스트: {result.testsRun}")
    print(f"성공: {result.testsRun - len(result.failures) - len(result.errors)}")
    print(f"실패: {len(result.failures)}")
    print(f"에러: {len(result.errors)}")
    
    return result.wasSuccessful()


if __name__ == "__main__":
    success = run_tests()
    exit(0 if success else 1)