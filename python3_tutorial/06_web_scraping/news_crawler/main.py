#!/usr/bin/env python3
"""
뉴스 크롤러 CLI
다양한 웹 스크래핑 도구를 활용한 뉴스 수집
"""

import argparse
import asyncio
import json
import sys
from pathlib import Path
from typing import List, Optional
import logging
from datetime import datetime

from core import (
    RequestsCrawler,
    SeleniumCrawler,
    HttpxCrawler,
    CrawlResult
)
from extractors import (
    NewsExtractor,
    CommentExtractor,
    MetadataExtractor
)
from analyzers import (
    SentimentAnalyzer,
    KeywordExtractor,
    TrendAnalyzer
)
from storage import FileStorage, DatabaseStorage
from utils import ProxyManager, UserAgentManager


class NewsCrawlerCLI:
    """뉴스 크롤러 CLI"""
    
    def __init__(self):
        self.setup_logging()
        self.news_extractor = NewsExtractor()
        self.comment_extractor = CommentExtractor()
        self.metadata_extractor = MetadataExtractor()
        self.user_agent_manager = UserAgentManager()
    
    def setup_logging(self):
        """로깅 설정"""
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            handlers=[
                logging.StreamHandler(),
                logging.FileHandler('news_crawler.log')
            ]
        )
        self.logger = logging.getLogger('NewsCrawlerCLI')
    
    def crawl_single(self, args):
        """단일 URL 크롤링"""
        self.logger.info(f"Crawling single URL: {args.url}")
        
        # 크롤러 선택
        crawler = self._get_crawler(args)
        
        # 크롤링 실행
        result = crawler.crawl(args.url)
        
        if result.success:
            self.logger.info(f"Successfully crawled: {args.url}")
            
            # 뉴스 데이터 추출
            if args.extract:
                news_data = self.news_extractor.extract(result.raw_html, args.url)
                result.metadata.update(news_data)
            
            # 댓글 추출
            if args.comments:
                comments = self.comment_extractor.extract(result.raw_html, args.url)
                result.metadata['comments'] = comments
            
            # 메타데이터 추출
            if args.metadata:
                metadata = self.metadata_extractor.extract(result.raw_html, args.url)
                result.metadata['full_metadata'] = metadata
            
            # 결과 저장
            self._save_result(result, args)
            
            # 결과 출력
            if args.verbose:
                self._print_result(result)
        else:
            self.logger.error(f"Failed to crawl: {result.error}")
        
        # 크롤러 종료
        crawler.close()
    
    def crawl_multiple(self, args):
        """여러 URL 크롤링"""
        # URL 목록 읽기
        urls = self._read_urls(args.urls_file)
        self.logger.info(f"Crawling {len(urls)} URLs")
        
        # 크롤러 선택
        crawler = self._get_crawler(args)
        
        # 크롤링 실행
        if args.type == 'httpx' and args.concurrent:
            # 비동기 동시 크롤링
            results = asyncio.run(
                crawler.crawl_multiple_async(urls[:args.limit])
            )
        else:
            # 순차 크롤링
            results = crawler.crawl_multiple(urls[:args.limit])
        
        # 결과 처리
        successful = [r for r in results if r.success]
        failed = [r for r in results if not r.success]
        
        self.logger.info(f"Completed: {len(successful)} successful, {len(failed)} failed")
        
        # 뉴스 데이터 추출
        if args.extract:
            for result in successful:
                news_data = self.news_extractor.extract(result.raw_html, result.url)
                result.metadata.update(news_data)
        
        # 결과 저장
        self._save_results(results, args)
        
        # 통계 출력
        if args.stats:
            self._print_stats(crawler)
        
        # 크롤러 종료
        crawler.close()
    
    def analyze(self, args):
        """크롤링 데이터 분석"""
        # 데이터 로드
        data = self._load_data(args.input)
        
        if not data:
            self.logger.error("No data to analyze")
            return
        
        self.logger.info(f"Analyzing {len(data)} items")
        
        results = {}
        
        # 감정 분석
        if args.sentiment:
            analyzer = SentimentAnalyzer()
            sentiments = []
            
            for item in data:
                content = item.get('content') or item.get('title', '')
                if content:
                    sentiment = analyzer.analyze(content)
                    sentiments.append(sentiment)
            
            results['sentiment_analysis'] = analyzer.get_summary(sentiments)
            self.logger.info("Sentiment analysis completed")
        
        # 키워드 추출
        if args.keywords:
            extractor = KeywordExtractor()
            all_keywords = []
            
            for item in data:
                content = item.get('content') or item.get('title', '')
                if content:
                    keywords = extractor.extract(content, top_n=args.top_keywords)
                    all_keywords.extend(keywords)
            
            results['keywords'] = extractor.get_top_keywords(all_keywords, top_n=50)
            self.logger.info("Keyword extraction completed")
        
        # 트렌드 분석
        if args.trends:
            analyzer = TrendAnalyzer()
            trends = analyzer.analyze(data)
            results['trends'] = trends
            self.logger.info("Trend analysis completed")
        
        # 결과 저장
        output_file = args.output or 'analysis_results.json'
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(results, f, indent=2, ensure_ascii=False)
        
        self.logger.info(f"Analysis results saved to: {output_file}")
        
        # 결과 출력
        if args.verbose:
            self._print_analysis_results(results)
    
    def monitor(self, args):
        """사이트 모니터링"""
        self.logger.info(f"Starting monitoring: {args.site}")
        
        crawler = self._get_crawler(args)
        storage = FileStorage(args.output_dir or 'monitoring_data')
        
        try:
            while True:
                self.logger.info(f"Checking {args.site}")
                
                # 크롤링
                result = crawler.crawl(args.site)
                
                if result.success:
                    # 뉴스 추출
                    news_data = self.news_extractor.extract(result.raw_html, args.site)
                    result.metadata.update(news_data)
                    
                    # 새 기사 확인
                    if self._is_new_article(result, storage):
                        self.logger.info(f"New article found: {result.title}")
                        
                        # 저장
                        storage.save_article(result)
                        
                        # 알림 (구현 필요)
                        if args.notify:
                            self._send_notification(result)
                
                # 대기
                self.logger.info(f"Waiting {args.interval} seconds...")
                time.sleep(args.interval)
                
        except KeyboardInterrupt:
            self.logger.info("Monitoring stopped")
        finally:
            crawler.close()
    
    def _get_crawler(self, args):
        """크롤러 인스턴스 생성"""
        # User-Agent 설정
        if args.random_ua:
            user_agent = self.user_agent_manager.get_random_user_agent()
        else:
            user_agent = args.user_agent
        
        # 프록시 설정
        proxy = None
        if args.proxy:
            proxy = args.proxy
        elif args.proxy_file:
            proxy_manager = ProxyManager()
            proxy_manager.load_from_file(args.proxy_file)
            proxy_obj = proxy_manager.get_proxy()
            proxy = proxy_obj.url if proxy_obj else None
        
        # 공통 설정
        crawler_config = {
            'timeout': args.timeout,
            'retry_count': args.retry,
            'delay': args.delay,
            'user_agent': user_agent,
            'proxy': proxy
        }
        
        # 크롤러 타입별 생성
        if args.type == 'requests':
            return RequestsCrawler(**crawler_config)
        
        elif args.type == 'selenium':
            return SeleniumCrawler(
                headless=not args.show_browser,
                **crawler_config
            )
        
        elif args.type == 'httpx':
            return HttpxCrawler(
                max_connections=args.concurrent or 10,
                **crawler_config
            )
        
        else:
            raise ValueError(f"Unknown crawler type: {args.type}")
    
    def _read_urls(self, filename: str) -> List[str]:
        """URL 목록 읽기"""
        urls = []
        
        with open(filename, 'r') as f:
            for line in f:
                url = line.strip()
                if url and not url.startswith('#'):
                    urls.append(url)
        
        return urls
    
    def _load_data(self, filename: str) -> List[dict]:
        """데이터 로드"""
        try:
            with open(filename, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            if isinstance(data, dict):
                # 단일 항목
                return [data]
            elif isinstance(data, list):
                return data
            else:
                return []
                
        except Exception as e:
            self.logger.error(f"Failed to load data: {e}")
            return []
    
    def _save_result(self, result: CrawlResult, args):
        """단일 결과 저장"""
        # 저장 형식
        if args.output_format == 'json':
            output_file = args.output or f"{result.url.replace('/', '_')}.json"
            
            with open(output_file, 'w', encoding='utf-8') as f:
                json.dump(result.to_dict(), f, indent=2, ensure_ascii=False)
        
        elif args.output_format == 'html':
            output_file = args.output or f"{result.url.replace('/', '_')}.html"
            
            with open(output_file, 'w', encoding='utf-8') as f:
                f.write(result.raw_html)
        
        elif args.output_format == 'text':
            output_file = args.output or f"{result.url.replace('/', '_')}.txt"
            
            with open(output_file, 'w', encoding='utf-8') as f:
                f.write(f"URL: {result.url}\n")
                f.write(f"Title: {result.title}\n")
                f.write(f"Author: {result.author}\n")
                f.write(f"Date: {result.published_date}\n")
                f.write(f"\nContent:\n{result.content}\n")
        
        self.logger.info(f"Result saved to: {output_file}")
    
    def _save_results(self, results: List[CrawlResult], args):
        """여러 결과 저장"""
        output_file = args.output or 'crawl_results.json'
        
        # JSON 형식으로 저장
        data = [r.to_dict() for r in results]
        
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
        
        self.logger.info(f"Results saved to: {output_file}")
    
    def _print_result(self, result: CrawlResult):
        """결과 출력"""
        print("\n" + "="*60)
        print(f"URL: {result.url}")
        print(f"Title: {result.title}")
        print(f"Author: {result.author}")
        print(f"Date: {result.published_date}")
        print(f"Content Length: {len(result.content) if result.content else 0} chars")
        print(f"Images: {len(result.images)}")
        print(f"Links: {len(result.links)}")
        
        if result.metadata.get('keywords'):
            print(f"Keywords: {', '.join(result.metadata['keywords'][:5])}")
        
        if result.metadata.get('comments'):
            print(f"Comments: {len(result.metadata['comments'])}")
    
    def _print_stats(self, crawler):
        """통계 출력"""
        stats = crawler.get_stats()
        
        print("\n" + "="*60)
        print("Crawling Statistics:")
        print(f"Total Requests: {stats['total_requests']}")
        print(f"Successful: {stats['successful_requests']}")
        print(f"Failed: {stats['failed_requests']}")
        print(f"Total Bytes: {stats['total_bytes']:,}")
        
        if 'duration' in stats:
            print(f"Duration: {stats['duration']:.2f} seconds")
            print(f"Requests/sec: {stats['requests_per_second']:.2f}")
    
    def _print_analysis_results(self, results: dict):
        """분석 결과 출력"""
        print("\n" + "="*60)
        print("Analysis Results:")
        
        # 감정 분석
        if 'sentiment_analysis' in results:
            print("\nSentiment Analysis:")
            for key, value in results['sentiment_analysis'].items():
                print(f"  {key}: {value}")
        
        # 키워드
        if 'keywords' in results:
            print("\nTop Keywords:")
            for keyword, count in results['keywords'][:10]:
                print(f"  {keyword}: {count}")
        
        # 트렌드
        if 'trends' in results:
            print("\nTrends:")
            for trend, data in results['trends'].items():
                print(f"  {trend}: {data}")
    
    def _is_new_article(self, result: CrawlResult, storage) -> bool:
        """새 기사인지 확인"""
        # 간단한 구현 - 제목으로 확인
        existing = storage.get_by_title(result.title)
        return existing is None
    
    def _send_notification(self, result: CrawlResult):
        """알림 전송"""
        # 구현 필요 (이메일, 푸시 알림 등)
        self.logger.info(f"Notification: New article - {result.title}")
    
    def main(self):
        """메인 함수"""
        parser = argparse.ArgumentParser(
            description="뉴스 크롤러 - 다양한 웹 스크래핑 도구 활용"
        )
        
        subparsers = parser.add_subparsers(dest='command', help='명령')
        
        # crawl 명령
        crawl_parser = subparsers.add_parser('crawl', help='단일 URL 크롤링')
        crawl_parser.add_argument('url', help='크롤링할 URL')
        crawl_parser.add_argument('--type', choices=['requests', 'selenium', 'httpx'],
                                default='requests', help='크롤러 타입')
        crawl_parser.add_argument('--extract', action='store_true',
                                help='뉴스 데이터 추출')
        crawl_parser.add_argument('--comments', action='store_true',
                                help='댓글 추출')
        crawl_parser.add_argument('--metadata', action='store_true',
                                help='메타데이터 추출')
        crawl_parser.add_argument('--output', help='출력 파일')
        crawl_parser.add_argument('--output-format', 
                                choices=['json', 'html', 'text'],
                                default='json', help='출력 형식')
        crawl_parser.add_argument('--verbose', action='store_true',
                                help='상세 출력')
        
        # crawl-multiple 명령
        multi_parser = subparsers.add_parser('crawl-multiple', 
                                           help='여러 URL 크롤링')
        multi_parser.add_argument('urls_file', help='URL 목록 파일')
        multi_parser.add_argument('--type', choices=['requests', 'selenium', 'httpx'],
                                default='requests', help='크롤러 타입')
        multi_parser.add_argument('--concurrent', type=int,
                                help='동시 실행 수 (httpx only)')
        multi_parser.add_argument('--limit', type=int, default=100,
                                help='최대 크롤링 수')
        multi_parser.add_argument('--extract', action='store_true',
                                help='뉴스 데이터 추출')
        multi_parser.add_argument('--output', help='출력 파일')
        multi_parser.add_argument('--stats', action='store_true',
                                help='통계 출력')
        
        # analyze 명령
        analyze_parser = subparsers.add_parser('analyze', 
                                             help='크롤링 데이터 분석')
        analyze_parser.add_argument('input', help='입력 데이터 파일')
        analyze_parser.add_argument('--sentiment', action='store_true',
                                  help='감정 분석')
        analyze_parser.add_argument('--keywords', action='store_true',
                                  help='키워드 추출')
        analyze_parser.add_argument('--top-keywords', type=int, default=10,
                                  help='상위 키워드 수')
        analyze_parser.add_argument('--trends', action='store_true',
                                  help='트렌드 분석')
        analyze_parser.add_argument('--output', help='출력 파일')
        analyze_parser.add_argument('--verbose', action='store_true',
                                  help='상세 출력')
        
        # monitor 명령
        monitor_parser = subparsers.add_parser('monitor', 
                                             help='사이트 모니터링')
        monitor_parser.add_argument('site', help='모니터링할 사이트 URL')
        monitor_parser.add_argument('--interval', type=int, default=3600,
                                  help='확인 간격 (초)')
        monitor_parser.add_argument('--type', choices=['requests', 'selenium', 'httpx'],
                                  default='requests', help='크롤러 타입')
        monitor_parser.add_argument('--output-dir', help='출력 디렉토리')
        monitor_parser.add_argument('--notify', action='store_true',
                                  help='새 기사 알림')
        
        # 공통 옵션
        for p in [crawl_parser, multi_parser, monitor_parser]:
            p.add_argument('--user-agent', help='User-Agent 헤더')
            p.add_argument('--random-ua', action='store_true',
                         help='랜덤 User-Agent 사용')
            p.add_argument('--proxy', help='프록시 서버')
            p.add_argument('--proxy-file', help='프록시 목록 파일')
            p.add_argument('--timeout', type=int, default=30,
                         help='요청 타임아웃 (초)')
            p.add_argument('--retry', type=int, default=3,
                         help='재시도 횟수')
            p.add_argument('--delay', type=float, default=1.0,
                         help='요청 간 지연 (초)')
        
        # Selenium 전용 옵션
        for p in [crawl_parser, multi_parser, monitor_parser]:
            p.add_argument('--show-browser', action='store_true',
                         help='브라우저 표시 (Selenium)')
        
        args = parser.parse_args()
        
        if not args.command:
            parser.print_help()
            return
        
        # 명령 실행
        try:
            if args.command == 'crawl':
                self.crawl_single(args)
            elif args.command == 'crawl-multiple':
                self.crawl_multiple(args)
            elif args.command == 'analyze':
                self.analyze(args)
            elif args.command == 'monitor':
                self.monitor(args)
                
        except Exception as e:
            self.logger.error(f"Error: {e}")
            sys.exit(1)


if __name__ == "__main__":
    cli = NewsCrawlerCLI()
    cli.main()