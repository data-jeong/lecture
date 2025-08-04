"""
웹 스크래핑 예제
비동기 웹 크롤링과 속도 제한
"""

import asyncio
import aiohttp
import time
from typing import List, Dict, Optional
from dataclasses import dataclass
import json
from bs4 import BeautifulSoup

from ..patterns.rate_limiter import AsyncRateLimiter
from ..patterns.producer_consumer import AsyncProducerConsumer
from ..utils.monitoring import PerformanceTracker


@dataclass
class WebPage:
    """웹 페이지 정보"""
    url: str
    title: Optional[str] = None
    content: Optional[str] = None
    links: List[str] = None
    error: Optional[str] = None
    fetch_time: float = 0
    
    def __post_init__(self):
        if self.links is None:
            self.links = []


class WebScraperExample:
    """웹 스크래퍼 예제"""
    
    def __init__(self):
        self.rate_limiter = AsyncRateLimiter(rate=5, per=1.0)  # 5 requests/second
        self.tracker = PerformanceTracker()
        self.session: Optional[aiohttp.ClientSession] = None
    
    async def fetch_page(self, url: str) -> WebPage:
        """페이지 가져오기"""
        page = WebPage(url=url)
        
        await self.rate_limiter.acquire()  # 속도 제한
        
        start_time = time.time()
        
        try:
            async with self.tracker.track_async(f"Fetch {url}"):
                async with self.session.get(url, timeout=10) as response:
                    if response.status == 200:
                        html = await response.text()
                        
                        # BeautifulSoup으로 파싱
                        soup = BeautifulSoup(html, 'html.parser')
                        
                        # 제목 추출
                        title_tag = soup.find('title')
                        page.title = title_tag.text.strip() if title_tag else "No Title"
                        
                        # 본문 추출 (첫 500자)
                        text = soup.get_text()
                        page.content = ' '.join(text.split())[:500]
                        
                        # 링크 추출
                        for link in soup.find_all('a', href=True):
                            href = link['href']
                            if href.startswith('http'):
                                page.links.append(href)
                        
                        page.fetch_time = time.time() - start_time
                    else:
                        page.error = f"HTTP {response.status}"
        
        except asyncio.TimeoutError:
            page.error = "Timeout"
        except Exception as e:
            page.error = str(e)
        
        return page
    
    async def scrape_urls(self, urls: List[str]) -> List[WebPage]:
        """여러 URL 스크래핑"""
        self.session = aiohttp.ClientSession()
        
        try:
            # 생산자-소비자 패턴 사용
            pc = AsyncProducerConsumer[str, WebPage](
                max_queue_size=20,
                num_consumers=5
            )
            
            # URL 생성기
            async def url_generator():
                for url in urls:
                    yield url
            
            # 페이지 처리 함수
            async def process_url(url: str) -> WebPage:
                return await self.fetch_page(url)
            
            # 실행
            results = await pc.run(
                source=url_generator(),
                processor=process_url
            )
            
            # 결과 추출
            pages = []
            for result in results:
                if "result" in result and result["result"]:
                    pages.append(result["result"])
            
            return pages
        
        finally:
            await self.session.close()
    
    async def crawl_recursive(self, start_url: str, max_depth: int = 2, max_pages: int = 20) -> Dict[str, WebPage]:
        """재귀적 크롤링"""
        visited = set()
        to_visit = {(start_url, 0)}  # (url, depth)
        pages = {}
        
        self.session = aiohttp.ClientSession()
        
        try:
            while to_visit and len(pages) < max_pages:
                # 현재 레벨의 URL들
                current_batch = []
                current_depth = None
                
                # 같은 깊이의 URL들 배치 처리
                for url, depth in list(to_visit):
                    if current_depth is None:
                        current_depth = depth
                    
                    if depth == current_depth and url not in visited:
                        current_batch.append(url)
                        to_visit.remove((url, depth))
                        visited.add(url)
                
                if not current_batch:
                    break
                
                print(f"\n깊이 {current_depth}: {len(current_batch)}개 페이지 크롤링")
                
                # 배치 처리
                batch_pages = await self.scrape_urls(current_batch)
                
                # 결과 저장 및 새 링크 추가
                for page in batch_pages:
                    if not page.error:
                        pages[page.url] = page
                        
                        # 다음 깊이 링크 추가
                        if current_depth < max_depth - 1:
                            for link in page.links[:5]:  # 각 페이지당 최대 5개 링크
                                if link not in visited:
                                    to_visit.add((link, current_depth + 1))
            
            return pages
        
        finally:
            await self.session.close()
    
    async def run(self):
        """예제 실행"""
        print("🌐 웹 스크래핑 예제")
        print("=" * 60)
        
        # 1. 단순 스크래핑
        print("\n1. 여러 페이지 동시 스크래핑")
        
        urls = [
            "https://example.com",
            "https://httpbin.org/html",
            "https://httpbin.org/delay/1",
            "https://httpbin.org/status/200",
            "https://httpbin.org/json"
        ]
        
        start_time = time.time()
        pages = await self.scrape_urls(urls)
        duration = time.time() - start_time
        
        print(f"\n✅ {len(pages)}개 페이지 스크래핑 완료 ({duration:.2f}초)")
        
        for page in pages:
            if page.error:
                print(f"  ❌ {page.url}: {page.error}")
            else:
                print(f"  ✅ {page.url}: {page.title} ({page.fetch_time:.2f}초)")
        
        # 2. 재귀적 크롤링 (시뮬레이션)
        print("\n\n2. 재귀적 웹 크롤링 (example.com 기준)")
        
        crawled_pages = await self.crawl_recursive(
            "https://example.com",
            max_depth=2,
            max_pages=10
        )
        
        print(f"\n✅ 총 {len(crawled_pages)}개 페이지 크롤링")
        
        # 깊이별 통계
        depth_stats = {}
        for url, page in crawled_pages.items():
            # URL 기반으로 깊이 추정 (실제로는 크롤링 중 추적)
            depth = 0 if url == "https://example.com" else 1
            if depth not in depth_stats:
                depth_stats[depth] = 0
            depth_stats[depth] += 1
        
        print("\n📊 깊이별 페이지 수:")
        for depth, count in sorted(depth_stats.items()):
            print(f"  깊이 {depth}: {count}개")
        
        # 3. 성능 통계
        print("\n\n3. 성능 통계")
        
        # 속도 제한 통계
        rate_stats = await self.rate_limiter.get_statistics()
        print("\n🚦 속도 제한 통계:")
        for key, value in rate_stats.items():
            print(f"  {key}: {value}")
        
        # 성능 추적 통계
        self.tracker.print_report()
        
        # 결과 저장
        print("\n💾 결과 저장")
        
        result_data = {
            "scraping_results": [
                {
                    "url": page.url,
                    "title": page.title,
                    "fetch_time": page.fetch_time,
                    "links_count": len(page.links),
                    "error": page.error
                }
                for page in pages
            ],
            "crawling_results": {
                "total_pages": len(crawled_pages),
                "depth_stats": depth_stats
            },
            "performance": self.tracker.get_statistics()
        }
        
        with open("web_scraping_results.json", "w", encoding="utf-8") as f:
            json.dump(result_data, f, indent=2, ensure_ascii=False)
        
        print("  ✅ web_scraping_results.json 저장 완료")


async def main():
    """메인 함수"""
    example = WebScraperExample()
    await example.run()


if __name__ == "__main__":
    asyncio.run(main())