"""
반크롤링 회피 유틸리티
봇 탐지를 회피하기 위한 다양한 기법
"""

import time
import random
from typing import Dict, List, Optional
import logging


class AntiBot:
    """반크롤링 회피 헬퍼"""
    
    def __init__(self):
        self.logger = logging.getLogger(self.__class__.__name__)
        
        # 브라우저 헤더 세트
        self.header_sets = [
            {
                'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
                'Accept-Language': 'ko-KR,ko;q=0.9,en-US;q=0.8,en;q=0.7',
                'Accept-Encoding': 'gzip, deflate, br',
                'DNT': '1',
                'Connection': 'keep-alive',
                'Upgrade-Insecure-Requests': '1',
                'Sec-Fetch-Dest': 'document',
                'Sec-Fetch-Mode': 'navigate',
                'Sec-Fetch-Site': 'none',
                'Sec-Fetch-User': '?1',
                'Cache-Control': 'max-age=0'
            },
            {
                'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
                'Accept-Language': 'en-US,en;q=0.9',
                'Accept-Encoding': 'gzip, deflate, br',
                'Connection': 'keep-alive',
                'Upgrade-Insecure-Requests': '1',
                'Pragma': 'no-cache',
                'Cache-Control': 'no-cache'
            }
        ]
        
        # 마우스 움직임 패턴
        self.mouse_patterns = [
            [(100, 100), (500, 300), (700, 500), (400, 400)],
            [(50, 50), (800, 100), (600, 600), (200, 400)],
            [(300, 200), (600, 400), (400, 600), (100, 300)]
        ]
        
        # 키보드 입력 패턴
        self.typing_patterns = {
            'slow': (0.1, 0.3),    # 최소, 최대 간격
            'normal': (0.05, 0.15),
            'fast': (0.02, 0.08)
        }
    
    def get_random_headers(self) -> Dict[str, str]:
        """랜덤 헤더 세트 반환"""
        return random.choice(self.header_sets).copy()
    
    def random_delay(self, base_delay: float = 1.0) -> None:
        """랜덤 지연"""
        # 기본 지연에 20-50% 변동 추가
        variation = random.uniform(0.2, 0.5)
        delay = base_delay * (1 + variation)
        
        self.logger.debug(f"Waiting {delay:.2f} seconds")
        time.sleep(delay)
    
    def get_random_delay(self, base_delay: float = 1.0) -> float:
        """랜덤 지연 시간 반환"""
        variation = random.uniform(0.2, 0.5)
        return base_delay * (1 + variation)
    
    def human_like_scroll(self, driver) -> None:
        """인간처럼 스크롤 (Selenium용)"""
        current_position = 0
        page_height = driver.execute_script("return document.body.scrollHeight")
        
        while current_position < page_height:
            # 랜덤한 스크롤 거리
            scroll_distance = random.randint(300, 700)
            
            # 부드러운 스크롤
            driver.execute_script(f"""
                window.scrollTo({{
                    top: {current_position + scroll_distance},
                    behavior: 'smooth'
                }});
            """)
            
            current_position += scroll_distance
            
            # 읽는 시간 시뮬레이션
            time.sleep(random.uniform(0.5, 2.0))
            
            # 가끔 위로 스크롤
            if random.random() < 0.1:
                back_scroll = random.randint(100, 300)
                driver.execute_script(f"window.scrollBy(0, -{back_scroll})")
                time.sleep(random.uniform(0.3, 0.8))
    
    def human_like_mouse_movement(self, driver, action_chains) -> None:
        """인간처럼 마우스 움직임 (Selenium용)"""
        pattern = random.choice(self.mouse_patterns)
        
        for x, y in pattern:
            # 목표 지점에 약간의 변동 추가
            target_x = x + random.randint(-20, 20)
            target_y = y + random.randint(-20, 20)
            
            # 베지어 곡선 움직임 시뮬레이션
            action_chains.move_by_offset(target_x, target_y)
            action_chains.pause(random.uniform(0.1, 0.3))
        
        action_chains.perform()
    
    def human_like_typing(self, element, text: str, speed: str = 'normal') -> None:
        """인간처럼 타이핑 (Selenium용)"""
        min_delay, max_delay = self.typing_patterns[speed]
        
        for char in text:
            element.send_keys(char)
            
            # 타이핑 속도 변화
            delay = random.uniform(min_delay, max_delay)
            
            # 가끔 더 긴 지연 (생각하는 중)
            if random.random() < 0.1:
                delay *= random.uniform(2, 4)
            
            time.sleep(delay)
            
            # 가끔 오타 시뮬레이션
            if random.random() < 0.02:
                wrong_char = random.choice('abcdefghijklmnopqrstuvwxyz')
                element.send_keys(wrong_char)
                time.sleep(random.uniform(0.1, 0.3))
                element.send_keys('\b')  # 백스페이스
    
    def check_bot_detection(self, driver) -> bool:
        """봇 탐지 확인 (Selenium용)"""
        # 일반적인 봇 탐지 신호
        detection_signs = [
            # Cloudflare
            "Checking your browser",
            "Please wait while we check your browser",
            
            # reCAPTCHA
            "I'm not a robot",
            "reCAPTCHA",
            
            # 일반적인 봇 차단 메시지
            "Access denied",
            "Bot detected",
            "Automated access prohibited",
            
            # 한국어
            "자동화된 접근",
            "봇 감지",
            "접근이 거부되었습니다"
        ]
        
        page_source = driver.page_source.lower()
        
        for sign in detection_signs:
            if sign.lower() in page_source:
                self.logger.warning(f"Bot detection sign found: {sign}")
                return True
        
        return False
    
    def get_cookie_string(self, cookies: List[Dict]) -> str:
        """쿠키 리스트를 문자열로 변환"""
        return '; '.join([f"{c['name']}={c['value']}" for c in cookies])
    
    def rotate_ip(self, proxy_list: List[str]) -> str:
        """프록시 로테이션"""
        if not proxy_list:
            return None
        
        proxy = random.choice(proxy_list)
        self.logger.info(f"Using proxy: {proxy}")
        return proxy
    
    def fingerprint_randomization(self) -> Dict[str, any]:
        """브라우저 핑거프린트 랜덤화"""
        return {
            'screen_resolution': random.choice([
                (1920, 1080), (1366, 768), (1440, 900),
                (1536, 864), (1280, 720), (1600, 900)
            ]),
            'color_depth': random.choice([24, 32]),
            'timezone_offset': random.choice([-480, -420, -360, -300, -240]),
            'platform': random.choice(['Win32', 'MacIntel', 'Linux x86_64']),
            'memory': random.choice([4, 8, 16, 32]),
            'hardware_concurrency': random.choice([2, 4, 8, 16])
        }
    
    def should_use_proxy(self, request_count: int, threshold: int = 100) -> bool:
        """프록시 사용 여부 결정"""
        # 일정 요청 수 이상이면 프록시 사용 권장
        return request_count >= threshold
    
    def calculate_backoff(self, attempt: int, base_delay: float = 1.0) -> float:
        """지수 백오프 계산"""
        # 2^attempt * base_delay + 랜덤 지터
        delay = (2 ** attempt) * base_delay
        jitter = random.uniform(0, delay * 0.1)
        return delay + jitter