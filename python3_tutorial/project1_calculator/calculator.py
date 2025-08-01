"""
Project 1: 파이썬 기초 - 계산기 앱
- 변수와 자료형
- 조건문과 반복문
- 기본 입출력
- 예외 처리
"""

def add(a, b):
    """두 수를 더하는 함수"""
    return a + b

def subtract(a, b):
    """두 수를 빼는 함수"""
    return a - b

def multiply(a, b):
    """두 수를 곱하는 함수"""
    return a * b

def divide(a, b):
    """두 수를 나누는 함수"""
    if b == 0:
        raise ValueError("0으로 나눌 수 없습니다!")
    return a / b

def calculator():
    """메인 계산기 함수"""
    print("="*40)
    print("파이썬 계산기 v1.0")
    print("="*40)
    
    while True:
        print("\n연산을 선택하세요:")
        print("1. 덧셈 (+)")
        print("2. 뺄셈 (-)")
        print("3. 곱셈 (*)")
        print("4. 나눗셈 (/)")
        print("5. 종료 (q)")
        
        choice = input("\n선택 (1-5): ").strip()
        
        if choice == 'q' or choice == '5':
            print("계산기를 종료합니다. 안녕히 가세요!")
            break
            
        if choice not in ['1', '2', '3', '4']:
            print("잘못된 선택입니다. 다시 시도해주세요.")
            continue
        
        try:
            num1 = float(input("첫 번째 숫자: "))
            num2 = float(input("두 번째 숫자: "))
            
            if choice == '1':
                result = add(num1, num2)
                operator = '+'
            elif choice == '2':
                result = subtract(num1, num2)
                operator = '-'
            elif choice == '3':
                result = multiply(num1, num2)
                operator = '*'
            elif choice == '4':
                result = divide(num1, num2)
                operator = '/'
            
            print(f"\n결과: {num1} {operator} {num2} = {result}")
            
        except ValueError as e:
            print(f"오류: {e}")
        except Exception as e:
            print(f"예상치 못한 오류가 발생했습니다: {e}")

if __name__ == "__main__":
    calculator()