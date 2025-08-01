"""
고급 계산기 - 리스트, 딕셔너리, 람다 함수 활용
"""

import math

operations = {
    '+': lambda x, y: x + y,
    '-': lambda x, y: x - y,
    '*': lambda x, y: x * y,
    '/': lambda x, y: x / y if y != 0 else "0으로 나눌 수 없습니다",
    '**': lambda x, y: x ** y,
    'sqrt': lambda x: math.sqrt(x) if x >= 0 else "음수의 제곱근은 계산할 수 없습니다"
}

history = []

def calculate_with_history():
    """계산 이력을 저장하는 고급 계산기"""
    print("고급 계산기 - 계산 이력 기능 포함")
    print("사용 가능한 연산: +, -, *, /, **, sqrt")
    print("이력 보기: history, 종료: quit\n")
    
    while True:
        expression = input("계산식 입력 (예: 5 + 3): ").strip()
        
        if expression.lower() == 'quit':
            print("계산기를 종료합니다.")
            break
            
        if expression.lower() == 'history':
            if history:
                print("\n--- 계산 이력 ---")
                for idx, item in enumerate(history, 1):
                    print(f"{idx}. {item}")
            else:
                print("계산 이력이 없습니다.")
            continue
        
        try:
            if 'sqrt' in expression:
                num = float(expression.replace('sqrt', '').strip())
                result = operations['sqrt'](num)
                history.append(f"sqrt({num}) = {result}")
            else:
                parts = expression.split()
                if len(parts) == 3:
                    num1 = float(parts[0])
                    operator = parts[1]
                    num2 = float(parts[2])
                    
                    if operator in operations:
                        result = operations[operator](num1, num2)
                        history.append(f"{num1} {operator} {num2} = {result}")
                    else:
                        print("지원하지 않는 연산자입니다.")
                        continue
                else:
                    print("올바른 형식으로 입력해주세요.")
                    continue
                    
            print(f"결과: {result}\n")
            
        except ValueError:
            print("숫자를 올바르게 입력해주세요.")
        except Exception as e:
            print(f"오류 발생: {e}")

if __name__ == "__main__":
    calculate_with_history()