"""
Requests 기반 크롤러
정적 웹페이지 크롤링에 최적화
"""

import time
import requests
from bs4 import BeautifulSoup
from typing import List, Dict, Optional
from datetime import datetime
import logging

from .base_crawler import BaseCrawler, CrawlResult
from ..utils.parser import HTMLParser
from ..utils.anti_bot import AntiBot


class RequestsCrawler(BaseCrawler):
    """Requests + BeautifulSoup 크롤러"""
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        
        # 세션 설정
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': self.user_agent,
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
            'Accept-Language': 'ko-KR,ko;q=0.9,en;q=0.8',
            'Accept-Encoding': 'gzip, deflate, br',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1'
        })
        
        # 프록시 설정
        if self.proxy:
            self.session.proxies = {
                'http': self.proxy,
                'https': self.proxy
            }
        
        self.parser = HTMLParser()
        self.anti_bot = AntiBot()
    
    def crawl(self, url: str) -> CrawlResult:
        """단일 URL 크롤링"""
        if not self.should_crawl(url):
            return CrawlResult(
                url=url,
                success=False,
                error="Invalid URL or not allowed to crawl"
            )
        
        self.logger.info(f"Crawling: {url}")
        
        # 통계 시작
        if self.stats["start_time"] is None:
            self.stats["start_time"] = datetime.now()
        
        for attempt in range(self.retry_count):
            try:
                # 반크롤링 회피
                self.anti_bot.random_delay(self.delay)
                
                # 요청 실행
                response = self.session.get(
                    url,
                    timeout=self.timeout,
                    allow_redirects=True
                )
                
                response.raise_for_status()
                
                # 인코딩 처리
                response.encoding = response.apparent_encoding
                
                # 통계 업데이트
                self.update_stats(True, len(response.content))
                
                # HTML 파싱
                soup = BeautifulSoup(response.text, 'html.parser')
                
                # 데이터 추출
                result = self._extract_data(url, soup, response.text)
                
                self.logger.info(f"Successfully crawled: {url}")
                return result
                
            except requests.exceptions.RequestException as e:
                self.logger.warning(f"Attempt {attempt + 1} failed for {url}: {e}")
                
                if attempt == self.retry_count - 1:
                    self.update_stats(False)
                    return CrawlResult(
                        url=url,
                        success=False,
                        error=str(e)
                    )
                
                # 재시도 전 대기
                time.sleep(self.delay * (attempt + 1))
        
        self.update_stats(False)
        return CrawlResult(
            url=url,
            success=False,
            error="Max retries exceeded"
        )
    
    def crawl_multiple(self, urls: List[str]) -> List[CrawlResult]:
        """여러 URL 순차 크롤링"""
        results = []
        
        self.logger.info(f"Crawling {len(urls)} URLs")
        self.reset_stats()
        self.stats["start_time"] = datetime.now()
        
        for i, url in enumerate(urls):
            self.logger.info(f"Progress: {i+1}/{len(urls)}")
            
            result = self.crawl(url)
            results.append(result)
            
            # 마지막 URL이 아니면 지연
            if i < len(urls) - 1:
                time.sleep(self.delay)
        
        self.stats["end_time"] = datetime.now()
        
        # 결과 요약
        successful = sum(1 for r in results if r.success)
        self.logger.info(f"Completed: {successful}/{len(urls)} successful")
        
        return results
    
    def _extract_data(self, url: str, soup: BeautifulSoup, raw_html: str) -> CrawlResult:
        """HTML에서 데이터 추출"""
        try:
            # 제목 추출
            title = self.parser.extract_title(soup)
            
            # 본문 추출
            content = self.parser.extract_content(soup)
            
            # 메타데이터 추출
            metadata = self.parser.extract_metadata(soup)
            
            # 작성자 추출
            author = metadata.get('author')
            
            # 날짜 추출
            published_date = self.parser.extract_date(soup, metadata)
            
            # 이미지 추출
            images = self.parser.extract_images(soup, url)
            
            # 링크 추출
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
    
    def crawl_with_pagination(self, base_url: str, max_pages: int = 10) -> List[CrawlResult]:
        """페이지네이션이 있는 사이트 크롤링"""
        results = []
        
        for page in range(1, max_pages + 1):
            # URL 패턴에 따라 수정 필요
            page_url = f"{base_url}?page={page}"
            
            self.logger.info(f"Crawling page {page}: {page_url}")
            
            result = self.crawl(page_url)
            
            if not result.success:
                self.logger.warning(f"Failed to crawl page {page}")
                break
            
            results.append(result)
            
            # 다음 페이지 링크가 없으면 중단
            soup = BeautifulSoup(result.raw_html, 'html.parser')
            if not self._has_next_page(soup):
                self.logger.info("No more pages to crawl")
                break
            
            time.sleep(self.delay)
        
        return results
    
    def _has_next_page(self, soup: BeautifulSoup) -> bool:
        """다음 페이지 존재 여부 확인"""
        # 사이트별로 구현 필요
        next_link = soup.find('a', {'class': 'next'}) or \
                   soup.find('a', string=re.compile('다음|next', re.I))
        return next_link is not None
    
    def crawl_sitemap(self, sitemap_url: str) -> List[str]:
        """사이트맵에서 URL 목록 추출"""
        try:
            response = self.session.get(sitemap_url, timeout=self.timeout)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.text, 'xml')
            urls = []
            
            # 일반 사이트맵
            for loc in soup.find_all('loc'):
                urls.append(loc.text)
            
            # 사이트맵 인덱스
            for sitemap in soup.find_all('sitemap'):
                loc = sitemap.find('loc')
                if loc:
                    # 재귀적으로 하위 사이트맵 크롤링
                    sub_urls = self.crawl_sitemap(loc.text)
                    urls.extend(sub_urls)
            
            self.logger.info(f"Found {len(urls)} URLs in sitemap")
            return urls
            
        except Exception as e:
            self.logger.error(f"Error crawling sitemap {sitemap_url}: {e}")
            return []
    
    def close(self):
        """세션 종료"""
        self.session.close()
        self.logger.info("Requests crawler closed")