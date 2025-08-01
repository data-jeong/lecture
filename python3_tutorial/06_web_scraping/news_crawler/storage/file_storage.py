"""
파일 저장소
크롤링 결과를 파일 시스템에 저장
"""

import json
import csv
from pathlib import Path
from typing import List, Dict, Optional, Any
from datetime import datetime
import logging

from ..core.base_crawler import CrawlResult


class FileStorage:
    """파일 기반 저장소"""
    
    def __init__(self, base_dir: str = "data"):
        self.base_dir = Path(base_dir)
        self.base_dir.mkdir(exist_ok=True)
        
        # 서브 디렉토리 생성
        (self.base_dir / "articles").mkdir(exist_ok=True)
        (self.base_dir / "raw_html").mkdir(exist_ok=True)
        (self.base_dir / "comments").mkdir(exist_ok=True)
        (self.base_dir / "metadata").mkdir(exist_ok=True)
        
        self.logger = logging.getLogger(self.__class__.__name__)
    
    def save_article(self, result: CrawlResult) -> str:
        """기사 데이터 저장"""
        # 파일명 생성
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        domain = self._extract_domain(result.url)
        filename = f"{domain}_{timestamp}.json"
        
        # 저장 경로
        filepath = self.base_dir / "articles" / filename
        
        # 데이터 준비
        article_data = result.to_dict()
        article_data['saved_at'] = datetime.now().isoformat()
        
        # JSON 저장
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(article_data, f, indent=2, ensure_ascii=False)
        
        self.logger.info(f"Article saved: {filepath}")
        return str(filepath)
    
    def save_raw_html(self, result: CrawlResult) -> str:
        """원본 HTML 저장"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        domain = self._extract_domain(result.url)
        filename = f"{domain}_{timestamp}.html"
        
        filepath = self.base_dir / "raw_html" / filename
        
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(result.raw_html or "")
        
        self.logger.info(f"Raw HTML saved: {filepath}")
        return str(filepath)
    
    def save_comments(self, comments: List[Dict], url: str) -> str:
        """댓글 데이터 저장"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        domain = self._extract_domain(url)
        filename = f"{domain}_comments_{timestamp}.json"
        
        filepath = self.base_dir / "comments" / filename
        
        data = {
            'url': url,
            'saved_at': datetime.now().isoformat(),
            'comment_count': len(comments),
            'comments': comments
        }
        
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
        
        self.logger.info(f"Comments saved: {filepath}")
        return str(filepath)
    
    def save_metadata(self, metadata: Dict, url: str) -> str:
        """메타데이터 저장"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        domain = self._extract_domain(url)
        filename = f"{domain}_metadata_{timestamp}.json"
        
        filepath = self.base_dir / "metadata" / filename
        
        data = {
            'url': url,
            'saved_at': datetime.now().isoformat(),
            'metadata': metadata
        }
        
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
        
        self.logger.info(f"Metadata saved: {filepath}")
        return str(filepath)
    
    def save_batch(self, results: List[CrawlResult]) -> str:
        """배치 저장"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"batch_crawl_{timestamp}.json"
        
        filepath = self.base_dir / filename
        
        data = {
            'saved_at': datetime.now().isoformat(),
            'total_count': len(results),
            'successful_count': sum(1 for r in results if r.success),
            'failed_count': sum(1 for r in results if not r.success),
            'results': [r.to_dict() for r in results]
        }
        
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
        
        self.logger.info(f"Batch saved: {filepath} ({len(results)} items)")
        return str(filepath)
    
    def export_to_csv(self, articles: List[Dict], filename: str) -> str:
        """CSV로 내보내기"""
        filepath = self.base_dir / filename
        
        if not articles:
            self.logger.warning("No articles to export")
            return str(filepath)
        
        # CSV 필드 정의
        fieldnames = [
            'url', 'title', 'author', 'published_date',
            'content', 'word_count', 'category', 'language',
            'crawled_at'
        ]
        
        with open(filepath, 'w', newline='', encoding='utf-8') as f:
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            
            for article in articles:
                # 필드 매핑
                row = {}
                for field in fieldnames:
                    if field == 'content':
                        # 내용은 줄바꿈 제거
                        content = article.get('content', '')
                        row[field] = content.replace('\n', ' ').replace('\r', '')
                    elif field == 'published_date':
                        # 날짜 형식 변환
                        date = article.get('published_date')
                        if isinstance(date, datetime):
                            row[field] = date.isoformat()
                        else:
                            row[field] = str(date) if date else ''
                    else:
                        row[field] = article.get(field, '')
                
                writer.writerow(row)
        
        self.logger.info(f"CSV exported: {filepath} ({len(articles)} articles)")
        return str(filepath)
    
    def load_articles(self, pattern: str = "*.json") -> List[Dict]:
        """저장된 기사 로드"""
        articles = []
        articles_dir = self.base_dir / "articles"
        
        for filepath in articles_dir.glob(pattern):
            try:
                with open(filepath, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    articles.append(data)
            except Exception as e:
                self.logger.error(f"Error loading {filepath}: {e}")
        
        self.logger.info(f"Loaded {len(articles)} articles")
        return articles
    
    def get_by_title(self, title: str) -> Optional[Dict]:
        """제목으로 기사 검색"""
        articles = self.load_articles()
        
        for article in articles:
            if article.get('title') == title:
                return article
        
        return None
    
    def get_by_url(self, url: str) -> Optional[Dict]:
        """URL로 기사 검색"""
        articles = self.load_articles()
        
        for article in articles:
            if article.get('url') == url:
                return article
        
        return None
    
    def search_articles(self, 
                       keyword: Optional[str] = None,
                       author: Optional[str] = None,
                       domain: Optional[str] = None,
                       start_date: Optional[datetime] = None,
                       end_date: Optional[datetime] = None) -> List[Dict]:
        """기사 검색"""
        articles = self.load_articles()
        results = []
        
        for article in articles:
            # 키워드 검색
            if keyword:
                content = (article.get('content', '') + ' ' + 
                          article.get('title', '')).lower()
                if keyword.lower() not in content:
                    continue
            
            # 작성자 검색
            if author:
                if article.get('author', '').lower() != author.lower():
                    continue
            
            # 도메인 검색
            if domain:
                article_domain = self._extract_domain(article.get('url', ''))
                if domain.lower() not in article_domain.lower():
                    continue
            
            # 날짜 필터
            if start_date or end_date:
                pub_date_str = article.get('published_date')
                if pub_date_str:
                    try:
                        pub_date = datetime.fromisoformat(pub_date_str)
                        
                        if start_date and pub_date < start_date:
                            continue
                        if end_date and pub_date > end_date:
                            continue
                    except:
                        continue
            
            results.append(article)
        
        self.logger.info(f"Search found {len(results)} articles")
        return results
    
    def get_statistics(self) -> Dict[str, Any]:
        """저장소 통계"""
        articles_count = len(list((self.base_dir / "articles").glob("*.json")))
        html_count = len(list((self.base_dir / "raw_html").glob("*.html")))
        comments_count = len(list((self.base_dir / "comments").glob("*.json")))
        metadata_count = len(list((self.base_dir / "metadata").glob("*.json")))
        
        # 디스크 사용량
        total_size = sum(
            f.stat().st_size for f in self.base_dir.rglob("*") 
            if f.is_file()
        )
        
        return {
            'articles_count': articles_count,
            'raw_html_count': html_count, 
            'comments_count': comments_count,
            'metadata_count': metadata_count,
            'total_size_mb': total_size / (1024 * 1024),
            'storage_path': str(self.base_dir)
        }
    
    def cleanup_old_files(self, days: int = 30):
        """오래된 파일 정리"""
        from datetime import timedelta
        
        cutoff = datetime.now() - timedelta(days=days)
        removed_count = 0
        
        for filepath in self.base_dir.rglob("*"):
            if filepath.is_file():
                file_time = datetime.fromtimestamp(filepath.stat().st_mtime)
                if file_time < cutoff:
                    filepath.unlink()
                    removed_count += 1
        
        self.logger.info(f"Cleaned up {removed_count} old files")
    
    def _extract_domain(self, url: str) -> str:
        """URL에서 도메인 추출"""
        from urllib.parse import urlparse
        
        try:
            parsed = urlparse(url)
            domain = parsed.netloc
            
            # www. 제거
            if domain.startswith('www.'):
                domain = domain[4:]
            
            return domain.replace('.', '_')
        except:
            return "unknown"