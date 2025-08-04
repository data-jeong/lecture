"""
기본 API 클라이언트
모든 API 클라이언트의 기반 클래스
"""

import asyncio
import logging
import time
from abc import ABC, abstractmethod
from typing import Optional, Dict, Any, Union
import requests
import aiohttp
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

from ..utils.config import Config


class APIError(Exception):
    """API 오류 기본 클래스"""
    
    def __init__(self, message: str, status_code: Optional[int] = None, response_data: Optional[Dict] = None):
        super().__init__(message)
        self.message = message
        self.status_code = status_code
        self.response_data = response_data
    
    def __str__(self):
        if self.status_code:
            return f"API Error ({self.status_code}): {self.message}"
        return f"API Error: {self.message}"


class RateLimitError(APIError):
    """요청 속도 제한 오류"""
    
    def __init__(self, message: str = "API 요청 속도 제한에 도달했습니다", retry_after: Optional[int] = None):
        super().__init__(message, 429)
        self.retry_after = retry_after


class AuthenticationError(APIError):
    """인증 오류"""
    
    def __init__(self, message: str = "API 키가 유효하지 않습니다"):
        super().__init__(message, 401)


class NetworkError(APIError):
    """네트워크 오류"""
    pass


class BaseAPIClient(ABC):
    """기본 API 클라이언트"""
    
    def __init__(self, config: Config, base_url: str):
        self.config = config
        self.base_url = base_url.rstrip('/')
        self.logger = logging.getLogger(self.__class__.__name__)
        
        # 세션 설정
        self.session = requests.Session()
        self._setup_session()
        
        # 비동기 세션 (필요시 생성)
        self._async_session: Optional[aiohttp.ClientSession] = None
    
    def _setup_session(self):
        """requests 세션 설정"""
        # 재시도 전략
        retry_strategy = Retry(
            total=self.config.max_retries,
            backoff_factor=1,
            status_forcelist=[429, 500, 502, 503, 504],
            allowed_methods=["HEAD", "GET", "OPTIONS"]
        )
        
        adapter = HTTPAdapter(max_retries=retry_strategy)
        self.session.mount("http://", adapter)
        self.session.mount("https://", adapter)
        
        # 기본 헤더 설정
        self.session.headers.update({
            'User-Agent': 'WeatherClient/1.0',
            'Accept': 'application/json',
            'Accept-Encoding': 'gzip, deflate'
        })
        
        # 타임아웃 설정
        self.session.timeout = self.config.request_timeout
    
    def _get_async_session(self) -> aiohttp.ClientSession:
        """비동기 세션 반환 (필요시 생성)"""
        if self._async_session is None or self._async_session.closed:
            timeout = aiohttp.ClientTimeout(total=self.config.request_timeout)
            self._async_session = aiohttp.ClientSession(timeout=timeout)
        return self._async_session
    
    def _build_url(self, endpoint: str) -> str:
        """완전한 URL 생성"""
        endpoint = endpoint.lstrip('/')
        return f"{self.base_url}/{endpoint}"
    
    def _handle_response(self, response: requests.Response) -> Dict[str, Any]:
        """응답 처리"""
        # 상태 코드별 오류 처리
        if response.status_code == 401:
            raise AuthenticationError("API 키가 유효하지 않거나 권한이 없습니다")
        elif response.status_code == 429:
            retry_after = response.headers.get('Retry-After')
            retry_after = int(retry_after) if retry_after else None
            raise RateLimitError(retry_after=retry_after)
        elif response.status_code == 404:
            raise APIError("요청한 리소스를 찾을 수 없습니다", response.status_code)
        elif response.status_code >= 500:
            raise APIError("서버 내부 오류가 발생했습니다", response.status_code)
        elif not response.ok:
            try:
                error_data = response.json()
                message = error_data.get('message', f'HTTP {response.status_code} 오류')
            except:
                message = f'HTTP {response.status_code} 오류'
            raise APIError(message, response.status_code)
        
        # JSON 응답 파싱
        try:
            return response.json()
        except ValueError as e:
            raise APIError(f"응답 JSON 파싱 실패: {e}")
    
    async def _handle_async_response(self, response: aiohttp.ClientResponse) -> Dict[str, Any]:
        """비동기 응답 처리"""
        if response.status == 401:
            raise AuthenticationError("API 키가 유효하지 않거나 권한이 없습니다")
        elif response.status == 429:
            retry_after = response.headers.get('Retry-After')
            retry_after = int(retry_after) if retry_after else None
            raise RateLimitError(retry_after=retry_after)
        elif response.status == 404:
            raise APIError("요청한 리소스를 찾을 수 없습니다", response.status)
        elif response.status >= 500:
            raise APIError("서버 내부 오류가 발생했습니다", response.status)
        elif response.status >= 400:
            try:
                error_data = await response.json()
                message = error_data.get('message', f'HTTP {response.status} 오류')
            except:
                message = f'HTTP {response.status} 오류'
            raise APIError(message, response.status)
        
        # JSON 응답 파싱
        try:
            return await response.json()
        except Exception as e:
            raise APIError(f"응답 JSON 파싱 실패: {e}")
    
    def get(self, endpoint: str, params: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """GET 요청"""
        url = self._build_url(endpoint)
        
        try:
            self.logger.debug(f"GET {url} with params: {params}")
            response = self.session.get(url, params=params)
            return self._handle_response(response)
            
        except requests.exceptions.Timeout:
            raise NetworkError("요청 시간 초과")
        except requests.exceptions.ConnectionError:
            raise NetworkError("네트워크 연결 오류")
        except requests.exceptions.RequestException as e:
            raise NetworkError(f"요청 오류: {e}")
    
    async def get_async(self, endpoint: str, params: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """비동기 GET 요청"""
        url = self._build_url(endpoint)
        session = self._get_async_session()
        
        try:
            self.logger.debug(f"Async GET {url} with params: {params}")
            async with session.get(url, params=params) as response:
                return await self._handle_async_response(response)
                
        except asyncio.TimeoutError:
            raise NetworkError("요청 시간 초과")
        except aiohttp.ClientError as e:
            raise NetworkError(f"네트워크 오류: {e}")
    
    def post(self, endpoint: str, data: Optional[Dict[str, Any]] = None, 
             json_data: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """POST 요청"""
        url = self._build_url(endpoint)
        
        try:
            self.logger.debug(f"POST {url}")
            response = self.session.post(url, data=data, json=json_data)
            return self._handle_response(response)
            
        except requests.exceptions.Timeout:
            raise NetworkError("요청 시간 초과")
        except requests.exceptions.ConnectionError:
            raise NetworkError("네트워크 연결 오류")
        except requests.exceptions.RequestException as e:
            raise NetworkError(f"요청 오류: {e}")
    
    async def post_async(self, endpoint: str, data: Optional[Dict[str, Any]] = None,
                        json_data: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """비동기 POST 요청"""
        url = self._build_url(endpoint)
        session = self._get_async_session()
        
        try:
            self.logger.debug(f"Async POST {url}")
            async with session.post(url, data=data, json=json_data) as response:
                return await self._handle_async_response(response)
                
        except asyncio.TimeoutError:
            raise NetworkError("요청 시간 초과")
        except aiohttp.ClientError as e:
            raise NetworkError(f"네트워크 오류: {e}")
    
    def with_retry(self, func, *args, max_retries: int = 3, delay: float = 1.0, **kwargs):
        """재시도 로직이 포함된 함수 실행"""
        last_exception = None
        
        for attempt in range(max_retries + 1):
            try:
                return func(*args, **kwargs)
            except RateLimitError as e:
                if attempt == max_retries:
                    raise
                
                # Rate limit의 경우 더 오래 대기
                wait_time = e.retry_after or delay * (2 ** attempt)
                self.logger.warning(f"Rate limit hit, waiting {wait_time}s before retry {attempt + 1}")
                time.sleep(wait_time)
                last_exception = e
                
            except (NetworkError, APIError) as e:
                if attempt == max_retries:
                    raise
                
                wait_time = delay * (2 ** attempt)
                self.logger.warning(f"Request failed, retrying in {wait_time}s (attempt {attempt + 1})")
                time.sleep(wait_time)
                last_exception = e
        
        # 모든 재시도 실패
        if last_exception:
            raise last_exception
    
    async def with_retry_async(self, func, *args, max_retries: int = 3, delay: float = 1.0, **kwargs):
        """비동기 재시도 로직"""
        last_exception = None
        
        for attempt in range(max_retries + 1):
            try:
                return await func(*args, **kwargs)
            except RateLimitError as e:
                if attempt == max_retries:
                    raise
                
                wait_time = e.retry_after or delay * (2 ** attempt)
                self.logger.warning(f"Rate limit hit, waiting {wait_time}s before retry {attempt + 1}")
                await asyncio.sleep(wait_time)
                last_exception = e
                
            except (NetworkError, APIError) as e:
                if attempt == max_retries:
                    raise
                
                wait_time = delay * (2 ** attempt)
                self.logger.warning(f"Request failed, retrying in {wait_time}s (attempt {attempt + 1})")
                await asyncio.sleep(wait_time)
                last_exception = e
        
        if last_exception:
            raise last_exception
    
    def close(self):
        """리소스 정리"""
        if self.session:
            self.session.close()
    
    async def close_async(self):
        """비동기 리소스 정리"""
        if self._async_session and not self._async_session.closed:
            await self._async_session.close()
    
    def __enter__(self):
        """컨텍스트 매니저 진입"""
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """컨텍스트 매니저 종료"""
        self.close()
    
    async def __aenter__(self):
        """비동기 컨텍스트 매니저 진입"""
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """비동기 컨텍스트 매니저 종료"""
        await self.close_async()
    
    @abstractmethod
    def test_connection(self) -> bool:
        """연결 테스트 (각 구현체에서 정의)"""
        pass
    
    def get_rate_limit_info(self) -> Dict[str, Any]:
        """Rate Limit 정보 반환 (기본 구현)"""
        return {
            'remaining': None,
            'limit': None,
            'reset_time': None
        }