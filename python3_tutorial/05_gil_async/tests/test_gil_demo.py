"""
GIL 데모 테스트
"""

import pytest
import time
from async_file_processor.core.gil_demo import GILDemo, BenchmarkResult


class TestGILDemo:
    """GIL 데모 테스트"""
    
    def test_benchmark_result(self):
        """벤치마크 결과 테스트"""
        result = BenchmarkResult(
            execution_time=1.5,
            cpu_usage=75.5,
            task_type="CPU-bound"
        )
        
        assert result.execution_time == 1.5
        assert result.cpu_usage == 75.5
        assert result.task_type == "CPU-bound"
    
    def test_cpu_bound_task(self):
        """CPU 집약적 작업 테스트"""
        demo = GILDemo(task_size=1000)
        
        start_time = time.time()
        result = demo.cpu_bound_task(1000)
        duration = time.time() - start_time
        
        assert result > 0
        assert duration > 0
    
    def test_io_bound_task(self):
        """I/O 집약적 작업 테스트"""
        demo = GILDemo(task_size=10)
        
        start_time = time.time()
        result = demo.io_bound_task(0.01)
        duration = time.time() - start_time
        
        assert result == 0.01
        assert duration >= 0.01
    
    def test_benchmark_single_thread(self):
        """단일 스레드 벤치마크 테스트"""
        demo = GILDemo(task_size=100)
        
        result = demo.benchmark_single_thread()
        
        assert isinstance(result, BenchmarkResult)
        assert result.execution_time > 0
        assert result.cpu_usage >= 0
        assert result.task_type == "CPU-bound"
    
    def test_benchmark_multi_thread(self):
        """멀티 스레드 벤치마크 테스트"""
        demo = GILDemo(task_size=100)
        
        result = demo.benchmark_multi_thread()
        
        assert isinstance(result, BenchmarkResult)
        assert result.execution_time > 0
        assert result.cpu_usage >= 0
        assert result.task_type == "CPU-bound"
    
    def test_benchmark_multi_process(self):
        """멀티 프로세스 벤치마크 테스트"""
        demo = GILDemo(task_size=100)
        
        result = demo.benchmark_multi_process()
        
        assert isinstance(result, BenchmarkResult)
        assert result.execution_time > 0
        assert result.cpu_usage >= 0
        assert result.task_type == "CPU-bound"
    
    def test_benchmark_async(self):
        """비동기 벤치마크 테스트"""
        demo = GILDemo(task_size=10)
        
        result = demo.benchmark_async()
        
        assert isinstance(result, BenchmarkResult)
        assert result.execution_time > 0
        assert result.cpu_usage >= 0
        assert result.task_type == "I/O-bound"
    
    def test_comparison(self):
        """처리 방식 비교 테스트"""
        demo = GILDemo(task_size=100)
        
        # 각 방식 실행
        single_result = demo.benchmark_single_thread()
        thread_result = demo.benchmark_multi_thread()
        process_result = demo.benchmark_multi_process()
        
        # 결과 확인
        assert all(isinstance(r, BenchmarkResult) for r in [
            single_result, thread_result, process_result
        ])
        
        # CPU 집약적 작업에서는 멀티프로세스가 가장 효율적
        # (하지만 작은 작업에서는 오버헤드로 인해 그렇지 않을 수 있음)