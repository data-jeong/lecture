# Scrapy settings for news_spider project
#
# For simplicity, this file contains only settings considered important or
# commonly used. You can find more settings consulting the documentation:
#
#     https://docs.scrapy.org/en/latest/topics/settings.html
#     https://docs.scrapy.org/en/latest/topics/downloader-middleware.html
#     https://docs.scrapy.org/en/latest/topics/spider-middleware.html

BOT_NAME = 'news_spider'

SPIDER_MODULES = ['news_spider.spiders']
NEWSPIDER_MODULE = 'news_spider.spiders'

# 로봇 배제 표준 준수
ROBOTSTXT_OBEY = True

# 사용자 에이전트
USER_AGENT = 'news_spider (+http://www.yourdomain.com)'

# 동시 요청 설정
CONCURRENT_REQUESTS = 16
CONCURRENT_REQUESTS_PER_DOMAIN = 8

# 다운로드 지연 (초)
DOWNLOAD_DELAY = 1
RANDOMIZE_DOWNLOAD_DELAY = 0.5

# AutoThrottle 설정
AUTOTHROTTLE_ENABLED = True
AUTOTHROTTLE_START_DELAY = 1
AUTOTHROTTLE_MAX_DELAY = 10
AUTOTHROTTLE_TARGET_CONCURRENCY = 2.0
AUTOTHROTTLE_DEBUG = False

# 캐시 설정
HTTPCACHE_ENABLED = True
HTTPCACHE_EXPIRATION_SECS = 3600

# 미들웨어 설정
SPIDER_MIDDLEWARES = {
    'news_spider.middlewares.NewsSpiderSpiderMiddleware': 543,
}

DOWNLOADER_MIDDLEWARES = {
    'news_spider.middlewares.NewsSpiderDownloaderMiddleware': 543,
}

# 파이프라인 설정
ITEM_PIPELINES = {
    'news_spider.pipelines.ValidationPipeline': 300,
    'news_spider.pipelines.DuplicatesPipeline': 400,
    'news_spider.pipelines.DatabasePipeline': 500,
    'news_spider.pipelines.FilesPipeline': 600,
}

# 로그 레벨
LOG_LEVEL = 'INFO'

# 요청 필터링
DUPEFILTER_DEBUG = True

# 확장 기능
EXTENSIONS = {
    'scrapy.extensions.telnet.TelnetConsole': None,
}

# 쿠키 설정
COOKIES_ENABLED = True

# 미디어 파이프라인 설정
MEDIA_ALLOW_REDIRECTS = True

# 통계 수집
STATS_CLASS = 'scrapy.statscollectors.MemoryStatsCollector'

# 메모리 사용량 제한
MEMUSAGE_ENABLED = True
MEMUSAGE_LIMIT_MB = 2048
MEMUSAGE_WARNING_MB = 1024

# 재시도 설정
RETRY_ENABLED = True
RETRY_TIMES = 3
RETRY_HTTP_CODES = [500, 502, 503, 504, 522, 524, 408, 429]

# 압축 설정
COMPRESSION_ENABLED = True

# DNS 캐시
DNSCACHE_ENABLED = True
DNSCACHE_SIZE = 10000