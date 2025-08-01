"""
벤치마킹 유틸리티
성능 측정과 비교를 위한 도구
"""

import time
import asyncio
from typing import Callable, Any, Dict, List, Optional, Union
from dataclasses import dataclass
from functools import wraps
import statistics
import json
from datetime import datetime
import psutil
import os


@dataclass
class BenchmarkResult:
    """벤치마크 결과"""
    name: str
    duration: float
    iterations: int = 1
    memory_used: Optional[float] = None
    cpu_percent: Optional[float] = None
    
    @property
    def average_duration(self) -> float:
        return self.duration / self.iterations
    
    def __str__(self) -> str:
        avg = self.average_duration
        return f"{self.name}: {avg:.4f}s (total: {self.duration:.4f}s, iterations: {self.iterations})"


class Benchmark:
    """벤치마킹 클래스"""
    
    def __init__(self, name: str = "Benchmark"):
        self.name = name
        self.results: List[BenchmarkResult] = []
        self.process = psutil.Process(os.getpid())
    
    def measure(
        self,
        func: Callable,
        *args,
        iterations: int = 1,
        name: Optional[str] = None,
        **kwargs
    ) -> BenchmarkResult:
        """함수 실행 시간 측정"""
        if name is None:
            name = func.__name__
        
        # 시작 전 메모리
        self.process.memory_info()
        start_memory = self.process.memory_info().rss / 1024 / 1024  # MB
        
        # CPU 사용률 측정 시작
        self.process.cpu_percent(interval=None)
        
        # 실행 시간 측정
        start_time = time.perf_counter()
        
        for _ in range(iterations):
            result = func(*args, **kwargs)
        
        duration = time.perf_counter() - start_time
        
        # 메모리 사용량
        end_memory = self.process.memory_info().rss / 1024 / 1024  # MB
        memory_used = end_memory - start_memory
        
        # CPU 사용률
        cpu_percent = self.process.cpu_percent(interval=None)
        
        benchmark_result = BenchmarkResult(
            name=name,
            duration=duration,
            iterations=iterations,
            memory_used=memory_used,
            cpu_percent=cpu_percent
        )
        
        self.results.append(benchmark_result)
        return benchmark_result
    
    async def measure_async(
        self,
        coro_func: Callable,
        *args,
        iterations: int = 1,
        name: Optional[str] = None,
        **kwargs
    ) -> BenchmarkResult:
        """비동기 함수 실행 시간 측정"""
        if name is None:
            name = coro_func.__name__
        
        # 시작 전 메모리
        start_memory = self.process.memory_info().rss / 1024 / 1024  # MB
        
        # CPU 사용률 측정 시작
        self.process.cpu_percent(interval=None)
        
        # 실행 시간 측정
        start_time = time.perf_counter()
        
        for _ in range(iterations):
            await coro_func(*args, **kwargs)
        
        duration = time.perf_counter() - start_time
        
        # 메모리 사용량
        end_memory = self.process.memory_info().rss / 1024 / 1024  # MB
        memory_used = end_memory - start_memory
        
        # CPU 사용률
        cpu_percent = self.process.cpu_percent(interval=None)
        
        benchmark_result = BenchmarkResult(
            name=name,
            duration=duration,
            iterations=iterations,
            memory_used=memory_used,
            cpu_percent=cpu_percent
        )
        
        self.results.append(benchmark_result)
        return benchmark_result
    
    def compare(
        self,
        funcs: List[Callable],
        args: tuple = (),
        kwargs: dict = None,
        iterations: int = 1
    ) -> Dict[str, BenchmarkResult]:
        """여러 함수 비교"""
        if kwargs is None:
            kwargs = {}
        
        results = {}
        
        for func in funcs:
            result = self.measure(
                func,
                *args,
                iterations=iterations,
                **kwargs
            )
            results[func.__name__] = result
        
        return results
    
    def warmup(self, func: Callable, *args, warmup_iterations: int = 3, **kwargs):
        """워밍업 실행"""
        for _ in range(warmup_iterations):
            func(*args, **kwargs)
    
    def report(self) -> None:
        """벤치마크 결과 리포트"""
        if not self.results:
            print("No benchmark results available.")
            return
        
        print(f"\n📊 {self.name} Benchmark Report")
        print("=" * 70)
        
        # 가장 빠른 결과 찾기
        fastest = min(self.results, key=lambda r: r.average_duration)
        
        # 헤더
        print(f"{'Name':<30} {'Avg Time':>12} {'Total Time':>12} {'Speedup':>8} {'Memory':>10} {'CPU%':>6}")
        print("-" * 70)
        
        # 결과 출력
        for result in sorted(self.results, key=lambda r: r.average_duration):
            speedup = fastest.average_duration / result.average_duration
            speedup_str = f"{speedup:.2f}x"
            
            memory_str = f"{result.memory_used:.1f}MB" if result.memory_used else "N/A"
            cpu_str = f"{result.cpu_percent:.1f}%" if result.cpu_percent else "N/A"
            
            print(f"{result.name:<30} {result.average_duration:>12.4f}s "
                  f"{result.duration:>12.4f}s {speedup_str:>8} "
                  f"{memory_str:>10} {cpu_str:>6}")
        
        # 통계
        if len(self.results) > 1:
            durations = [r.average_duration for r in self.results]
            print("\n📈 Statistics:")
            print(f"  Mean: {statistics.mean(durations):.4f}s")
            print(f"  Median: {statistics.median(durations):.4f}s")
            print(f"  Std Dev: {statistics.stdev(durations):.4f}s")
    
    def save_results(self, filename: str = "benchmark_results.json") -> None:
        """결과를 JSON 파일로 저장"""
        data = {
            "benchmark_name": self.name,
            "timestamp": datetime.now().isoformat(),
            "results": [
                {
                    "name": r.name,
                    "duration": r.duration,
                    "iterations": r.iterations,
                    "average_duration": r.average_duration,
                    "memory_used": r.memory_used,
                    "cpu_percent": r.cpu_percent
                }
                for r in self.results
            ]
        }
        
        with open(filename, 'w') as f:
            json.dump(data, f, indent=2)
        
        print(f"\n💾 Results saved to {filename}")
    
    def plot_results(self, output_file: str = "benchmark_plot.png") -> None:
        """결과를 그래프로 시각화 (matplotlib 필요)"""
        try:
            import matplotlib.pyplot as plt
            
            names = [r.name for r in self.results]
            durations = [r.average_duration for r in self.results]
            
            plt.figure(figsize=(10, 6))
            bars = plt.bar(names, durations)
            
            # 색상 그라데이션
            colors = plt.cm.viridis(np.linspace(0, 1, len(bars)))
            for bar, color in zip(bars, colors):
                bar.set_color(color)
            
            plt.xlabel('Method')
            plt.ylabel('Average Time (seconds)')
            plt.title(f'{self.name} Benchmark Results')
            plt.xticks(rotation=45, ha='right')
            
            # 값 표시
            for i, (name, duration) in enumerate(zip(names, durations)):
                plt.text(i, duration, f'{duration:.3f}s', 
                        ha='center', va='bottom')
            
            plt.tight_layout()
            plt.savefig(output_file)
            print(f"\n📊 Plot saved to {output_file}")
            
        except ImportError:
            print("\n⚠️  matplotlib not installed. Cannot create plot.")


def benchmark_decorator(iterations: int = 1):
    """벤치마크 데코레이터"""
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            start_time = time.perf_counter()
            
            for _ in range(iterations):
                result = func(*args, **kwargs)
            
            duration = time.perf_counter() - start_time
            avg_duration = duration / iterations
            
            print(f"⏱️  {func.__name__}: {avg_duration:.4f}s "
                  f"(total: {duration:.4f}s, iterations: {iterations})")
            
            return result
        return wrapper
    return decorator


def async_benchmark_decorator(iterations: int = 1):
    """비동기 벤치마크 데코레이터"""
    def decorator(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            start_time = time.perf_counter()
            
            for _ in range(iterations):
                result = await func(*args, **kwargs)
            
            duration = time.perf_counter() - start_time
            avg_duration = duration / iterations
            
            print(f"⏱️  {func.__name__}: {avg_duration:.4f}s "
                  f"(total: {duration:.4f}s, iterations: {iterations})")
            
            return result
        return wrapper
    return decorator


def compare_methods(
    methods: Dict[str, Callable],
    test_data: Any,
    iterations: int = 100,
    warmup: bool = True
) -> None:
    """여러 메서드 성능 비교"""
    benchmark = Benchmark("Method Comparison")
    
    for name, method in methods.items():
        if warmup:
            benchmark.warmup(method, test_data, warmup_iterations=3)
        
        benchmark.measure(
            method,
            test_data,
            iterations=iterations,
            name=name
        )
    
    benchmark.report()
    return benchmark


def example_usage():
    """사용 예제"""
    import numpy as np
    
    print("⏱️  벤치마킹 예제")
    print("=" * 60)
    
    # 테스트할 함수들
    def bubble_sort(arr):
        n = len(arr)
        for i in range(n):
            for j in range(0, n-i-1):
                if arr[j] > arr[j+1]:
                    arr[j], arr[j+1] = arr[j+1], arr[j]
        return arr
    
    def quick_sort(arr):
        if len(arr) <= 1:
            return arr
        pivot = arr[len(arr) // 2]
        left = [x for x in arr if x < pivot]
        middle = [x for x in arr if x == pivot]
        right = [x for x in arr if x > pivot]
        return quick_sort(left) + middle + quick_sort(right)
    
    def python_sort(arr):
        return sorted(arr)
    
    # 벤치마크 실행
    benchmark = Benchmark("Sorting Algorithms")
    
    # 테스트 데이터
    test_data = list(range(100, 0, -1))  # 역순 정렬된 데이터
    
    # 각 알고리즘 테스트
    methods = {
        "Bubble Sort": lambda: bubble_sort(test_data.copy()),
        "Quick Sort": lambda: quick_sort(test_data.copy()),
        "Python Sort": lambda: python_sort(test_data.copy())
    }
    
    for name, method in methods.items():
        benchmark.measure(method, iterations=10, name=name)
    
    # 결과 리포트
    benchmark.report()
    
    # 비동기 함수 벤치마킹 예제
    print("\n\n🔄 비동기 함수 벤치마킹")
    print("=" * 60)
    
    async def async_sleep_test(duration):
        await asyncio.sleep(duration)
    
    async def run_async_benchmark():
        async_benchmark = Benchmark("Async Operations")
        
        await async_benchmark.measure_async(
            async_sleep_test, 
            0.1, 
            iterations=5,
            name="Async Sleep 0.1s"
        )
        
        async_benchmark.report()
    
    # 비동기 벤치마크 실행
    asyncio.run(run_async_benchmark())


if __name__ == "__main__":
    example_usage()