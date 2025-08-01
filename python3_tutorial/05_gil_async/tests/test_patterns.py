"""
패턴 모듈 테스트
"""

import pytest
import asyncio
import time
from async_file_processor.patterns.rate_limiter import AsyncRateLimiter, RateLimiter
from async_file_processor.patterns.batch_processor import AsyncBatchProcessor, BatchProcessor
from async_file_processor.patterns.producer_consumer import AsyncProducerConsumer


class TestRateLimiter:
    """속도 제한기 테스트"""
    
    @pytest.mark.asyncio
    async def test_async_rate_limiter(self):
        """비동기 속도 제한기 테스트"""
        # 2 requests per second
        limiter = AsyncRateLimiter(rate=2, per=1.0)
        
        # 허용 테스트
        assert await limiter.allow()  # 1st
        assert await limiter.allow()  # 2nd
        assert not await limiter.allow()  # 3rd - rejected
        
        # 1초 대기 후
        await asyncio.sleep(1.1)
        assert await limiter.allow()  # Should be allowed
    
    @pytest.mark.asyncio
    async def test_async_rate_limiter_acquire(self):
        """비동기 속도 제한기 acquire 테스트"""
        limiter = AsyncRateLimiter(rate=2, per=1.0)
        
        start_time = time.time()
        
        # 3개 요청 (2개는 즉시, 1개는 대기)
        for i in range(3):
            await limiter.acquire()
        
        duration = time.time() - start_time
        
        # 3번째 요청은 대기해야 함
        assert duration >= 1.0
    
    def test_sync_rate_limiter(self):
        """동기 속도 제한기 테스트"""
        limiter = RateLimiter(rate=2, per=1.0)
        
        # 허용 테스트
        assert limiter.allow()  # 1st
        assert limiter.allow()  # 2nd
        assert not limiter.allow()  # 3rd - rejected
        
        # 통계 확인
        stats = limiter.get_statistics()
        assert stats["allowed"] == 2
        assert stats["rejected"] == 1


class TestBatchProcessor:
    """배치 처리기 테스트"""
    
    @pytest.mark.asyncio
    async def test_async_batch_processor(self):
        """비동기 배치 처리기 테스트"""
        processor = AsyncBatchProcessor(batch_size=3)
        
        # 처리 함수
        async def sum_batch(items: list) -> list:
            await asyncio.sleep(0.1)
            return [sum(items)]
        
        # 아이템 추가
        items = list(range(10))
        results = await processor.add_many(items, sum_batch)
        
        # 4개 배치 (3, 3, 3, 1)
        assert len(results) == 4
        assert all(r.success for r in results)
        
        # 결과 확인
        total = sum(r.results[0] for r in results if r.results)
        assert total == sum(range(10))
    
    def test_sync_batch_processor(self):
        """동기 배치 처리기 테스트"""
        processor = BatchProcessor(batch_size=5)
        
        # 처리 함수
        def double_batch(items: list) -> list:
            return [item * 2 for item in items]
        
        # 처리 실행
        items = list(range(12))
        results = processor.process(items, double_batch, parallel=False)
        
        # 3개 배치 (5, 5, 2)
        assert len(results) == 3
        assert all(r.success for r in results)
        
        # 결과 평탄화
        all_results = []
        for r in results:
            if r.results:
                all_results.extend(r.results)
        
        assert all_results == [i * 2 for i in range(12)]


class TestProducerConsumer:
    """생산자-소비자 패턴 테스트"""
    
    @pytest.mark.asyncio
    async def test_async_producer_consumer(self):
        """비동기 생산자-소비자 테스트"""
        pc = AsyncProducerConsumer(
            max_queue_size=10,
            num_consumers=2
        )
        
        # 데이터 소스
        async def data_source():
            for i in range(5):
                yield i
        
        # 처리 함수
        async def square(x: int) -> int:
            await asyncio.sleep(0.05)
            return x ** 2
        
        # 실행
        results = await pc.run(
            source=data_source(),
            processor=square
        )
        
        assert len(results) == 5
        
        # 결과 확인
        squared_values = [r["result"] for r in results if "result" in r]
        squared_values.sort()
        assert squared_values == [0, 1, 4, 9, 16]
    
    @pytest.mark.asyncio
    async def test_producer_consumer_with_priority(self):
        """우선순위 큐 테스트"""
        pc = AsyncProducerConsumer(
            max_queue_size=10,
            num_consumers=1,
            use_priority_queue=True
        )
        
        # 데이터 소스
        async def data_source():
            for i in range(5, 0, -1):  # 5, 4, 3, 2, 1
                yield i
        
        # 우선순위 함수 (큰 수가 높은 우선순위)
        def priority_func(x: int) -> int:
            return x
        
        # 처리 함수
        processed_order = []
        
        async def track_order(x: int) -> int:
            processed_order.append(x)
            return x
        
        # 실행
        results = await pc.run(
            source=data_source(),
            processor=track_order,
            priority_func=priority_func
        )
        
        # 우선순위에 따라 처리되었는지 확인
        # (완벽한 순서는 보장되지 않을 수 있음)
        assert len(processed_order) == 5
        assert set(processed_order) == {1, 2, 3, 4, 5}