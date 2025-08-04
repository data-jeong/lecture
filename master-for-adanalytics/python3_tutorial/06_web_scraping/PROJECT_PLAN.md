# 06. 웹 스크래핑 - 멀티 크롤러 시스템

## 프로젝트 개요
다양한 웹 스크래핑 도구와 기법을 활용하여 강력한 멀티 크롤러 시스템을 구축합니다.

## 학습 목표
- 정적/동적 웹페이지 크롤링 차이 이해
- 다양한 크롤링 도구 마스터 (requests, Selenium, Scrapy)
- 비동기 HTTP 요청 처리
- 크롤링 윤리와 robots.txt 준수
- 안티 크롤링 우회 기법

## 프로젝트 기능

### 1. 기본 크롤러 (requests + BeautifulSoup)
- HTML 파싱과 CSS 선택자
- 뉴스 사이트 크롤링
- 이미지 다운로드
- 페이지네이션 처리
- 폼 데이터 전송

### 2. 동적 크롤러 (Selenium)
- JavaScript 렌더링 페이지 처리
- 스크롤 이벤트 처리
- 클릭/입력 자동화
- 스크린샷 캡처
- 헤드리스 브라우저

### 3. 대규모 크롤러 (Scrapy)
- Spider 작성
- Item Pipeline
- 미들웨어 커스터마이징
- 분산 크롤링
- 크롤링 스케줄링

### 4. 비동기 크롤러 (httpx + aiohttp)
- 동시 다중 요청
- 연결 풀 관리
- 타임아웃 처리
- 재시도 로직
- 속도 제한

### 5. Curl 래퍼
- subprocess로 curl 명령 실행
- 다양한 HTTP 메서드
- 헤더 커스터마이징
- 프록시 설정
- 인증 처리

### 6. 고급 기능
- User-Agent 로테이션
- 프록시 서버 활용
- 쿠키/세션 관리
- CAPTCHA 처리 전략
- 크롤링 데이터 저장 (JSON, CSV, SQLite)

## 주요 학습 포인트
```python
import requests
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.common.by import By
import scrapy
import httpx
import aiohttp
import asyncio
from fake_useragent import UserAgent
import subprocess
```

## 코드 구조
```
web_scraping/
    crawlers/
        __init__.py
        basic_crawler.py      # requests + BeautifulSoup
        dynamic_crawler.py    # Selenium
        scrapy_spider/       # Scrapy 프로젝트
            spiders/
                news_spider.py
                shop_spider.py
            items.py
            pipelines.py
            settings.py
        async_crawler.py     # httpx/aiohttp
        curl_wrapper.py      # curl 명령어 래퍼
    
    utils/
        proxy_manager.py     # 프록시 관리
        user_agents.py       # User-Agent 로테이션
        rate_limiter.py      # 속도 제한
        data_storage.py      # 데이터 저장
        robots_parser.py     # robots.txt 파서
    
    examples/
        news_crawler.py      # 뉴스 사이트 예제
        ecommerce_crawler.py # 쇼핑몰 예제
        social_crawler.py    # SNS 예제
        api_crawler.py       # API 크롤링 예제
    
    config/
        settings.py          # 전역 설정
        targets.json         # 크롤링 대상 URL
    
main.py                     # 통합 실행 프로그램
requirements.txt            # 의존성 패키지
```

## 크롤링 예제

### 1. 기본 크롤링
```python
def crawl_static_page(url):
    headers = {'User-Agent': UserAgent().random}
    response = requests.get(url, headers=headers)
    soup = BeautifulSoup(response.text, 'html.parser')
    return soup.select('.article-title')
```

### 2. 동적 페이지 크롤링
```python
async def crawl_dynamic_page(url):
    options = webdriver.ChromeOptions()
    options.add_argument('--headless')
    driver = webdriver.Chrome(options=options)
    driver.get(url)
    await asyncio.sleep(3)  # JS 렌더링 대기
    return driver.page_source
```

### 3. Scrapy Spider
```python
class NewsSpider(scrapy.Spider):
    name = 'news'
    custom_settings = {
        'DOWNLOAD_DELAY': 1,
        'CONCURRENT_REQUESTS': 16,
    }
    
    def parse(self, response):
        for article in response.css('.article'):
            yield {
                'title': article.css('h2::text').get(),
                'url': article.css('a::attr(href)').get(),
            }
```

## 실행 방법
```bash
# 기본 크롤러 실행
python main.py --crawler basic --url https://example.com

# Selenium 크롤러
python main.py --crawler selenium --headless

# Scrapy 실행
scrapy crawl news -o news.json

# 비동기 크롤러 (여러 URL 동시 처리)
python main.py --crawler async --urls urls.txt

# 통합 크롤링 (모든 방식 비교)
python main.py --benchmark --url https://example.com
```

## 윤리적 크롤링 가이드
- robots.txt 확인 및 준수
- 적절한 딜레이 설정 (1-3초)
- 과도한 요청 자제
- API가 있다면 API 우선 사용
- 저작권 및 이용약관 확인