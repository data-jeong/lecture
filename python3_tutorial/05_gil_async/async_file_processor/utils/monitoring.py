"""
모니터링 유틸리티
실시간 성능 모니터링과 리소스 추적
"""

import time
import psutil
import threading
import asyncio
from typing import Dict, List, Optional, Callable, Any
from dataclasses import dataclass, field
from datetime import datetime
from collections import deque
import json


@dataclass
class ResourceSnapshot:
    """리소스 스냅샷"""
    timestamp: float
    cpu_percent: float
    memory_mb: float
    memory_percent: float
    disk_read_mb: float
    disk_write_mb: float
    threads: int
    
    def to_dict(self) -> dict:
        return {
            "timestamp": self.timestamp,
            "cpu_percent": self.cpu_percent,
            "memory_mb": self.memory_mb,
            "memory_percent": self.memory_percent,
            "disk_read_mb": self.disk_read_mb,
            "disk_write_mb": self.disk_write_mb,
            "threads": self.threads
        }


@dataclass
class PerformanceMetrics:
    """성능 메트릭"""
    operation_name: str
    start_time: float
    end_time: Optional[float] = None
    success: bool = True
    error: Optional[str] = None
    custom_metrics: Dict[str, Any] = field(default_factory=dict)
    
    @property
    def duration(self) -> float:
        if self.end_time:
            return self.end_time - self.start_time
        return time.time() - self.start_time
    
    def to_dict(self) -> dict:
        return {
            "operation_name": self.operation_name,
            "start_time": self.start_time,
            "end_time": self.end_time,
            "duration": self.duration,
            "success": self.success,
            "error": self.error,
            "custom_metrics": self.custom_metrics
        }


class Monitor:
    """시스템 리소스 모니터"""
    
    def __init__(self, interval: float = 1.0, max_history: int = 300):
        self.interval = interval
        self.max_history = max_history
        self.process = psutil.Process()
        self.history: deque[ResourceSnapshot] = deque(maxlen=max_history)
        self.monitoring = False
        self.monitor_thread = None
        
        # 초기 디스크 I/O 카운터
        self._last_disk_io = psutil.disk_io_counters()
        self._last_time = time.time()
    
    def start(self):
        """모니터링 시작"""
        if self.monitoring:
            return
        
        self.monitoring = True
        self.monitor_thread = threading.Thread(target=self._monitor_loop)
        self.monitor_thread.daemon = True
        self.monitor_thread.start()
        print("📊 모니터링 시작")
    
    def stop(self):
        """모니터링 중지"""
        self.monitoring = False
        if self.monitor_thread:
            self.monitor_thread.join()
        print("📊 모니터링 중지")
    
    def _monitor_loop(self):
        """모니터링 루프"""
        while self.monitoring:
            try:
                snapshot = self._take_snapshot()
                self.history.append(snapshot)
                time.sleep(self.interval)
            except Exception as e:
                print(f"모니터링 오류: {e}")
    
    def _take_snapshot(self) -> ResourceSnapshot:
        """현재 리소스 스냅샷"""
        current_time = time.time()
        
        # CPU 사용률
        cpu_percent = self.process.cpu_percent(interval=None)
        
        # 메모리 사용량
        memory_info = self.process.memory_info()
        memory_mb = memory_info.rss / 1024 / 1024
        memory_percent = self.process.memory_percent()
        
        # 디스크 I/O
        disk_io = psutil.disk_io_counters()
        time_delta = current_time - self._last_time
        
        if time_delta > 0:
            disk_read_mb = (disk_io.read_bytes - self._last_disk_io.read_bytes) / 1024 / 1024 / time_delta
            disk_write_mb = (disk_io.write_bytes - self._last_disk_io.write_bytes) / 1024 / 1024 / time_delta
        else:
            disk_read_mb = 0
            disk_write_mb = 0
        
        self._last_disk_io = disk_io
        self._last_time = current_time
        
        # 스레드 수
        threads = self.process.num_threads()
        
        return ResourceSnapshot(
            timestamp=current_time,
            cpu_percent=cpu_percent,
            memory_mb=memory_mb,
            memory_percent=memory_percent,
            disk_read_mb=disk_read_mb,
            disk_write_mb=disk_write_mb,
            threads=threads
        )
    
    def get_current_stats(self) -> dict:
        """현재 통계"""
        if not self.history:
            return {}
        
        latest = self.history[-1]
        
        # 최근 10개 샘플의 평균
        recent_samples = list(self.history)[-10:]
        
        return {
            "current": {
                "cpu_percent": latest.cpu_percent,
                "memory_mb": latest.memory_mb,
                "memory_percent": latest.memory_percent,
                "threads": latest.threads
            },
            "average": {
                "cpu_percent": sum(s.cpu_percent for s in recent_samples) / len(recent_samples),
                "memory_mb": sum(s.memory_mb for s in recent_samples) / len(recent_samples),
                "disk_read_mb_s": sum(s.disk_read_mb for s in recent_samples) / len(recent_samples),
                "disk_write_mb_s": sum(s.disk_write_mb for s in recent_samples) / len(recent_samples)
            },
            "peak": {
                "cpu_percent": max(s.cpu_percent for s in self.history),
                "memory_mb": max(s.memory_mb for s in self.history)
            }
        }
    
    def save_history(self, filename: str = "monitor_history.json"):
        """히스토리 저장"""
        data = {
            "start_time": self.history[0].timestamp if self.history else None,
            "end_time": self.history[-1].timestamp if self.history else None,
            "interval": self.interval,
            "snapshots": [s.to_dict() for s in self.history]
        }
        
        with open(filename, 'w') as f:
            json.dump(data, f, indent=2)
        
        print(f"💾 모니터링 데이터가 {filename}에 저장되었습니다.")
    
    def print_summary(self):
        """요약 출력"""
        stats = self.get_current_stats()
        
        if not stats:
            print("모니터링 데이터가 없습니다.")
            return
        
        print("\n📊 리소스 사용 요약")
        print("=" * 50)
        
        print("현재 상태:")
        for key, value in stats["current"].items():
            print(f"  {key}: {value:.2f}")
        
        print("\n평균값:")
        for key, value in stats["average"].items():
            print(f"  {key}: {value:.2f}")
        
        print("\n최대값:")
        for key, value in stats["peak"].items():
            print(f"  {key}: {value:.2f}")


class PerformanceTracker:
    """성능 추적기"""
    
    def __init__(self):
        self.metrics: List[PerformanceMetrics] = []
        self.active_operations: Dict[str, PerformanceMetrics] = {}
    
    def start_operation(self, operation_name: str) -> PerformanceMetrics:
        """작업 시작"""
        metric = PerformanceMetrics(
            operation_name=operation_name,
            start_time=time.time()
        )
        self.active_operations[operation_name] = metric
        return metric
    
    def end_operation(
        self, 
        operation_name: str, 
        success: bool = True, 
        error: Optional[str] = None,
        custom_metrics: Optional[Dict[str, Any]] = None
    ) -> Optional[PerformanceMetrics]:
        """작업 종료"""
        if operation_name not in self.active_operations:
            return None
        
        metric = self.active_operations.pop(operation_name)
        metric.end_time = time.time()
        metric.success = success
        metric.error = error
        
        if custom_metrics:
            metric.custom_metrics.update(custom_metrics)
        
        self.metrics.append(metric)
        return metric
    
    def track(self, operation_name: str):
        """컨텍스트 매니저로 사용"""
        class OperationContext:
            def __init__(self, tracker, name):
                self.tracker = tracker
                self.name = name
                self.metric = None
            
            def __enter__(self):
                self.metric = self.tracker.start_operation(self.name)
                return self.metric
            
            def __exit__(self, exc_type, exc_val, exc_tb):
                success = exc_type is None
                error = str(exc_val) if exc_val else None
                self.tracker.end_operation(self.name, success, error)
        
        return OperationContext(self, operation_name)
    
    async def track_async(self, operation_name: str):
        """비동기 컨텍스트 매니저"""
        class AsyncOperationContext:
            def __init__(self, tracker, name):
                self.tracker = tracker
                self.name = name
                self.metric = None
            
            async def __aenter__(self):
                self.metric = self.tracker.start_operation(self.name)
                return self.metric
            
            async def __aexit__(self, exc_type, exc_val, exc_tb):
                success = exc_type is None
                error = str(exc_val) if exc_val else None
                self.tracker.end_operation(self.name, success, error)
        
        return AsyncOperationContext(self, operation_name)
    
    def get_statistics(self, operation_name: Optional[str] = None) -> dict:
        """통계 조회"""
        if operation_name:
            metrics = [m for m in self.metrics if m.operation_name == operation_name]
        else:
            metrics = self.metrics
        
        if not metrics:
            return {}
        
        successful = [m for m in metrics if m.success]
        failed = [m for m in metrics if not m.success]
        
        durations = [m.duration for m in successful]
        
        return {
            "total_operations": len(metrics),
            "successful": len(successful),
            "failed": len(failed),
            "success_rate": len(successful) / len(metrics) * 100,
            "average_duration": sum(durations) / len(durations) if durations else 0,
            "min_duration": min(durations) if durations else 0,
            "max_duration": max(durations) if durations else 0,
            "total_duration": sum(durations)
        }
    
    def print_report(self):
        """리포트 출력"""
        print("\n📈 성능 추적 리포트")
        print("=" * 50)
        
        # 작업별 그룹화
        operations = {}
        for metric in self.metrics:
            if metric.operation_name not in operations:
                operations[metric.operation_name] = []
            operations[metric.operation_name].append(metric)
        
        for operation_name, metrics in operations.items():
            stats = self.get_statistics(operation_name)
            
            print(f"\n{operation_name}:")
            print(f"  총 실행: {stats['total_operations']}회")
            print(f"  성공률: {stats['success_rate']:.1f}%")
            print(f"  평균 시간: {stats['average_duration']:.4f}초")
            print(f"  최소/최대: {stats['min_duration']:.4f}s / {stats['max_duration']:.4f}s")
    
    def save_report(self, filename: str = "performance_report.json"):
        """리포트 저장"""
        data = {
            "timestamp": datetime.now().isoformat(),
            "metrics": [m.to_dict() for m in self.metrics],
            "summary": self.get_statistics()
        }
        
        with open(filename, 'w') as f:
            json.dump(data, f, indent=2)
        
        print(f"💾 성능 리포트가 {filename}에 저장되었습니다.")


def example_usage():
    """사용 예제"""
    print("📊 모니터링 예제")
    print("=" * 60)
    
    # 1. 시스템 모니터링
    monitor = Monitor(interval=0.5)
    monitor.start()
    
    # 2. 성능 추적
    tracker = PerformanceTracker()
    
    # CPU 집약적 작업 시뮬레이션
    print("\n🔥 CPU 집약적 작업 실행중...")
    
    with tracker.track("CPU Intensive Task"):
        # CPU 작업 시뮬레이션
        result = 0
        for i in range(10_000_000):
            result += i ** 2
    
    # 메모리 집약적 작업
    print("💾 메모리 집약적 작업 실행중...")
    
    with tracker.track("Memory Intensive Task"):
        # 메모리 할당
        data = [i for i in range(1_000_000)]
        
    # I/O 작업
    print("📂 I/O 작업 실행중...")
    
    with tracker.track("I/O Task"):
        time.sleep(1)  # I/O 대기 시뮬레이션
    
    # 잠시 대기
    time.sleep(2)
    
    # 모니터링 중지
    monitor.stop()
    
    # 결과 출력
    print("\n" + "=" * 60)
    monitor.print_summary()
    tracker.print_report()
    
    # 비동기 예제
    async def async_example():
        print("\n\n🔄 비동기 작업 추적 예제")
        print("=" * 60)
        
        async_tracker = PerformanceTracker()
        
        async with async_tracker.track_async("Async Task 1"):
            await asyncio.sleep(0.5)
        
        async with async_tracker.track_async("Async Task 2"):
            await asyncio.sleep(0.3)
        
        async_tracker.print_report()
    
    # 비동기 예제 실행
    asyncio.run(async_example())


if __name__ == "__main__":
    example_usage()