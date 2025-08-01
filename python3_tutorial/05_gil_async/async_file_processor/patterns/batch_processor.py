"""
배치 처리 패턴
대량의 데이터를 효율적으로 처리하기 위한 패턴
"""

import asyncio
import time
from typing import List, Any, Callable, Optional, TypeVar, Generic, Union
from dataclasses import dataclass, field
from collections import defaultdict
import logging
from concurrent.futures import ProcessPoolExecutor, ThreadPoolExecutor


T = TypeVar('T')
R = TypeVar('R')


@dataclass
class BatchResult(Generic[T, R]):
    """배치 처리 결과"""
    batch_id: int
    items: List[T]
    results: Optional[List[R]] = None
    error: Optional[str] = None
    start_time: float = 0
    end_time: float = 0
    
    @property
    def duration(self) -> float:
        return self.end_time - self.start_time
    
    @property
    def success(self) -> bool:
        return self.error is None
    
    @property
    def items_per_second(self) -> float:
        if self.duration > 0:
            return len(self.items) / self.duration
        return 0


class BatchProcessor(Generic[T, R]):
    """동기 배치 처리기"""
    
    def __init__(
        self,
        batch_size: int = 100,
        max_workers: Optional[int] = None,
        use_processes: bool = False
    ):
        self.batch_size = batch_size
        self.max_workers = max_workers
        self.use_processes = use_processes
        self.results: List[BatchResult[T, R]] = []
        self._batch_counter = 0
    
    def process(
        self,
        items: List[T],
        processor: Callable[[List[T]], List[R]],
        parallel: bool = True
    ) -> List[BatchResult[T, R]]:
        """아이템들을 배치로 처리"""
        batches = self._create_batches(items)
        results = []
        
        if parallel and len(batches) > 1:
            # 병렬 처리
            Executor = ProcessPoolExecutor if self.use_processes else ThreadPoolExecutor
            
            with Executor(max_workers=self.max_workers) as executor:
                futures = []
                
                for batch in batches:
                    self._batch_counter += 1
                    batch_result = BatchResult(
                        batch_id=self._batch_counter,
                        items=batch,
                        start_time=time.time()
                    )
                    
                    future = executor.submit(self._process_batch, batch, processor)
                    futures.append((future, batch_result))
                
                # 결과 수집
                for future, batch_result in futures:
                    try:
                        batch_result.results = future.result()
                        batch_result.end_time = time.time()
                    except Exception as e:
                        batch_result.error = str(e)
                        batch_result.end_time = time.time()
                    
                    results.append(batch_result)
                    self.results.append(batch_result)
        else:
            # 순차 처리
            for batch in batches:
                self._batch_counter += 1
                batch_result = self._process_batch_with_result(batch, processor)
                results.append(batch_result)
                self.results.append(batch_result)
        
        return results
    
    def _create_batches(self, items: List[T]) -> List[List[T]]:
        """아이템들을 배치로 분할"""
        batches = []
        for i in range(0, len(items), self.batch_size):
            batch = items[i:i + self.batch_size]
            batches.append(batch)
        return batches
    
    def _process_batch(self, batch: List[T], processor: Callable[[List[T]], List[R]]) -> List[R]:
        """단일 배치 처리"""
        return processor(batch)
    
    def _process_batch_with_result(
        self,
        batch: List[T],
        processor: Callable[[List[T]], List[R]]
    ) -> BatchResult[T, R]:
        """배치 처리 및 결과 생성"""
        batch_result = BatchResult(
            batch_id=self._batch_counter,
            items=batch,
            start_time=time.time()
        )
        
        try:
            batch_result.results = processor(batch)
        except Exception as e:
            batch_result.error = str(e)
        finally:
            batch_result.end_time = time.time()
        
        return batch_result
    
    def get_statistics(self) -> dict:
        """처리 통계"""
        if not self.results:
            return {}
        
        successful = [r for r in self.results if r.success]
        failed = [r for r in self.results if not r.success]
        
        total_items = sum(len(r.items) for r in self.results)
        total_duration = sum(r.duration for r in self.results)
        
        return {
            "total_batches": len(self.results),
            "successful_batches": len(successful),
            "failed_batches": len(failed),
            "total_items": total_items,
            "total_duration": total_duration,
            "average_batch_duration": total_duration / len(self.results),
            "items_per_second": total_items / total_duration if total_duration > 0 else 0,
            "batch_size": self.batch_size
        }


class AsyncBatchProcessor(Generic[T, R]):
    """비동기 배치 처리기"""
    
    def __init__(
        self,
        batch_size: int = 100,
        max_concurrent_batches: int = 10,
        batch_timeout: Optional[float] = None,
        auto_flush_interval: Optional[float] = None
    ):
        self.batch_size = batch_size
        self.max_concurrent_batches = max_concurrent_batches
        self.batch_timeout = batch_timeout
        self.auto_flush_interval = auto_flush_interval
        
        self.current_batch: List[T] = []
        self.batch_lock = asyncio.Lock()
        self.semaphore = asyncio.Semaphore(max_concurrent_batches)
        self.results: List[BatchResult[T, R]] = []
        self._batch_counter = 0
        self._auto_flush_task: Optional[asyncio.Task] = None
    
    async def add(self, item: T, processor: Callable[[List[T]], List[R]]) -> Optional[BatchResult[T, R]]:
        """아이템 추가 (배치가 가득 차면 자동 처리)"""
        async with self.batch_lock:
            self.current_batch.append(item)
            
            if len(self.current_batch) >= self.batch_size:
                return await self._flush_batch(processor)
        
        return None
    
    async def add_many(
        self,
        items: List[T],
        processor: Callable[[List[T]], List[R]]
    ) -> List[BatchResult[T, R]]:
        """여러 아이템 추가"""
        results = []
        
        for item in items:
            result = await self.add(item, processor)
            if result:
                results.append(result)
        
        # 남은 아이템 처리
        if self.current_batch:
            result = await self._flush_batch(processor)
            if result:
                results.append(result)
        
        return results
    
    async def _flush_batch(self, processor: Callable[[List[T]], List[R]]) -> Optional[BatchResult[T, R]]:
        """현재 배치 처리"""
        if not self.current_batch:
            return None
        
        batch = self.current_batch.copy()
        self.current_batch.clear()
        self._batch_counter += 1
        
        # 배치 처리
        async with self.semaphore:
            batch_result = await self._process_batch_async(batch, processor)
        
        self.results.append(batch_result)
        return batch_result
    
    async def _process_batch_async(
        self,
        batch: List[T],
        processor: Callable[[List[T]], List[R]]
    ) -> BatchResult[T, R]:
        """비동기 배치 처리"""
        batch_result = BatchResult(
            batch_id=self._batch_counter,
            items=batch,
            start_time=time.time()
        )
        
        try:
            if asyncio.iscoroutinefunction(processor):
                batch_result.results = await processor(batch)
            else:
                # 동기 함수는 executor에서 실행
                loop = asyncio.get_event_loop()
                batch_result.results = await loop.run_in_executor(
                    None, processor, batch
                )
            
            if self.batch_timeout:
                # 타임아웃 적용
                batch_result.results = await asyncio.wait_for(
                    processor(batch) if asyncio.iscoroutinefunction(processor) 
                    else loop.run_in_executor(None, processor, batch),
                    timeout=self.batch_timeout
                )
        
        except asyncio.TimeoutError:
            batch_result.error = f"Batch processing timeout ({self.batch_timeout}s)"
        except Exception as e:
            batch_result.error = str(e)
        finally:
            batch_result.end_time = time.time()
        
        return batch_result
    
    async def process_stream(
        self,
        stream: asyncio.Queue,
        processor: Callable[[List[T]], List[R]]
    ) -> None:
        """스트림에서 아이템을 받아 배치 처리"""
        if self.auto_flush_interval:
            self._auto_flush_task = asyncio.create_task(
                self._auto_flush_loop(processor)
            )
        
        try:
            while True:
                try:
                    item = await asyncio.wait_for(stream.get(), timeout=1.0)
                    if item is None:  # 종료 신호
                        break
                    
                    await self.add(item, processor)
                    
                except asyncio.TimeoutError:
                    continue
            
            # 남은 배치 처리
            if self.current_batch:
                await self._flush_batch(processor)
        
        finally:
            if self._auto_flush_task:
                self._auto_flush_task.cancel()
    
    async def _auto_flush_loop(self, processor: Callable[[List[T]], List[R]]):
        """자동 플러시 루프"""
        while True:
            await asyncio.sleep(self.auto_flush_interval)
            async with self.batch_lock:
                if self.current_batch:
                    await self._flush_batch(processor)
    
    def get_statistics(self) -> dict:
        """처리 통계"""
        if not self.results:
            return {}
        
        successful = [r for r in self.results if r.success]
        failed = [r for r in self.results if not r.success]
        
        total_items = sum(len(r.items) for r in self.results)
        total_duration = sum(r.duration for r in self.results)
        
        batch_sizes = [len(r.items) for r in self.results]
        avg_batch_size = sum(batch_sizes) / len(batch_sizes) if batch_sizes else 0
        
        return {
            "total_batches": len(self.results),
            "successful_batches": len(successful),
            "failed_batches": len(failed),
            "total_items": total_items,
            "total_duration": total_duration,
            "average_batch_duration": total_duration / len(self.results) if self.results else 0,
            "average_batch_size": avg_batch_size,
            "items_per_second": total_items / total_duration if total_duration > 0 else 0,
            "configured_batch_size": self.batch_size
        }


class AdaptiveBatchProcessor(AsyncBatchProcessor[T, R]):
    """적응형 배치 처리기 - 처리 속도에 따라 배치 크기 자동 조정"""
    
    def __init__(
        self,
        initial_batch_size: int = 100,
        min_batch_size: int = 10,
        max_batch_size: int = 1000,
        target_duration: float = 1.0,
        adjustment_factor: float = 0.2
    ):
        super().__init__(batch_size=initial_batch_size)
        self.min_batch_size = min_batch_size
        self.max_batch_size = max_batch_size
        self.target_duration = target_duration
        self.adjustment_factor = adjustment_factor
        
        self.performance_history = defaultdict(list)
    
    async def _process_batch_async(
        self,
        batch: List[T],
        processor: Callable[[List[T]], List[R]]
    ) -> BatchResult[T, R]:
        """배치 처리 및 성능 기록"""
        result = await super()._process_batch_async(batch, processor)
        
        if result.success:
            # 성능 기록
            batch_size = len(batch)
            self.performance_history[batch_size].append(result.duration)
            
            # 배치 크기 조정
            self._adjust_batch_size(result)
        
        return result
    
    def _adjust_batch_size(self, result: BatchResult[T, R]):
        """처리 시간에 따라 배치 크기 조정"""
        if result.duration < self.target_duration * 0.8:
            # 처리가 너무 빠름 - 배치 크기 증가
            new_size = int(self.batch_size * (1 + self.adjustment_factor))
            self.batch_size = min(new_size, self.max_batch_size)
        
        elif result.duration > self.target_duration * 1.2:
            # 처리가 너무 느림 - 배치 크기 감소
            new_size = int(self.batch_size * (1 - self.adjustment_factor))
            self.batch_size = max(new_size, self.min_batch_size)
        
        logging.info(f"Batch size adjusted to {self.batch_size} (duration: {result.duration:.2f}s)")


async def example_batch_processing():
    """배치 처리 예제"""
    print("📦 배치 처리 패턴 예제")
    print("=" * 60)
    
    # 1. 비동기 배치 처리
    print("\n1. 비동기 배치 처리")
    
    # 처리 함수 (시뮬레이션)
    async def process_batch(items: List[int]) -> List[int]:
        await asyncio.sleep(0.1)  # 처리 시뮬레이션
        return [item * 2 for item in items]
    
    processor = AsyncBatchProcessor[int, int](
        batch_size=5,
        max_concurrent_batches=3
    )
    
    # 아이템 추가
    items = list(range(20))
    results = await processor.add_many(items, process_batch)
    
    print(f"처리된 배치 수: {len(results)}")
    for result in results:
        print(f"  배치 {result.batch_id}: {len(result.items)}개 아이템, "
              f"{result.duration:.3f}초")
    
    # 2. 스트림 처리
    print("\n2. 스트림 배치 처리")
    
    stream_processor = AsyncBatchProcessor[str, str](
        batch_size=3,
        auto_flush_interval=1.0  # 1초마다 자동 플러시
    )
    
    # 스트림 시뮬레이션
    stream_queue = asyncio.Queue()
    
    async def producer():
        for i in range(10):
            await stream_queue.put(f"Item {i}")
            await asyncio.sleep(0.3)
        await stream_queue.put(None)  # 종료 신호
    
    async def string_processor(items: List[str]) -> List[str]:
        return [f"Processed: {item}" for item in items]
    
    # 생산자와 배치 처리 동시 실행
    await asyncio.gather(
        producer(),
        stream_processor.process_stream(stream_queue, string_processor)
    )
    
    print(f"스트림 처리 완료: {len(stream_processor.results)}개 배치")
    
    # 3. 적응형 배치 처리
    print("\n3. 적응형 배치 처리")
    
    adaptive_processor = AdaptiveBatchProcessor[int, int](
        initial_batch_size=10,
        min_batch_size=5,
        max_batch_size=50,
        target_duration=0.5
    )
    
    # 가변 처리 시간 시뮬레이션
    async def variable_processor(items: List[int]) -> List[int]:
        # 아이템 수에 따라 처리 시간 증가
        process_time = len(items) * 0.05
        await asyncio.sleep(process_time)
        return [item ** 2 for item in items]
    
    # 여러 번 처리하여 적응 확인
    for round in range(5):
        items = list(range(20))
        results = await adaptive_processor.add_many(items, variable_processor)
        
        print(f"\n라운드 {round + 1}:")
        print(f"  현재 배치 크기: {adaptive_processor.batch_size}")
        print(f"  처리된 배치: {len(results)}")
        
        for result in results:
            print(f"    배치 {result.batch_id}: {len(result.items)}개, "
                  f"{result.duration:.3f}초")
    
    # 통계 출력
    print("\n📊 전체 통계:")
    stats = adaptive_processor.get_statistics()
    for key, value in stats.items():
        if isinstance(value, float):
            print(f"  {key}: {value:.2f}")
        else:
            print(f"  {key}: {value}")


def example_sync_batch_processing():
    """동기 배치 처리 예제"""
    print("\n\n⚙️  동기 배치 처리 예제")
    print("=" * 60)
    
    # 처리 함수
    def cpu_intensive_processor(items: List[int]) -> List[int]:
        # CPU 집약적 작업 시뮬레이션
        results = []
        for item in items:
            result = sum(i ** 2 for i in range(item * 100))
            results.append(result)
        return results
    
    # 프로세스 기반 배치 처리
    processor = BatchProcessor[int, int](
        batch_size=10,
        max_workers=4,
        use_processes=True
    )
    
    # 데이터 처리
    data = list(range(50))
    results = processor.process(data, cpu_intensive_processor, parallel=True)
    
    print(f"처리 완료: {len(results)}개 배치")
    
    # 통계
    stats = processor.get_statistics()
    print("\n📊 처리 통계:")
    for key, value in stats.items():
        if isinstance(value, float):
            print(f"  {key}: {value:.2f}")
        else:
            print(f"  {key}: {value}")


if __name__ == "__main__":
    # 비동기 예제
    asyncio.run(example_batch_processing())
    
    # 동기 예제
    example_sync_batch_processing()