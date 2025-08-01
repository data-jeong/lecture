"""
크롤러 기본 클래스
모든 크롤러의 공통 인터페이스 정의
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import List, Dict, Optional, Any
from datetime import datetime
import logging
from urllib.parse import urlparse, urljoin


@dataclass
class CrawlResult:
    """크롤링 결과"""
    url: str
    title: Optional[str] = None
    content: Optional[str] = None
    author: Optional[str] = None
    published_date: Optional[datetime] = None
    images: List[str] = field(default_factory=list)
    links: List[str] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)
    raw_html: Optional[str] = None
    crawled_at: datetime = field(default_factory=datetime.now)
    success: bool = True
    error: Optional[str] = None
    
    def to_dict(self) -> dict:
        """딕셔너리로 변환"""
        return {
            "url": self.url,
            "title": self.title,
            "content": self.content,
            "author": self.author,
            "published_date": self.published_date.isoformat() if self.published_date else None,
            "images": self.images,
            "links": self.links,
            "metadata": self.metadata,
            "crawled_at": self.crawled_at.isoformat(),
            "success": self.success,
            "error": self.error
        }


class BaseCrawler(ABC):
    """크롤러 기본 클래스"""
    
    def __init__(self, 
                 timeout: int = 30,
                 retry_count: int = 3,
                 delay: float = 1.0,
                 user_agent: Optional[str] = None,
                 proxy: Optional[str] = None):
        """
        Args:
            timeout: 요청 타임아웃 (초)
            retry_count: 재시도 횟수
            delay: 요청 간 지연 시간 (초)
            user_agent: User-Agent 헤더
            proxy: 프록시 서버 URL
        """
        self.timeout = timeout
        self.retry_count = retry_count
        self.delay = delay
        self.user_agent = user_agent or self._get_default_user_agent()
        self.proxy = proxy
        
        # 로거 설정
        self.logger = logging.getLogger(self.__class__.__name__)
        
        # 통계
        self.stats = {
            "total_requests": 0,
            "successful_requests": 0,
            "failed_requests": 0,
            "total_bytes": 0,
            "start_time": None,
            "end_time": None
        }
    
    @abstractmethod
    def crawl(self, url: str) -> CrawlResult:
        """단일 URL 크롤링"""
        pass
    
    @abstractmethod
    def crawl_multiple(self, urls: List[str]) -> List[CrawlResult]:
        """여러 URL 크롤링"""
        pass
    
    def validate_url(self, url: str) -> bool:
        """URL 유효성 검사"""
        try:
            result = urlparse(url)
            return all([result.scheme, result.netloc])
        except Exception:
            return False
    
    def normalize_url(self, url: str, base_url: Optional[str] = None) -> str:
        """URL 정규화"""
        if not url:
            return ""
        
        # 상대 경로 처리
        if base_url and not url.startswith(('http://', 'https://')):
            return urljoin(base_url, url)
        
        return url
    
    def should_crawl(self, url: str) -> bool:
        """크롤링 가능 여부 확인"""
        # robots.txt 확인 등
        # 여기서는 간단히 구현
        if not self.validate_url(url):
            return False
        
        # 이미지, 문서 파일 등 제외
        excluded_extensions = ['.jpg', '.png', '.pdf', '.zip', '.mp4']
        for ext in excluded_extensions:
            if url.lower().endswith(ext):
                return False
        
        return True
    
    def _get_default_user_agent(self) -> str:
        """기본 User-Agent"""
        return (
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
            "AppleWebKit/537.36 (KHTML, like Gecko) "
            "Chrome/120.0.0.0 Safari/537.36"
        )
    
    def update_stats(self, success: bool, bytes_downloaded: int = 0):
        """통계 업데이트"""
        self.stats["total_requests"] += 1
        
        if success:
            self.stats["successful_requests"] += 1
        else:
            self.stats["failed_requests"] += 1
        
        self.stats["total_bytes"] += bytes_downloaded
    
    def get_stats(self) -> dict:
        """통계 반환"""
        stats = self.stats.copy()
        
        if stats["start_time"] and stats["end_time"]:
            duration = (stats["end_time"] - stats["start_time"]).total_seconds()
            stats["duration"] = duration
            stats["requests_per_second"] = stats["total_requests"] / duration if duration > 0 else 0
        
        return stats
    
    def reset_stats(self):
        """통계 초기화"""
        self.stats = {
            "total_requests": 0,
            "successful_requests": 0,
            "failed_requests": 0,
            "total_bytes": 0,
            "start_time": None,
            "end_time": None
        }
    
    @abstractmethod
    def close(self):
        """리소스 정리"""
        pass