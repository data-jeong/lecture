"""
뉴스 데이터 추출기
뉴스 기사에서 구조화된 데이터 추출
"""

import re
from typing import Dict, List, Optional, Any
from datetime import datetime
from bs4 import BeautifulSoup, Tag
import logging
from urllib.parse import urlparse

from ..utils.parser import HTMLParser


class NewsExtractor:
    """뉴스 기사 추출기"""
    
    def __init__(self):
        self.parser = HTMLParser()
        self.logger = logging.getLogger(self.__class__.__name__)
        
        # 뉴스 사이트별 선택자
        self.site_configs = {
            'default': {
                'title': ['h1', 'h2.title', '.article-title'],
                'content': ['article', '.article-body', '.content'],
                'author': ['.author', '.byline', '.writer'],
                'date': ['time', '.date', '.published']
            },
            'naver.com': {
                'title': ['h2.media_end_head_headline', 'h3.tit_view'],
                'content': ['div#articleBodyContents', 'div.article_body'],
                'author': ['.media_end_head_journalist_name', '.journalist_name'],
                'date': ['span.media_end_head_info_datestamp_time', '.t11']
            },
            'daum.net': {
                'title': ['h3.tit_view', '.tit_article'],
                'content': ['div.article_view', '.news_view'],
                'author': ['.info_view .txt_info:first-child'],
                'date': ['.info_view .txt_info:last-child']
            }
        }
    
    def extract(self, html: str, url: str) -> Dict[str, Any]:
        """HTML에서 뉴스 데이터 추출"""
        soup = BeautifulSoup(html, 'html.parser')
        
        # 사이트별 설정 선택
        config = self._get_site_config(url)
        
        # 기본 추출
        article_data = {
            'url': url,
            'title': self._extract_title(soup, config),
            'content': self._extract_content(soup, config),
            'author': self._extract_author(soup, config),
            'published_date': self._extract_date(soup, config),
            'category': self._extract_category(soup, url),
            'tags': self._extract_tags(soup),
            'images': self._extract_images(soup, url),
            'related_articles': self._extract_related(soup, url),
            'metadata': self.parser.extract_metadata(soup)
        }
        
        # 추가 정보
        article_data.update({
            'word_count': len(article_data['content'].split()) if article_data['content'] else 0,
            'reading_time': self._calculate_reading_time(article_data['content']),
            'language': self._detect_language(article_data['content']),
            'extracted_at': datetime.now().isoformat()
        })
        
        return article_data
    
    def _get_site_config(self, url: str) -> Dict[str, List[str]]:
        """사이트별 설정 반환"""
        domain = urlparse(url).netloc
        
        for site, config in self.site_configs.items():
            if site in domain:
                return config
        
        return self.site_configs['default']
    
    def _extract_title(self, soup: BeautifulSoup, config: Dict[str, List[str]]) -> Optional[str]:
        """제목 추출"""
        # 설정된 선택자로 시도
        for selector in config['title']:
            element = soup.select_one(selector)
            if element:
                return self.parser._clean_text(element.text)
        
        # 기본 파서 사용
        return self.parser.extract_title(soup)
    
    def _extract_content(self, soup: BeautifulSoup, config: Dict[str, List[str]]) -> Optional[str]:
        """본문 추출"""
        # 설정된 선택자로 시도
        for selector in config['content']:
            element = soup.select_one(selector)
            if element:
                # 불필요한 요소 제거
                self._clean_content_element(element)
                
                # 단락별로 추출
                paragraphs = []
                for p in element.find_all(['p', 'div']):
                    text = self.parser._clean_text(p.text)
                    if len(text) > 20:
                        paragraphs.append(text)
                
                if paragraphs:
                    return '\n\n'.join(paragraphs)
        
        # 기본 파서 사용
        return self.parser.extract_content(soup)
    
    def _extract_author(self, soup: BeautifulSoup, config: Dict[str, List[str]]) -> Optional[str]:
        """작성자 추출"""
        # 설정된 선택자로 시도
        for selector in config['author']:
            element = soup.select_one(selector)
            if element:
                author = self.parser._clean_text(element.text)
                # 기자, 리포터 등 제거
                author = re.sub(r'(기자|리포터|PD|앵커|특파원)$', '', author).strip()
                return author
        
        # 기본 파서 사용
        return self.parser.extract_author(soup)
    
    def _extract_date(self, soup: BeautifulSoup, config: Dict[str, List[str]]) -> Optional[datetime]:
        """날짜 추출"""
        # 설정된 선택자로 시도
        for selector in config['date']:
            element = soup.select_one(selector)
            if element:
                # datetime 속성 확인
                if element.get('datetime'):
                    try:
                        import dateutil.parser
                        return dateutil.parser.parse(element['datetime'])
                    except:
                        pass
                
                # 텍스트에서 추출
                date_text = self.parser._clean_text(element.text)
                try:
                    import dateutil.parser
                    return dateutil.parser.parse(date_text)
                except:
                    pass
        
        # 기본 파서 사용
        return self.parser.extract_date(soup, {})
    
    def _extract_category(self, soup: BeautifulSoup, url: str) -> Optional[str]:
        """카테고리 추출"""
        # URL에서 추출
        path_parts = urlparse(url).path.split('/')
        common_categories = ['politics', 'economy', 'society', 'culture', 'sports', 'tech', 'world']
        
        for part in path_parts:
            if part.lower() in common_categories:
                return part.capitalize()
        
        # 페이지에서 추출
        category_selectors = [
            '.category', '.section', 'nav .active',
            '[class*="category"]', '[class*="section"]'
        ]
        
        for selector in category_selectors:
            element = soup.select_one(selector)
            if element:
                return self.parser._clean_text(element.text)
        
        return None
    
    def _extract_tags(self, soup: BeautifulSoup) -> List[str]:
        """태그/키워드 추출"""
        tags = []
        
        # 태그 선택자
        tag_selectors = [
            '.tag', '.keyword', '.tags a',
            '[class*="tag"] a', '[class*="keyword"]'
        ]
        
        for selector in tag_selectors:
            elements = soup.select(selector)
            for element in elements:
                tag = self.parser._clean_text(element.text)
                if tag and tag not in tags:
                    tags.append(tag)
        
        # 메타 키워드
        meta_keywords = soup.find('meta', attrs={'name': 'keywords'})
        if meta_keywords and meta_keywords.get('content'):
            keywords = meta_keywords['content'].split(',')
            for keyword in keywords:
                keyword = keyword.strip()
                if keyword and keyword not in tags:
                    tags.append(keyword)
        
        return tags
    
    def _extract_images(self, soup: BeautifulSoup, url: str) -> List[Dict[str, str]]:
        """이미지 정보 추출"""
        images = []
        
        # 기사 본문 영역
        content_area = soup.find('article') or soup.find(class_='content') or soup
        
        for img in content_area.find_all('img'):
            image_data = {
                'url': self.parser._normalize_url(
                    img.get('src') or img.get('data-src') or '', 
                    url
                ),
                'alt': img.get('alt', ''),
                'caption': ''
            }
            
            # 캡션 찾기
            parent = img.parent
            if parent:
                # figure > figcaption 구조
                if parent.name == 'figure':
                    caption = parent.find('figcaption')
                    if caption:
                        image_data['caption'] = self.parser._clean_text(caption.text)
                # 다음 요소가 캡션인 경우
                else:
                    next_sibling = img.find_next_sibling()
                    if next_sibling and next_sibling.name in ['p', 'div', 'span']:
                        if 'caption' in str(next_sibling.get('class', [])):
                            image_data['caption'] = self.parser._clean_text(next_sibling.text)
            
            if image_data['url']:
                images.append(image_data)
        
        return images
    
    def _extract_related(self, soup: BeautifulSoup, url: str) -> List[Dict[str, str]]:
        """관련 기사 추출"""
        related = []
        
        # 관련 기사 영역
        related_selectors = [
            '.related-articles', '.related', '.more-articles',
            '[class*="related"]', '[class*="recommend"]'
        ]
        
        for selector in related_selectors:
            area = soup.select_one(selector)
            if area:
                for link in area.find_all('a', href=True):
                    article = {
                        'title': self.parser._clean_text(link.text),
                        'url': self.parser._normalize_url(link['href'], url)
                    }
                    
                    if article['title'] and article['url']:
                        related.append(article)
        
        return related[:10]  # 최대 10개
    
    def _clean_content_element(self, element: Tag):
        """컨텐츠 요소 정리"""
        # 제거할 요소들
        remove_selectors = [
            'script', 'style', '.ad', '.advertisement',
            '.related', '.share', '.comment', '[class*="social"]'
        ]
        
        for selector in remove_selectors:
            for tag in element.select(selector):
                tag.decompose()
    
    def _calculate_reading_time(self, content: Optional[str]) -> int:
        """읽기 시간 계산 (분)"""
        if not content:
            return 0
        
        # 평균 읽기 속도: 분당 200-250 단어 (한글은 분당 500-600자)
        words = len(content.split())
        chars = len(content)
        
        # 한글이 많은 경우
        if chars / words > 2:  # 한글 비중이 높음
            return max(1, chars // 500)
        else:  # 영어 위주
            return max(1, words // 200)
    
    def _detect_language(self, content: Optional[str]) -> str:
        """언어 감지 (간단한 버전)"""
        if not content:
            return 'unknown'
        
        # 한글 비율 확인
        korean_chars = len(re.findall(r'[가-힣]', content))
        total_chars = len(re.findall(r'\w', content))
        
        if total_chars > 0:
            korean_ratio = korean_chars / total_chars
            if korean_ratio > 0.3:
                return 'ko'
        
        return 'en'
    
    def extract_structured_data(self, soup: BeautifulSoup) -> Optional[Dict[str, Any]]:
        """구조화된 데이터 추출 (JSON-LD, Microdata)"""
        # JSON-LD
        json_ld = soup.find('script', type='application/ld+json')
        if json_ld:
            try:
                import json
                data = json.loads(json_ld.string)
                
                # NewsArticle 타입 찾기
                if isinstance(data, list):
                    for item in data:
                        if item.get('@type') == 'NewsArticle':
                            return item
                elif data.get('@type') == 'NewsArticle':
                    return data
            except:
                pass
        
        return None