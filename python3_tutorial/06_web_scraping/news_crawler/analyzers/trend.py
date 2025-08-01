"""
트렌드 분석기
시간별, 키워드별 트렌드 분석
"""

from typing import List, Dict, Any, Optional, Tuple
from collections import Counter, defaultdict
from datetime import datetime, timedelta
import logging
import re


class TrendAnalyzer:
    """트렌드 분석기"""
    
    def __init__(self):
        self.logger = logging.getLogger(self.__class__.__name__)
    
    def analyze(self, articles: List[Dict[str, Any]]) -> Dict[str, Any]:
        """종합 트렌드 분석"""
        if not articles:
            return {}
        
        trends = {
            'temporal_trends': self.analyze_temporal_trends(articles),
            'keyword_trends': self.analyze_keyword_trends(articles),
            'category_trends': self.analyze_category_trends(articles),
            'author_trends': self.analyze_author_trends(articles),
            'sentiment_trends': self.analyze_sentiment_trends(articles),
            'source_trends': self.analyze_source_trends(articles),
            'content_length_trends': self.analyze_content_length_trends(articles)
        }
        
        return trends
    
    def analyze_temporal_trends(self, articles: List[Dict[str, Any]]) -> Dict[str, Any]:
        """시간별 트렌드 분석"""
        # 날짜별 기사 수
        daily_counts = defaultdict(int)
        hourly_counts = defaultdict(int)
        weekly_counts = defaultdict(int)
        monthly_counts = defaultdict(int)
        
        date_formats = [
            '%Y-%m-%d',
            '%Y-%m-%dT%H:%M:%S',
            '%Y-%m-%d %H:%M:%S'
        ]
        
        valid_dates = []
        
        for article in articles:
            date_str = article.get('published_date') or article.get('crawled_at')
            if not date_str:
                continue
            
            # 날짜 파싱
            parsed_date = None
            for fmt in date_formats:
                try:
                    if isinstance(date_str, str):
                        parsed_date = datetime.strptime(date_str[:len(fmt)], fmt)
                    elif isinstance(date_str, datetime):
                        parsed_date = date_str
                    break
                except:
                    continue
            
            if not parsed_date:
                continue
            
            valid_dates.append(parsed_date)
            
            # 시간대별 집계
            daily_key = parsed_date.strftime('%Y-%m-%d')
            hourly_key = parsed_date.strftime('%Y-%m-%d %H')
            weekly_key = f"{parsed_date.year}-W{parsed_date.isocalendar().week:02d}"
            monthly_key = parsed_date.strftime('%Y-%m')
            
            daily_counts[daily_key] += 1
            hourly_counts[hourly_key] += 1
            weekly_counts[weekly_key] += 1
            monthly_counts[monthly_key] += 1
        
        # 통계 계산
        if valid_dates:
            date_range = max(valid_dates) - min(valid_dates)
            avg_articles_per_day = len(valid_dates) / max(date_range.days, 1)
        else:
            avg_articles_per_day = 0
        
        return {
            'total_articles': len(articles),
            'articles_with_dates': len(valid_dates),
            'date_range_days': date_range.days if valid_dates else 0,
            'avg_articles_per_day': avg_articles_per_day,
            'daily_distribution': dict(daily_counts),
            'hourly_distribution': dict(hourly_counts),
            'weekly_distribution': dict(weekly_counts),
            'monthly_distribution': dict(monthly_counts),
            'peak_day': max(daily_counts.items(), key=lambda x: x[1]) if daily_counts else None,
            'peak_hour': max(hourly_counts.items(), key=lambda x: x[1]) if hourly_counts else None
        }
    
    def analyze_keyword_trends(self, articles: List[Dict[str, Any]]) -> Dict[str, Any]:
        """키워드 트렌드 분석"""
        all_keywords = []
        keyword_by_date = defaultdict(list)
        
        for article in articles:
            # 키워드 추출
            keywords = []
            
            # 태그에서 키워드
            if 'tags' in article and article['tags']:
                keywords.extend(article['tags'])
            
            # 제목에서 키워드 추출
            title = article.get('title', '')
            if title:
                title_keywords = self._extract_keywords_from_text(title)
                keywords.extend(title_keywords)
            
            # 내용에서 키워드 추출 (처음 200자)
            content = article.get('content', '')
            if content:
                content_keywords = self._extract_keywords_from_text(content[:200])
                keywords.extend(content_keywords)
            
            all_keywords.extend(keywords)
            
            # 날짜별 키워드
            date_str = article.get('published_date')
            if date_str:
                try:
                    if isinstance(date_str, str):
                        date = datetime.fromisoformat(date_str.replace('Z', '+00:00'))
                    else:
                        date = date_str
                    date_key = date.strftime('%Y-%m-%d')
                    keyword_by_date[date_key].extend(keywords)
                except:
                    pass
        
        # 키워드 빈도 분석
        keyword_counts = Counter(all_keywords)
        top_keywords = keyword_counts.most_common(50)
        
        # 날짜별 키워드 트렌드
        daily_keyword_trends = {}
        for date, keywords in keyword_by_date.items():
            daily_counts = Counter(keywords)
            daily_keyword_trends[date] = daily_counts.most_common(10)
        
        # 급상승 키워드 찾기
        trending_keywords = self._find_trending_keywords(keyword_by_date)
        
        return {
            'total_keywords': len(all_keywords),
            'unique_keywords': len(set(all_keywords)),
            'top_keywords': top_keywords,
            'daily_keyword_trends': daily_keyword_trends,
            'trending_keywords': trending_keywords,
            'keyword_diversity': len(set(all_keywords)) / len(all_keywords) if all_keywords else 0
        }
    
    def analyze_category_trends(self, articles: List[Dict[str, Any]]) -> Dict[str, Any]:
        """카테고리 트렌드 분석"""
        categories = [article.get('category') for article in articles if article.get('category')]
        
        if not categories:
            return {'message': 'No category information available'}
        
        category_counts = Counter(categories)
        
        # 카테고리별 시간 분포
        category_by_date = defaultdict(lambda: defaultdict(int))
        
        for article in articles:
            category = article.get('category')
            date_str = article.get('published_date')
            
            if category and date_str:
                try:
                    if isinstance(date_str, str):
                        date = datetime.fromisoformat(date_str.replace('Z', '+00:00'))
                    else:
                        date = date_str
                    date_key = date.strftime('%Y-%m-%d')
                    category_by_date[category][date_key] += 1
                except:
                    pass
        
        return {
            'category_distribution': dict(category_counts),
            'total_categories': len(category_counts),
            'most_popular_category': category_counts.most_common(1)[0] if category_counts else None,
            'category_daily_trends': dict(category_by_date)
        }
    
    def analyze_author_trends(self, articles: List[Dict[str, Any]]) -> Dict[str, Any]:
        """작성자 트렌드 분석"""
        authors = [article.get('author') for article in articles if article.get('author')]
        
        if not authors:
            return {'message': 'No author information available'}
        
        author_counts = Counter(authors)
        
        # 작성자별 기사 길이 분석
        author_content_lengths = defaultdict(list)
        
        for article in articles:
            author = article.get('author')
            content = article.get('content', '')
            
            if author and content:
                author_content_lengths[author].append(len(content))
        
        # 평균 기사 길이 계산
        author_avg_lengths = {}
        for author, lengths in author_content_lengths.items():
            if lengths:
                author_avg_lengths[author] = sum(lengths) / len(lengths)
        
        return {
            'total_authors': len(set(authors)),
            'author_article_counts': dict(author_counts.most_common(20)),
            'most_prolific_author': author_counts.most_common(1)[0] if author_counts else None,
            'author_avg_article_lengths': author_avg_lengths
        }
    
    def analyze_sentiment_trends(self, articles: List[Dict[str, Any]]) -> Dict[str, Any]:
        """감정 트렌드 분석"""
        sentiments = []
        sentiment_by_date = defaultdict(list)
        
        for article in articles:
            # 메타데이터에서 감정 정보 찾기
            sentiment = None
            
            if 'sentiment_analysis' in article:
                sentiment = article['sentiment_analysis'].get('sentiment')
            elif 'sentiment' in article:
                sentiment = article['sentiment']
            else:
                # 간단한 감정 분석 (키워드 기반)
                title = article.get('title', '')
                content = article.get('content', '')
                text = f"{title} {content}"
                sentiment = self._simple_sentiment_analysis(text)
            
            if sentiment:
                sentiments.append(sentiment)
                
                # 날짜별 감정
                date_str = article.get('published_date')
                if date_str:
                    try:
                        if isinstance(date_str, str):
                            date = datetime.fromisoformat(date_str.replace('Z', '+00:00'))
                        else:
                            date = date_str
                        date_key = date.strftime('%Y-%m-%d')
                        sentiment_by_date[date_key].append(sentiment)
                    except:
                        pass
        
        if not sentiments:
            return {'message': 'No sentiment information available'}
        
        sentiment_counts = Counter(sentiments)
        
        # 날짜별 감정 분포
        daily_sentiment = {}
        for date, day_sentiments in sentiment_by_date.items():
            daily_sentiment[date] = dict(Counter(day_sentiments))
        
        return {
            'overall_sentiment_distribution': dict(sentiment_counts),
            'positive_ratio': sentiment_counts.get('positive', 0) / len(sentiments),
            'negative_ratio': sentiment_counts.get('negative', 0) / len(sentiments),
            'neutral_ratio': sentiment_counts.get('neutral', 0) / len(sentiments),
            'daily_sentiment_trends': daily_sentiment
        }
    
    def analyze_source_trends(self, articles: List[Dict[str, Any]]) -> Dict[str, Any]:
        """소스 트렌드 분석"""
        sources = []
        
        for article in articles:
            url = article.get('url', '')
            if url:
                # URL에서 도메인 추출
                import re
                domain_match = re.search(r'https?://(?:www\.)?([^/]+)', url)
                if domain_match:
                    domain = domain_match.group(1)
                    sources.append(domain)
        
        if not sources:
            return {'message': 'No source information available'}
        
        source_counts = Counter(sources)
        
        return {
            'total_sources': len(set(sources)),
            'source_distribution': dict(source_counts.most_common(20)),
            'most_active_source': source_counts.most_common(1)[0] if source_counts else None
        }
    
    def analyze_content_length_trends(self, articles: List[Dict[str, Any]]) -> Dict[str, Any]:
        """컨텐츠 길이 트렌드 분석"""
        lengths = []
        lengths_by_date = defaultdict(list)
        
        for article in articles:
            content = article.get('content', '')
            word_count = article.get('word_count')
            
            if word_count:
                length = word_count
            elif content:
                length = len(content.split())
            else:
                continue
            
            lengths.append(length)
            
            # 날짜별 길이
            date_str = article.get('published_date')
            if date_str:
                try:
                    if isinstance(date_str, str):
                        date = datetime.fromisoformat(date_str.replace('Z', '+00:00'))
                    else:
                        date = date_str
                    date_key = date.strftime('%Y-%m-%d')
                    lengths_by_date[date_key].append(length)
                except:
                    pass
        
        if not lengths:
            return {'message': 'No content length information available'}
        
        # 통계 계산
        avg_length = sum(lengths) / len(lengths)
        min_length = min(lengths)
        max_length = max(lengths)
        
        # 날짜별 평균 길이
        daily_avg_lengths = {}
        for date, day_lengths in lengths_by_date.items():
            if day_lengths:
                daily_avg_lengths[date] = sum(day_lengths) / len(day_lengths)
        
        return {
            'average_content_length': avg_length,
            'min_content_length': min_length,
            'max_content_length': max_length,
            'daily_avg_content_lengths': daily_avg_lengths,
            'content_length_distribution': self._get_length_distribution(lengths)
        }
    
    def _extract_keywords_from_text(self, text: str) -> List[str]:
        """텍스트에서 간단한 키워드 추출"""
        # 간단한 키워드 추출 (정규표현식 기반)
        keywords = []
        
        # 한글 키워드 (2글자 이상)
        korean_words = re.findall(r'[가-힣]{2,}', text)
        keywords.extend(korean_words)
        
        # 영어 키워드 (3글자 이상, 대문자 시작)
        english_words = re.findall(r'\b[A-Z][a-z]{2,}\b', text)
        keywords.extend(english_words)
        
        # 불용어 제거
        stopwords = {'그런', '이런', '저런', '그리고', '하지만', '그래서', '그러나'}
        keywords = [kw for kw in keywords if kw not in stopwords]
        
        return keywords
    
    def _find_trending_keywords(self, keyword_by_date: Dict[str, List[str]]) -> List[Tuple[str, float]]:
        """급상승 키워드 찾기"""
        if len(keyword_by_date) < 2:
            return []
        
        dates = sorted(keyword_by_date.keys())
        recent_dates = dates[-3:]  # 최근 3일
        earlier_dates = dates[:-3] if len(dates) > 3 else []
        
        if not earlier_dates:
            return []
        
        # 최근 키워드 빈도
        recent_keywords = []
        for date in recent_dates:
            recent_keywords.extend(keyword_by_date[date])
        recent_counts = Counter(recent_keywords)
        
        # 이전 키워드 빈도
        earlier_keywords = []
        for date in earlier_dates:
            earlier_keywords.extend(keyword_by_date[date])
        earlier_counts = Counter(earlier_keywords)
        
        # 트렌드 점수 계산
        trending = []
        for keyword, recent_count in recent_counts.items():
            earlier_count = earlier_counts.get(keyword, 0)
            
            if recent_count >= 2:  # 최소 빈도
                if earlier_count == 0:
                    trend_score = float('inf')
                else:
                    trend_score = recent_count / earlier_count
                
                trending.append((keyword, trend_score))
        
        # 상위 10개 반환
        trending.sort(key=lambda x: x[1], reverse=True)
        return trending[:10]
    
    def _simple_sentiment_analysis(self, text: str) -> str:
        """간단한 감정 분석"""
        text = text.lower()
        
        positive_words = ['좋다', '훌륭하다', '멋지다', '성공', '발전', '향상', '개선']
        negative_words = ['나쁘다', '최악', '실패', '문제', '심각', '걱정', '위험']
        
        positive_count = sum(1 for word in positive_words if word in text)
        negative_count = sum(1 for word in negative_words if word in text)
        
        if positive_count > negative_count:
            return 'positive'
        elif negative_count > positive_count:
            return 'negative'
        else:
            return 'neutral'
    
    def _get_length_distribution(self, lengths: List[int]) -> Dict[str, int]:
        """길이 분포 계산"""
        distribution = {
            'very_short': 0,  # < 100 단어
            'short': 0,       # 100-300 단어
            'medium': 0,      # 300-600 단어
            'long': 0,        # 600-1000 단어
            'very_long': 0    # > 1000 단어
        }
        
        for length in lengths:
            if length < 100:
                distribution['very_short'] += 1
            elif length < 300:
                distribution['short'] += 1
            elif length < 600:
                distribution['medium'] += 1
            elif length < 1000:
                distribution['long'] += 1
            else:
                distribution['very_long'] += 1
        
        return distribution