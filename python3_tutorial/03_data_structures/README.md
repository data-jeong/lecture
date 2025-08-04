# 🔄 Project 03: Data Structures - 정렬 알고리즘 시각화

## 🎯 학습 목표
다양한 정렬 알고리즘을 구현하고 시각화하며 시간/공간 복잡도를 이해합니다.

## 📖 학습 순서

### 1단계: Big-O 복잡도 이해 (20분)
```python
# 시간 복잡도 체크리스트
# O(1)     - 상수 시간 (최고!)
# O(log n) - 로그 시간 (훌륭!)
# O(n)     - 선형 시간 (좋음)
# O(n log n) - 선형로그 (괜찮음)
# O(n²)    - 이차 시간 (느림)
# O(2ⁿ)    - 지수 시간 (피하세요!)
```

### 2단계: 정렬 알고리즘 마스터 (40분)

#### 🎯 구현할 알고리즘
```python
class SortingAlgorithms:
    """각 알고리즘의 특징을 이해하며 구현"""
    
    def bubble_sort(self, arr):
        """O(n²) - 가장 간단하지만 느림"""
        # 인접 요소 비교 및 교환
        
    def quick_sort(self, arr):
        """O(n log n) 평균 - 실무에서 자주 사용"""
        # 피벗 기준 분할 정복
        
    def merge_sort(self, arr):
        """O(n log n) 보장 - 안정적"""
        # 분할 후 병합
        
    def heap_sort(self, arr):
        """O(n log n) - 힙 자료구조 활용"""
        # 최대힙 구성 후 정렬
```

### 3단계: 시각화 구현 (30분)

#### 🎨 터미널 시각화
```python
import time
import os

def visualize_sort(arr, highlight_indices=[]):
    """실시간 정렬 과정 시각화"""
    os.system('clear')  # Windows: 'cls'
    
    max_val = max(arr)
    for i, val in enumerate(arr):
        bar = '█' * int((val/max_val) * 40)
        color = '\033[91m' if i in highlight_indices else '\033[94m'
        print(f'{color}{bar}\033[0m {val}')
    
    time.sleep(0.1)
```

### 4단계: 실습 과제 (60분)

#### 🔥 초급 과제
1. **선택 정렬 추가 구현**
2. **정렬 시간 측정 및 비교**
3. **역순 정렬 옵션 추가**

#### 🚀 중급 과제
1. **Radix Sort 구현** (기수 정렬)
   ```python
   def radix_sort(arr):
       # 자릿수별로 정렬
       # O(d × n) - d는 자릿수
   ```

2. **Tim Sort 분석** (Python 내장 정렬)
   ```python
   # Merge Sort + Insertion Sort 하이브리드
   # 실제 데이터에 최적화
   ```

3. **정렬 애니메이션 생성**
   ```python
   import matplotlib.pyplot as plt
   from matplotlib.animation import FuncAnimation
   ```

#### 💎 고급 과제
1. **병렬 정렬 구현** (multiprocessing)
2. **외부 정렬** (메모리보다 큰 데이터)
3. **GPU 가속 정렬** (CUDA/OpenCL)

## 💡 학습 팁

### 📊 알고리즘 선택 가이드
```python
def choose_algorithm(data_size, data_type, stability_needed):
    """상황별 최적 알고리즘 선택"""
    
    if data_size < 50:
        return "Insertion Sort"  # 작은 데이터
    
    elif data_type == "nearly_sorted":
        return "Tim Sort"  # 거의 정렬된 데이터
    
    elif stability_needed:
        return "Merge Sort"  # 안정 정렬 필요
    
    else:
        return "Quick Sort"  # 일반적인 경우
```

### 🐛 최적화 팁
```python
# 나쁜 예 - 불필요한 복사
def bad_sort(arr):
    sorted_arr = arr.copy()
    # 정렬...
    return sorted_arr

# 좋은 예 - 제자리 정렬
def good_sort(arr):
    # arr를 직접 수정
    arr.sort()  # 또는 custom in-place sort
    return arr
```

### 🏃‍♂️ 성능 프로파일링
```python
import cProfile
import pstats

def profile_sort(sort_func, data):
    profiler = cProfile.Profile()
    profiler.enable()
    
    sort_func(data)
    
    profiler.disable()
    stats = pstats.Stats(profiler)
    stats.sort_stats('cumulative')
    stats.print_stats(10)
```

## 🏆 도전 과제

### 프로젝트: "정렬 알고리즘 경쟁 플랫폼"
```python
class SortingCompetition:
    """
    기능 요구사항:
    1. 다양한 데이터셋 생성 (랜덤, 역순, 거의 정렬됨)
    2. 실시간 성능 비교
    3. 메모리 사용량 추적
    4. 웹 기반 시각화
    5. 리더보드 시스템
    """
    
    def benchmark_all(self, algorithms, datasets):
        results = {}
        for algo in algorithms:
            for dataset in datasets:
                time_taken = self.measure_time(algo, dataset)
                memory_used = self.measure_memory(algo, dataset)
                results[algo.__name__] = {
                    'time': time_taken,
                    'memory': memory_used,
                    'complexity': self.analyze_complexity(algo)
                }
        return results
```

### 🎮 게임화 아이디어
1. **정렬 퍼즐 게임**: 최소 이동으로 정렬
2. **알고리즘 레이싱**: 실시간 속도 대결
3. **복잡도 퀴즈**: Big-O 맞추기

## 📝 체크리스트
- [ ] 6개 이상 정렬 알고리즘 구현
- [ ] 시간 복잡도 분석 문서화
- [ ] 시각화 기능 구현
- [ ] 성능 벤치마크 완료
- [ ] 단위 테스트 작성
- [ ] 최적화 적용 (3가지 이상)

## 🔬 심화 학습

### 특수 정렬 알고리즘
```python
# 1. Counting Sort - O(n+k)
def counting_sort(arr, max_val):
    """정수 전용, 범위가 작을 때"""
    count = [0] * (max_val + 1)
    # ...

# 2. Bucket Sort - O(n+k)
def bucket_sort(arr, num_buckets):
    """균등 분포 데이터에 최적"""
    buckets = [[] for _ in range(num_buckets)]
    # ...

# 3. Sleep Sort - O(잠깐, 뭐라고요?)
import threading
def sleep_sort(arr):
    """농담 알고리즘 - 실제로 작동!"""
    result = []
    def sleep_and_append(x):
        time.sleep(x/1000)
        result.append(x)
    # ...
```

## 🎯 다음 단계
✅ 완료 후 **Project 04: Type Hints & Modern Python**으로 이동!

---
💻 **실행**: `python sorting_algorithms/main.py`
🧪 **테스트**: `pytest sorting_algorithms/tests.py -v`
📊 **벤치마크**: `python benchmark.py`
🎨 **시각화**: `python visualizer.py` 또는 `demo.html`