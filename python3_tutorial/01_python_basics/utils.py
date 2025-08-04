"""
유틸리티 모듈
계산기에서 사용하는 도우미 함수들
"""

import json
from datetime import datetime
from typing import List, Dict, Any, Optional, Union

def format_number(number: Union[float, int, str]) -> str:
    """숫자를 보기 좋게 포맷팅합니다"""
    if isinstance(number, float):
        # 정수로 표현 가능하면 정수로
        if number.is_integer():
            return str(int(number))
        # 소수점 4자리까지만 표시
        formatted = f"{number:.4f}".rstrip('0').rstrip('.')
        return formatted
    return str(number)

def save_history(history: List[str], filename: str = "calculator_history.json") -> bool:
    """계산 히스토리를 파일에 저장합니다"""
    try:
        data = {
            "timestamp": datetime.now().isoformat(),
            "history": history
        }
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        return True
    except Exception as e:
        print(f"히스토리 저장 실패: {e}")
        return False

def load_history(filename: str = "calculator_history.json") -> List[Dict[str, str]]:
    """파일에서 계산 히스토리를 불러옵니다"""
    try:
        with open(filename, 'r', encoding='utf-8') as f:
            data = json.load(f)
            return data.get("history", [])
    except FileNotFoundError:
        return []
    except Exception as e:
        print(f"히스토리 불러오기 실패: {e}")
        return []

def print_header(title: str) -> None:
    """제목을 보기 좋게 출력합니다"""
    width = 50
    print("=" * width)
    print(f"{title:^{width}}")
    print("=" * width)

def print_menu(menu_dict: Dict[str, tuple]) -> None:
    """메뉴를 보기 좋게 출력합니다"""
    for key, (name, _) in sorted(menu_dict.items()):
        print(f"{key:>3}. {name}")

def get_choice(prompt: str, valid_choices: List[str]) -> str:
    """사용자로부터 유효한 선택을 받습니다"""
    while True:
        choice = input(prompt).strip()
        if choice in valid_choices:
            return choice
        print(f"올바른 선택이 아닙니다. {valid_choices} 중에서 선택해주세요.")

def format_calculation(num1: float, operation: str, num2: Optional[float], result: Union[float, str, int]) -> str:
    """계산 결과를 보기 좋게 포맷팅합니다"""
    num1_str = format_number(num1)
    num2_str = format_number(num2) if num2 is not None else ""
    result_str = format_number(result) if not isinstance(result, str) else result
    
    if num2 is not None:
        return f"{num1_str} {operation} {num2_str} = {result_str}"
    else:
        return f"{operation}({num1_str}) = {result_str}"

class Calculator:
    """계산기 상태를 관리하는 클래스"""
    def __init__(self) -> None:
        self.memory: float = 0
        self.history: List[Dict[str, str]] = []
        self.last_result: float = 0
    
    def add_to_memory(self, value: float) -> None:
        """메모리에 값을 더합니다"""
        self.memory += value
    
    def subtract_from_memory(self, value: float) -> None:
        """메모리에서 값을 뺍니다"""
        self.memory -= value
    
    def clear_memory(self) -> None:
        """메모리를 초기화합니다"""
        self.memory = 0
    
    def get_memory(self) -> float:
        """메모리 값을 반환합니다"""
        return self.memory
    
    def add_to_history(self, record: str) -> None:
        """계산 기록을 추가합니다"""
        self.history.append({
            "timestamp": datetime.now().isoformat(),
            "calculation": record
        })
        # 최대 100개까지만 저장
        if len(self.history) > 100:
            self.history.pop(0)
    
    def get_history(self, limit: int = 10) -> List[Dict[str, str]]:
        """최근 계산 기록을 반환합니다"""
        return self.history[-limit:]
    
    def clear_history(self) -> None:
        """계산 기록을 모두 지웁니다"""
        self.history = []
        self.last_result = 0


def is_valid_number(value: Any) -> bool:
    """문자열이 유효한 숫자인지 확인합니다"""
    try:
        float(value)
        return True
    except (ValueError, TypeError):
        return False