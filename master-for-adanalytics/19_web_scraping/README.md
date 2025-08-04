# 19. Web Scraping - 웹 스크래핑

## 📚 과정 소개
경쟁사 광고 모니터링, 시장 조사, 가격 추적을 위한 웹 스크래핑 기술을 마스터합니다. BeautifulSoup, Scrapy, Selenium을 활용한 대규모 데이터 수집을 학습합니다.

## 🎯 학습 목표
- 경쟁사 광고 모니터링 시스템
- 동적 웹사이트 스크래핑
- 대규모 데이터 수집 파이프라인
- 안티 스크래핑 우회 기법

## 📖 주요 내용

### 기본 웹 스크래핑
```python
import requests
from bs4 import BeautifulSoup
import pandas as pd
import time
import random
from typing import List, Dict, Optional
from urllib.parse import urljoin, urlparse
import logging
from dataclasses import dataclass
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options

@dataclass
class AdData:
    """광고 데이터 구조"""
    title: str
    description: str
    url: str
    image_url: Optional[str]
    platform: str
    advertiser: str
    timestamp: str
    price: Optional[float] = None
    category: Optional[str] = None

class BaseWebScraper:
    """기본 웹 스크래퍼"""
    
    def __init__(self, delay_range: tuple = (1, 3)):
        self.session = requests.Session()
        self.delay_range = delay_range
        self.setup_session()
        
    def setup_session(self):
        """세션 설정"""
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'ko-KR,ko;q=0.8,en-US;q=0.5,en;q=0.3',
            'Accept-Encoding': 'gzip, deflate',
            'Connection': 'keep-alive',
        }
        self.session.headers.update(headers)
        
    def get_page(self, url: str, **kwargs) -> Optional[requests.Response]:
        """페이지 요청"""
        try:
            response = self.session.get(url, **kwargs)
            response.raise_for_status()
            
            # 요청 간 지연
            time.sleep(random.uniform(*self.delay_range))
            
            return response
        except requests.RequestException as e:
            logging.error(f"Error fetching {url}: {e}")
            return None
    
    def parse_html(self, html: str) -> BeautifulSoup:
        """HTML 파싱"""
        return BeautifulSoup(html, 'html.parser')

class CompetitorAdMonitor(BaseWebScraper):
    """경쟁사 광고 모니터링"""
    
    def __init__(self):
        super().__init__()
        self.monitored_sites = {
            'naver': {
                'search_url': 'https://search.naver.com/search.naver',
                'ad_selector': '.ad_area',
                'title_selector': '.ad_tit',
                'desc_selector': '.ad_desc',
                'url_selector': '.ad_tit a'
            },
            'google': {
                'search_url': 'https://www.google.com/search',
                'ad_selector': '[data-text-ad]',
                'title_selector': 'h3',
                'desc_selector': '.VwiC3b',
                'url_selector': 'h3 a'
            }
        }
    
    def monitor_search_ads(self, keywords: List[str], 
                          platforms: List[str] = ['naver', 'google']) -> List[AdData]:
        """검색 광고 모니터링"""
        all_ads = []
        
        for keyword in keywords:
            for platform in platforms:
                if platform in self.monitored_sites:
                    ads = self._scrape_search_ads(keyword, platform)
                    all_ads.extend(ads)
                    
        return all_ads
    
    def _scrape_search_ads(self, keyword: str, platform: str) -> List[AdData]:
        """특정 플랫폼의 검색 광고 스크래핑"""
        config = self.monitored_sites[platform]
        
        # 검색 URL 구성
        params = {'query': keyword} if platform == 'naver' else {'q': keyword}
        response = self.get_page(config['search_url'], params=params)
        
        if not response:
            return []
        
        soup = self.parse_html(response.text)
        ads = []
        
        # 광고 영역 찾기
        ad_elements = soup.select(config['ad_selector'])
        
        for ad_element in ad_elements:
            try:
                # 광고 정보 추출
                title_elem = ad_element.select_one(config['title_selector'])
                desc_elem = ad_element.select_one(config['desc_selector'])
                url_elem = ad_element.select_one(config['url_selector'])
                
                if title_elem and url_elem:
                    ad_data = AdData(
                        title=title_elem.get_text(strip=True),
                        description=desc_elem.get_text(strip=True) if desc_elem else '',
                        url=url_elem.get('href', ''),
                        image_url=None,
                        platform=platform,
                        advertiser=self._extract_advertiser(url_elem.get('href', '')),
                        timestamp=pd.Timestamp.now().isoformat()
                    )
                    ads.append(ad_data)
                    
            except Exception as e:
                logging.error(f"Error parsing ad element: {e}")
                continue
                
        return ads
    
    def _extract_advertiser(self, url: str) -> str:
        """URL에서 광고주 도메인 추출"""
        try:
            parsed = urlparse(url)
            return parsed.netloc
        except:
            return 'unknown'
    
    def monitor_shopping_ads(self, product_keywords: List[str]) -> List[AdData]:
        """쇼핑 광고 모니터링"""
        shopping_sites = {
            'naver_shopping': 'https://shopping.naver.com/search/all',
            'coupang': 'https://www.coupang.com/np/search',
            'gmarket': 'http://browse.gmarket.co.kr/search'
        }
        
        all_ads = []
        
        for keyword in product_keywords:
            for site_name, base_url in shopping_sites.items():
                ads = self._scrape_shopping_site(keyword, site_name, base_url)
                all_ads.extend(ads)
                
        return all_ads
    
    def _scrape_shopping_site(self, keyword: str, site_name: str, base_url: str) -> List[AdData]:
        """쇼핑 사이트 스크래핑"""
        params = {'query': keyword}
        response = self.get_page(base_url, params=params)
        
        if not response:
            return []
        
        soup = self.parse_html(response.text)
        ads = []
        
        # 사이트별 선택자 (간소화)
        selectors = {
            'naver_shopping': {
                'container': '.basicList_item__2XT81',
                'title': '.basicList_title__3P9Q7',
                'price': '.price_num__2WUXn',
                'link': 'a'
            },
            'coupang': {
                'container': '.search-product',
                'title': '.name',
                'price': '.price-value',
                'link': 'a'
            }
        }
        
        if site_name in selectors:
            config = selectors[site_name]
            items = soup.select(config['container'])
            
            for item in items[:10]:  # 상위 10개만
                try:
                    title_elem = item.select_one(config['title'])
                    price_elem = item.select_one(config['price'])
                    link_elem = item.select_one(config['link'])
                    
                    if title_elem and link_elem:
                        ad_data = AdData(
                            title=title_elem.get_text(strip=True),
                            description='',
                            url=urljoin(base_url, link_elem.get('href', '')),
                            image_url=None,
                            platform=site_name,
                            advertiser=site_name,
                            timestamp=pd.Timestamp.now().isoformat(),
                            price=self._extract_price(price_elem.get_text() if price_elem else '')
                        )
                        ads.append(ad_data)
                        
                except Exception as e:
                    logging.error(f"Error parsing shopping item: {e}")
                    continue
        
        return ads
    
    def _extract_price(self, price_text: str) -> Optional[float]:
        """가격 텍스트에서 숫자 추출"""
        import re
        if not price_text:
            return None
        # 숫자만 추출
        numbers = re.findall(r'[\d,]+', price_text.replace(',', ''))
        return float(numbers[0]) if numbers else None

class DynamicWebScraper:
    """동적 웹사이트 스크래핑 (Selenium)"""
    
    def __init__(self, headless: bool = True):
        self.headless = headless
        self.driver = None
        
    def setup_driver(self):
        """WebDriver 설정"""
        options = Options()
        if self.headless:
            options.add_argument('--headless')
        options.add_argument('--no-sandbox')
        options.add_argument('--disable-dev-shm-usage')
        options.add_argument('--disable-gpu')
        options.add_argument('--window-size=1920,1080')
        
        # User-Agent 설정
        options.add_argument('--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36')
        
        self.driver = webdriver.Chrome(options=options)
        self.driver.implicitly_wait(10)
        
    def close_driver(self):
        """WebDriver 종료"""
        if self.driver:
            self.driver.quit()
    
    def scrape_instagram_ads(self, hashtags: List[str]) -> List[AdData]:
        """Instagram 광고 스크래핑"""
        if not self.driver:
            self.setup_driver()
            
        all_ads = []
        
        for hashtag in hashtags:
            try:
                # Instagram 해시태그 페이지 이동
                url = f"https://www.instagram.com/explore/tags/{hashtag}/"
                self.driver.get(url)
                
                # 페이지 로딩 대기
                time.sleep(3)
                
                # 스크롤하여 더 많은 콘텐츠 로드
                self._scroll_page(3)
                
                # 광고 포스트 찾기 (Sponsored 표시가 있는 것들)
                sponsored_posts = self.driver.find_elements(
                    By.XPATH, "//article[contains(.//text(), 'Sponsored')]"
                )
                
                for post in sponsored_posts[:5]:  # 상위 5개만
                    try:
                        # 포스트 클릭
                        post.click()
                        time.sleep(2)
                        
                        # 광고 정보 추출
                        ad_data = self._extract_instagram_ad_info()
                        if ad_data:
                            all_ads.append(ad_data)
                        
                        # 모달 닫기
                        self.driver.find_element(By.XPATH, "//button[contains(@aria-label, 'Close')]").click()
                        time.sleep(1)
                        
                    except Exception as e:
                        logging.error(f"Error processing Instagram post: {e}")
                        continue
                        
            except Exception as e:
                logging.error(f"Error scraping Instagram hashtag {hashtag}: {e}")
                continue
                
        return all_ads
    
    def _scroll_page(self, times: int):
        """페이지 스크롤"""
        for _ in range(times):
            self.driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
            time.sleep(2)
    
    def _extract_instagram_ad_info(self) -> Optional[AdData]:
        """Instagram 광고 정보 추출"""
        try:
            # 광고 텍스트
            caption_elem = self.driver.find_element(
                By.XPATH, "//article//span[contains(@class, 'caption')]"
            )
            caption = caption_elem.text if caption_elem else ''
            
            # 광고주 정보
            advertiser_elem = self.driver.find_element(
                By.XPATH, "//header//a[contains(@class, 'username')]"
            )
            advertiser = advertiser_elem.text if advertiser_elem else 'unknown'
            
            # 이미지 URL
            img_elem = self.driver.find_element(By.TAG_NAME, "img")
            image_url = img_elem.get_attribute('src') if img_elem else None
            
            return AdData(
                title=caption[:100],  # 처음 100자
                description=caption,
                url=self.driver.current_url,
                image_url=image_url,
                platform='instagram',
                advertiser=advertiser,
                timestamp=pd.Timestamp.now().isoformat()
            )
            
        except Exception as e:
            logging.error(f"Error extracting Instagram ad info: {e}")
            return None
    
    def scrape_youtube_ads(self, search_terms: List[str]) -> List[AdData]:
        """YouTube 광고 스크래핑"""
        if not self.driver:
            self.setup_driver()
            
        all_ads = []
        
        for term in search_terms:
            try:
                # YouTube 검색
                search_url = f"https://www.youtube.com/results?search_query={term}"
                self.driver.get(search_url)
                
                # 페이지 로딩 대기
                WebDriverWait(self.driver, 10).until(
                    EC.presence_of_element_located((By.ID, "contents"))
                )
                
                # 광고 비디오 찾기
                ad_videos = self.driver.find_elements(
                    By.XPATH, "//span[contains(text(), 'Ad')]/ancestor::div[contains(@class, 'ytd-video-renderer')]"
                )
                
                for ad_video in ad_videos[:3]:  # 상위 3개만
                    try:
                        title_elem = ad_video.find_element(By.ID, "video-title")
                        channel_elem = ad_video.find_element(By.XPATH, ".//a[contains(@class, 'channel-name')]")
                        
                        ad_data = AdData(
                            title=title_elem.text,
                            description='',
                            url=title_elem.get_attribute('href'),
                            image_url=None,
                            platform='youtube',
                            advertiser=channel_elem.text,
                            timestamp=pd.Timestamp.now().isoformat()
                        )
                        all_ads.append(ad_data)
                        
                    except Exception as e:
                        logging.error(f"Error processing YouTube ad: {e}")
                        continue
                        
            except Exception as e:
                logging.error(f"Error scraping YouTube for {term}: {e}")
                continue
                
        return all_ads

class ScrapingPipeline:
    """스크래핑 파이프라인"""
    
    def __init__(self):
        self.results = []
        self.scrapers = {
            'competitor': CompetitorAdMonitor(),
            'dynamic': DynamicWebScraper()
        }
        
    def run_monitoring_campaign(self, config: Dict) -> pd.DataFrame:
        """모니터링 캠페인 실행"""
        # 검색 광고 모니터링
        if 'search_keywords' in config:
            search_ads = self.scrapers['competitor'].monitor_search_ads(
                config['search_keywords'],
                config.get('platforms', ['naver', 'google'])
            )
            self.results.extend(search_ads)
        
        # 쇼핑 광고 모니터링
        if 'product_keywords' in config:
            shopping_ads = self.scrapers['competitor'].monitor_shopping_ads(
                config['product_keywords']
            )
            self.results.extend(shopping_ads)
        
        # 소셜 미디어 광고 모니터링
        if 'social_hashtags' in config:
            social_ads = self.scrapers['dynamic'].scrape_instagram_ads(
                config['social_hashtags']
            )
            self.results.extend(social_ads)
        
        # 결과를 DataFrame으로 변환
        return self._results_to_dataframe()
    
    def _results_to_dataframe(self) -> pd.DataFrame:
        """결과를 DataFrame으로 변환"""
        if not self.results:
            return pd.DataFrame()
        
        data = []
        for ad in self.results:
            data.append({
                'title': ad.title,
                'description': ad.description,
                'url': ad.url,
                'image_url': ad.image_url,
                'platform': ad.platform,
                'advertiser': ad.advertiser,
                'timestamp': ad.timestamp,
                'price': ad.price,
                'category': ad.category
            })
        
        return pd.DataFrame(data)
    
    def save_results(self, filepath: str, format: str = 'csv'):
        """결과 저장"""
        df = self._results_to_dataframe()
        
        if format == 'csv':
            df.to_csv(filepath, index=False, encoding='utf-8')
        elif format == 'json':
            df.to_json(filepath, orient='records', force_ascii=False, indent=2)
        elif format == 'excel':
            df.to_excel(filepath, index=False)
    
    def cleanup(self):
        """리소스 정리"""
        self.scrapers['dynamic'].close_driver()

class AntiScrapingHandler:
    """안티 스크래핑 우회"""
    
    def __init__(self):
        self.proxies = []
        self.user_agents = [
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
            'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36',
            'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36'
        ]
        
    def rotate_user_agent(self) -> str:
        """User-Agent 로테이션"""
        return random.choice(self.user_agents)
    
    def add_proxies(self, proxy_list: List[str]):
        """프록시 추가"""
        self.proxies.extend(proxy_list)
    
    def get_random_proxy(self) -> Optional[Dict]:
        """랜덤 프록시 선택"""
        if not self.proxies:
            return None
        
        proxy = random.choice(self.proxies)
        return {
            'http': proxy,
            'https': proxy
        }
    
    def handle_rate_limiting(self, retry_count: int = 3):
        """속도 제한 처리"""
        base_delay = 2
        for attempt in range(retry_count):
            delay = base_delay * (2 ** attempt) + random.uniform(0, 1)
            time.sleep(delay)
            yield attempt + 1

class PriceTracker:
    """가격 추적기"""
    
    def __init__(self):
        self.scraper = BaseWebScraper()
        
    def track_competitor_prices(self, products: List[Dict]) -> pd.DataFrame:
        """경쟁사 가격 추적"""
        results = []
        
        for product in products:
            product_name = product['name']
            sites = product['sites']
            
            for site, config in sites.items():
                try:
                    price = self._scrape_price(config['url'], config['selector'])
                    
                    results.append({
                        'product': product_name,
                        'site': site,
                        'price': price,
                        'timestamp': pd.Timestamp.now(),
                        'url': config['url']
                    })
                    
                except Exception as e:
                    logging.error(f"Error tracking price for {product_name} on {site}: {e}")
                    continue
        
        return pd.DataFrame(results)
    
    def _scrape_price(self, url: str, selector: str) -> Optional[float]:
        """가격 스크래핑"""
        response = self.scraper.get_page(url)
        if not response:
            return None
        
        soup = self.scraper.parse_html(response.text)
        price_elem = soup.select_one(selector)
        
        if price_elem:
            price_text = price_elem.get_text(strip=True)
            return self._extract_price(price_text)
        
        return None
    
    def _extract_price(self, price_text: str) -> Optional[float]:
        """가격 추출"""
        import re
        # 숫자와 쉼표만 추출
        numbers = re.findall(r'[\d,]+', price_text.replace(',', ''))
        if numbers:
            try:
                return float(numbers[0])
            except ValueError:
                return None
        return None

# 사용 예시
def example_monitoring_campaign():
    """모니터링 캠페인 예시"""
    # 파이프라인 설정
    pipeline = ScrapingPipeline()
    
    # 모니터링 설정
    config = {
        'search_keywords': ['마케팅 도구', '광고 플랫폼', 'CRM 소프트웨어'],
        'product_keywords': ['노트북', '스마트폰', '태블릿'],
        'social_hashtags': ['마케팅', '광고', '디지털마케팅'],
        'platforms': ['naver', 'google']
    }
    
    try:
        # 모니터링 실행
        results_df = pipeline.run_monitoring_campaign(config)
        
        # 결과 저장
        pipeline.save_results('competitor_ads_monitoring.csv')
        
        # 결과 분석
        print(f"총 {len(results_df)} 개의 광고 수집됨")
        print(f"플랫폼별 분포: {results_df['platform'].value_counts().to_dict()}")
        
        return results_df
        
    finally:
        # 리소스 정리
        pipeline.cleanup()

if __name__ == "__main__":
    results = example_monitoring_campaign()
```

## 🚀 프로젝트
1. **경쟁사 광고 모니터링 시스템**
2. **가격 추적 및 알림 서비스**
3. **소셜 미디어 트렌드 분석**
4. **시장 조사 자동화 플랫폼**