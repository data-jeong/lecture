"""
기본 계산기
Python 기초 학습을 위한 간단한 계산기 프로그램
"""

from typing import Union

def add(a: float, b: float) -> float:
    """두 수를 더합니다"""
    return a + b

def subtract(a: float, b: float) -> float:
    """두 수를 뺍니다"""
    return a - b

def multiply(a: float, b: float) -> float:
    """두 수를 곱합니다"""
    return a * b

def divide(a: float, b: float) -> Union[float, str]:
    """두 수를 나눕니다
    
    Args:
        a: 피제수
        b: 제수
    
    Returns:
        나눗셈 결과 또는 에러 메시지
    
    Raises:
        None (에러는 문자열로 반환)
    """
    if b == 0:
        return "에러: 0으로 나눌 수 없습니다"
    return a / b

def get_number(prompt: str) -> float:
    """사용자로부터 숫자를 입력받습니다
    
    Args:
        prompt: 사용자에게 보여줄 프롬프트 메시지
    
    Returns:
        입력받은 숫자 (float)
    """
    while True:
        try:
            return float(input(prompt))
        except ValueError:
            print("올바른 숫자를 입력해주세요.")
        except KeyboardInterrupt:
            print("\n입력이 취소되었습니다.")
            raise
        except EOFError:
            print("\n입력이 종료되었습니다.")
            raise

def main() -> None:
    """메인 프로그램"""
    print("=" * 30)
    print("   파이썬 기본 계산기")
    print("=" * 30)
    
    # 계산 히스토리
    history = []
    
    while True:
        print("\n[메뉴]")
        print("1. 더하기 (+)")
        print("2. 빼기 (-)")
        print("3. 곱하기 (*)")
        print("4. 나누기 (/)")
        print("5. 계산 히스토리")
        print("0. 종료")
        
        choice = input("\n선택하세요: ")
        
        if choice == "0":
            print("\n계산기를 종료합니다. 안녕히 가세요!")
            break
        
        if choice == "5":
            if not history:
                print("\n계산 히스토리가 없습니다.")
            else:
                print("\n[계산 히스토리]")
                for i, record in enumerate(history, 1):
                    print(f"{i}. {record}")
            continue
        
        if choice not in ["1", "2", "3", "4"]:
            print("올바른 메뉴를 선택해주세요.")
            continue
        
        # 숫자 입력
        num1 = get_number("첫 번째 숫자: ")
        num2 = get_number("두 번째 숫자: ")
        
        # 계산 수행
        if choice == "1":
            result = add(num1, num2)
            operation = "+"
        elif choice == "2":
            result = subtract(num1, num2)
            operation = "-"
        elif choice == "3":
            result = multiply(num1, num2)
            operation = "*"
        elif choice == "4":
            result = divide(num1, num2)
            operation = "/"
        
        # 결과 출력
        if isinstance(result, str):  # 에러 메시지인 경우
            print(f"\n{result}")
        else:
            record = f"{num1} {operation} {num2} = {result}"
            print(f"\n결과: {record}")
            history.append(record)
            
            # 히스토리 최대 10개 유지
            if len(history) > 10:
                history.pop(0)

if __name__ == "__main__":
    main()