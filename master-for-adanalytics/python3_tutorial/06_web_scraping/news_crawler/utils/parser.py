"""
HTML 파싱 유틸리티
뉴스 콘텐츠 추출을 위한 공통 파서
"""

import re
from typing import List, Dict, Optional, Any
from datetime import datetime
from urllib.parse import urljoin, urlparse
from bs4 import BeautifulSoup, Tag
import dateutil.parser
import logging


class HTMLParser:
    """HTML 파싱 헬퍼"""
    
    def __init__(self):
        self.logger = logging.getLogger(self.__class__.__name__)
        
        # 제거할 태그들
        self.remove_tags = ['script', 'style', 'noscript', 'iframe', 'svg']
        
        # 컨텐츠로 간주하지 않을 클래스/ID 패턴
        self.exclude_patterns = [
            'sidebar', 'menu', 'nav', 'header', 'footer',
            'advertisement', 'banner', 'popup', 'modal',
            'related', 'share', 'social', 'comment'
        ]
    
    def extract_title(self, soup: BeautifulSoup) -> Optional[str]:
        """제목 추출"""
        # 1. og:title 메타 태그
        og_title = soup.find('meta', property='og:title')
        if og_title and og_title.get('content'):
            return self._clean_text(og_title['content'])
        
        # 2. title 태그
        title_tag = soup.find('title')
        if title_tag:
            return self._clean_text(title_tag.text)
        
        # 3. h1 태그
        h1_tag = soup.find('h1')
        if h1_tag:
            return self._clean_text(h1_tag.text)
        
        # 4. article 내 제목
        article = soup.find('article')
        if article:
            title = article.find(['h1', 'h2'])
            if title:
                return self._clean_text(title.text)
        
        return None
    
    def extract_content(self, soup: BeautifulSoup) -> Optional[str]:
        """본문 추출"""
        # 불필요한 태그 제거
        self._remove_unwanted_tags(soup)
        
        # 1. article 태그
        article = soup.find('article')
        if article:
            return self._extract_text_from_element(article)
        
        # 2. 본문 관련 클래스/ID
        content_selectors = [
            {'class': re.compile('content|article|body|text', re.I)},
            {'id': re.compile('content|article|body|text', re.I)},
            {'itemprop': 'articleBody'},
            {'role': 'main'}
        ]
        
        for selector in content_selectors:
            element = soup.find(['div', 'section', 'main'], selector)
            if element:
                text = self._extract_text_from_element(element)
                if len(text) > 100:  # 최소 길이 확인
                    return text
        
        # 3. 가장 긴 텍스트 블록 찾기
        paragraphs = soup.find_all('p')
        if paragraphs:
            text_blocks = []
            current_block = []
            
            for p in paragraphs:
                text = self._clean_text(p.text)
                if len(text) > 20:
                    current_block.append(text)
                elif current_block:
                    text_blocks.append('\n'.join(current_block))
                    current_block = []
            
            if current_block:
                text_blocks.append('\n'.join(current_block))
            
            if text_blocks:
                # 가장 긴 블록 반환
                return max(text_blocks, key=len)
        
        return None
    
    def extract_metadata(self, soup: BeautifulSoup) -> Dict[str, Any]:
        """메타데이터 추출"""
        metadata = {}
        
        # Open Graph 메타 태그
        og_tags = soup.find_all('meta', property=re.compile('^og:'))
        for tag in og_tags:
            if tag.get('content'):
                key = tag['property'].replace('og:', '')
                metadata[f'og_{key}'] = tag['content']
        
        # Twitter 메타 태그
        twitter_tags = soup.find_all('meta', attrs={'name': re.compile('^twitter:')})
        for tag in twitter_tags:
            if tag.get('content'):
                key = tag['name'].replace('twitter:', '')
                metadata[f'twitter_{key}'] = tag['content']
        
        # 일반 메타 태그
        meta_names = ['author', 'description', 'keywords', 'publisher', 'robots']
        for name in meta_names:
            tag = soup.find('meta', attrs={'name': name})
            if tag and tag.get('content'):
                metadata[name] = tag['content']
        
        # JSON-LD 구조화 데이터
        json_ld = soup.find('script', type='application/ld+json')
        if json_ld:
            try:
                import json
                ld_data = json.loads(json_ld.string)
                metadata['json_ld'] = ld_data
            except:
                pass
        
        return metadata
    
    def extract_date(self, soup: BeautifulSoup, metadata: Dict[str, Any]) -> Optional[datetime]:
        """날짜 추출"""
        # 1. time 태그
        time_tag = soup.find('time')
        if time_tag and time_tag.get('datetime'):
            try:
                return dateutil.parser.parse(time_tag['datetime'])
            except:
                pass
        
        # 2. 메타데이터에서
        date_keys = [
            'article:published_time', 'datePublished', 'pubdate',
            'og_article:published_time', 'publish_date'
        ]
        
        for key in date_keys:
            if key in metadata:
                try:
                    return dateutil.parser.parse(metadata[key])
                except:
                    pass
        
        # 3. 텍스트에서 날짜 패턴 찾기
        date_patterns = [
            r'\d{4}[-/]\d{1,2}[-/]\d{1,2}',  # 2024-01-15
            r'\d{1,2}[-/]\d{1,2}[-/]\d{4}',  # 01/15/2024
            r'\d{4}년\s*\d{1,2}월\s*\d{1,2}일',  # 2024년 1월 15일
        ]
        
        text = str(soup)[:1000]  # 상단 부분만 검색
        
        for pattern in date_patterns:
            match = re.search(pattern, text)
            if match:
                try:
                    return dateutil.parser.parse(match.group())
                except:
                    pass
        
        return None
    
    def extract_author(self, soup: BeautifulSoup) -> Optional[str]:
        """작성자 추출"""
        # 1. 메타 태그
        author_meta = soup.find('meta', attrs={'name': 'author'})
        if author_meta and author_meta.get('content'):
            return self._clean_text(author_meta['content'])
        
        # 2. 작성자 관련 클래스/속성
        author_selectors = [
            {'class': re.compile('author|byline|by', re.I)},
            {'itemprop': 'author'},
            {'rel': 'author'}
        ]
        
        for selector in author_selectors:
            element = soup.find(['span', 'div', 'p', 'a'], selector)
            if element:
                text = self._clean_text(element.text)
                # "By " 제거
                text = re.sub(r'^(by|작성자)\s*:?\s*', '', text, flags=re.I)
                if text and len(text) < 100:  # 너무 긴 텍스트는 제외
                    return text
        
        return None
    
    def extract_images(self, soup: BeautifulSoup, base_url: str) -> List[str]:
        """이미지 URL 추출"""
        images = []
        
        # 1. og:image
        og_image = soup.find('meta', property='og:image')
        if og_image and og_image.get('content'):
            images.append(self._normalize_url(og_image['content'], base_url))
        
        # 2. article 내 이미지
        article = soup.find('article') or soup
        
        for img in article.find_all('img'):
            src = img.get('src') or img.get('data-src') or img.get('data-lazy-src')
            if src:
                normalized_url = self._normalize_url(src, base_url)
                if normalized_url and normalized_url not in images:
                    images.append(normalized_url)
        
        # 3. picture 태그 내 source
        for picture in article.find_all('picture'):
            source = picture.find('source')
            if source and source.get('srcset'):
                # srcset에서 첫 번째 URL 추출
                srcset = source['srcset'].split(',')[0]
                url = srcset.split()[0]
                normalized_url = self._normalize_url(url, base_url)
                if normalized_url and normalized_url not in images:
                    images.append(normalized_url)
        
        return images
    
    def extract_links(self, soup: BeautifulSoup, base_url: str) -> List[str]:
        """링크 추출"""
        links = []
        
        article = soup.find('article') or soup
        
        for a in article.find_all('a', href=True):
            href = a['href']
            
            # 앵커 링크, 자바스크립트 제외
            if href.startswith('#') or href.startswith('javascript:'):
                continue
            
            normalized_url = self._normalize_url(href, base_url)
            if normalized_url and normalized_url not in links:
                links.append(normalized_url)
        
        return links
    
    def _remove_unwanted_tags(self, soup: BeautifulSoup):
        """불필요한 태그 제거"""
        # 스크립트, 스타일 등 제거
        for tag_name in self.remove_tags:
            for tag in soup.find_all(tag_name):
                tag.decompose()
        
        # 광고, 네비게이션 등 제거
        for pattern in self.exclude_patterns:
            # 클래스로 찾기
            for tag in soup.find_all(class_=re.compile(pattern, re.I)):
                tag.decompose()
            
            # ID로 찾기
            for tag in soup.find_all(id=re.compile(pattern, re.I)):
                tag.decompose()
    
    def _extract_text_from_element(self, element: Tag) -> str:
        """요소에서 텍스트 추출"""
        # 단락별로 추출
        paragraphs = []
        
        for p in element.find_all(['p', 'div', 'section']):
            text = self._clean_text(p.text)
            if len(text) > 20:  # 최소 길이
                paragraphs.append(text)
        
        if not paragraphs:
            # 전체 텍스트 추출
            text = self._clean_text(element.text)
            if text:
                paragraphs = [text]
        
        return '\n\n'.join(paragraphs)
    
    def _clean_text(self, text: str) -> str:
        """텍스트 정리"""
        if not text:
            return ""
        
        # 공백 정규화
        text = re.sub(r'\s+', ' ', text)
        
        # 앞뒤 공백 제거
        text = text.strip()
        
        # 특수 문자 정리
        text = text.replace('\u200b', '')  # Zero-width space
        text = text.replace('\xa0', ' ')   # Non-breaking space
        
        return text
    
    def _normalize_url(self, url: str, base_url: str) -> Optional[str]:
        """URL 정규화"""
        if not url:
            return None
        
        # 상대 경로를 절대 경로로
        url = urljoin(base_url, url)
        
        # URL 유효성 검사
        parsed = urlparse(url)
        if not parsed.scheme or not parsed.netloc:
            return None
        
        return url