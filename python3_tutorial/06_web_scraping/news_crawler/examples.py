#!/usr/bin/env python3
"""
뉴스 크롤러 사용 예제
다양한 크롤링 시나리오 시연
"""

import asyncio
import time
from pathlib import Path

from core import (
    RequestsCrawler,
    SeleniumCrawler,
    HttpxCrawler
)
from extractors import NewsExtractor, CommentExtractor
from utils import UserAgentManager, ProxyManager
from storage import FileStorage


async def example_basic_crawling():
    """기본 크롤링 예제"""
    print("🕷️  기본 크롤링 예제")
    print("=" * 60)
    
    # 테스트 URL들
    test_urls = [
        "https://httpbin.org/html",
        "https://example.com",
    ]
    
    # 1. Requests 크롤러
    print("\n1. Requests 크롤러")
    crawler = RequestsCrawler(delay=0.5)
    
    for url in test_urls:
        print(f"  크롤링: {url}")
        result = crawler.crawl(url)
        
        if result.success:
            print(f"    ✅ 성공 - 제목: {result.title}")
            print(f"    📄 컨텐츠 크기: {len(result.content or '')} 글자")
        else:
            print(f"    ❌ 실패: {result.error}")
    
    crawler.close()
    
    # 2. HTTPX 비동기 크롤러
    print("\n2. HTTPX 비동기 크롤러")
    httpx_crawler = HttpxCrawler()
    
    # 동시 크롤링
    start_time = time.time()
    results = await httpx_crawler.crawl_multiple_async(test_urls)
    duration = time.time() - start_time
    
    print(f"  ⚡ {len(results)}개 페이지를 {duration:.2f}초에 완료")
    
    for result in results:
        if result.success:
            print(f"    ✅ {result.url}: {result.title}")
        else:
            print(f"    ❌ {result.url}: {result.error}")


async def example_news_extraction():
    """뉴스 데이터 추출 예제"""
    print("\n\n📰 뉴스 데이터 추출 예제")
    print("=" * 60)
    
    # 뉴스 사이트 URL (실제로는 허가된 사이트만 사용)
    news_urls = [
        "https://httpbin.org/html",  # 테스트용
    ]
    
    crawler = RequestsCrawler()
    extractor = NewsExtractor()
    
    for url in news_urls:
        print(f"\n📖 분석 중: {url}")
        
        # 크롤링
        result = crawler.crawl(url)
        
        if result.success:
            # 뉴스 데이터 추출
            news_data = extractor.extract(result.raw_html, url)
            
            print(f"  제목: {news_data.get('title', 'N/A')}")
            print(f"  작성자: {news_data.get('author', 'N/A')}")
            print(f"  날짜: {news_data.get('published_date', 'N/A')}")
            print(f"  카테고리: {news_data.get('category', 'N/A')}")
            print(f"  단어 수: {news_data.get('word_count', 0)}")
            print(f"  예상 읽기 시간: {news_data.get('reading_time', 0)}분")
            print(f"  언어: {news_data.get('language', 'N/A')}")
            print(f"  이미지 수: {len(news_data.get('images', []))}")
            print(f"  관련 기사: {len(news_data.get('related_articles', []))}")
    
    crawler.close()


def example_user_agent_rotation():
    """User-Agent 로테이션 예제"""
    print("\n\n🎭 User-Agent 로테이션 예제")
    print("=" * 60)
    
    ua_manager = UserAgentManager()
    
    # 다양한 User-Agent 생성
    print("생성된 User-Agent들:")
    for i in range(5):
        ua = ua_manager.get_random_user_agent()
        print(f"  {i+1}. {ua}")
    
    # 브라우저별 User-Agent
    print("\n브라우저별 User-Agent:")
    browsers = ['chrome', 'firefox', 'safari', 'edge']
    
    for browser in browsers:
        ua = ua_manager.get_random_user_agent(browser=browser)
        print(f"  {browser.capitalize()}: {ua}")
    
    # 모바일 User-Agent
    print("\n모바일 User-Agent:")
    mobile_ua = ua_manager.get_random_user_agent(mobile=True)
    print(f"  Mobile: {mobile_ua}")


async def example_rate_limiting():
    """속도 제한 예제"""
    print("\n\n🚦 속도 제한 예제")
    print("=" * 60)
    
    from utils.rate_limiter import AsyncRateLimiter
    
    # 속도 제한기 설정 (2 requests/second)
    rate_limiter = AsyncRateLimiter(rate=2, per=1.0)
    
    # 제한된 크롤링 함수
    @rate_limiter
    async def limited_crawl(url):
        print(f"  🕐 {time.strftime('%H:%M:%S')} - 크롤링: {url}")
        # 실제 크롤링 시뮬레이션
        await asyncio.sleep(0.1)
        return f"Result from {url}"
    
    # 5개 요청 실행
    urls = [f"https://example.com/page/{i}" for i in range(5)]
    
    print("속도 제한 적용 (2 requests/second):")
    start_time = time.time()
    
    tasks = [limited_crawl(url) for url in urls]
    results = await asyncio.gather(*tasks)
    
    duration = time.time() - start_time
    print(f"\n⏱️  총 시간: {duration:.2f}초 (예상: ~2초)")
    print(f"📊 처리된 요청: {len(results)}개")


def example_proxy_management():
    """프록시 관리 예제"""
    print("\n\n🌐 프록시 관리 예제")
    print("=" * 60)
    
    # 테스트용 프록시 목록 (실제로는 작동하지 않을 수 있음)
    test_proxies = [
        "http://proxy1.example.com:8080",
        "http://proxy2.example.com:8080",
        "socks5://proxy3.example.com:1080",
    ]
    
    proxy_manager = ProxyManager(test_proxies)
    
    print(f"등록된 프록시: {len(proxy_manager.proxies)}개")
    
    # 프록시 선택
    for i in range(3):
        proxy = proxy_manager.get_proxy()
        if proxy:
            print(f"  {i+1}. 선택된 프록시: {proxy.address}")
        else:
            print(f"  {i+1}. 사용 가능한 프록시 없음")
    
    # 통계 출력
    stats = proxy_manager.get_statistics()
    print(f"\n📊 프록시 통계:")
    print(f"  총 프록시: {stats['total_proxies']}")
    print(f"  사용 가능: {stats['available_proxies']}")
    print(f"  블랙리스트: {stats['blacklisted_proxies']}")


async def example_batch_crawling():
    """배치 크롤링 예제"""
    print("\n\n📦 배치 크롤링 예제")
    print("=" * 60)
    
    # URL 목록
    urls = [
        "https://httpbin.org/html",
        "https://httpbin.org/json",
        "https://httpbin.org/xml",
        "https://example.com",
    ]
    
    # 비동기 배치 크롤링
    crawler = HttpxCrawler(max_connections=2)
    
    print(f"🚀 {len(urls)}개 URL 배치 크롤링 시작")
    start_time = time.time()
    
    results = await crawler.crawl_multiple_async(urls)
    
    duration = time.time() - start_time
    successful = sum(1 for r in results if r.success)
    
    print(f"\n✅ 완료:")
    print(f"  성공: {successful}/{len(results)}")
    print(f"  소요 시간: {duration:.2f}초")
    print(f"  평균 속도: {len(results)/duration:.2f} requests/sec")
    
    # 결과 상세
    for result in results:
        status = "✅" if result.success else "❌"
        print(f"  {status} {result.url}")


def example_data_storage():
    """데이터 저장 예제"""
    print("\n\n💾 데이터 저장 예제")
    print("=" * 60)
    
    from core.base_crawler import CrawlResult
    from datetime import datetime
    
    # 저장소 초기화
    storage = FileStorage("example_data")
    
    # 가상 크롤링 결과 생성
    sample_results = []
    for i in range(3):
        result = CrawlResult(
            url=f"https://example.com/article/{i+1}",
            title=f"테스트 기사 {i+1}",
            content=f"이것은 테스트 기사 {i+1}의 내용입니다. " * 20,
            author=f"기자{i+1}",
            published_date=datetime.now(),
            success=True
        )
        sample_results.append(result)
    
    # 개별 저장
    print("개별 기사 저장:")
    for result in sample_results:
        filepath = storage.save_article(result)
        print(f"  저장됨: {Path(filepath).name}")
    
    # 배치 저장
    batch_file = storage.save_batch(sample_results)
    print(f"\n배치 파일 저장: {Path(batch_file).name}")
    
    # CSV 내보내기
    articles_data = [r.to_dict() for r in sample_results]
    csv_file = storage.export_to_csv(articles_data, "sample_articles.csv")
    print(f"CSV 내보내기: {Path(csv_file).name}")
    
    # 저장소 통계
    stats = storage.get_statistics()
    print(f"\n📊 저장소 통계:")
    print(f"  기사 수: {stats['articles_count']}")
    print(f"  총 용량: {stats['total_size_mb']:.2f} MB")


async def example_selenium_crawling():
    """Selenium 크롤링 예제 (JavaScript 페이지)"""
    print("\n\n🖥️  Selenium 크롤링 예제")
    print("=" * 60)
    
    # Selenium 크롤러 (헤드리스 모드)
    try:
        crawler = SeleniumCrawler(headless=True)
        
        # JavaScript가 많은 페이지 (SPA 등)
        spa_url = "https://httpbin.org/html"  # 테스트용
        
        print(f"JavaScript 페이지 크롤링: {spa_url}")
        result = crawler.crawl(spa_url)
        
        if result.success:
            print(f"  ✅ 성공")
            print(f"  📄 제목: {result.title}")
            print(f"  📊 컨텐츠 크기: {len(result.content or '')} 글자")
        else:
            print(f"  ❌ 실패: {result.error}")
        
        crawler.close()
        
    except Exception as e:
        print(f"  ⚠️  Selenium 크롤러 초기화 실패: {e}")
        print("  (Chrome 드라이버가 설치되지 않았을 수 있습니다)")


async def main():
    """모든 예제 실행"""
    print("🚀 뉴스 크롤러 예제 시연")
    print("=" * 80)
    
    examples = [
        example_basic_crawling,
        example_news_extraction,
        example_user_agent_rotation,
        example_rate_limiting,
        example_proxy_management,
        example_batch_crawling,
        example_data_storage,
        example_selenium_crawling,
    ]
    
    for i, example in enumerate(examples, 1):
        try:
            if asyncio.iscoroutinefunction(example):
                await example()
            else:
                example()
        except Exception as e:
            print(f"\n❌ 예제 {i} 실행 중 오류: {e}")
        
        if i < len(examples):
            print("\n" + "-" * 80)
            await asyncio.sleep(1)  # 예제 간 잠시 대기
    
    print("\n\n✨ 모든 예제 완료!")
    print("\n💡 더 많은 사용법:")
    print("  - python -m news_crawler.main --help")
    print("  - python -m news_crawler.main crawl https://example.com")
    print("  - python -m news_crawler.main crawl-multiple urls.txt")


if __name__ == "__main__":
    asyncio.run(main())