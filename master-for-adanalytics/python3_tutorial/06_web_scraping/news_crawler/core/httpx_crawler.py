"""
HTTPX 기반 비동기 크롤러
고성능 비동기 HTTP 클라이언트
"""

import asyncio
import httpx
from typing import List, Dict, Optional, Union
from datetime import datetime
import logging
from bs4 import BeautifulSoup

from .base_crawler import BaseCrawler, CrawlResult
from ..utils.parser import HTMLParser
from ..utils.anti_bot import AntiBot


class HttpxCrawler(BaseCrawler):
    """HTTPX 비동기 크롤러"""
    
    def __init__(self, 
                 max_connections: int = 10,
                 http2: bool = True,
                 **kwargs):
        """
        Args:
            max_connections: 최대 동시 연결 수
            http2: HTTP/2 지원 여부
        """
        super().__init__(**kwargs)
        
        self.max_connections = max_connections
        self.http2 = http2
        self.parser = HTMLParser()
        self.anti_bot = AntiBot()
        
        # 클라이언트 설정
        self.client_config = {
            'http2': http2,
            'timeout': httpx.Timeout(self.timeout),
            'limits': httpx.Limits(
                max_connections=max_connections,
                max_keepalive_connections=max_connections // 2
            ),
            'headers': {
                'User-Agent': self.user_agent,
                'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
                'Accept-Language': 'ko-KR,ko;q=0.9,en;q=0.8',
                'Accept-Encoding': 'gzip, deflate, br'
            }
        }
        
        # 프록시 설정
        if self.proxy:
            self.client_config['proxies'] = {
                'http://': self.proxy,
                'https://': self.proxy
            }
    
    def crawl(self, url: str) -> CrawlResult:
        """동기 방식으로 단일 URL 크롤링"""
        return asyncio.run(self.crawl_async(url))
    
    def crawl_multiple(self, urls: List[str]) -> List[CrawlResult]:
        """동기 방식으로 여러 URL 크롤링"""
        return asyncio.run(self.crawl_multiple_async(urls))
    
    async def crawl_async(self, url: str) -> CrawlResult:
        """비동기 단일 URL 크롤링"""
        if not self.should_crawl(url):
            return CrawlResult(
                url=url,
                success=False,
                error="Invalid URL or not allowed to crawl"
            )
        
        self.logger.info(f"Async crawling: {url}")
        
        # 통계 시작
        if self.stats["start_time"] is None:
            self.stats["start_time"] = datetime.now()
        
        async with httpx.AsyncClient(**self.client_config) as client:
            for attempt in range(self.retry_count):
                try:
                    # 반크롤링 회피
                    await asyncio.sleep(self.anti_bot.get_random_delay(self.delay))
                    
                    # 요청 실행
                    response = await client.get(url, follow_redirects=True)
                    response.raise_for_status()
                    
                    # 통계 업데이트
                    self.update_stats(True, len(response.content))
                    
                    # HTML 파싱
                    soup = BeautifulSoup(response.text, 'html.parser')
                    
                    # 데이터 추출
                    result = self._extract_data(url, soup, response.text)
                    
                    self.logger.info(f"Successfully crawled: {url}")
                    return result
                    
                except httpx.HTTPError as e:
                    self.logger.warning(f"Attempt {attempt + 1} failed for {url}: {e}")
                    
                    if attempt == self.retry_count - 1:
                        self.update_stats(False)
                        return CrawlResult(
                            url=url,
                            success=False,
                            error=str(e)
                        )
                    
                    # 재시도 전 대기
                    await asyncio.sleep(self.delay * (attempt + 1))
        
        self.update_stats(False)
        return CrawlResult(
            url=url,
            success=False,
            error="Max retries exceeded"
        )
    
    async def crawl_multiple_async(self, urls: List[str]) -> List[CrawlResult]:
        """비동기 여러 URL 동시 크롤링"""
        self.logger.info(f"Async crawling {len(urls)} URLs")
        self.reset_stats()
        self.stats["start_time"] = datetime.now()
        
        # 세마포어로 동시 실행 제한
        semaphore = asyncio.Semaphore(self.max_connections)
        
        async def crawl_with_semaphore(url: str) -> CrawlResult:
            async with semaphore:
                return await self.crawl_async(url)
        
        # 동시 실행
        tasks = [crawl_with_semaphore(url) for url in urls]
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        # 예외 처리
        processed_results = []
        for i, result in enumerate(results):
            if isinstance(result, Exception):
                processed_results.append(CrawlResult(
                    url=urls[i],
                    success=False,
                    error=str(result)
                ))
            else:
                processed_results.append(result)
        
        self.stats["end_time"] = datetime.now()
        
        # 결과 요약
        successful = sum(1 for r in processed_results if r.success)
        self.logger.info(f"Completed: {successful}/{len(urls)} successful")
        
        return processed_results
    
    async def crawl_stream_async(self, urls: List[str], callback=None):
        """스트리밍 방식으로 크롤링 (결과를 즉시 처리)"""
        async with httpx.AsyncClient(**self.client_config) as client:
            for url in urls:
                result = await self._crawl_single_with_client(client, url)
                
                if callback:
                    await callback(result)
                
                yield result
    
    async def _crawl_single_with_client(self, 
                                       client: httpx.AsyncClient, 
                                       url: str) -> CrawlResult:
        """클라이언트 재사용하여 단일 URL 크롤링"""
        if not self.should_crawl(url):
            return CrawlResult(
                url=url,
                success=False,
                error="Invalid URL or not allowed to crawl"
            )
        
        try:
            # 요청 실행
            response = await client.get(url, follow_redirects=True)
            response.raise_for_status()
            
            # HTML 파싱
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # 데이터 추출
            return self._extract_data(url, soup, response.text)
            
        except httpx.HTTPError as e:
            return CrawlResult(
                url=url,
                success=False,
                error=str(e)
            )
    
    def _extract_data(self, url: str, soup: BeautifulSoup, raw_html: str) -> CrawlResult:
        """HTML에서 데이터 추출"""
        try:
            title = self.parser.extract_title(soup)
            content = self.parser.extract_content(soup)
            metadata = self.parser.extract_metadata(soup)
            author = metadata.get('author')
            published_date = self.parser.extract_date(soup, metadata)
            images = self.parser.extract_images(soup, url)
            links = self.parser.extract_links(soup, url)
            
            return CrawlResult(
                url=url,
                title=title,
                content=content,
                author=author,
                published_date=published_date,
                images=images,
                links=links,
                metadata=metadata,
                raw_html=raw_html,
                success=True
            )
            
        except Exception as e:
            self.logger.error(f"Error extracting data from {url}: {e}")
            return CrawlResult(
                url=url,
                raw_html=raw_html,
                success=False,
                error=f"Extraction error: {str(e)}"
            )
    
    async def crawl_with_rate_limit(self, 
                                   urls: List[str], 
                                   rate_limit: int = 10) -> List[CrawlResult]:
        """속도 제한을 적용한 크롤링"""
        from ..utils.rate_limiter import AsyncRateLimiter
        
        rate_limiter = AsyncRateLimiter(rate=rate_limit, per=1.0)
        results = []
        
        async with httpx.AsyncClient(**self.client_config) as client:
            for url in urls:
                await rate_limiter.acquire()
                result = await self._crawl_single_with_client(client, url)
                results.append(result)
        
        return results
    
    async def crawl_with_retry_policy(self,
                                     url: str,
                                     max_retries: int = 5,
                                     backoff_factor: float = 2.0) -> CrawlResult:
        """지수 백오프를 적용한 재시도"""
        async with httpx.AsyncClient(**self.client_config) as client:
            for attempt in range(max_retries):
                try:
                    result = await self._crawl_single_with_client(client, url)
                    
                    if result.success:
                        return result
                    
                    # 실패 시 대기
                    wait_time = self.delay * (backoff_factor ** attempt)
                    self.logger.info(f"Retry {attempt + 1}/{max_retries} after {wait_time}s")
                    await asyncio.sleep(wait_time)
                    
                except Exception as e:
                    self.logger.error(f"Attempt {attempt + 1} failed: {e}")
                    
                    if attempt == max_retries - 1:
                        return CrawlResult(
                            url=url,
                            success=False,
                            error=f"Max retries exceeded: {str(e)}"
                        )
        
        return CrawlResult(
            url=url,
            success=False,
            error="Crawling failed"
        )
    
    def close(self):
        """리소스 정리"""
        self.logger.info("HTTPX crawler closed")