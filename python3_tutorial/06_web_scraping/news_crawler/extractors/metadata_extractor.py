"""
메타데이터 추출기
웹페이지의 다양한 메타데이터 추출
"""

import re
import json
from typing import Dict, List, Optional, Any
from bs4 import BeautifulSoup
import logging
from urllib.parse import urlparse


class MetadataExtractor:
    """메타데이터 추출기"""
    
    def __init__(self):
        self.logger = logging.getLogger(self.__class__.__name__)
    
    def extract(self, html: str, url: str) -> Dict[str, Any]:
        """HTML에서 메타데이터 추출"""
        soup = BeautifulSoup(html, 'html.parser')
        
        metadata = {
            'url': url,
            'domain': urlparse(url).netloc,
            'basic': self._extract_basic_meta(soup),
            'open_graph': self._extract_open_graph(soup),
            'twitter_card': self._extract_twitter_card(soup),
            'structured_data': self._extract_structured_data(soup),
            'links': self._extract_links(soup),
            'feeds': self._extract_feeds(soup),
            'social': self._extract_social_links(soup),
            'seo': self._extract_seo_info(soup),
            'technical': self._extract_technical_info(soup, html)
        }
        
        return metadata
    
    def _extract_basic_meta(self, soup: BeautifulSoup) -> Dict[str, Any]:
        """기본 메타 태그 추출"""
        basic_meta = {}
        
        # title
        title_tag = soup.find('title')
        if title_tag:
            basic_meta['title'] = title_tag.text.strip()
        
        # 일반 메타 태그
        meta_names = [
            'description', 'keywords', 'author', 'publisher',
            'robots', 'viewport', 'generator', 'application-name',
            'theme-color', 'msapplication-TileColor'
        ]
        
        for name in meta_names:
            meta = soup.find('meta', attrs={'name': name})
            if meta and meta.get('content'):
                basic_meta[name] = meta['content']
        
        # charset
        charset_meta = soup.find('meta', charset=True)
        if charset_meta:
            basic_meta['charset'] = charset_meta['charset']
        
        # http-equiv 메타 태그
        http_equiv_tags = soup.find_all('meta', attrs={'http-equiv': True})
        for tag in http_equiv_tags:
            if tag.get('content'):
                key = tag['http-equiv'].lower().replace('-', '_')
                basic_meta[f'http_equiv_{key}'] = tag['content']
        
        # canonical URL
        canonical = soup.find('link', rel='canonical')
        if canonical and canonical.get('href'):
            basic_meta['canonical'] = canonical['href']
        
        # language
        html_tag = soup.find('html')
        if html_tag and html_tag.get('lang'):
            basic_meta['language'] = html_tag['lang']
        
        return basic_meta
    
    def _extract_open_graph(self, soup: BeautifulSoup) -> Dict[str, Any]:
        """Open Graph 메타데이터 추출"""
        og_data = {}
        
        og_tags = soup.find_all('meta', property=re.compile('^og:'))
        
        for tag in og_tags:
            if tag.get('content'):
                # og: 제거
                key = tag['property'][3:]
                value = tag['content']
                
                # 중첩된 속성 처리 (예: og:image:width)
                if ':' in key:
                    parts = key.split(':', 1)
                    main_key, sub_key = parts[0], parts[1]
                    
                    if main_key not in og_data:
                        og_data[main_key] = {}
                    
                    if isinstance(og_data[main_key], dict):
                        og_data[main_key][sub_key] = value
                    else:
                        # 이미 문자열 값이 있는 경우
                        og_data[main_key] = {
                            'url': og_data[main_key],
                            sub_key: value
                        }
                else:
                    og_data[key] = value
        
        return og_data
    
    def _extract_twitter_card(self, soup: BeautifulSoup) -> Dict[str, Any]:
        """Twitter Card 메타데이터 추출"""
        twitter_data = {}
        
        twitter_tags = soup.find_all('meta', attrs={'name': re.compile('^twitter:')})
        
        for tag in twitter_tags:
            if tag.get('content'):
                # twitter: 제거
                key = tag['name'][8:]
                twitter_data[key] = tag['content']
        
        return twitter_data
    
    def _extract_structured_data(self, soup: BeautifulSoup) -> List[Dict[str, Any]]:
        """구조화된 데이터 추출 (JSON-LD, Microdata, RDFa)"""
        structured_data = []
        
        # JSON-LD
        json_ld_scripts = soup.find_all('script', type='application/ld+json')
        for script in json_ld_scripts:
            try:
                data = json.loads(script.string)
                structured_data.append({
                    'type': 'json-ld',
                    'data': data
                })
            except Exception as e:
                self.logger.debug(f"Error parsing JSON-LD: {e}")
        
        # Schema.org Microdata
        microdata_items = soup.find_all(attrs={'itemscope': True})
        for item in microdata_items:
            item_data = self._extract_microdata_item(item)
            if item_data:
                structured_data.append({
                    'type': 'microdata',
                    'data': item_data
                })
        
        return structured_data
    
    def _extract_microdata_item(self, item_elem: BeautifulSoup) -> Dict[str, Any]:
        """Microdata 아이템 추출"""
        item_data = {}
        
        # itemtype
        if item_elem.get('itemtype'):
            item_data['@type'] = item_elem['itemtype']
        
        # itemprops
        props = item_elem.find_all(attrs={'itemprop': True})
        for prop in props:
            prop_name = prop['itemprop']
            
            # 값 추출
            if prop.get('content'):
                value = prop['content']
            elif prop.get('href'):
                value = prop['href']
            elif prop.get('src'):
                value = prop['src']
            elif prop.get('datetime'):
                value = prop['datetime']
            else:
                value = prop.text.strip()
            
            # 중복 속성 처리
            if prop_name in item_data:
                if not isinstance(item_data[prop_name], list):
                    item_data[prop_name] = [item_data[prop_name]]
                item_data[prop_name].append(value)
            else:
                item_data[prop_name] = value
        
        return item_data
    
    def _extract_links(self, soup: BeautifulSoup) -> Dict[str, Any]:
        """링크 정보 추출"""
        links = {
            'stylesheets': [],
            'scripts': [],
            'images': [],
            'alternate': [],
            'prefetch': [],
            'preload': [],
            'icon': None,
            'manifest': None
        }
        
        # 스타일시트
        for link in soup.find_all('link', rel='stylesheet'):
            if link.get('href'):
                links['stylesheets'].append(link['href'])
        
        # 스크립트
        for script in soup.find_all('script', src=True):
            links['scripts'].append(script['src'])
        
        # 이미지
        for img in soup.find_all('img', src=True):
            links['images'].append(img['src'])
        
        # alternate 링크 (RSS, 언어 버전 등)
        for link in soup.find_all('link', rel='alternate'):
            alt_link = {
                'href': link.get('href'),
                'type': link.get('type'),
                'title': link.get('title'),
                'hreflang': link.get('hreflang')
            }
            links['alternate'].append(alt_link)
        
        # 리소스 힌트
        for link in soup.find_all('link', rel=['prefetch', 'preload', 'preconnect']):
            rel = link['rel'][0]
            if rel in links:
                links[rel].append(link.get('href'))
        
        # 파비콘
        icon = soup.find('link', rel=re.compile('icon'))
        if icon and icon.get('href'):
            links['icon'] = icon['href']
        
        # 웹 앱 매니페스트
        manifest = soup.find('link', rel='manifest')
        if manifest and manifest.get('href'):
            links['manifest'] = manifest['href']
        
        return links
    
    def _extract_feeds(self, soup: BeautifulSoup) -> List[Dict[str, str]]:
        """RSS/Atom 피드 추출"""
        feeds = []
        
        feed_types = ['application/rss+xml', 'application/atom+xml']
        
        for feed_type in feed_types:
            feed_links = soup.find_all('link', type=feed_type)
            for link in feed_links:
                if link.get('href'):
                    feed = {
                        'url': link['href'],
                        'type': feed_type,
                        'title': link.get('title', 'Unknown Feed')
                    }
                    feeds.append(feed)
        
        return feeds
    
    def _extract_social_links(self, soup: BeautifulSoup) -> Dict[str, Optional[str]]:
        """소셜 미디어 링크 추출"""
        social = {}
        
        # 소셜 플랫폼 패턴
        social_patterns = {
            'facebook': r'facebook\.com/[\w\-\.]+',
            'twitter': r'twitter\.com/[\w\-\.]+',
            'instagram': r'instagram\.com/[\w\-\.]+',
            'youtube': r'youtube\.com/(channel|user|c)/[\w\-\.]+',
            'linkedin': r'linkedin\.com/(company|in)/[\w\-\.]+',
            'github': r'github\.com/[\w\-\.]+',
            'medium': r'medium\.com/@?[\w\-\.]+',
            'tiktok': r'tiktok\.com/@[\w\-\.]+'
        }
        
        # 모든 링크에서 소셜 미디어 찾기
        for link in soup.find_all('a', href=True):
            href = link['href']
            
            for platform, pattern in social_patterns.items():
                if platform not in social and re.search(pattern, href):
                    social[platform] = href
        
        return social
    
    def _extract_seo_info(self, soup: BeautifulSoup) -> Dict[str, Any]:
        """SEO 정보 추출"""
        seo = {
            'headings': self._extract_headings(soup),
            'meta_robots': None,
            'sitemap': None,
            'schema_types': []
        }
        
        # robots 메타 태그
        robots_meta = soup.find('meta', attrs={'name': 'robots'})
        if robots_meta and robots_meta.get('content'):
            seo['meta_robots'] = robots_meta['content']
        
        # 사이트맵 링크
        sitemap_link = soup.find('link', rel='sitemap')
        if sitemap_link and sitemap_link.get('href'):
            seo['sitemap'] = sitemap_link['href']
        
        # Schema.org 타입
        for item in soup.find_all(attrs={'itemtype': True}):
            schema_type = item['itemtype']
            if schema_type not in seo['schema_types']:
                seo['schema_types'].append(schema_type)
        
        # JSON-LD의 @type
        for script in soup.find_all('script', type='application/ld+json'):
            try:
                data = json.loads(script.string)
                if isinstance(data, dict) and '@type' in data:
                    if data['@type'] not in seo['schema_types']:
                        seo['schema_types'].append(data['@type'])
            except:
                pass
        
        return seo
    
    def _extract_headings(self, soup: BeautifulSoup) -> Dict[str, List[str]]:
        """제목 태그 구조 추출"""
        headings = {
            'h1': [],
            'h2': [],
            'h3': [],
            'h4': [],
            'h5': [],
            'h6': []
        }
        
        for level in range(1, 7):
            tag_name = f'h{level}'
            for heading in soup.find_all(tag_name):
                text = heading.text.strip()
                if text:
                    headings[tag_name].append(text)
        
        return headings
    
    def _extract_technical_info(self, soup: BeautifulSoup, html: str) -> Dict[str, Any]:
        """기술적 정보 추출"""
        tech = {
            'doctype': self._detect_doctype(html),
            'html_size': len(html),
            'dom_depth': self._calculate_dom_depth(soup),
            'total_elements': len(soup.find_all()),
            'external_resources': {
                'stylesheets': len(soup.find_all('link', rel='stylesheet')),
                'scripts': len(soup.find_all('script', src=True)),
                'images': len(soup.find_all('img'))
            },
            'performance_hints': self._extract_performance_hints(soup),
            'accessibility': self._extract_accessibility_info(soup)
        }
        
        return tech
    
    def _detect_doctype(self, html: str) -> Optional[str]:
        """DOCTYPE 감지"""
        doctype_match = re.match(r'<!DOCTYPE\s+([^>]+)>', html, re.I)
        if doctype_match:
            return doctype_match.group(1)
        return None
    
    def _calculate_dom_depth(self, soup: BeautifulSoup) -> int:
        """DOM 트리 최대 깊이 계산"""
        def get_depth(element):
            if not element.find_all():
                return 1
            return 1 + max(get_depth(child) for child in element.find_all())
        
        try:
            return get_depth(soup.body) if soup.body else 0
        except:
            return 0
    
    def _extract_performance_hints(self, soup: BeautifulSoup) -> Dict[str, Any]:
        """성능 관련 힌트 추출"""
        hints = {
            'lazy_loading_images': 0,
            'async_scripts': 0,
            'defer_scripts': 0,
            'inline_styles': 0,
            'inline_scripts': 0
        }
        
        # lazy loading 이미지
        hints['lazy_loading_images'] = len(
            soup.find_all('img', loading='lazy')
        )
        
        # async/defer 스크립트
        hints['async_scripts'] = len(
            soup.find_all('script', async_=True)
        )
        hints['defer_scripts'] = len(
            soup.find_all('script', defer=True)
        )
        
        # 인라인 스타일/스크립트
        hints['inline_styles'] = len(
            soup.find_all('style')
        )
        hints['inline_scripts'] = len(
            soup.find_all('script', src=False)
        )
        
        return hints
    
    def _extract_accessibility_info(self, soup: BeautifulSoup) -> Dict[str, Any]:
        """접근성 정보 추출"""
        accessibility = {
            'images_with_alt': 0,
            'images_without_alt': 0,
            'aria_labels': 0,
            'form_labels': 0,
            'lang_attribute': bool(soup.find('html', lang=True))
        }
        
        # 이미지 alt 속성
        all_images = soup.find_all('img')
        for img in all_images:
            if img.get('alt'):
                accessibility['images_with_alt'] += 1
            else:
                accessibility['images_without_alt'] += 1
        
        # ARIA 라벨
        accessibility['aria_labels'] = len(
            soup.find_all(attrs={'aria-label': True})
        )
        
        # 폼 라벨
        accessibility['form_labels'] = len(
            soup.find_all('label')
        )
        
        return accessibility