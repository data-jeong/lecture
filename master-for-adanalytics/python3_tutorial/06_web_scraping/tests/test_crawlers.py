"""
크롤러 테스트
"""

import pytest
import asyncio
from unittest.mock import Mock, patch
from news_crawler.core import RequestsCrawler, HttpxCrawler


class TestRequestsCrawler:
    """Requests 크롤러 테스트"""
    
    def test_crawler_init(self):
        """크롤러 초기화 테스트"""
        crawler = RequestsCrawler(timeout=20, retry_count=5)
        
        assert crawler.timeout == 20
        assert crawler.retry_count == 5
        assert crawler.session is not None
    
    def test_url_validation(self):
        """URL 유효성 검사 테스트"""
        crawler = RequestsCrawler()
        
        assert crawler.validate_url("https://example.com")
        assert crawler.validate_url("http://test.com/path")
        assert not crawler.validate_url("invalid-url")
        assert not crawler.validate_url("")
    
    def test_should_crawl(self):
        """크롤링 가능 여부 테스트"""
        crawler = RequestsCrawler()
        
        assert crawler.should_crawl("https://example.com/article")
        assert not crawler.should_crawl("https://example.com/image.jpg")
        assert not crawler.should_crawl("https://example.com/file.pdf")
    
    @patch('requests.Session.get')
    def test_crawl_success(self, mock_get):
        """성공적인 크롤링 테스트"""
        # Mock 응답 설정
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.text = '<html><head><title>Test</title></head><body><p>Content</p></body></html>'
        mock_response.content = b'test content'
        mock_response.apparent_encoding = 'utf-8'
        mock_get.return_value = mock_response
        
        crawler = RequestsCrawler()
        result = crawler.crawl("https://example.com")
        
        assert result.success
        assert result.url == "https://example.com"
        assert "Test" in result.title
        crawler.close()
    
    @patch('requests.Session.get')
    def test_crawl_failure(self, mock_get):
        """실패 크롤링 테스트"""
        mock_get.side_effect = Exception("Network error")
        
        crawler = RequestsCrawler(retry_count=1)
        result = crawler.crawl("https://example.com")
        
        assert not result.success
        assert "Network error" in result.error
        crawler.close()


class TestHttpxCrawler:
    """HTTPX 크롤러 테스트"""
    
    def test_crawler_init(self):
        """크롤러 초기화 테스트"""
        crawler = HttpxCrawler(max_connections=5)
        
        assert crawler.max_connections == 5
        assert 'http2' in crawler.client_config
    
    @pytest.mark.asyncio
    async def test_crawl_async(self):
        """비동기 크롤링 테스트"""
        crawler = HttpxCrawler()
        
        # Mock 사용이 복잡하므로 실제 테스트는 통합 테스트에서
        # 여기서는 기본 설정만 확인
        assert crawler.client_config['timeout'] is not None
        assert crawler.client_config['limits'] is not None


@pytest.mark.integration
class TestCrawlerIntegration:
    """크롤러 통합 테스트"""
    
    def test_httpbin_get(self):
        """HTTPBin으로 실제 요청 테스트"""
        crawler = RequestsCrawler()
        result = crawler.crawl("https://httpbin.org/json")
        
        assert result.success
        assert result.content is not None
        crawler.close()
    
    @pytest.mark.asyncio
    async def test_httpx_httpbin(self):
        """HTTPX로 실제 요청 테스트"""
        crawler = HttpxCrawler()
        result = await crawler.crawl_async("https://httpbin.org/json")
        
        assert result.success
        assert result.content is not None