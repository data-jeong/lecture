# 프로젝트 6: 뉴스 크롤러 (Web Scraping)

다양한 웹 스크래핑 도구(Selenium, requests, curl, Scrapy, httpx)를 활용한 뉴스 수집 및 분석 시스템입니다.

## 🎯 학습 목표

- 다양한 웹 스크래핑 도구의 특징과 사용법
- 동적/정적 웹 페이지 크롤링
- 반크롤링 회피 기법
- 대규모 크롤링 시스템 설계
- 데이터 추출 및 정제

## 📁 프로젝트 구조

```
06_web_scraping/
├── news_crawler/
│   ├── __init__.py
│   ├── core/
│   │   ├── __init__.py
│   │   ├── base_crawler.py      # 크롤러 기본 클래스
│   │   ├── requests_crawler.py  # requests 기반 크롤러
│   │   ├── selenium_crawler.py  # Selenium 기반 크롤러
│   │   ├── scrapy_crawler.py    # Scrapy 기반 크롤러
│   │   └── httpx_crawler.py     # httpx 비동기 크롤러
│   ├── utils/
│   │   ├── __init__.py
│   │   ├── parser.py            # HTML 파싱 유틸리티
│   │   ├── proxy_manager.py     # 프록시 관리
│   │   ├── user_agent.py        # User-Agent 관리
│   │   └── anti_bot.py          # 반크롤링 회피
│   ├── extractors/
│   │   ├── __init__.py
│   │   ├── news_extractor.py    # 뉴스 데이터 추출
│   │   ├── comment_extractor.py # 댓글 추출
│   │   └── metadata_extractor.py # 메타데이터 추출
│   ├── storage/
│   │   ├── __init__.py
│   │   ├── file_storage.py      # 파일 저장
│   │   ├── database.py          # DB 저장
│   │   └── cache.py             # 캐싱
│   ├── analyzers/
│   │   ├── __init__.py
│   │   ├── sentiment.py         # 감정 분석
│   │   ├── keyword.py           # 키워드 추출
│   │   └── trend.py             # 트렌드 분석
│   ├── main.py                  # CLI 인터페이스
│   └── examples.py              # 사용 예제
├── scrapy_project/             # Scrapy 프로젝트
│   ├── scrapy.cfg
│   └── news_spider/
│       ├── __init__.py
│       ├── items.py
│       ├── pipelines.py
│       ├── settings.py
│       └── spiders/
│           └── news.py
├── tests/
│   ├── __init__.py
│   ├── test_crawlers.py
│   ├── test_extractors.py
│   └── test_analyzers.py
├── requirements.txt
└── README.md
```

## 🚀 시작하기

### 설치
```bash
cd 06_web_scraping
pip install -r requirements.txt

# Scrapy 프로젝트 초기화
cd scrapy_project
scrapy crawl news
```

### 기본 사용법

#### 1. Requests 크롤러
```python
from news_crawler.core import RequestsCrawler

crawler = RequestsCrawler()
articles = crawler.crawl_news("https://news.ycombinator.com")
```

#### 2. Selenium 크롤러 (동적 페이지)
```python
from news_crawler.core import SeleniumCrawler

crawler = SeleniumCrawler(headless=True)
articles = crawler.crawl_news("https://dynamic-news-site.com")
```

#### 3. Scrapy 크롤러 (대규모)
```bash
cd scrapy_project
scrapy crawl news -a start_urls=https://example.com
```

#### 4. HTTPX 비동기 크롤러
```python
import asyncio
from news_crawler.core import HttpxCrawler

async def main():
    crawler = HttpxCrawler()
    articles = await crawler.crawl_multiple_async(urls)

asyncio.run(main())
```

## 📚 주요 기능

### 1. 다양한 크롤링 방식

#### Requests + BeautifulSoup
```python
# 정적 페이지에 최적
response = requests.get(url, headers=headers)
soup = BeautifulSoup(response.text, 'html.parser')
```

#### Selenium WebDriver
```python
# JavaScript 렌더링 페이지
driver = webdriver.Chrome()
driver.get(url)
WebDriverWait(driver, 10).until(
    EC.presence_of_element_located((By.CLASS_NAME, "article"))
)
```

#### Scrapy Framework
```python
# 대규모 크롤링
class NewsSpider(scrapy.Spider):
    name = 'news'
    
    def parse(self, response):
        for article in response.css('article'):
            yield {
                'title': article.css('h2::text').get(),
                'content': article.css('.content::text').getall()
            }
```

#### HTTPX 비동기
```python
# 고성능 비동기 크롤링
async with httpx.AsyncClient() as client:
    tasks = [client.get(url) for url in urls]
    responses = await asyncio.gather(*tasks)
```

### 2. 반크롤링 회피

- User-Agent 로테이션
- 프록시 서버 사용
- 요청 간격 조절
- 쿠키/세션 관리
- JavaScript 실행

### 3. 데이터 추출 및 분석

- 뉴스 본문 추출
- 메타데이터 파싱
- 댓글 수집
- 감정 분석
- 키워드 추출
- 트렌드 분석

## 🔧 CLI 사용법

```bash
# 단일 사이트 크롤링
python -m news_crawler.main crawl --url https://example.com --type requests

# 여러 사이트 동시 크롤링
python -m news_crawler.main crawl-multiple --urls-file sites.txt --concurrent 5

# 동적 페이지 크롤링
python -m news_crawler.main crawl --url https://spa-site.com --type selenium

# 분석 실행
python -m news_crawler.main analyze --input crawled_data.json --sentiment --keywords

# 모니터링 모드
python -m news_crawler.main monitor --site https://news.com --interval 3600
```

## 📊 크롤러 비교

| 도구 | 장점 | 단점 | 적합한 상황 |
|------|------|------|------------|
| Requests | 빠르고 간단 | JS 렌더링 불가 | 정적 페이지 |
| Selenium | JS 완벽 지원 | 느림, 리소스 많이 사용 | 동적 페이지 |
| Scrapy | 대규모 크롤링 최적화 | 학습 곡선 | 대량 데이터 |
| HTTPX | 비동기, 빠름 | JS 미지원 | 다수 페이지 동시 |

## 🧪 테스트

```bash
# 전체 테스트
pytest

# 특정 크롤러 테스트
pytest tests/test_crawlers.py::TestRequestsCrawler -v

# 커버리지 확인
pytest --cov=news_crawler
```

## 💡 학습 포인트

1. **크롤러 선택**: 상황에 맞는 적절한 도구 선택
2. **윤리적 크롤링**: robots.txt 준수, 서버 부하 고려
3. **에러 처리**: 네트워크 오류, 파싱 오류 대응
4. **확장성**: 대규모 크롤링 시스템 설계

## 🎓 다음 단계

- 프로젝트 7: API 기초 (날씨 API 클라이언트)
- 프로젝트 8: 데이터베이스 (학생 성적 관리)
- 프로젝트 9: FastAPI 백엔드