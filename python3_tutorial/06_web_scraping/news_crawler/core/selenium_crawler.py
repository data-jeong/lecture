"""
Selenium 기반 크롤러
JavaScript로 렌더링되는 동적 웹페이지 크롤링
"""

import time
from typing import List, Dict, Optional
from datetime import datetime
import logging
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.action_chains import ActionChains
from selenium.common.exceptions import TimeoutException, WebDriverException
from bs4 import BeautifulSoup

from .base_crawler import BaseCrawler, CrawlResult
from ..utils.parser import HTMLParser
from ..utils.anti_bot import AntiBot


class SeleniumCrawler(BaseCrawler):
    """Selenium WebDriver 기반 크롤러"""
    
    def __init__(self, 
                 headless: bool = True,
                 driver_path: Optional[str] = None,
                 window_size: tuple = (1920, 1080),
                 **kwargs):
        """
        Args:
            headless: 헤드리스 모드 사용 여부
            driver_path: 크롬 드라이버 경로
            window_size: 브라우저 창 크기
        """
        super().__init__(**kwargs)
        
        self.headless = headless
        self.driver_path = driver_path
        self.window_size = window_size
        self.driver = None
        
        self.parser = HTMLParser()
        self.anti_bot = AntiBot()
        
        # 드라이버 초기화
        self._init_driver()
    
    def _init_driver(self):
        """웹드라이버 초기화"""
        options = Options()
        
        # 헤드리스 모드
        if self.headless:
            options.add_argument('--headless')
        
        # 기본 옵션
        options.add_argument(f'--window-size={self.window_size[0]},{self.window_size[1]}')
        options.add_argument('--no-sandbox')
        options.add_argument('--disable-dev-shm-usage')
        options.add_argument('--disable-blink-features=AutomationControlled')
        options.add_experimental_option("excludeSwitches", ["enable-automation"])
        options.add_experimental_option('useAutomationExtension', False)
        
        # User-Agent 설정
        options.add_argument(f'user-agent={self.user_agent}')
        
        # 프록시 설정
        if self.proxy:
            options.add_argument(f'--proxy-server={self.proxy}')
        
        # 이미지 로딩 비활성화 (옵션)
        prefs = {
            "profile.default_content_setting_values": {
                "images": 2  # 이미지 로딩 비활성화
            }
        }
        options.add_experimental_option("prefs", prefs)
        
        try:
            if self.driver_path:
                self.driver = webdriver.Chrome(
                    executable_path=self.driver_path,
                    options=options
                )
            else:
                self.driver = webdriver.Chrome(options=options)
            
            # 암시적 대기 설정
            self.driver.implicitly_wait(10)
            
            self.logger.info("Selenium driver initialized")
            
        except Exception as e:
            self.logger.error(f"Failed to initialize driver: {e}")
            raise
    
    def crawl(self, url: str) -> CrawlResult:
        """단일 URL 크롤링"""
        if not self.should_crawl(url):
            return CrawlResult(
                url=url,
                success=False,
                error="Invalid URL or not allowed to crawl"
            )
        
        self.logger.info(f"Crawling with Selenium: {url}")
        
        # 통계 시작
        if self.stats["start_time"] is None:
            self.stats["start_time"] = datetime.now()
        
        for attempt in range(self.retry_count):
            try:
                # 페이지 로드
                self.driver.get(url)
                
                # 페이지 로딩 대기
                self._wait_for_page_load()
                
                # 동적 컨텐츠 로딩 대기
                self._wait_for_dynamic_content()
                
                # 스크롤하여 lazy loading 컨텐츠 로드
                self._scroll_to_bottom()
                
                # HTML 가져오기
                page_source = self.driver.page_source
                
                # 통계 업데이트
                self.update_stats(True, len(page_source.encode()))
                
                # BeautifulSoup으로 파싱
                soup = BeautifulSoup(page_source, 'html.parser')
                
                # 데이터 추출
                result = self._extract_data(url, soup, page_source)
                
                # JavaScript 실행으로 추가 데이터 수집
                result = self._extract_js_data(result)
                
                self.logger.info(f"Successfully crawled: {url}")
                return result
                
            except (TimeoutException, WebDriverException) as e:
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
                
                # 드라이버 재시작
                if attempt > 0:
                    self._restart_driver()
        
        self.update_stats(False)
        return CrawlResult(
            url=url,
            success=False,
            error="Max retries exceeded"
        )
    
    def crawl_multiple(self, urls: List[str]) -> List[CrawlResult]:
        """여러 URL 크롤링"""
        results = []
        
        self.logger.info(f"Crawling {len(urls)} URLs with Selenium")
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
    
    def _wait_for_page_load(self, timeout: int = 30):
        """페이지 로딩 대기"""
        WebDriverWait(self.driver, timeout).until(
            lambda driver: driver.execute_script("return document.readyState") == "complete"
        )
    
    def _wait_for_dynamic_content(self):
        """동적 컨텐츠 로딩 대기"""
        # 주요 컨텐츠 선택자 (사이트별로 수정 필요)
        content_selectors = [
            "article",
            ".article",
            "#content",
            ".content",
            "main",
            "[role='main']"
        ]
        
        for selector in content_selectors:
            try:
                WebDriverWait(self.driver, 10).until(
                    EC.presence_of_element_located((By.CSS_SELECTOR, selector))
                )
                break
            except TimeoutException:
                continue
    
    def _scroll_to_bottom(self):
        """페이지 끝까지 스크롤 (lazy loading 대응)"""
        last_height = self.driver.execute_script("return document.body.scrollHeight")
        
        while True:
            # 끝까지 스크롤
            self.driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
            
            # 로딩 대기
            time.sleep(2)
            
            # 새 높이 확인
            new_height = self.driver.execute_script("return document.body.scrollHeight")
            
            if new_height == last_height:
                break
                
            last_height = new_height
    
    def _extract_data(self, url: str, soup: BeautifulSoup, raw_html: str) -> CrawlResult:
        """HTML에서 데이터 추출"""
        try:
            # 기본 추출 (RequestsCrawler와 동일)
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
    
    def _extract_js_data(self, result: CrawlResult) -> CrawlResult:
        """JavaScript로 추가 데이터 추출"""
        try:
            # 댓글 수 등 동적 데이터
            comment_count = self.driver.execute_script("""
                var comments = document.querySelectorAll('.comment, [class*="comment"]');
                return comments.length;
            """)
            
            if comment_count:
                result.metadata['comment_count'] = comment_count
            
            # 조회수 등 추가 정보
            view_count = self.driver.execute_script("""
                var viewElement = document.querySelector('.views, .view-count, [class*="view"]');
                return viewElement ? viewElement.textContent : null;
            """)
            
            if view_count:
                result.metadata['view_count'] = view_count
            
        except Exception as e:
            self.logger.warning(f"Error extracting JS data: {e}")
        
        return result
    
    def handle_popup(self):
        """팝업 처리"""
        try:
            # 팝업 닫기 버튼 찾기
            close_buttons = self.driver.find_elements(By.CSS_SELECTOR, 
                "[class*='close'], [class*='dismiss'], [aria-label='close']")
            
            for button in close_buttons:
                if button.is_displayed():
                    button.click()
                    time.sleep(1)
                    break
                    
        except Exception as e:
            self.logger.debug(f"No popup to close: {e}")
    
    def handle_cookie_banner(self):
        """쿠키 배너 처리"""
        try:
            # 쿠키 수락 버튼
            accept_buttons = self.driver.find_elements(By.CSS_SELECTOR,
                "[class*='accept'], [class*='agree'], button[onclick*='accept']")
            
            for button in accept_buttons:
                if button.is_displayed() and 'cookie' in button.text.lower():
                    button.click()
                    time.sleep(1)
                    break
                    
        except Exception as e:
            self.logger.debug(f"No cookie banner to handle: {e}")
    
    def take_screenshot(self, filename: str):
        """스크린샷 저장"""
        try:
            self.driver.save_screenshot(filename)
            self.logger.info(f"Screenshot saved: {filename}")
        except Exception as e:
            self.logger.error(f"Failed to take screenshot: {e}")
    
    def _restart_driver(self):
        """드라이버 재시작"""
        self.logger.info("Restarting driver...")
        self.close()
        self._init_driver()
    
    def close(self):
        """드라이버 종료"""
        if self.driver:
            try:
                self.driver.quit()
                self.logger.info("Selenium driver closed")
            except Exception as e:
                self.logger.error(f"Error closing driver: {e}")
            finally:
                self.driver = None