"""
고급 공학용 계산기
모든 기능이 통합된 계산기 프로그램
"""

from calculator import add, subtract, multiply, divide, get_number
from operations import *
from constants import *
from utils import *

def show_full_menu():
    """전체 메뉴를 표시합니다"""
    print("\n[기본 연산]")
    print_menu(BASIC_MENU)
    
    print("\n[고급 연산]")
    print_menu(ADVANCED_MENU)
    
    print("\n[삼각함수]")
    print_menu(TRIGONOMETRY_MENU)
    
    print("\n[로그함수]")
    print_menu(LOGARITHM_MENU)
    
    print("\n[기타 기능]")
    print(" 15. 단위 변환")
    print(" 16. 메모리 기능")
    print(" 17. 계산 히스토리")
    print(" 18. 히스토리 저장")
    print(" 19. 상수 보기")
    print("  0. 종료")

def unit_conversion():
    """단위 변환 기능"""
    print("\n[단위 변환]")
    print("1. 길이")
    print("2. 무게")
    print("3. 온도")
    
    choice = get_choice("선택: ", ["1", "2", "3"])
    
    if choice == "1":
        print("\n[길이 변환]")
        print("1. 미터 → 킬로미터")
        print("2. 미터 → 센티미터")
        print("3. 미터 → 인치")
        print("4. 킬로미터 → 마일")
        
        sub_choice = get_choice("선택: ", ["1", "2", "3", "4"])
        value = get_number("값 입력: ")
        
        if sub_choice == "1":
            result = value * METER_TO_KILOMETER
            print(f"{value} m = {result} km")
        elif sub_choice == "2":
            result = value * METER_TO_CENTIMETER
            print(f"{value} m = {result} cm")
        elif sub_choice == "3":
            result = value * METER_TO_INCH
            print(f"{value} m = {result} inch")
        elif sub_choice == "4":
            result = value * KILOMETER_TO_MILE
            print(f"{value} km = {result} mile")
    
    elif choice == "2":
        print("\n[무게 변환]")
        print("1. 킬로그램 → 그램")
        print("2. 킬로그램 → 파운드")
        
        sub_choice = get_choice("선택: ", ["1", "2"])
        value = get_number("값 입력: ")
        
        if sub_choice == "1":
            result = value * KILOGRAM_TO_GRAM
            print(f"{value} kg = {result} g")
        elif sub_choice == "2":
            result = value * KILOGRAM_TO_POUND
            print(f"{value} kg = {result} lb")
    
    elif choice == "3":
        print("\n[온도 변환]")
        print("1. 섭씨 → 화씨")
        print("2. 화씨 → 섭씨")
        print("3. 섭씨 → 켈빈")
        
        sub_choice = get_choice("선택: ", ["1", "2", "3"])
        value = get_number("값 입력: ")
        
        if sub_choice == "1":
            result = celsius_to_fahrenheit(value)
            print(f"{value}°C = {result}°F")
        elif sub_choice == "2":
            result = fahrenheit_to_celsius(value)
            print(f"{value}°F = {result}°C")
        elif sub_choice == "3":
            result = celsius_to_kelvin(value)
            print(f"{value}°C = {result}K")

def memory_operations(calc):
    """메모리 기능"""
    print("\n[메모리 기능]")
    print(f"현재 메모리: {format_number(calc.get_memory())}")
    print("1. M+ (메모리에 더하기)")
    print("2. M- (메모리에서 빼기)")
    print("3. MR (메모리 읽기)")
    print("4. MC (메모리 초기화)")
    
    choice = get_choice("선택: ", ["1", "2", "3", "4"])
    
    if choice == "1":
        value = get_number("더할 값: ")
        calc.add_to_memory(value)
        print(f"메모리에 {value} 더함. 현재 메모리: {calc.get_memory()}")
    elif choice == "2":
        value = get_number("뺄 값: ")
        calc.subtract_from_memory(value)
        print(f"메모리에서 {value} 뺌. 현재 메모리: {calc.get_memory()}")
    elif choice == "3":
        print(f"메모리 값: {calc.get_memory()}")
    elif choice == "4":
        calc.clear_memory()
        print("메모리가 초기화되었습니다.")

def show_constants():
    """상수 표시"""
    print("\n[수학 상수]")
    print(f"π (파이) = {PI}")
    print(f"e (자연상수) = {E}")
    print(f"황금비 = {GOLDEN_RATIO}")
    
    print("\n[물리 상수]")
    print(f"빛의 속도 = {SPEED_OF_LIGHT} m/s")
    print(f"중력가속도 = {GRAVITY} m/s²")

def main():
    """메인 프로그램"""
    calc = Calculator()
    
    # 저장된 히스토리 불러오기
    calc.history = load_history()
    
    print_header("고급 공학용 계산기")
    print("계산 결과를 재사용하려면 'ANS'를 입력하세요.")
    
    while True:
        show_full_menu()
        
        choice = input("\n선택하세요: ").strip()
        
        if choice == "0":
            print("\n계산기를 종료합니다.")
            save = input("히스토리를 저장하시겠습니까? (y/n): ")
            if save.lower() == 'y':
                if save_history([h['calculation'] for h in calc.history]):
                    print("히스토리가 저장되었습니다.")
            break
        
        # 단위 변환
        if choice == "15":
            unit_conversion()
            continue
        
        # 메모리 기능
        if choice == "16":
            memory_operations(calc)
            continue
        
        # 히스토리 보기
        if choice == "17":
            history = calc.get_history()
            if not history:
                print("\n계산 히스토리가 없습니다.")
            else:
                print("\n[최근 계산 히스토리]")
                for i, record in enumerate(history, 1):
                    print(f"{i}. {record['calculation']}")
            continue
        
        # 히스토리 저장
        if choice == "18":
            if save_history([h['calculation'] for h in calc.history]):
                print("히스토리가 저장되었습니다.")
            continue
        
        # 상수 보기
        if choice == "19":
            show_constants()
            continue
        
        # 연산 수행
        all_menus = {**BASIC_MENU, **ADVANCED_MENU, **TRIGONOMETRY_MENU, **LOGARITHM_MENU}
        
        if choice not in all_menus:
            print("올바른 메뉴를 선택해주세요.")
            continue
        
        operation_name, operation_symbol = all_menus[choice]
        
        # 숫자 입력
        num1_input = input("첫 번째 숫자 (또는 ANS): ")
        if num1_input.upper() == "ANS":
            num1 = calc.last_result
            print(f"이전 결과 사용: {format_number(num1)}")
        else:
            try:
                num1 = float(num1_input)
            except ValueError:
                print("올바른 숫자를 입력해주세요.")
                continue
        
        # 단항 연산
        if choice in ["6", "7", "9", "10", "11", "12", "13"]:
            if choice == "6":  # 제곱근
                result = square_root(num1)
            elif choice == "7":  # 팩토리얼
                result = factorial(num1)
            elif choice == "9":  # 사인
                result = sin_degrees(num1)
            elif choice == "10":  # 코사인
                result = cos_degrees(num1)
            elif choice == "11":  # 탄젠트
                result = tan_degrees(num1)
            elif choice == "12":  # 상용로그
                result = logarithm(num1, 10)
            elif choice == "13":  # 자연로그
                result = natural_log(num1)
            
            record = format_calculation(num1, operation_symbol, None, result)
        
        # 이항 연산
        else:
            num2_input = input("두 번째 숫자 (또는 ANS): ")
            if num2_input.upper() == "ANS":
                num2 = calc.last_result
                print(f"이전 결과 사용: {format_number(num2)}")
            else:
                try:
                    num2 = float(num2_input)
                except ValueError:
                    print("올바른 숫자를 입력해주세요.")
                    continue
            
            if choice == "1":
                result = add(num1, num2)
            elif choice == "2":
                result = subtract(num1, num2)
            elif choice == "3":
                result = multiply(num1, num2)
            elif choice == "4":
                result = divide(num1, num2)
            elif choice == "5":
                result = power(num1, num2)
            elif choice == "8":
                result = modulo(num1, num2)
            elif choice == "14":  # 임의 밑 로그
                result = logarithm(num1, num2)
            
            record = format_calculation(num1, operation_symbol, num2, result)
        
        # 결과 출력
        print(f"\n결과: {record}")
        
        if not isinstance(result, str):  # 에러가 아닌 경우
            calc.last_result = result
            calc.add_to_history(record)

if __name__ == "__main__":
    main()