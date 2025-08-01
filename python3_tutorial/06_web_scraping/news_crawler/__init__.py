"""
뉴스 크롤러 패키지
다양한 웹 스크래핑 도구를 활용한 뉴스 수집 시스템
"""

__version__ = "1.0.0"

from .core import (
    RequestsCrawler,
    SeleniumCrawler,
    ScrapyCrawler,
    HttpxCrawler
)

from .extractors import (
    NewsExtractor,
    CommentExtractor,
    MetadataExtractor
)

from .analyzers import (
    SentimentAnalyzer,
    KeywordExtractor,
    TrendAnalyzer
)

__all__ = [
    "RequestsCrawler",
    "SeleniumCrawler", 
    "ScrapyCrawler",
    "HttpxCrawler",
    "NewsExtractor",
    "CommentExtractor",
    "MetadataExtractor",
    "SentimentAnalyzer",
    "KeywordExtractor",
    "TrendAnalyzer",
]