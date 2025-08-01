"""
GIL(Global Interpreter Lock) 데모
GIL의 영향을 시각적으로 보여주는 예제
"""

import time
import threading
import multiprocessing
from typing import List, Tuple, Callable, Any
import concurrent.futures
import asyncio
import aiohttp
from dataclasses import dataclass
import json


@dataclass
class BenchmarkResult:
    """벤치마크 결과"""
    name: str
    duration: float
    speedup: float = 1.0
    
    def __str__(self) -> str:
        return f"{self.name}: {self.duration:.2f}초 (속도향상: {self.speedup:.2f}x)"


class GILDemo:
    """GIL 데모 클래스"""
    
    def __init__(self, task_size: int = 10_000_000):
        self.task_size = task_size
        self.results: List[BenchmarkResult] = []
    
    def cpu_bound_task(self, n: int) -> int:
        """CPU 집약적 작업"""
        result = 0
        for i in range(n):
            result += i ** 2
        return result
    
    def io_bound_task(self, delay: float) -> str:
        """I/O 집약적 작업 (시뮬레이션)"""
        time.sleep(delay)
        return f"Slept for {delay} seconds"
    
    async def async_io_task(self, url: str) -> int:
        """비동기 I/O 작업"""
        async with aiohttp.ClientSession() as session:
            try:
                async with session.get(url, timeout=5) as response:
                    return len(await response.text())
            except Exception as e:
                print(f"Error fetching {url}: {e}")
                return 0
    
    def benchmark_single_thread(self) -> BenchmarkResult:
        """단일 스레드 벤치마크"""
        print("\n🔹 단일 스레드 테스트...")
        start = time.perf_counter()
        
        # 두 번의 CPU 작업 순차 실행
        self.cpu_bound_task(self.task_size)
        self.cpu_bound_task(self.task_size)
        
        duration = time.perf_counter() - start
        result = BenchmarkResult("단일 스레드", duration)
        self.results.append(result)
        return result
    
    def benchmark_multi_thread(self) -> BenchmarkResult:
        """멀티 스레드 벤치마크"""
        print("\n🔹 멀티 스레드 테스트...")
        start = time.perf_counter()
        
        threads = []
        for _ in range(2):
            t = threading.Thread(
                target=self.cpu_bound_task, 
                args=(self.task_size,)
            )
            t.start()
            threads.append(t)
        
        for t in threads:
            t.join()
        
        duration = time.perf_counter() - start
        speedup = self.results[0].duration / duration if self.results else 1.0
        result = BenchmarkResult("멀티 스레드", duration, speedup)
        self.results.append(result)
        return result
    
    def benchmark_multi_process(self) -> BenchmarkResult:
        """멀티 프로세스 벤치마크"""
        print("\n🔹 멀티 프로세스 테스트...")
        start = time.perf_counter()
        
        with multiprocessing.Pool(2) as pool:
            pool.map(self.cpu_bound_task, [self.task_size, self.task_size])
        
        duration = time.perf_counter() - start
        speedup = self.results[0].duration / duration if self.results else 1.0
        result = BenchmarkResult("멀티 프로세스", duration, speedup)
        self.results.append(result)
        return result
    
    def benchmark_thread_pool(self) -> BenchmarkResult:
        """스레드 풀 벤치마크"""
        print("\n🔹 스레드 풀 테스트...")
        start = time.perf_counter()
        
        with concurrent.futures.ThreadPoolExecutor(max_workers=2) as executor:
            futures = [
                executor.submit(self.cpu_bound_task, self.task_size)
                for _ in range(2)
            ]
            concurrent.futures.wait(futures)
        
        duration = time.perf_counter() - start
        speedup = self.results[0].duration / duration if self.results else 1.0
        result = BenchmarkResult("스레드 풀", duration, speedup)
        self.results.append(result)
        return result
    
    def benchmark_process_pool(self) -> BenchmarkResult:
        """프로세스 풀 벤치마크"""
        print("\n🔹 프로세스 풀 테스트...")
        start = time.perf_counter()
        
        with concurrent.futures.ProcessPoolExecutor(max_workers=2) as executor:
            futures = [
                executor.submit(self.cpu_bound_task, self.task_size)
                for _ in range(2)
            ]
            concurrent.futures.wait(futures)
        
        duration = time.perf_counter() - start
        speedup = self.results[0].duration / duration if self.results else 1.0
        result = BenchmarkResult("프로세스 풀", duration, speedup)
        self.results.append(result)
        return result
    
    async def benchmark_async_io(self) -> BenchmarkResult:
        """비동기 I/O 벤치마크"""
        print("\n🔹 비동기 I/O 테스트...")
        
        urls = [
            "https://httpbin.org/delay/1",
            "https://httpbin.org/delay/1",
            "https://httpbin.org/delay/1",
            "https://httpbin.org/delay/1",
        ]
        
        # 동기 방식
        print("  - 동기 방식 테스트...")
        start = time.perf_counter()
        for _ in urls:
            self.io_bound_task(1.0)
        sync_duration = time.perf_counter() - start
        
        # 비동기 방식
        print("  - 비동기 방식 테스트...")
        start = time.perf_counter()
        tasks = [self.async_io_task(url) for url in urls]
        await asyncio.gather(*tasks)
        async_duration = time.perf_counter() - start
        
        speedup = sync_duration / async_duration
        result = BenchmarkResult(
            f"비동기 I/O ({len(urls)}개 요청)", 
            async_duration, 
            speedup
        )
        return result
    
    def run_all_benchmarks(self) -> None:
        """모든 벤치마크 실행"""
        print(f"\n🚀 GIL 벤치마크 시작 (작업 크기: {self.task_size:,})")
        print("=" * 60)
        
        # CPU 집약적 작업 벤치마크
        self.benchmark_single_thread()
        self.benchmark_multi_thread()
        self.benchmark_multi_process()
        self.benchmark_thread_pool()
        self.benchmark_process_pool()
        
        # 결과 출력
        self.print_results()
    
    def print_results(self) -> None:
        """결과 출력"""
        print("\n📊 벤치마크 결과")
        print("=" * 60)
        
        baseline = self.results[0].duration if self.results else 1.0
        
        for result in self.results:
            speedup_bar = "█" * int(result.speedup * 10)
            print(f"{result.name:15} | {result.duration:6.2f}초 | "
                  f"속도향상: {result.speedup:4.2f}x {speedup_bar}")
        
        print("\n💡 GIL 영향 분석:")
        
        # GIL 영향 계산
        thread_result = next((r for r in self.results if "멀티 스레드" in r.name), None)
        process_result = next((r for r in self.results if "멀티 프로세스" in r.name), None)
        
        if thread_result and process_result:
            gil_impact = (thread_result.duration - process_result.duration) / thread_result.duration * 100
            print(f"- GIL로 인한 성능 저하: {gil_impact:.1f}%")
            print(f"- 멀티프로세싱 효율: {process_result.speedup:.1f}x")
            
            if gil_impact > 50:
                print("- 권장사항: CPU 집약적 작업에는 multiprocessing 사용")
            else:
                print("- 권장사항: I/O 집약적 작업에는 threading 또는 asyncio 사용")
    
    def save_results(self, filename: str = "gil_benchmark_results.json") -> None:
        """결과를 JSON 파일로 저장"""
        data = {
            "task_size": self.task_size,
            "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
            "results": [
                {
                    "name": r.name,
                    "duration": r.duration,
                    "speedup": r.speedup
                }
                for r in self.results
            ]
        }
        
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
        
        print(f"\n💾 결과가 {filename}에 저장되었습니다.")


def measure_gil_impact(task_size: int = 5_000_000) -> dict:
    """GIL 영향 측정 함수"""
    demo = GILDemo(task_size)
    demo.run_all_benchmarks()
    
    # 결과 반환
    return {
        result.name: {
            "duration": result.duration,
            "speedup": result.speedup
        }
        for result in demo.results
    }


def demonstrate_gil_with_io():
    """I/O 작업에서의 GIL 영향 데모"""
    print("\n🌐 I/O 작업에서의 GIL 영향 데모")
    print("=" * 60)
    
    def io_task(n: int) -> str:
        """I/O 시뮬레이션"""
        time.sleep(0.1)  # I/O 대기 시뮬레이션
        return f"Task {n} completed"
    
    # 순차 실행
    print("\n1. 순차 실행 (4개 작업):")
    start = time.perf_counter()
    for i in range(4):
        io_task(i)
    sequential_time = time.perf_counter() - start
    print(f"   소요 시간: {sequential_time:.2f}초")
    
    # 스레드 실행
    print("\n2. 스레드 실행 (4개 작업):")
    start = time.perf_counter()
    with concurrent.futures.ThreadPoolExecutor(max_workers=4) as executor:
        futures = [executor.submit(io_task, i) for i in range(4)]
        concurrent.futures.wait(futures)
    threaded_time = time.perf_counter() - start
    print(f"   소요 시간: {threaded_time:.2f}초")
    print(f"   속도 향상: {sequential_time / threaded_time:.2f}x")
    
    print("\n💡 결론: I/O 작업에서는 GIL이 해제되어 멀티스레딩이 효과적입니다!")


if __name__ == "__main__":
    # GIL 영향 측정
    print("🔬 Python GIL(Global Interpreter Lock) 데모")
    print("=" * 60)
    
    # CPU 집약적 작업에서의 GIL 영향
    results = measure_gil_impact()
    
    # I/O 작업에서의 GIL 영향
    demonstrate_gil_with_io()
    
    # 비동기 I/O 데모
    print("\n🔄 비동기 I/O 데모")
    async def async_demo():
        demo = GILDemo()
        result = await demo.benchmark_async_io()
        print(f"\n{result}")
    
    asyncio.run(async_demo())