import scrapy
from datetime import datetime
from urllib.parse import urljoin
from ..items import NewsItem


class NewsSpider(scrapy.Spider):
    name = 'news'
    allowed_domains = []  # 동적으로 설정
    start_urls = []       # 동적으로 설정
    
    def __init__(self, start_urls=None, *args, **kwargs):
        super(NewsSpider, self).__init__(*args, **kwargs)
        
        if start_urls:
            if isinstance(start_urls, str):
                self.start_urls = start_urls.split(',')
            else:
                self.start_urls = start_urls
            
            # allowed_domains 자동 설정
            from urllib.parse import urlparse
            for url in self.start_urls:
                domain = urlparse(url).netloc
                if domain not in self.allowed_domains:
                    self.allowed_domains.append(domain)
    
    def parse(self, response):
        """메인 파싱 메서드"""
        # 기사 목록 페이지 파싱
        article_links = self.extract_article_links(response)
        
        for link in article_links:
            absolute_url = urljoin(response.url, link)
            yield scrapy.Request(
                absolute_url,
                callback=self.parse_article,
                meta={'source_page': response.url}
            )
        
        # 다음 페이지 링크
        next_page = self.extract_next_page(response)
        if next_page:
            yield response.follow(next_page, self.parse)
    
    def parse_article(self, response):
        """개별 기사 파싱"""
        item = NewsItem()
        
        # 기본 정보
        item['url'] = response.url
        item['title'] = self.extract_title(response)
        item['content'] = self.extract_content(response)
        item['author'] = self.extract_author(response)
        item['published_date'] = self.extract_date(response)
        item['category'] = self.extract_category(response)
        item['tags'] = self.extract_tags(response)
        item['images'] = self.extract_images(response)
        item['links'] = self.extract_links(response)
        item['crawled_at'] = datetime.now().isoformat()
        
        # 추가 처리
        if item['content']:
            item['word_count'] = len(item['content'].split())
            item['reading_time'] = max(1, item['word_count'] // 200)
            item['language'] = self.detect_language(item['content'])
        
        # 메타데이터
        item['metadata'] = {
            'source_page': response.meta.get('source_page'),
            'scrapy_spider': self.name,
            'response_status': response.status,
            'response_headers': dict(response.headers)
        }
        
        yield item
    
    def extract_article_links(self, response):
        """기사 링크 추출"""
        # 일반적인 뉴스 사이트 패턴
        selectors = [
            'a[href*="/article/"]::attr(href)',
            'a[href*="/news/"]::attr(href)',
            'a[href*="/story/"]::attr(href)',
            '.article-title a::attr(href)',
            '.news-item a::attr(href)',
            'h2 a::attr(href)',
            'h3 a::attr(href)',
        ]
        
        links = []
        for selector in selectors:
            found_links = response.css(selector).getall()
            links.extend(found_links)
            
            if links:  # 하나라도 찾으면 중단
                break
        
        # 중복 제거
        return list(set(links))
    
    def extract_next_page(self, response):
        """다음 페이지 링크 추출"""
        next_selectors = [
            'a.next::attr(href)',
            'a[rel="next"]::attr(href)',
            '.pagination .next::attr(href)',
            '.paging .next::attr(href)',
            'a:contains("다음")::attr(href)',
            'a:contains("Next")::attr(href)',
        ]
        
        for selector in next_selectors:
            next_link = response.css(selector).get()
            if next_link:
                return next_link
        
        return None
    
    def extract_title(self, response):
        """제목 추출"""
        selectors = [
            'h1::text',
            '.article-title::text',
            '.news-title::text',
            'title::text',
            'h2::text',
        ]
        
        for selector in selectors:
            title = response.css(selector).get()
            if title:
                return title.strip()
        
        return None
    
    def extract_content(self, response):
        """본문 추출"""
        # 먼저 article 태그 시도
        article_content = response.css('article').get()
        if article_content:
            paragraphs = response.css('article p::text').getall()
            if paragraphs:
                return '\n\n'.join(p.strip() for p in paragraphs if p.strip())
        
        # 일반적인 컨텐츠 선택자
        content_selectors = [
            '.article-content p::text',
            '.article-body p::text',
            '.news-content p::text',
            '.content p::text',
            '.entry-content p::text',
            'div[id*="content"] p::text',
            'div[class*="content"] p::text',
        ]
        
        for selector in content_selectors:
            paragraphs = response.css(selector).getall()
            if paragraphs:
                content = '\n\n'.join(p.strip() for p in paragraphs if p.strip())
                if len(content) > 100:  # 최소 길이 확인
                    return content
        
        return None
    
    def extract_author(self, response):
        """작성자 추출"""
        author_selectors = [
            '.author::text',
            '.byline::text',
            '.writer::text',
            '.journalist::text',
            'span[class*="author"]::text',
            'div[class*="author"]::text',
            '[itemprop="author"]::text',
        ]
        
        for selector in author_selectors:
            author = response.css(selector).get()
            if author:
                # 불필요한 텍스트 제거
                author = author.strip()
                author = author.replace('기자', '').replace('리포터', '').strip()
                if author:
                    return author
        
        return None
    
    def extract_date(self, response):
        """날짜 추출"""
        # time 태그의 datetime 속성
        datetime_attr = response.css('time::attr(datetime)').get()
        if datetime_attr:
            return datetime_attr
        
        # 기타 날짜 선택자
        date_selectors = [
            '.date::text',
            '.published::text',
            '.timestamp::text',
            'time::text',
            'span[class*="date"]::text',
        ]
        
        for selector in date_selectors:
            date_text = response.css(selector).get()
            if date_text:
                return date_text.strip()
        
        return None
    
    def extract_category(self, response):
        """카테고리 추출"""
        # URL에서 추출
        url_path = response.url.split('/')
        categories = ['politics', 'economy', 'society', 'culture', 'sports', 'tech', 'world']
        
        for part in url_path:
            if part.lower() in categories:
                return part.capitalize()
        
        # 페이지에서 추출
        category_selectors = [
            '.category::text',
            '.section::text',
            'nav .active::text',
            '.breadcrumb a:last-child::text',
        ]
        
        for selector in category_selectors:
            category = response.css(selector).get()
            if category:
                return category.strip()
        
        return None
    
    def extract_tags(self, response):
        """태그 추출"""
        tag_selectors = [
            '.tags a::text',
            '.keywords a::text',
            '.tag-list a::text',
            '[class*="tag"] a::text',
        ]
        
        tags = []
        for selector in tag_selectors:
            found_tags = response.css(selector).getall()
            tags.extend(t.strip() for t in found_tags)
        
        return list(set(tags))  # 중복 제거
    
    def extract_images(self, response):
        """이미지 추출"""
        # 기사 영역의 이미지만
        article_area = response.css('article') or response
        
        images = []
        for img in article_area.css('img'):
            src = img.css('::attr(src)').get()
            if src:
                absolute_url = urljoin(response.url, src)
                images.append({
                    'url': absolute_url,
                    'alt': img.css('::attr(alt)').get() or '',
                    'caption': self.extract_image_caption(img)
                })
        
        return images
    
    def extract_image_caption(self, img_selector):
        """이미지 캡션 추출"""
        # figcaption 찾기
        figcaption = img_selector.xpath('./following-sibling::figcaption/text()').get()
        if figcaption:
            return figcaption.strip()
        
        # 다음 요소가 캡션인 경우
        next_elem = img_selector.xpath('./following-sibling::*[1]')
        if next_elem:
            class_attr = next_elem.css('::attr(class)').get() or ''
            if 'caption' in class_attr:
                return next_elem.css('::text').get() or ''
        
        return ''
    
    def extract_links(self, response):
        """관련 링크 추출"""
        article_area = response.css('article') or response
        
        links = []
        for link in article_area.css('a[href]'):
            href = link.css('::attr(href)').get()
            text = link.css('::text').get()
            
            if href and text:
                absolute_url = urljoin(response.url, href)
                links.append({
                    'url': absolute_url,
                    'text': text.strip()
                })
        
        return links
    
    def detect_language(self, content):
        """언어 감지 (간단한 구현)"""
        if not content:
            return 'unknown'
        
        # 한글 문자 비율 확인
        korean_chars = len([c for c in content if '\uac00' <= c <= '\ud7af'])
        total_chars = len([c for c in content if c.isalpha()])
        
        if total_chars > 0:
            korean_ratio = korean_chars / total_chars
            if korean_ratio > 0.3:
                return 'ko'
        
        return 'en'