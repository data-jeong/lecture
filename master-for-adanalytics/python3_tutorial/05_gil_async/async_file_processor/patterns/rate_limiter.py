"""
속도 제한 (Rate Limiting) 패턴
API 호출이나 리소스 접근을 제한하는 패턴
"""

import asyncio
import time
import threading
from typing import Optional, Callable, Any
from dataclasses import dataclass, field
from collections import deque
import functools


class TokenBucket:
    """토큰 버킷 알고리즘 구현"""
    
    def __init__(self, capacity: int, refill_rate: float):
        """
        Args:
            capacity: 버킷 용량 (최대 토큰 수)
            refill_rate: 초당 토큰 충전 속도
        """
        self.capacity = capacity
        self.refill_rate = refill_rate
        self.tokens = capacity
        self.last_refill = time.time()
        self.lock = threading.Lock()
    
    def _refill(self):
        """토큰 충전"""
        now = time.time()
        elapsed = now - self.last_refill
        
        # 경과 시간만큼 토큰 추가
        tokens_to_add = elapsed * self.refill_rate
        self.tokens = min(self.capacity, self.tokens + tokens_to_add)
        self.last_refill = now
    
    def consume(self, tokens: int = 1) -> bool:
        """토큰 소비"""
        with self.lock:
            self._refill()
            
            if self.tokens >= tokens:
                self.tokens -= tokens
                return True
            return False
    
    def wait_for_tokens(self, tokens: int = 1) -> float:
        """토큰이 충분할 때까지 대기 시간 계산"""
        with self.lock:
            self._refill()
            
            if self.tokens >= tokens:
                return 0
            
            # 필요한 토큰까지 대기 시간 계산
            needed = tokens - self.tokens
            wait_time = needed / self.refill_rate
            return wait_time


class RateLimiter:
    """동기 속도 제한기"""
    
    def __init__(self, rate: int, per: float = 1.0):
        """
        Args:
            rate: 허용 횟수
            per: 시간 단위 (초)
        """
        self.rate = rate
        self.per = per
        self.token_bucket = TokenBucket(rate, rate / per)
        self.stats = {
            "allowed": 0,
            "rejected": 0,
            "total_wait_time": 0
        }
    
    def allow(self) -> bool:
        """요청 허용 여부"""
        allowed = self.token_bucket.consume()
        
        if allowed:
            self.stats["allowed"] += 1
        else:
            self.stats["rejected"] += 1
        
        return allowed
    
    def wait(self):
        """토큰이 사용 가능할 때까지 대기"""
        wait_time = self.token_bucket.wait_for_tokens()
        
        if wait_time > 0:
            self.stats["total_wait_time"] += wait_time
            time.sleep(wait_time)
            self.token_bucket.consume()
        
        self.stats["allowed"] += 1
    
    def __call__(self, func: Callable) -> Callable:
        """데코레이터로 사용"""
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            self.wait()
            return func(*args, **kwargs)
        return wrapper
    
    def get_statistics(self) -> dict:
        """통계 반환"""
        total = self.stats["allowed"] + self.stats["rejected"]
        
        return {
            "allowed": self.stats["allowed"],
            "rejected": self.stats["rejected"],
            "total": total,
            "rejection_rate": (
                self.stats["rejected"] / total * 100 if total > 0 else 0
            ),
            "total_wait_time": self.stats["total_wait_time"],
            "current_tokens": self.token_bucket.tokens
        }


class AsyncRateLimiter:
    """비동기 속도 제한기"""
    
    def __init__(self, rate: int, per: float = 1.0, burst: Optional[int] = None):
        """
        Args:
            rate: 허용 횟수
            per: 시간 단위 (초)
            burst: 버스트 허용량 (기본값: rate)
        """
        self.rate = rate
        self.per = per
        self.burst = burst or rate
        
        # 슬라이딩 윈도우 방식
        self.calls = deque()
        self.lock = asyncio.Lock()
        
        self.stats = {
            "allowed": 0,
            "rejected": 0,
            "total_wait_time": 0
        }
    
    async def _clean_old_calls(self):
        """오래된 호출 기록 정리"""
        now = time.time()
        cutoff = now - self.per
        
        while self.calls and self.calls[0] < cutoff:
            self.calls.popleft()
    
    async def allow(self) -> bool:
        """요청 허용 여부 (논블로킹)"""
        async with self.lock:
            await self._clean_old_calls()
            
            if len(self.calls) < self.rate:
                self.calls.append(time.time())
                self.stats["allowed"] += 1
                return True
            else:
                self.stats["rejected"] += 1
                return False
    
    async def acquire(self):
        """토큰 획득 (블로킹)"""
        while True:
            async with self.lock:
                await self._clean_old_calls()
                
                if len(self.calls) < self.rate:
                    self.calls.append(time.time())
                    self.stats["allowed"] += 1
                    return
                
                # 다음 토큰이 사용 가능할 때까지 대기
                if self.calls:
                    oldest = self.calls[0]
                    wait_time = oldest + self.per - time.time()
                    
                    if wait_time > 0:
                        self.stats["total_wait_time"] += wait_time
            
            if wait_time > 0:
                await asyncio.sleep(wait_time)
    
    def __call__(self, func: Callable) -> Callable:
        """비동기 데코레이터로 사용"""
        @functools.wraps(func)
        async def wrapper(*args, **kwargs):
            await self.acquire()
            return await func(*args, **kwargs)
        return wrapper
    
    async def get_statistics(self) -> dict:
        """통계 반환"""
        async with self.lock:
            await self._clean_old_calls()
            
            total = self.stats["allowed"] + self.stats["rejected"]
            current_rate = len(self.calls)
            
            return {
                "allowed": self.stats["allowed"],
                "rejected": self.stats["rejected"],
                "total": total,
                "rejection_rate": (
                    self.stats["rejected"] / total * 100 if total > 0 else 0
                ),
                "total_wait_time": self.stats["total_wait_time"],
                "current_rate": current_rate,
                "available": self.rate - current_rate
            }


class LeakyBucket:
    """Leaky Bucket 알고리즘"""
    
    def __init__(self, capacity: int, leak_rate: float):
        """
        Args:
            capacity: 버킷 용량
            leak_rate: 초당 누출 속도
        """
        self.capacity = capacity
        self.leak_rate = leak_rate
        self.water_level = 0
        self.last_leak = time.time()
        self.lock = asyncio.Lock()
    
    async def _leak(self):
        """물 누출 처리"""
        now = time.time()
        elapsed = now - self.last_leak
        
        # 경과 시간만큼 물 누출
        leaked = elapsed * self.leak_rate
        self.water_level = max(0, self.water_level - leaked)
        self.last_leak = now
    
    async def add(self, amount: float = 1.0) -> bool:
        """물 추가 (요청 처리)"""
        async with self.lock:
            await self._leak()
            
            if self.water_level + amount <= self.capacity:
                self.water_level += amount
                return True
            return False
    
    async def wait_time(self, amount: float = 1.0) -> float:
        """추가 가능할 때까지 대기 시간"""
        async with self.lock:
            await self._leak()
            
            if self.water_level + amount <= self.capacity:
                return 0
            
            # 필요한 공간이 생길 때까지 대기 시간
            overflow = (self.water_level + amount) - self.capacity
            wait_time = overflow / self.leak_rate
            return wait_time


async def example_rate_limiting():
    """속도 제한 예제"""
    print("🚦 속도 제한 패턴 예제")
    print("=" * 60)
    
    # 1. 비동기 속도 제한기 테스트
    print("\n1. 비동기 속도 제한기 (5회/초)")
    rate_limiter = AsyncRateLimiter(rate=5, per=1.0)
    
    # API 호출 시뮬레이션
    @rate_limiter
    async def api_call(i: int) -> str:
        return f"API call {i} completed"
    
    # 10개 요청 동시 실행
    start_time = time.time()
    tasks = [api_call(i) for i in range(10)]
    results = await asyncio.gather(*tasks)
    duration = time.time() - start_time
    
    print(f"10개 요청 완료: {duration:.2f}초")
    
    # 통계 출력
    stats = await rate_limiter.get_statistics()
    print("\n📊 통계:")
    for key, value in stats.items():
        print(f"  {key}: {value}")
    
    # 2. Leaky Bucket 테스트
    print("\n\n2. Leaky Bucket (용량: 5, 누출: 2/초)")
    bucket = LeakyBucket(capacity=5, leak_rate=2)
    
    async def process_with_bucket(i: int):
        wait = await bucket.wait_time()
        if wait > 0:
            print(f"  요청 {i}: {wait:.2f}초 대기 필요")
            await asyncio.sleep(wait)
        
        success = await bucket.add()
        return f"요청 {i}: {'성공' if success else '실패'}"
    
    # 연속 요청
    for i in range(8):
        result = await process_with_bucket(i)
        print(f"  {result}")
        await asyncio.sleep(0.2)


def example_sync_rate_limiting():
    """동기 속도 제한 예제"""
    print("\n\n⏱️  동기 속도 제한 예제")
    print("=" * 60)
    
    # 속도 제한기 생성 (3회/초)
    rate_limiter = RateLimiter(rate=3, per=1.0)
    
    # API 함수
    @rate_limiter
    def sync_api_call(i: int) -> str:
        return f"Sync API call {i} completed"
    
    print("3회/초 제한으로 6개 요청 실행:")
    start_time = time.time()
    
    for i in range(6):
        result = sync_api_call(i)
        elapsed = time.time() - start_time
        print(f"  [{elapsed:.2f}s] {result}")
    
    # 통계
    stats = rate_limiter.get_statistics()
    print("\n📊 통계:")
    for key, value in stats.items():
        print(f"  {key}: {value}")


def example_burst_handling():
    """버스트 처리 예제"""
    print("\n\n💥 버스트 처리 예제")
    print("=" * 60)
    
    async def burst_test():
        # 버스트 허용 속도 제한기
        burst_limiter = AsyncRateLimiter(rate=5, per=2.0, burst=10)
        
        print("속도: 5회/2초, 버스트: 10회")
        
        # 첫 번째 버스트 (10개 요청)
        print("\n첫 번째 버스트 (10개):")
        for i in range(10):
            allowed = await burst_limiter.allow()
            print(f"  요청 {i+1}: {'✅ 허용' if allowed else '❌ 거부'}")
        
        # 추가 요청 (거부될 것)
        print("\n추가 요청:")
        for i in range(3):
            allowed = await burst_limiter.allow()
            print(f"  요청 {i+11}: {'✅ 허용' if allowed else '❌ 거부'}")
        
        # 2초 대기 후 다시 시도
        print("\n2초 대기 후...")
        await asyncio.sleep(2)
        
        print("\n재시도:")
        for i in range(5):
            allowed = await burst_limiter.allow()
            print(f"  요청 {i+14}: {'✅ 허용' if allowed else '❌ 거부'}")
    
    asyncio.run(burst_test())


if __name__ == "__main__":
    # 비동기 예제
    asyncio.run(example_rate_limiting())
    
    # 동기 예제
    example_sync_rate_limiting()
    
    # 버스트 처리 예제
    example_burst_handling()