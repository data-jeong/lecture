"""
생산자-소비자 패턴
비동기 작업 처리를 위한 효율적인 패턴
"""

import asyncio
import threading
import queue
from typing import Any, Callable, Optional, List, AsyncIterator, TypeVar, Generic
from dataclasses import dataclass
import time
import logging


T = TypeVar('T')
R = TypeVar('R')


@dataclass
class WorkItem(Generic[T]):
    """작업 아이템"""
    id: int
    data: T
    priority: int = 0
    timestamp: float = None
    
    def __post_init__(self):
        if self.timestamp is None:
            self.timestamp = time.time()
    
    def __lt__(self, other):
        # 우선순위 큐를 위한 비교
        return self.priority > other.priority


class AsyncProducerConsumer(Generic[T, R]):
    """비동기 생산자-소비자 패턴"""
    
    def __init__(
        self, 
        max_queue_size: int = 100,
        num_consumers: int = 5,
        use_priority_queue: bool = False
    ):
        self.max_queue_size = max_queue_size
        self.num_consumers = num_consumers
        
        if use_priority_queue:
            self.queue: asyncio.Queue = asyncio.PriorityQueue(maxsize=max_queue_size)
        else:
            self.queue: asyncio.Queue = asyncio.Queue(maxsize=max_queue_size)
        
        self.results_queue: asyncio.Queue = asyncio.Queue()
        self.running = False
        self.stats = {
            "produced": 0,
            "consumed": 0,
            "errors": 0,
            "total_wait_time": 0
        }
        self._item_counter = 0
    
    async def producer(
        self, 
        source: AsyncIterator[T],
        priority_func: Optional[Callable[[T], int]] = None
    ):
        """생산자 - 데이터를 큐에 추가"""
        try:
            async for item in source:
                self._item_counter += 1
                
                priority = priority_func(item) if priority_func else 0
                work_item = WorkItem(
                    id=self._item_counter,
                    data=item,
                    priority=priority
                )
                
                await self.queue.put(work_item)
                self.stats["produced"] += 1
                
                # 백프레셔 처리
                if self.queue.qsize() >= self.max_queue_size * 0.8:
                    await asyncio.sleep(0.1)
        
        finally:
            # 종료 신호
            for _ in range(self.num_consumers):
                await self.queue.put(None)
    
    async def consumer(
        self,
        processor: Callable[[T], R],
        consumer_id: int
    ):
        """소비자 - 큐에서 데이터를 가져와 처리"""
        while self.running:
            try:
                work_item = await self.queue.get()
                
                if work_item is None:  # 종료 신호
                    break
                
                # 대기 시간 계산
                wait_time = time.time() - work_item.timestamp
                self.stats["total_wait_time"] += wait_time
                
                # 처리
                start_time = time.time()
                
                if asyncio.iscoroutinefunction(processor):
                    result = await processor(work_item.data)
                else:
                    # 동기 함수는 executor에서 실행
                    loop = asyncio.get_event_loop()
                    result = await loop.run_in_executor(None, processor, work_item.data)
                
                process_time = time.time() - start_time
                
                # 결과 저장
                await self.results_queue.put({
                    "work_item_id": work_item.id,
                    "consumer_id": consumer_id,
                    "result": result,
                    "wait_time": wait_time,
                    "process_time": process_time
                })
                
                self.stats["consumed"] += 1
                self.queue.task_done()
                
            except Exception as e:
                self.stats["errors"] += 1
                logging.error(f"Consumer {consumer_id} error: {e}")
                
                if 'work_item' in locals() and work_item is not None:
                    await self.results_queue.put({
                        "work_item_id": work_item.id,
                        "consumer_id": consumer_id,
                        "error": str(e)
                    })
    
    async def run(
        self,
        source: AsyncIterator[T],
        processor: Callable[[T], R],
        priority_func: Optional[Callable[[T], int]] = None
    ) -> List[dict]:
        """생산자-소비자 실행"""
        self.running = True
        
        # 생산자 태스크
        producer_task = asyncio.create_task(
            self.producer(source, priority_func)
        )
        
        # 소비자 태스크들
        consumer_tasks = [
            asyncio.create_task(
                self.consumer(processor, i)
            )
            for i in range(self.num_consumers)
        ]
        
        # 생산자 완료 대기
        await producer_task
        
        # 모든 소비자 완료 대기
        await asyncio.gather(*consumer_tasks)
        
        self.running = False
        
        # 결과 수집
        results = []
        while not self.results_queue.empty():
            results.append(await self.results_queue.get())
        
        return results
    
    def get_statistics(self) -> dict:
        """통계 반환"""
        avg_wait_time = (
            self.stats["total_wait_time"] / self.stats["consumed"]
            if self.stats["consumed"] > 0 else 0
        )
        
        return {
            "produced": self.stats["produced"],
            "consumed": self.stats["consumed"],
            "errors": self.stats["errors"],
            "pending": self.queue.qsize(),
            "average_wait_time": avg_wait_time,
            "error_rate": (
                self.stats["errors"] / self.stats["consumed"] * 100
                if self.stats["consumed"] > 0 else 0
            )
        }


class ProducerConsumerPool:
    """스레드 기반 생산자-소비자 풀"""
    
    def __init__(
        self,
        num_producers: int = 2,
        num_consumers: int = 5,
        max_queue_size: int = 100
    ):
        self.num_producers = num_producers
        self.num_consumers = num_consumers
        self.work_queue = queue.Queue(maxsize=max_queue_size)
        self.results_queue = queue.Queue()
        self.running = False
        self.threads = []
    
    def producer_worker(
        self,
        producer_func: Callable[[], Optional[Any]],
        producer_id: int
    ):
        """생산자 워커"""
        while self.running:
            try:
                item = producer_func()
                if item is None:
                    break
                
                self.work_queue.put({
                    "producer_id": producer_id,
                    "data": item,
                    "timestamp": time.time()
                })
                
            except Exception as e:
                logging.error(f"Producer {producer_id} error: {e}")
        
        # 종료 신호
        self.work_queue.put(None)
    
    def consumer_worker(
        self,
        processor_func: Callable[[Any], Any],
        consumer_id: int
    ):
        """소비자 워커"""
        while True:
            try:
                item = self.work_queue.get()
                
                if item is None:  # 종료 신호
                    # 다른 소비자를 위해 다시 넣기
                    self.work_queue.put(None)
                    break
                
                # 처리
                start_time = time.time()
                result = processor_func(item["data"])
                process_time = time.time() - start_time
                
                # 결과 저장
                self.results_queue.put({
                    "consumer_id": consumer_id,
                    "producer_id": item["producer_id"],
                    "result": result,
                    "process_time": process_time,
                    "wait_time": start_time - item["timestamp"]
                })
                
                self.work_queue.task_done()
                
            except Exception as e:
                logging.error(f"Consumer {consumer_id} error: {e}")
                self.results_queue.put({
                    "consumer_id": consumer_id,
                    "error": str(e)
                })
    
    def start(
        self,
        producer_func: Callable[[], Optional[Any]],
        processor_func: Callable[[Any], Any]
    ):
        """풀 시작"""
        self.running = True
        
        # 생산자 스레드 시작
        for i in range(self.num_producers):
            t = threading.Thread(
                target=self.producer_worker,
                args=(producer_func, i)
            )
            t.start()
            self.threads.append(t)
        
        # 소비자 스레드 시작
        for i in range(self.num_consumers):
            t = threading.Thread(
                target=self.consumer_worker,
                args=(processor_func, i)
            )
            t.start()
            self.threads.append(t)
    
    def stop(self) -> List[dict]:
        """풀 중지 및 결과 반환"""
        self.running = False
        
        # 모든 스레드 종료 대기
        for t in self.threads:
            t.join()
        
        # 결과 수집
        results = []
        while not self.results_queue.empty():
            results.append(self.results_queue.get())
        
        return results


async def example_async_producer_consumer():
    """비동기 생산자-소비자 예제"""
    print("🔄 비동기 생산자-소비자 패턴 예제")
    print("=" * 60)
    
    # 데이터 소스 (비동기 제너레이터)
    async def data_source():
        for i in range(20):
            await asyncio.sleep(0.1)  # 데이터 생성 시뮬레이션
            yield f"Item {i+1}"
    
    # 처리 함수
    async def process_item(item: str) -> str:
        await asyncio.sleep(0.2)  # 처리 시뮬레이션
        return f"Processed: {item}"
    
    # 우선순위 함수 (짝수 아이템 우선)
    def priority_func(item: str) -> int:
        num = int(item.split()[-1])
        return 10 if num % 2 == 0 else 1
    
    # 생산자-소비자 실행
    pc = AsyncProducerConsumer[str, str](
        max_queue_size=10,
        num_consumers=3,
        use_priority_queue=True
    )
    
    results = await pc.run(
        source=data_source(),
        processor=process_item,
        priority_func=priority_func
    )
    
    # 결과 출력
    print(f"\n처리 완료: {len(results)}개 아이템")
    
    # 통계 출력
    stats = pc.get_statistics()
    print("\n📊 통계:")
    for key, value in stats.items():
        print(f"  {key}: {value:.2f}")
    
    # 처리 순서 확인 (우선순위 큐 효과)
    print("\n처리 순서 (처음 10개):")
    for r in results[:10]:
        if "result" in r:
            print(f"  Consumer {r['consumer_id']}: {r['result']}")


def example_thread_producer_consumer():
    """스레드 기반 생산자-소비자 예제"""
    print("\n\n🧵 스레드 기반 생산자-소비자 패턴 예제")
    print("=" * 60)
    
    counter = [0]
    
    # 생산자 함수
    def producer():
        if counter[0] < 15:
            counter[0] += 1
            time.sleep(0.1)  # 생산 시뮬레이션
            return f"Task {counter[0]}"
        return None
    
    # 처리 함수
    def processor(task):
        time.sleep(0.2)  # 처리 시뮬레이션
        return f"Completed: {task}"
    
    # 풀 생성 및 실행
    pool = ProducerConsumerPool(
        num_producers=2,
        num_consumers=4,
        max_queue_size=10
    )
    
    pool.start(producer, processor)
    
    # 진행 상황 모니터링
    for _ in range(5):
        time.sleep(1)
        print(f"큐 크기: {pool.work_queue.qsize()}")
    
    # 종료 및 결과 수집
    results = pool.stop()
    
    print(f"\n처리 완료: {len(results)}개 작업")
    
    # 소비자별 통계
    consumer_stats = {}
    for r in results:
        if "error" not in r:
            cid = r["consumer_id"]
            if cid not in consumer_stats:
                consumer_stats[cid] = {"count": 0, "total_time": 0}
            consumer_stats[cid]["count"] += 1
            consumer_stats[cid]["total_time"] += r["process_time"]
    
    print("\n소비자별 통계:")
    for cid, stats in consumer_stats.items():
        avg_time = stats["total_time"] / stats["count"] if stats["count"] > 0 else 0
        print(f"  Consumer {cid}: {stats['count']}개 처리, 평균 {avg_time:.3f}초")


if __name__ == "__main__":
    # 비동기 예제 실행
    asyncio.run(example_async_producer_consumer())
    
    # 스레드 예제 실행
    example_thread_producer_consumer()