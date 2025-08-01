"""
프록시 관리자
프록시 서버 관리 및 로테이션
"""

import random
import time
import requests
from typing import List, Dict, Optional, Tuple
from dataclasses import dataclass, field
from datetime import datetime, timedelta
import logging
from concurrent.futures import ThreadPoolExecutor, as_completed


@dataclass
class Proxy:
    """프록시 정보"""
    address: str
    protocol: str = "http"  # http, https, socks5
    username: Optional[str] = None
    password: Optional[str] = None
    last_used: Optional[datetime] = None
    success_count: int = 0
    fail_count: int = 0
    response_times: List[float] = field(default_factory=list)
    blacklisted_until: Optional[datetime] = None
    
    @property
    def url(self) -> str:
        """프록시 URL 생성"""
        if self.username and self.password:
            return f"{self.protocol}://{self.username}:{self.password}@{self.address}"
        return f"{self.protocol}://{self.address}"
    
    @property
    def success_rate(self) -> float:
        """성공률"""
        total = self.success_count + self.fail_count
        return self.success_count / total if total > 0 else 0
    
    @property
    def avg_response_time(self) -> float:
        """평균 응답 시간"""
        if not self.response_times:
            return 0
        return sum(self.response_times[-10:]) / len(self.response_times[-10:])
    
    def is_available(self) -> bool:
        """사용 가능 여부"""
        if self.blacklisted_until:
            return datetime.now() > self.blacklisted_until
        return True


class ProxyManager:
    """프록시 관리자"""
    
    def __init__(self, 
                 proxy_list: Optional[List[str]] = None,
                 auto_rotate: bool = True,
                 blacklist_threshold: int = 3,
                 blacklist_duration: int = 300):
        """
        Args:
            proxy_list: 프록시 주소 목록
            auto_rotate: 자동 로테이션 여부
            blacklist_threshold: 블랙리스트 임계값 (연속 실패 횟수)
            blacklist_duration: 블랙리스트 지속 시간 (초)
        """
        self.proxies: List[Proxy] = []
        self.auto_rotate = auto_rotate
        self.blacklist_threshold = blacklist_threshold
        self.blacklist_duration = blacklist_duration
        self.current_index = 0
        self.logger = logging.getLogger(self.__class__.__name__)
        
        if proxy_list:
            self.add_proxies(proxy_list)
    
    def add_proxies(self, proxy_list: List[str]):
        """프록시 추가"""
        for proxy_str in proxy_list:
            proxy = self._parse_proxy(proxy_str)
            if proxy:
                self.proxies.append(proxy)
        
        self.logger.info(f"Added {len(self.proxies)} proxies")
    
    def _parse_proxy(self, proxy_str: str) -> Optional[Proxy]:
        """프록시 문자열 파싱"""
        try:
            # 형식: protocol://username:password@host:port
            # 또는: host:port
            
            if "://" in proxy_str:
                protocol, rest = proxy_str.split("://", 1)
            else:
                protocol = "http"
                rest = proxy_str
            
            if "@" in rest:
                auth, address = rest.split("@", 1)
                username, password = auth.split(":", 1)
            else:
                username = password = None
                address = rest
            
            return Proxy(
                address=address,
                protocol=protocol,
                username=username,
                password=password
            )
            
        except Exception as e:
            self.logger.error(f"Failed to parse proxy {proxy_str}: {e}")
            return None
    
    def get_proxy(self) -> Optional[Proxy]:
        """사용 가능한 프록시 반환"""
        available_proxies = [p for p in self.proxies if p.is_available()]
        
        if not available_proxies:
            self.logger.warning("No available proxies")
            return None
        
        if self.auto_rotate:
            # 성공률과 응답 시간 기반 선택
            proxy = self._select_best_proxy(available_proxies)
        else:
            # 순차적 선택
            proxy = available_proxies[self.current_index % len(available_proxies)]
            self.current_index += 1
        
        proxy.last_used = datetime.now()
        return proxy
    
    def _select_best_proxy(self, proxies: List[Proxy]) -> Proxy:
        """최적 프록시 선택"""
        # 사용된 적 없는 프록시 우선
        unused = [p for p in proxies if p.last_used is None]
        if unused:
            return random.choice(unused)
        
        # 성공률과 응답 시간 기반 점수 계산
        scored_proxies = []
        for proxy in proxies:
            # 최근 사용하지 않은 프록시 선호
            time_since_use = (datetime.now() - proxy.last_used).total_seconds()
            time_score = min(time_since_use / 60, 10)  # 최대 10점
            
            # 성공률 점수
            success_score = proxy.success_rate * 10
            
            # 응답 시간 점수 (빠를수록 높은 점수)
            speed_score = 10 / (1 + proxy.avg_response_time) if proxy.avg_response_time > 0 else 5
            
            total_score = time_score + success_score + speed_score
            scored_proxies.append((proxy, total_score))
        
        # 점수 기반 확률적 선택
        scored_proxies.sort(key=lambda x: x[1], reverse=True)
        
        # 상위 프록시 중 랜덤 선택
        top_proxies = scored_proxies[:max(len(scored_proxies) // 3, 1)]
        return random.choice(top_proxies)[0]
    
    def mark_success(self, proxy: Proxy, response_time: float):
        """성공 기록"""
        proxy.success_count += 1
        proxy.response_times.append(response_time)
        
        # 최대 100개 응답 시간만 유지
        if len(proxy.response_times) > 100:
            proxy.response_times = proxy.response_times[-100:]
        
        self.logger.debug(f"Proxy {proxy.address} success (rate: {proxy.success_rate:.2f})")
    
    def mark_failure(self, proxy: Proxy):
        """실패 기록"""
        proxy.fail_count += 1
        
        # 연속 실패 확인
        recent_uses = proxy.fail_count - proxy.success_count
        if recent_uses >= self.blacklist_threshold:
            # 블랙리스트 처리
            proxy.blacklisted_until = datetime.now() + timedelta(seconds=self.blacklist_duration)
            self.logger.warning(f"Proxy {proxy.address} blacklisted until {proxy.blacklisted_until}")
        
        self.logger.debug(f"Proxy {proxy.address} failure (rate: {proxy.success_rate:.2f})")
    
    def test_proxies(self, test_url: str = "http://httpbin.org/ip", 
                    timeout: int = 10) -> Dict[str, bool]:
        """모든 프록시 테스트"""
        results = {}
        
        self.logger.info(f"Testing {len(self.proxies)} proxies...")
        
        with ThreadPoolExecutor(max_workers=10) as executor:
            future_to_proxy = {
                executor.submit(self._test_single_proxy, proxy, test_url, timeout): proxy
                for proxy in self.proxies
            }
            
            for future in as_completed(future_to_proxy):
                proxy = future_to_proxy[future]
                try:
                    success, response_time = future.result()
                    results[proxy.address] = success
                    
                    if success:
                        self.mark_success(proxy, response_time)
                    else:
                        self.mark_failure(proxy)
                        
                except Exception as e:
                    self.logger.error(f"Error testing proxy {proxy.address}: {e}")
                    results[proxy.address] = False
                    self.mark_failure(proxy)
        
        # 결과 요약
        working = sum(1 for v in results.values() if v)
        self.logger.info(f"Proxy test complete: {working}/{len(results)} working")
        
        return results
    
    def _test_single_proxy(self, proxy: Proxy, test_url: str, timeout: int) -> Tuple[bool, float]:
        """단일 프록시 테스트"""
        try:
            start_time = time.time()
            
            response = requests.get(
                test_url,
                proxies={
                    'http': proxy.url,
                    'https': proxy.url
                },
                timeout=timeout
            )
            
            response_time = time.time() - start_time
            
            if response.status_code == 200:
                return True, response_time
            else:
                return False, 0
                
        except Exception as e:
            self.logger.debug(f"Proxy {proxy.address} test failed: {e}")
            return False, 0
    
    def remove_dead_proxies(self):
        """작동하지 않는 프록시 제거"""
        before_count = len(self.proxies)
        
        # 성공률 0%이고 충분히 테스트된 프록시 제거
        self.proxies = [
            p for p in self.proxies 
            if not (p.success_rate == 0 and p.fail_count >= 5)
        ]
        
        removed = before_count - len(self.proxies)
        if removed > 0:
            self.logger.info(f"Removed {removed} dead proxies")
    
    def get_statistics(self) -> Dict[str, any]:
        """프록시 통계"""
        total = len(self.proxies)
        available = sum(1 for p in self.proxies if p.is_available())
        blacklisted = total - available
        
        success_rates = [p.success_rate for p in self.proxies if p.success_count + p.fail_count > 0]
        avg_success_rate = sum(success_rates) / len(success_rates) if success_rates else 0
        
        response_times = [p.avg_response_time for p in self.proxies if p.response_times]
        avg_response_time = sum(response_times) / len(response_times) if response_times else 0
        
        return {
            'total_proxies': total,
            'available_proxies': available,
            'blacklisted_proxies': blacklisted,
            'average_success_rate': avg_success_rate,
            'average_response_time': avg_response_time,
            'proxies': [
                {
                    'address': p.address,
                    'success_rate': p.success_rate,
                    'avg_response_time': p.avg_response_time,
                    'is_available': p.is_available()
                }
                for p in self.proxies
            ]
        }
    
    def load_from_file(self, filename: str):
        """파일에서 프록시 로드"""
        try:
            with open(filename, 'r') as f:
                proxy_list = [line.strip() for line in f if line.strip()]
            
            self.add_proxies(proxy_list)
            self.logger.info(f"Loaded proxies from {filename}")
            
        except Exception as e:
            self.logger.error(f"Failed to load proxies from {filename}: {e}")
    
    def export_working_proxies(self, filename: str):
        """작동하는 프록시 내보내기"""
        working_proxies = [
            p for p in self.proxies 
            if p.success_rate > 0.5 and p.is_available()
        ]
        
        try:
            with open(filename, 'w') as f:
                for proxy in working_proxies:
                    f.write(f"{proxy.url}\n")
            
            self.logger.info(f"Exported {len(working_proxies)} working proxies to {filename}")
            
        except Exception as e:
            self.logger.error(f"Failed to export proxies: {e}")