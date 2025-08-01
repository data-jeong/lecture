"""
Scrapy 기반 크롤러
대규모 웹 크롤링에 최적화
"""

import json
from typing import List, Dict, Optional, Any
from datetime import datetime
import logging
from pathlib import Path
import subprocess
import tempfile

from .base_crawler import BaseCrawler, CrawlResult


class ScrapyCrawler(BaseCrawler):
    """Scrapy Framework 래퍼"""
    
    def __init__(self, 
                 spider_name: str = "news",
                 scrapy_project_path: Optional[str] = None,
                 settings: Optional[Dict[str, Any]] = None,
                 **kwargs):
        """
        Args:
            spider_name: 스파이더 이름
            scrapy_project_path: Scrapy 프로젝트 경로
            settings: Scrapy 설정 오버라이드
        """
        super().__init__(**kwargs)
        
        self.spider_name = spider_name
        self.scrapy_project_path = scrapy_project_path or "scrapy_project"
        self.custom_settings = settings or {}
        
        # 기본 설정
        self.default_settings = {
            'USER_AGENT': self.user_agent,
            'ROBOTSTXT_OBEY': True,
            'CONCURRENT_REQUESTS': 16,
            'DOWNLOAD_DELAY': self.delay,
            'COOKIES_ENABLED': True,
            'TELNETCONSOLE_ENABLED': False,
            'LOG_LEVEL': 'INFO',
            'RETRY_TIMES': self.retry_count,
            'DOWNLOAD_TIMEOUT': self.timeout,
        }
        
        # 프록시 설정
        if self.proxy:
            self.default_settings['PROXY'] = self.proxy
    
    def crawl(self, url: str) -> CrawlResult:
        """단일 URL 크롤링"""
        results = self.crawl_multiple([url])
        return results[0] if results else CrawlResult(
            url=url,
            success=False,
            error="Scrapy crawling failed"
        )
    
    def crawl_multiple(self, urls: List[str]) -> List[CrawlResult]:
        """여러 URL 크롤링"""
        self.logger.info(f"Crawling {len(urls)} URLs with Scrapy")
        
        # 임시 파일에 결과 저장
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            output_file = f.name
        
        try:
            # Scrapy 명령 실행
            self._run_scrapy(urls, output_file)
            
            # 결과 읽기
            results = self._parse_results(output_file)
            
            self.logger.info(f"Scrapy crawled {len(results)} pages")
            return results
            
        except Exception as e:
            self.logger.error(f"Scrapy crawling failed: {e}")
            return [CrawlResult(url=url, success=False, error=str(e)) for url in urls]
            
        finally:
            # 임시 파일 삭제
            Path(output_file).unlink(missing_ok=True)
    
    def _run_scrapy(self, urls: List[str], output_file: str):
        """Scrapy 명령 실행"""
        # 설정 병합
        settings = {**self.default_settings, **self.custom_settings}
        
        # 명령 구성
        cmd = [
            'scrapy', 'crawl', self.spider_name,
            '-o', output_file,
            '-a', f'start_urls={",".join(urls)}'
        ]
        
        # 설정 추가
        for key, value in settings.items():
            cmd.extend(['-s', f'{key}={value}'])
        
        # 프로젝트 디렉토리에서 실행
        self.logger.info(f"Running Scrapy command: {' '.join(cmd[:5])}...")
        
        process = subprocess.Popen(
            cmd,
            cwd=self.scrapy_project_path,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )
        
        stdout, stderr = process.communicate()
        
        if process.returncode != 0:
            raise RuntimeError(f"Scrapy failed: {stderr}")
        
        self.logger.debug(f"Scrapy output: {stdout}")
    
    def _parse_results(self, output_file: str) -> List[CrawlResult]:
        """Scrapy 결과 파싱"""
        results = []
        
        try:
            with open(output_file, 'r', encoding='utf-8') as f:
                items = json.load(f)
            
            for item in items:
                result = CrawlResult(
                    url=item.get('url', ''),
                    title=item.get('title'),
                    content=item.get('content'),
                    author=item.get('author'),
                    published_date=self._parse_date(item.get('published_date')),
                    images=item.get('images', []),
                    links=item.get('links', []),
                    metadata=item.get('metadata', {}),
                    success=True
                )
                results.append(result)
                
        except Exception as e:
            self.logger.error(f"Error parsing Scrapy results: {e}")
        
        return results
    
    def _parse_date(self, date_str: Optional[str]) -> Optional[datetime]:
        """날짜 문자열 파싱"""
        if not date_str:
            return None
            
        try:
            return datetime.fromisoformat(date_str)
        except:
            return None
    
    def create_spider_code(self) -> str:
        """스파이더 코드 생성"""
        return '''
import scrapy
from datetime import datetime


class NewsSpider(scrapy.Spider):
    name = 'news'
    
    def __init__(self, start_urls=None, *args, **kwargs):
        super(NewsSpider, self).__init__(*args, **kwargs)
        if start_urls:
            self.start_urls = start_urls.split(',')
        else:
            self.start_urls = []
    
    def parse(self, response):
        """메인 파싱 메서드"""
        # 뉴스 기사 추출
        articles = response.css('article, .article, .news-item')
        
        if not articles:
            # 대체 선택자
            articles = response.css('[class*="article"], [class*="news"]')
        
        for article in articles:
            yield self.parse_article(article, response)
        
        # 다음 페이지
        next_page = response.css('a.next::attr(href), a[rel="next"]::attr(href)').get()
        if next_page:
            yield response.follow(next_page, self.parse)
    
    def parse_article(self, article, response):
        """기사 파싱"""
        # 제목
        title = article.css('h1::text, h2::text, h3::text').get()
        if not title:
            title = article.css('[class*="title"]::text').get()
        
        # 본문
        content_selectors = [
            '.content',
            '.article-body',
            '.text',
            'p'
        ]
        
        content = []
        for selector in content_selectors:
            paragraphs = article.css(f'{selector}::text').getall()
            if paragraphs:
                content = paragraphs
                break
        
        # 작성자
        author = article.css('.author::text, .by::text, [class*="author"]::text').get()
        
        # 날짜
        date_text = article.css('time::attr(datetime), .date::text, [class*="date"]::text').get()
        
        # 이미지
        images = article.css('img::attr(src)').getall()
        images = [response.urljoin(img) for img in images]
        
        # 링크
        links = article.css('a::attr(href)').getall()
        links = [response.urljoin(link) for link in links]
        
        return {
            'url': response.url,
            'title': title.strip() if title else None,
            'content': '\\n'.join(content),
            'author': author.strip() if author else None,
            'published_date': date_text,
            'images': images,
            'links': links,
            'metadata': {
                'crawled_at': datetime.now().isoformat(),
                'spider': self.name
            }
        }
'''
    
    def run_spider_in_process(self, urls: List[str]) -> List[CrawlResult]:
        """프로세스 내에서 스파이더 실행 (테스트용)"""
        try:
            from scrapy.crawler import CrawlerProcess
            from scrapy.utils.project import get_project_settings
            
            # 결과 저장용
            results = []
            
            class InMemoryPipeline:
                def process_item(self, item, spider):
                    results.append(dict(item))
                    return item
            
            # 설정
            settings = get_project_settings()
            settings.update(self.default_settings)
            settings.update(self.custom_settings)
            settings['ITEM_PIPELINES'] = {
                InMemoryPipeline: 100
            }
            
            # 프로세스 실행
            process = CrawlerProcess(settings)
            process.crawl(self.spider_name, start_urls=urls)
            process.start()
            
            # 결과 변환
            return [self._item_to_result(item) for item in results]
            
        except ImportError:
            self.logger.error("Scrapy not installed or not in project directory")
            return []
    
    def _item_to_result(self, item: dict) -> CrawlResult:
        """Scrapy 아이템을 CrawlResult로 변환"""
        return CrawlResult(
            url=item.get('url', ''),
            title=item.get('title'),
            content=item.get('content'),
            author=item.get('author'),
            published_date=self._parse_date(item.get('published_date')),
            images=item.get('images', []),
            links=item.get('links', []),
            metadata=item.get('metadata', {}),
            success=True
        )
    
    def close(self):
        """리소스 정리"""
        self.logger.info("Scrapy crawler closed")