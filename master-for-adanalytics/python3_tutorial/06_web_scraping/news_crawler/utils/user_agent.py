"""
User-Agent 관리
다양한 브라우저 User-Agent 제공
"""

import random
from typing import List, Optional
from datetime import datetime


class UserAgentManager:
    """User-Agent 관리자"""
    
    def __init__(self):
        # 최신 브라우저 버전 (2024년 기준)
        self.chrome_versions = list(range(120, 125))
        self.firefox_versions = list(range(120, 125))
        self.safari_versions = ["17.0", "17.1", "17.2"]
        self.edge_versions = list(range(120, 125))
        
        # 운영체제 정보
        self.windows_versions = [
            "Windows NT 10.0; Win64; x64",
            "Windows NT 10.0; WOW64",
            "Windows NT 11.0; Win64; x64"
        ]
        
        self.mac_versions = [
            "Macintosh; Intel Mac OS X 14_0",
            "Macintosh; Intel Mac OS X 13_6",
            "Macintosh; Intel Mac OS X 12_7"
        ]
        
        self.linux_versions = [
            "X11; Linux x86_64",
            "X11; Ubuntu; Linux x86_64",
            "X11; Linux i686"
        ]
        
        # 모바일 디바이스
        self.mobile_devices = [
            "iPhone; CPU iPhone OS 17_0 like Mac OS X",
            "iPad; CPU OS 17_0 like Mac OS X",
            "Linux; Android 14; SM-S908B",
            "Linux; Android 13; Pixel 7"
        ]
    
    def get_random_user_agent(self, browser: Optional[str] = None, 
                            mobile: bool = False) -> str:
        """랜덤 User-Agent 생성"""
        if mobile:
            return self._get_mobile_user_agent()
        
        if browser:
            browser = browser.lower()
            if browser == 'chrome':
                return self._get_chrome_user_agent()
            elif browser == 'firefox':
                return self._get_firefox_user_agent()
            elif browser == 'safari':
                return self._get_safari_user_agent()
            elif browser == 'edge':
                return self._get_edge_user_agent()
        
        # 랜덤 브라우저 선택
        browsers = [
            self._get_chrome_user_agent,
            self._get_firefox_user_agent,
            self._get_safari_user_agent,
            self._get_edge_user_agent
        ]
        
        return random.choice(browsers)()
    
    def _get_chrome_user_agent(self) -> str:
        """Chrome User-Agent"""
        version = random.choice(self.chrome_versions)
        os = random.choice(self.windows_versions + self.mac_versions + self.linux_versions)
        
        return (
            f"Mozilla/5.0 ({os}) AppleWebKit/537.36 "
            f"(KHTML, like Gecko) Chrome/{version}.0.0.0 Safari/537.36"
        )
    
    def _get_firefox_user_agent(self) -> str:
        """Firefox User-Agent"""
        version = random.choice(self.firefox_versions)
        os = random.choice(self.windows_versions + self.mac_versions + self.linux_versions)
        
        gecko_version = "20100101"
        
        return (
            f"Mozilla/5.0 ({os}; rv:{version}.0) "
            f"Gecko/{gecko_version} Firefox/{version}.0"
        )
    
    def _get_safari_user_agent(self) -> str:
        """Safari User-Agent (Mac only)"""
        version = random.choice(self.safari_versions)
        os = random.choice(self.mac_versions)
        
        webkit_version = "605.1.15"
        
        return (
            f"Mozilla/5.0 ({os}) AppleWebKit/{webkit_version} "
            f"(KHTML, like Gecko) Version/{version} Safari/{webkit_version}"
        )
    
    def _get_edge_user_agent(self) -> str:
        """Edge User-Agent"""
        version = random.choice(self.edge_versions)
        os = random.choice(self.windows_versions)
        
        return (
            f"Mozilla/5.0 ({os}) AppleWebKit/537.36 "
            f"(KHTML, like Gecko) Chrome/{version}.0.0.0 Safari/537.36 Edg/{version}.0.0.0"
        )
    
    def _get_mobile_user_agent(self) -> str:
        """모바일 User-Agent"""
        device = random.choice(self.mobile_devices)
        
        if "iPhone" in device or "iPad" in device:
            webkit = "605.1.15"
            return (
                f"Mozilla/5.0 ({device}) AppleWebKit/{webkit} "
                f"(KHTML, like Gecko) Version/17.0 Mobile/15E148 Safari/604.1"
            )
        else:  # Android
            chrome_version = random.choice(self.chrome_versions)
            return (
                f"Mozilla/5.0 ({device}) AppleWebKit/537.36 "
                f"(KHTML, like Gecko) Chrome/{chrome_version}.0.0.0 Mobile Safari/537.36"
            )
    
    def get_bot_user_agent(self) -> str:
        """봇 User-Agent (정직하게 봇임을 표시)"""
        return "NewsCrawlerBot/1.0 (+https://example.com/bot)"
    
    def get_curl_user_agent(self) -> str:
        """curl User-Agent"""
        return "curl/8.4.0"
    
    def get_user_agent_list(self, count: int = 10) -> List[str]:
        """여러 User-Agent 목록 생성"""
        agents = []
        
        for _ in range(count):
            agents.append(self.get_random_user_agent())
        
        return list(set(agents))  # 중복 제거
    
    def is_outdated(self, user_agent: str) -> bool:
        """User-Agent가 오래되었는지 확인"""
        # 간단한 버전 체크
        outdated_patterns = [
            "Chrome/[0-9]{1,2}\\.",  # Chrome 99 이하
            "Firefox/[0-9]{1,2}\\.",  # Firefox 99 이하
            "Windows NT 6",           # Windows 7/8
            "Mac OS X 10_[0-9]\\b",   # macOS 10.9 이하
        ]
        
        import re
        for pattern in outdated_patterns:
            if re.search(pattern, user_agent):
                return True
        
        return False
    
    def rotate_user_agent(self, current: str, browser_type: Optional[str] = None) -> str:
        """User-Agent 로테이션"""
        # 같은 브라우저 타입 유지
        if browser_type is None and current:
            if "Chrome" in current and "Edg" not in current:
                browser_type = "chrome"
            elif "Firefox" in current:
                browser_type = "firefox"
            elif "Safari" in current and "Chrome" not in current:
                browser_type = "safari"
            elif "Edg" in current:
                browser_type = "edge"
        
        new_agent = self.get_random_user_agent(browser=browser_type)
        
        # 이전과 다른 것 보장
        while new_agent == current:
            new_agent = self.get_random_user_agent(browser=browser_type)
        
        return new_agent