"""
속도 제한 유틸리티
요청 속도를 제한하여 서버 부하 방지
"""

import time
import asyncio
from typing import Optional, Callable, Any
from collections import deque
import functools


class RateLimiter:
    """동기 속도 제한기"""
    
    def __init__(self, rate: int = 10, per: float = 1.0):
        """
        Args:
            rate: 허용 요청 수
            per: 시간 단위 (초)
        """
        self.rate = rate
        self.per = per
        self.allowance = rate
        self.last_check = time.time()
    
    def __call__(self, func: Callable) -> Callable:
        """데코레이터로 사용"""
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            self.wait()
            return func(*args, **kwargs)
        return wrapper
    
    def wait(self):
        """속도 제한 대기"""
        current = time.time()
        time_passed = current - self.last_check
        self.last_check = current
        
        # 시간 경과에 따른 허용량 증가
        self.allowance += time_passed * (self.rate / self.per)
        
        # 최대 허용량 제한
        if self.allowance > self.rate:
            self.allowance = self.rate
        
        # 허용량이 1 미만이면 대기
        if self.allowance < 1.0:
            sleep_time = (1.0 - self.allowance) * (self.per / self.rate)
            time.sleep(sleep_time)
            self.allowance = 0
        else:
            self.allowance -= 1


class AsyncRateLimiter:
    """비동기 속도 제한기"""
    
    def __init__(self, rate: int = 10, per: float = 1.0):
        """
        Args:
            rate: 허용 요청 수
            per: 시간 단위 (초)
        """
        self.rate = rate
        self.per = per
        self.calls = deque()
        self.lock = asyncio.Lock()
    
    def __call__(self, func: Callable) -> Callable:
        """데코레이터로 사용"""
        @functools.wraps(func)
        async def wrapper(*args, **kwargs):
            await self.acquire()
            return await func(*args, **kwargs)
        return wrapper
    
    async def acquire(self):
        """토큰 획득 (대기)"""
        async with self.lock:
            now = time.time()
            
            # 오래된 호출 기록 제거
            cutoff = now - self.per
            while self.calls and self.calls[0] < cutoff:
                self.calls.popleft()
            
            # 현재 호출 수가 제한에 도달했으면 대기
            if len(self.calls) >= self.rate:
                sleep_time = self.calls[0] + self.per - now
                if sleep_time > 0:
                    await asyncio.sleep(sleep_time)
                    # 대기 후 다시 확인
                    return await self.acquire()
            
            # 호출 기록
            self.calls.append(now)


class TokenBucketLimiter:
    """토큰 버킷 알고리즘 기반 속도 제한기"""
    
    def __init__(self, capacity: int = 10, refill_rate: float = 1.0):
        """
        Args:
            capacity: 버킷 용량 (최대 토큰 수)
            refill_rate: 초당 토큰 충전 속도
        """
        self.capacity = capacity
        self.refill_rate = refill_rate
        self.tokens = capacity
        self.last_refill = time.time()
    
    def consume(self, tokens: int = 1) -> bool:
        """토큰 소비 시도"""
        self._refill()
        
        if self.tokens >= tokens:
            self.tokens -= tokens
            return True
        return False
    
    def wait_and_consume(self, tokens: int = 1):
        """토큰이 충분할 때까지 대기 후 소비"""
        while not self.consume(tokens):
            # 필요한 토큰이 생길 때까지 대기
            needed = tokens - self.tokens
            wait_time = needed / self.refill_rate
            time.sleep(wait_time)
    
    def _refill(self):
        """토큰 충전"""
        now = time.time()
        elapsed = now - self.last_refill
        
        # 경과 시간만큼 토큰 추가
        tokens_to_add = elapsed * self.refill_rate
        self.tokens = min(self.capacity, self.tokens + tokens_to_add)
        self.last_refill = now


class SlidingWindowLimiter:
    """슬라이딩 윈도우 방식 속도 제한기"""
    
    def __init__(self, rate: int = 10, window: float = 60.0):
        """
        Args:
            rate: 윈도우 내 최대 요청 수
            window: 윈도우 크기 (초)
        """
        self.rate = rate
        self.window = window
        self.requests = deque()
    
    def allow(self) -> bool:
        """요청 허용 여부"""
        now = time.time()
        
        # 윈도우 밖 요청 제거
        cutoff = now - self.window
        while self.requests and self.requests[0] < cutoff:
            self.requests.popleft()
        
        # 현재 요청 수 확인
        if len(self.requests) < self.rate:
            self.requests.append(now)
            return True
        
        return False
    
    def wait_time(self) -> float:
        """다음 요청까지 대기 시간"""
        if len(self.requests) < self.rate:
            return 0
        
        # 가장 오래된 요청이 윈도우를 벗어날 때까지
        oldest = self.requests[0]
        now = time.time()
        wait = (oldest + self.window) - now
        
        return max(0, wait)